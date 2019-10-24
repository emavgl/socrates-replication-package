# TODO: Continue


from models import astnode

class Expression():

	def __init__(self, dic, parent = None):
		self.parent = parent
		self.dic = dic
		self.nodeType = self.dic['nodeType']
		self.operator = None
		self.leftArgument = None
		self.rightArgument = None

		operationsNodeType = ['BinaryOperation', 'UnaryOperation']

		if self.nodeType == 'BinaryOperation':
			self.operator = dic['operator']

			if self.dic['leftExpression']['nodeType'] in operationsNodeType:
				self.leftArgument = Expression(self.dic['leftExpression'], self.dic)
			else:
				self.leftArgument = astnode.AstNode(self.dic, self.dic['leftExpression'])
				self._convert_if_null_address(self.leftArgument, self.dic)

			if self.dic['rightExpression']['nodeType'] in operationsNodeType:
				self.rightArgument = Expression(self.dic['rightExpression'], self.dic)
			else:
				self.rightArgument = astnode.AstNode(self.dic, self.dic['rightExpression'])
				self._convert_if_null_address(self.rightArgument, self.dic)

		elif self.nodeType == 'UnaryOperation':
			self.operator = dic['operator']
			if self.operator in ['++', '--']:
				raise Exception('Unary expression not handled (because implicit assignments)')
			else:
				# -2, -4, +6
				self.rightArgument = astnode.AstNode(self.dic, self.dic['subExpression'])


			"""
			# code for later use
			self.operator = dic['operator']

			if self.operator not in ['++', '--']:
				raise Exception('Unary expression {} not handled'.format(self.operator))

			self.operator = dic['operator'][0]
			self.rightArgument = astnode.AstNode(self.parent, {'nodeType': 'Literal', 'value': 1})

			if self.dic['subExpression']['nodeType'] in operationsNodeType:
				self.leftArgument = Expression(self.dic['subExpression'], self.dic)
			else:
				self.leftArgument = astnode.AstNode(self.parent, self.dic['subExpression'])

			"""

	def __repr__(self):
		return self.to_string()

	def _convert_if_null_address(self, node, parent):
		if 'value' in node.dic and parent['commonType']['typeString'] == 'address':
			value = node.dic['value']
			if 'x' in value:
				value = int(value, 16)
			if int(value) == 0:
				node.dic['name'] = 'null_address_index'

	def to_string(self) -> str:
		"""
		Returns a string representing the Expression
		Convert to a Z3 conditions
		:rtype: str
		"""
		logic_operators = ['&&', '||']

		to_return = ""

		if self.operator is not None and self.operator in logic_operators:
			if self.operator == '&&':
				to_return += 'And({}, {})'.format(self.leftArgument.to_string(), self.rightArgument.to_string())
			if self.operator == '||':
				to_return += 'Or({}, {})'.format(self.leftArgument.to_string(), self.rightArgument.to_string())

		if self.operator is not None and self.operator not in logic_operators:
			if self.leftArgument is not None:
				to_return += '{} {} {}'.format(self.leftArgument.to_string(), self.operator, self.rightArgument.to_string())
			elif self.operator == '!':
				to_return += 'Not({})'.format(self.rightArgument.to_string())
			else:
				to_return += '{}{}'.format(self.operator, self.rightArgument.to_string())

		return to_return

	def to_sol_string(self) -> str:
		"""
		Convert to a Solidity Expression
		:rtype: str
		"""
		to_return = ""
		if self.operator is not None:
			if self.leftArgument is not None:
				to_return += '{} {} {}'.format(self.leftArgument.to_sol_string(), self.operator, self.rightArgument.to_sol_string())
			else:
				to_return += '{}{}'.format(self.operator, self.rightArgument.to_sol_string())

		to_return = to_return.replace('null_address_index', 'address(0x0)')
		return to_return


