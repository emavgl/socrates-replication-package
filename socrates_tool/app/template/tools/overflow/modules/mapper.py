import re
from modules import expressionhelper
from models import astnode
from collections import ChainMap


def _add_symbolic_constraints(local_variables: [dict], formal_variables) -> str:
	"""
	Add symbolic constraints - based on types - for local variables and formal variables.
	:param local_variables:
	:param formal_variables:
	:return: conditions
	"""

	symb_var_const_str = "\n# === SYM VARIABLES CONSTRAINTS ===\n"

	# === Add type constraints to formal variables
	# === Note: formal parameters are different from local one
	# because their value cannot overflow/underflow
	# since their are passed as function parameters
	# and their value will remain the same becouse our
	# not-reassignment assumption
	for fvar in formal_variables:

		name = fvar['name']
		vtype = fvar['typeDescriptions']['typeString']

		if '[]' in vtype:

			# Constraint for an array
			name_len = name+'_length'
			symb_var_const_str += "solver.add({} >= 0, {} < max_array_len)\n".format(name_len, name_len)

			if 'address' in vtype:
				# address[] foo

				symb_var_const_str += 'for x in {}: solver.add(x < accounts_len)\n'.format(name)
				symb_var_const_str += "solver.add({} == Sum([If(x >= 0, 1, 0) for x in {}]))\n".format(name_len, name)
				symb_var_const_str += "if (args.distinct): solver.add(Distinct({0}))\n".format(name)

			elif vtype.startswith('uint'):
				# uint8[] foo

				numbers = re.findall(r'\d+', vtype)
				if not numbers: numbers = ['256']
				symb_var_const_str += 'for x in {}: solver.add(x < max_uint({}))\n'.format(name, numbers[0])
				symb_var_const_str += "solver.add({} == Sum([If(x >= 0, 1, 0) for x in {}]))\n".format(name_len, name)
				symb_var_const_str += "if (args.distinct): solver.add(Distinct({0}))\n".format(name)

			elif vtype.startswith('int'):
				# int8[] foo
				# int[] foo

				numbers = re.findall(r'\d+', vtype)
				if not numbers: numbers = ['256']
				symb_var_const_str += 'for x in {}: solver.add(x < max_int({}))\n'.format(name, numbers[0])
				symb_var_const_str += "solver.add({0} == Sum([If(x >= min_int({1}), 1, 0) for x in {2}]))\n".format(name_len, numbers[0], name)
				symb_var_const_str += "if (args.distinct): solver.add(Distinct({0}))\n".format(name)

			else:
				# Type not handled exception
				# This means we don't have additional constraints
				# but the type could be a valid type, for example,
				# a boolean as formal parameter
				pass

		else:
			# Constraint for an elementary type

			if 'address' in vtype:
				symb_var_const_str += 'solver.add({0} >= 0, {0} < accounts_len)\n'.format(name)
			elif vtype.startswith('uint'):
				numbers = re.findall(r'\d+', vtype)
				if not numbers: numbers = ['256']
				symb_var_const_str += 'solver.add({0} >= 0, {0} < max_uint({1}))\n'.format(name, numbers[0])
			elif vtype.startswith('int'):
				numbers = re.findall(r'\d+', vtype)
				if not numbers: numbers = ['256']
				symb_var_const_str += 'solver.add({0} >= min_int({1}), {0} < max_int({1}))\n'.format(name, numbers[0])
			else:
				# Type not handled exception
				# This means we don't have additional constraints
				# but the type could be a valid type, for example,
				# a boolean as formal parameter
				pass

	# === Add type constraints to local variables
	# === Note: local variables are those variables that can overflow
	for lvar in local_variables:

		name = lvar['name']
		vtype = lvar['typeDescriptions']['typeString']

		if '[]' in vtype:
			# ONLY THE LENGTH IS HANDLED
			name_len = name+'_length'
			symb_var_const_str += "solver.add({0} >= 0, {0} < max_array_len)\n".format(name_len)
		else:

			# Constraint for an elementary type

			if 'address' in vtype:
				symb_var_const_str += 'solver.add({0} >= 0, {0} < accounts_len)\n'.format(name)
			elif vtype.startswith('uint'):
				# remove constraints if we consider also the underflow conditions
				pass
			else:
				# Type not handled exception
				# Just ignored, it could be that
				# the value is never used in the future
				pass

	symb_var_const_str += "solver.add(msg_sender == user_address_index)\n"

	return symb_var_const_str + "\n\n"


def _add_symbolic_variables_declaration(local_variables: [dict], formal_variables) -> str:
	"""
	Declare symbolic variables for variables declaration and formal variables
	:param local_variables:
	:param formal_variables:
	:return: conditions
	"""
	symb_var_declaration_str = "\n# === FORMAL PARAMETERS AND LOCAL VARIABLES ===\n"
	symbolic_variables = local_variables + formal_variables

	# Check for unhandled type
	for sym_var in symbolic_variables:
		type_string = sym_var['typeDescriptions']['typeString']
		if 'byte' in type_string or 'string' in type_string:
			raise Exception("Z3MapperErr", 'Not handled symbolic variable')

	# === Declare symbolic variables
	# = Declare Z3'Int variables
	list_of_variables_str = ""
	for sym_var in symbolic_variables:
		type_string = sym_var['typeDescriptions']['typeString']
		if '[' not in type_string and 'bool' not in type_string:
			list_of_variables_str += sym_var['name'] + ", "

	list_of_variables_str = list_of_variables_str.strip()
	symb_var_declaration_str += "{0} = Ints('{1}')\n\n".format(list_of_variables_str, list_of_variables_str.replace(",", ""))

	# === Declare symbolic variables
	# = Declare Z3'Bool variables
	list_of_variables_str = ""
	for sym_var in symbolic_variables:
		type_string = sym_var['typeDescriptions']['typeString']
		if '[' not in type_string and 'bool' in type_string:
			list_of_variables_str += sym_var['name'] + ", "

	if list_of_variables_str:
		list_of_variables_str = list_of_variables_str[:-2]
		symb_var_declaration_str += "{0} = Bool('{1}')\n\n".format(list_of_variables_str, list_of_variables_str.replace(",", ""))

	# = Declare array variables
	for sym_var in symbolic_variables:
		type_string = sym_var['typeDescriptions']['typeString']

		if '[' in type_string and ']' in type_string:

			name = sym_var['name']
			name_len = name+'_length'

			if 'bool' in type_string:
				symb_var_declaration_str += "{} = BoolVector('{}', max_array_len)\n".format(name, name)
			else:
				symb_var_declaration_str += "{} = IntVector('{}', max_array_len)\n".format(name, name)

			symb_var_declaration_str += "{} = Int('{}')\n".format(name_len, name_len)

	return symb_var_declaration_str + "\n\n"


def _add_symbolic_state_variables(state_variables) -> str:
	"""
	It looks at the accesses state variables and add their Z3's declaration in addiction to their constraints.
	:param state_variables:
	:return: str: conditions
	"""
	symb_state_variable = "\n# === SYMBOLIC STATE VARIABLES INITIALIZATION ===\n"

	for var in state_variables:
		type_string = var['typeDescriptions']['typeString']
		name = var['name']

		if 'mapping' in type_string:
			number_of_indexes = type_string.count('mapping')
			number_of_addresses = type_string.count('address')

			if number_of_indexes != number_of_addresses:
				# TODO? Do exist different indexes?
				# For example, could a map be also int -> int?
				# For sure could exists different indexes.
				# However, since values are copied inside symbolic array
				# indexes should have a bound. In case of address, the bound
				# is the length of the account list.
				# otherwise it is not feasible to access the map 2**256 times
				# and copy all the values.
				raise Exception("Z3MapperErr", 'Indexes different than addresses are not handled.')

			symb_state_variable += "accounts_list = [accounts_concrete]*{}\n".format(number_of_addresses)
			symb_state_variable += "{0}_concrete = [get_state_variable(contract_instance, '{0}', *x) for x in list(itertools.product(*accounts_list))]\n".format(name)
			if 'bool' in type_string:
				symb_state_variable += "{0} = Array('{0}', IntSort(), BoolSort())\n".format(name)
			else:
				symb_state_variable += "{0} = Array('{0}', IntSort(), IntSort())\n".format(name)
			symb_state_variable += "i = 0\n"
			symb_state_variable += "for value in {}_concrete:\n".format(name)
			symb_state_variable += "    {0} = Store({0}, i, value); i = i + 1\n\n".format(name)

		elif '[' in type_string and ']' in type_string:

			# IMPLEMENTATION:
			# instrumentation of the code it is needed to add getter function for array length
			# https://ethereum.stackexchange.com/questions/20812/get-array-length-without-a-getter-from-other-contract

			# State list are mapped in Z3's array, because with our assumption (no assignment)
			# the values of the list are not modified inside the functions, but only accessed.
			# If Z3 has not to determine concrete values for each symbolic array's entry
			# we could map the value in a Z3's array

			# In contrast to what we have see before, in solidity I can access
			# the value .length of the list. And knowing the bound, it
			# should be possible to access the list and copy its values
			# inside a Z3's Array.

			if 'int' not in type_string:
				raise Exception("Z3MapperErr", 'Arrays value different than numbers are not handled.')

			symb_state_variable += "{0}_length = get_state_variable(contract_instance, 'get_{0}_len')\n".format(name)
			symb_state_variable += "{0}_concrete = [get_state_variable(contract_instance, '{0}', x) for x in range({0}_length)]\n".format(name)
			symb_state_variable += "{} = Array('{}', IntSort(), IntSort())\n".format(name, name)
			symb_state_variable += "i = 0\n"
			symb_state_variable += "for value in {}_concrete:\n".format(name)
			symb_state_variable += "    {} = Store({}, i, value); i = i + 1\n\n".format(name, name)
		else:
			# It is an elementary type, no index is required
			symb_state_variable += "{0}_concrete = get_state_variable(contract_instance, '{0}')\n".format(name)
			if type_string.startswith('bool'):
				symb_state_variable += "{} = Bool('{}')\n".format(name, name)
			elif 'int' in type_string:
				symb_state_variable += "{} = Int('{}')\n".format(name, name)
				if 'u' in type_string:
					symb_state_variable += "solver.add({} >= 0)\n".format(name)
			elif type_string.startswith('address'):
				symb_state_variable += "{0}_concrete = accounts_concrete.index({0}_concrete)\n".format(name)
				symb_state_variable += "{} = Int('{}')\n".format(name, name)
				symb_state_variable += 'solver.add({0} >= 0, {0} < accounts_len)\n'.format(name)
			elif name == 'this':
				# do nothing, this is handled in top_template as concrete value
				pass
			else:
				raise Exception("Z3MapperErr", 'Type of the state variable is not handled.')

			symb_state_variable += "solver.add({} == {}_concrete)\n".format(name, name)

	return symb_state_variable + "\n\n"


def _add_symbolic_expressions(local_variables, map_id_variable_name) -> str:
	"""
	Convert a solidity expression at the right of a local variable declaration
	in a Z3 expression.

	WARNING: casts are not handled. If there is a cast, it is simple ignored.
	anyway it is very important to handle casts in the future, for instance,
	take in consideration this code:

	uint cast;
    function play() public returns (uint) {
    	int testNumber = -1;
        uint cast = uint(testNumber);
        return cast + 2; # overflow
    }

    If testNumber is a negative number, cast variable will result in a very huge number.
    Anyway, casts are very difficult to handle, because of the Z3 limitation and because
    it requires further static analysis, not only int -> uint, but also uint -> uint8
    for example.

	:param local_variables:
	:return: conditions: str
	"""

	# For each local variable
	# Inspect its definition (right expression)

	sym_var_initialization_str = "\n# === SYMBOLIC VARIABLES INITIALIZATION ===\n"
	for lvar in local_variables:

		declared_variable_name = lvar['declarations'][0]['name']
		initialValue = lvar['initialValue']
		nodeType = initialValue['nodeType']

		if nodeType == 'MemberAccess':
			base_variable = initialValue['expression']['name']
			member_name = initialValue['memberName']
			if base_variable == 'msg' and (member_name == 'value' or member_name == 'sender' or member_name == 'gas'):
				sym_var_initialization_str += "solver.add({} == {}_{})\n".format(
					declared_variable_name, base_variable, member_name)
			elif member_name == 'length':
				sym_var_initialization_str += "solver.add({} == {})\n".format(declared_variable_name, base_variable + '_length')
			else:
				raise Exception("Z3MapperErr", 'Member access not handled')
		elif nodeType == 'BinaryOperation':
			s = expressionhelper.Expression(initialValue)
			sym_var_initialization_str += "solver.add({} == {})\n".format(declared_variable_name, s)
		elif nodeType == 'Literal':
			value = initialValue['value']
			sym_var_initialization_str += "solver.add({} == {})\n".format(declared_variable_name, value)
		elif nodeType == 'Identifier':
			referenced_variable_id = initialValue['referencedDeclaration']
			value = map_id_variable_name[str(referenced_variable_id)]
			sym_var_initialization_str += "solver.add({} == {})\n".format(declared_variable_name, value)
		elif nodeType == 'UnaryOperation':
			raise Exception('Unary expression not handled because implicit assignment')
		elif nodeType == 'FunctionCall':
			value = astnode.AstNode(None, initialValue['arguments'][0]).to_string().replace('x', '')
			if initialValue['typeDescriptions']['typeString'] == "address" and 0 == int(value):
				value = 'null_address_index'
			sym_var_initialization_str += "solver.add({} == {})\n".format(declared_variable_name, value)
		else:
			err_msg = 'nodeType {0}({1}) not handled in variable initialization'.format(nodeType, declared_variable_name)
			raise Exception("Z3MapperErr", err_msg)

	return sym_var_initialization_str + "\n\n"


def _add_overflow_constraints(candidate_variable_for_overflow) -> str:
	"""
	Add a constraints for overflow candidates (both candidates from variable
	declaration and expression candidates inside the requires)

	:param candidate_variable_for_overflow:
	:return: conditions: str
	"""
	overflow_constraints_str = "\n# === OVERFLOW CONSTRAINTS ===\n"

	variables_overflow_str = ""
	for v in candidate_variable_for_overflow:
		name = v.dic['name']
		vtype = v.dic['typeDescriptions']['typeString']
		numbers = re.findall(r'\d+', vtype)
		if not numbers:
			numbers = ['256']
		number_of_bytes = numbers[0]
		if 'u' in vtype:
			variables_overflow_str += 'u_is_overflow({}, {}) == True,'.format(name, number_of_bytes)
		else:
			variables_overflow_str += 'is_overflow({}, {}) == True,'.format(name, number_of_bytes)

	variables_overflow_str = variables_overflow_str[:-1]

	overflow_constraints_str += "solver.add(Or({}))\n".format(variables_overflow_str)

	# for each candidate variable
	# add z3 constraints
	# {variable_name}_actual_value == afterOverflow() ...
	for v in candidate_variable_for_overflow:
		name = v.dic['name']
		vtype = v.dic['typeDescriptions']['typeString']
		numbers = re.findall(r'\d+', vtype)
		if not numbers:
			numbers = ['256']
		number_of_bytes = numbers[0]
		if 'u' in vtype:
			overflow_constraints_str += "{}_actual_value = Int('{}_actual_value')\n".format(name, name)
			overflow_constraints_str += "solver.add({}_actual_value >= 0)\n".format(name)
			overflow_actual_value = \
				"{0}_actual_value == If(u_is_overflow({0}, {1}), u_overflow_value({0}, {1}), {0})".format(
					name, number_of_bytes)
			overflow_constraints_str += "solver.add({})\n".format(overflow_actual_value)
		else:
			overflow_constraints_str += "{}_actual_value = Int('{}_actual_value')\n".format(name, name)
			overflow_actual_value = \
				"{0}_actual_value == If(is_overflow({0}, {1}), overflow_value({0}, {1}), {0})".format(
					name, number_of_bytes)
			overflow_constraints_str += "solver.add({})\n".format(overflow_actual_value)

	return overflow_constraints_str + '\n\n'


def _requires_constraints(requires) -> str:
	"""
	Get the expression inside the require, and create a Z3 condition for
	each of them.
	:param requires:
	:return:
	"""
	requires_constraints_str = "\n# === REQUIRES CONSTRAINTS ===\n"
	for require in requires:
		argument = require['expression']['arguments'][0]
		base_str = 'solver.add({})\n'.format(astnode.AstNode(None, argument).to_string())
		requires_constraints_str += base_str
	return requires_constraints_str + "\n\n"


def _add_require_condition_with_overflow(require_conditions_str, candidate_variable_for_overflow) -> str:
	"""
	Get the Z3 conditions extracted using the requires_constraints function,
	and replace each candidate variable with its overflowed symbolic variables
	called <candidate_name>_actual_value
	:param require_conditions_str:
	:param candidate_variable_for_overflow:
	:return:
	"""
	for v in candidate_variable_for_overflow:
		name = v.dic['name']
		reg = re.compile(r"(^|\s|\W)({})(\s|\W|$)".format(re.escape(name)))
		require_conditions_str = re.sub(reg, '\g<1>\g<2>_actual_value\g<3>', require_conditions_str)

	return require_conditions_str + "\n\n"


def _add_symbolic_require_expressions(require_expression_map: list) -> str:
	"""
	Declare Z3 symbolic variable and expression for newly created variable
	from the overflow expression inside the requires
	:param require_expression_map:
	:return: str: variable declarations and conditions
	"""
	conditions = "\n# === SYMBOLIC REQUIRE-OVERFLOW-EXPRESSION ===\n"

	if not require_expression_map:
		return conditions

	require_expression_map = dict(ChainMap(*require_expression_map))
	key_list_left = ','.join(list(require_expression_map.keys()))
	key_list_right = ' '.join(list(require_expression_map.keys()))
	conditions += "{}, = Ints('{}')\n".format(key_list_left, key_list_right)

	for key, value in require_expression_map.items():
		expression_str = value.to_string()
		conditions += "solver.add({} == {})\n".format(key, expression_str)

	return conditions + "\n\n"


def ast_to_z3(inspected_function: dict):
	"""
	Get the inspected object from the ast visit
	and call each mapper from extracted object to its generated Z3 conditions
	then, concatenate their results in a single string.

	:param inspected_function generated from the AST Visit
	:return:
	"""
	local_variables = [x['declarations'][0] for x in inspected_function['local_variables']]

	formal_parameters = inspected_function['formal_parameters']

	symbolic_state_variables = _add_symbolic_state_variables(inspected_function['accessed_state_variables'])
	symbolic_variable_decl_str = _add_symbolic_variables_declaration(local_variables, formal_parameters)
	symbolic_variable_constraints_str = _add_symbolic_constraints(local_variables, formal_parameters)
	symbolic_expressions = _add_symbolic_expressions(
		inspected_function['local_variables'], inspected_function['map_id_variable_name'])
	symbolic_require_expression = _add_symbolic_require_expressions(inspected_function['require_expression_map'])

	overflow_constraints = _add_overflow_constraints(inspected_function['candidate_for_overflow'])
	require_conditions = _requires_constraints(inspected_function['require_nodes'])
	require_conditions_overflow = _add_require_condition_with_overflow(
		require_conditions, inspected_function['candidate_for_overflow'])

	generate_str = symbolic_state_variables + symbolic_variable_decl_str
	generate_str = generate_str + symbolic_variable_constraints_str
	generate_str = generate_str + symbolic_expressions + symbolic_require_expression
	generate_str = generate_str + overflow_constraints + require_conditions_overflow

	return generate_str
