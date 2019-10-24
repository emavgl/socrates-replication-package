from modules import asthelper
from modules import expressionhelper


def filter_statements(events, statements_nodes):
	"""
	Analyzes all the statements passed to the function.
	Returns a list with the first not-banned statements
	:param events: List with the declaration IDs of the events
	:param statements_nodes: List of statements as a list of astnode
	:return: List<AstNode> | []
	"""
	banned = ["ForStatement", "IfStatement", "WhileStatement"]
	ignored = ['Assignment']
	events_ids = [x['id'] for x in events]

	return_list = []

	for node in statements_nodes:

		# if banned statement -> return current list
		if node['nodeType'] in banned or 'expression' in node and node['expression']['nodeType'] in banned:
			return return_list

		# if ignored statement -> skip
		if node['nodeType'] in ignored or 'expression' in node and node['expression']['nodeType'] in ignored:
			continue

		# if statement contains a function call
		#  - if require or type conversion -> add the statement
		#  - if it is an event -> just skip
		#  - otherwise -> reject

		function_call_node = asthelper.find_node(node, {"nodeType": "^FunctionCall$"})

		# Check the function call (typeConversion pass the check)
		# Skip the logs, save the require, abort if there is a custom function call
		if function_call_node and 'referencedDeclaration' in function_call_node['expression']:
			referenced_declaration = function_call_node['expression']['referencedDeclaration']

			is_an_event = referenced_declaration in events_ids
			is_a_require = 'name' in function_call_node['expression'] and function_call_node['expression']['name'] == 'require'

			if is_an_event:
				continue

			if not is_an_event and not is_a_require:
				# is a function call to a custom function
				return return_list

		return_list.append(node)

	return return_list


def check_for_overflow_candidate(node):
	"""
	Checks if the node contains an expression which can potentially produce an overflow
	meaning an expression which is not wrapped by any cast, which involves the operator
	+, ++, *, **. Note, the expression can have several sub-expression. It is the case
	of the expression (a + 3 > 0 && a * 3 > 5). In this case, the control is not just
	done for the first expression (which is the &&), but should be applied recursively
	to all the subexpression, until it founds the expression with one of the whitelisted
	operator.

	:param node: 	Node could be an Expression or AstNode (Tuple or Literal) in both cases, they have a dictionary called 'dic'.
	:return: List of tuples [(AstNode, {exp_id: expression}], where the AstNode is a node which of type Identifier
	and it is refereeing to a newly created variable called exp_id. The seconds object of the tuple is the map
	between the name of the variable added and its expression.
	"""

	# Check if in all the expression (also in depth) there is some operations
	expression_candidates = []
	whitelist_operators = ['+', '++', '*', '**', '-', '--']
	logic_operators = ['||', '&&', '>', '>=', '<', '<=', '==', '!=']

	# to let find_parent works
	if not node:
		return None

	if node.parent:
		node.parent = None

	first_expression = asthelper.find_node(node.dic, {'nodeType': r'.*Operation'})

	if not first_expression:
		# no expression it is or an identifier or a literal
		return None

	if asthelper.find_parent(first_expression, {'kind': 'typeConversion'}) is not None:
		# The expression is wrapped by a cast, if wrapped, can't be a candidate
		return None

	if first_expression['operator'] in whitelist_operators:
		exp_map = {}
		if 'name' not in first_expression.dic:
			# if not name, it is not a variable declaration
			# so expression is identifier
			exp_name = 'exp_{}'.format(first_expression.dic['id'])
			exp_map[exp_name] = expressionhelper.Expression(first_expression.dic)

			# override
			first_expression.dic['name'] = exp_name
			first_expression.dic['nodeType'] = 'Identifier'

		return [(first_expression, exp_map)]

	# recursive case
	if first_expression['operator'] in logic_operators:
		left_candidates = check_for_overflow_candidate(expressionhelper.Expression(first_expression['leftExpression']))
		right_candidates = check_for_overflow_candidate(expressionhelper.Expression(first_expression['rightExpression']))
		if left_candidates is not None: expression_candidates += left_candidates
		if right_candidates is not None: expression_candidates += right_candidates
		return expression_candidates

	return None


def visit_ast(ast_json: list, function_name: str) -> dict:
	"""
	Given the AST of the complete solidity source file and
	the function name of the function under test, visit_ast
	checks if the function has a list of valid statements
	which precede the last require statements (using the
	sub-function filter_statements) and collect information
	for later analysis such as the candidate variables
	for an overflow, variable declarations, accessed state
	variables and the require expressions.

	:param ast_json: ast of the file generated using solc
	:param function_name: str, function name under test
	:return: inspected_parameters: dict
	"""
	function_nodes = asthelper.find_all_nodes(ast_json, {'nodeType': 'FunctionDefinition', 'name': "^" + function_name + "$"})
	function_nodes_with_body = [x for x in function_nodes if x['body'] and x['body']['statements']]

	if not function_nodes_with_body:
		raise Exception("AstVisitErr", "No function definition")

	function_node = function_nodes_with_body[0]

	function_body = function_node['body']
	function_statements = function_body['statements']

	# ====
	# ==== EXTRACT STATEMENTS AND CHECKS VALIDITY
	# ====

	# Enumerate all the stataments with a require
	require_nodes = [i for (i, x) in enumerate(function_statements) if asthelper.find_node(x, {'name': '^require$'})]

	statements_under_inspection = function_statements

	# Remove event emit statements
	# Remove banned statements
	events_definition_nodes = asthelper.find_all_nodes(ast_json, {'nodeType': '^EventDefinition$'})

	filtered_statements = filter_statements(events_definition_nodes, statements_under_inspection)

	if not filtered_statements:
		raise Exception("AstVisitErr", "Not handled statements")

	# ====
	# ==== LOCAL VARIABLE DECLARATION
	# ====
	local_variables = [x for x in filtered_statements if x['nodeType'] == 'VariableDeclarationStatement']

	# remove local variable decleration without initial values
	local_variables = list(filter(lambda a: 'initialValue' in a and a['initialValue'], local_variables))

	# ====
	# ==== REQUIRES
	# ====

	"""
	Description: Test the function _add_require_condition_with_overflow

	Each require contains an expression, this expression, which is then used
	to evaluate a boolean formula can lead to an overflow. So it is important
	to extract from the expression which contains the candidate to overflow value
	an implicit symbolic variable that is then added as a normal overflow candidate.
	"""

	expression_candidates = []
	expressions_map = []
	requires_nodes = [x for x in filtered_statements if asthelper.find_node(x, {'name': '^require$'})]
	for require_node in requires_nodes:
		require_exp = expressionhelper.Expression(require_node['expression']['arguments'][0])
		candidate_check_results = check_for_overflow_candidate(require_exp)
		if candidate_check_results:
			candidates_exp = [x[0] for x in candidate_check_results]
			expression_map = [x[1] for x in candidate_check_results]
			expression_candidates += candidates_exp
			expressions_map += expression_map


	# ====
	# ==== CANDIDATE FOR OVERFLOW
	# ====
	# Check if there is a at least one candidate for overflow

	local_variables_candidates = []
	for lv in local_variables:
		name = lv['declarations'][0]['name']
		lv_exp = expressionhelper.Expression(lv['initialValue'])
		lv_exp.dic['name'] = name # set a name to the expression
		candidate_check_results = check_for_overflow_candidate(lv_exp)
		if candidate_check_results:
			candidate_exp, expression_map = candidate_check_results[0]
			local_variables_candidates.append(candidate_exp)

	variables_candidate_for_overflow = local_variables_candidates + expression_candidates

	if not variables_candidate_for_overflow:
		raise Exception("AstVisitErr", "No variable is a good candidate for overflow ")

	# ====
	# ==== ACCESSED STATE VARIABLES
	# ====
	# Enumerate all the state variables
	state_variables_declaration = \
		[x for x in asthelper.find_all_nodes(ast_json, {'nodeType': 'VariableDeclaration', 'stateVariable': True})]

	# Find the accessed variables
	# No repetition of variable accessed
	# multiple times
	accessed_state_variables = []
	for state_variable_declaration in state_variables_declaration:
		state_id = state_variable_declaration['id']
		for statement in filtered_statements:
			access = asthelper.find_node(statement, {'nodeType': 'Identifier', 'referencedDeclaration': state_id})
			if access:
				accessed_state_variables.append(state_variable_declaration)
				break

	# ====
	# ==== FORMAL PARAMETERS
	# ====
	# List the input parameters of the function under test
	formal_parameters = function_node['parameters']['parameters']

	map_id_variable_name = {}
	local_variables_tmp = [x['declarations'][0] for x in local_variables ]

	for v in local_variables_tmp + formal_parameters + accessed_state_variables:
		map_id_variable_name[str(v['id'])] = v['name']

	# append 'this' identifier
	this_identifiers = asthelper.find_all_nodes(ast_json, {'nodeType': 'Identifier', 'name': 'this'})

	for this_id in this_identifiers:
		map_id_variable_name[str(this_id['id'])] = this_id['name']
		map_id_variable_name[str(this_id['referencedDeclaration'])] = this_id['name']

	return {
		'formal_parameters': formal_parameters,
		'local_variables': local_variables,
		'require_nodes': requires_nodes,
		'require_expression_map': expressions_map,
		'candidate_for_overflow': variables_candidate_for_overflow,
		'accessed_state_variables': accessed_state_variables,
		'map_id_variable_name': map_id_variable_name
	}