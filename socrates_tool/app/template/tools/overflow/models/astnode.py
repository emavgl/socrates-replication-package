
from modules import expressionhelper

class AstNode:

	def __init__(self, parent, dic):
		self.parent = parent
		self.dic = dic

	def __getitem__(self, key: str) -> dict:
		"""
		Returns a dictionary, accessing with the "key" to the dictionary
		:rtype: dict
		"""
		if type(key) == 'string':
			raise Exception("The argument key must be a string")

		if key in self.dic:
			child = self.dic[key]
			if type(child) == 'list' and len(child) == 1:
				return child[0]

			return self.dic[key]

		return None

	def get_child(self, key: str):
		"""
		Returns the child as AstNode
		:rtype: AstNode
		"""
		return AstNode(self, self.dic[key])

	def to_string(self):

		if 'name' in self.dic:
			return self.dic['name']

		if 'value' in self.dic:
			if self.dic['value'] == 'true' or self.dic['value'] == 'false':
				return str(self.dic['value']).capitalize()
			else:
				return self.dic['value']

		if self.dic['nodeType'] == 'IndexAccess':
			baseExpression = AstNode(self.dic, self.dic['baseExpression']).to_string()
			indexExpression = AstNode(self.dic, self.dic['indexExpression']).to_string()

			if '[' in baseExpression and ']' in baseExpression:
				# it is a matrix
				newIndexExpression = baseExpression
				newIndexExpression = newIndexExpression.replace(']', '')
				newIndexExpression += '* accounts_len + ' + indexExpression + ']'
				return newIndexExpression

			return "{}[{}]".format(baseExpression, indexExpression)

		if self.dic['nodeType'] == 'MemberAccess':
			member_str = AstNode(self.dic, self.dic['expression']).to_string()
			member_name = self.dic['memberName']
			return "{}_{}".format(member_str, member_name)

		if self.dic['nodeType'] == 'FunctionCall':
			if self.dic['kind'] == 'typeConversion':
				if 'name' in self.dic['arguments'][0]:
					return str(self.dic['arguments'][0]['name'])
				elif 'value' in self.dic['arguments'][0]:
					value = str(self.dic['arguments'][0]['value'])
					type_of_conversion = str(self.dic['typeDescriptions']['typeString'])

					if 'x' in value:
						value = int(value, 16)

					if type_of_conversion:
						return 'null_address_index'

					return value
				else:
					raise  Exception("Error while casting")
			else:
				raise Exception('Conversion to string of type ' + self.dic['nodeType'] + ' not handled')

		if self.dic['nodeType'] == 'TupleExpression':
			if 'operator' in self.dic and self.dic['operator'] == '!':
				return 'Not({})'.format(AstNode(self.parent, self.dic['components'][0]).to_string())
			else:
				return '({})'.format(AstNode(self.parent, self.dic['components'][0]).to_string())


		if self.dic['nodeType'] in ['BinaryOperation', 'UnaryOperation']:
			return expressionhelper.Expression(self.dic, self.parent).to_string()

		return self.dic['nodeType']

	def to_sol_string(self):
		if 'name' in self.dic:
			return self.dic['name']

		if 'value' in self.dic:
			return self.dic['value']

		if self.dic['nodeType'] == 'IndexAccess':
			baseExpression = AstNode(self.dic, self.dic['baseExpression']).to_sol_string()
			indexExpression = AstNode(self.dic, self.dic['indexExpression']).to_sol_string()
			return "{}[{}]".format(baseExpression, indexExpression)

		if self.dic['nodeType'] == 'MemberAccess':
			member_str = AstNode(self.dic, self.dic['expression']).to_sol_string()
			member_name = self.dic['memberName']
			return "{}.{}".format(member_str, member_name)

		if self.dic['nodeType'] == 'FunctionCall':
			if self.dic['kind'] == 'typeConversion':
				if 'name' in self.dic['arguments'][0]:
					return str(self.dic['arguments'][0]['name'])
				elif 'value' in self.dic['arguments'][0]:
					value = str(self.dic['arguments'][0]['value'])
					type_of_conversion = str(self.dic['typeDescriptions']['typeString'])

					if 'x' in value:
						value = int(value, 16)

					if type_of_conversion:
						return 'address(0)'

					return value
				else:
					raise  Exception("Error while casting")
			else:
				raise Exception('Conversion to string of type ' + self.dic['nodeType'] + ' not handled')

		if self.dic['nodeType'] == 'TupleExpression':
			return '({})'.format(AstNode(self.parent, self.dic['components'][0]).to_sol_string())

		if self.dic['nodeType'] in ['BinaryOperation', 'UnaryOperation']:
			return expressionhelper.Expression(self.dic, self.parent).to_sol_string()

		return self.dic['nodeType']

