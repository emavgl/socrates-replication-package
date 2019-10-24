from unittest import TestCase
from modules.astvisitor import filter_statements
from modules import asthelper

"""
	filter_statements docs:
	
	If there are no banned statements (loops, function call etc),
	returns a list of statements that precede the last require statement.
	Otherwise, it returns an empty list.
	
	:param events: List with the declaration IDs of the events
	:param nodeList: List of statements as a list of astnode
	:return: List<AstNode> | []
"""

class TestFilter_statements(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'

		function_node = asthelper.find_node(ast_json, {'nodeType': 'FunctionDefinition', 'name': function_name})
		function_body = function_node['body']
		function_statements = function_body['statements']

		# Enumerate all the stataments with a require
		require_nodes = [i for (i, x) in enumerate(function_statements) if asthelper.find_node(x, {'name': 'require'})]

		if not require_nodes:
			raise Exception("No requires")

		# stataments_under_inspection = All the stataments of the function until the last require (included)
		statements_under_inspection = function_statements[:require_nodes[-1] + 1]

		# Remove event emit statements
		# Remove banned statements
		events_definition_nodes = asthelper.find_all_nodes(ast_json, {'nodeType': 'EventDefinition'})

		return events_definition_nodes, statements_under_inspection

	def test_number_of_valid_statements(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		events, statements = self.before_test(source)
		statement_under_test = filter_statements(events, statements)
		self.assertTrue(len(statement_under_test) == 2)

	def test_not_valid_function_loop(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					for (uint i = 0; i < 5; i++){
						uint a = i;
					}
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		events, statements = self.before_test(source)
		statement_under_test = filter_statements(events, statements)
		self.assertTrue(len(statement_under_test) == 0)

	def test_not_valid_function_function_call(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function getNumber () public pure returns (uint) {
					uint foo = 5;
					return foo;
				}
				
				function testFunction () public pure returns (string) {
					uint foo = 5;
					uint bar = getNumber();
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		events, statements = self.before_test(source)
		self.assertTrue(len(statements) > 0)
		statement_under_test = filter_statements(events, statements)
		self.assertTrue(len(statement_under_test) == 0)

	def test_not_valid_function_assignment(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					foo = 6;
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		events, statements = self.before_test(source)
		self.assertTrue(len(statements) > 0)
		statement_under_test = filter_statements(events, statements)
		print(len(statement_under_test))
		self.assertTrue(len(statement_under_test) == 2) # foo and requ are ok, foo re-assigment is skipped

	def test_not_valid_function_condition(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					if (foo > 0) {
						uint bar = 4;
					}
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		events, statements = self.before_test(source)
		self.assertTrue(len(statements) > 0)
		statement_under_test = filter_statements(events, statements)
		self.assertTrue(len(statement_under_test) == 0)

	def test_valid_function_cast(self):
		"""
			type casts are not consider as function call
			they are consider as valid statements
			and should be properly handle during the mapping
			from solidity to z3
		"""
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				event TestEvent(uint t);
				function testFunction () public returns (string) {
					uint foo = 5;
					uint bar = uint8(foo);
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		events, statements = self.before_test(source)
		self.assertTrue(len(statements) > 0)
		statement_under_test = filter_statements(events, statements)
		self.assertTrue(len(statement_under_test) == 3)

	def test_valid_function_emitted_events(self):
		"""
			the function should ignore all the emit events
			statements
		"""
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				event TestEvent(uint t);
				function testFunction () public returns (string) {
					uint foo = 5;
					emit TestEvent(foo);
					uint bar = uint8(foo);
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		events, statements = self.before_test(source)
		self.assertTrue(len(statements) > 0)
		self.assertTrue(len(events) == 1)
		statement_under_test = filter_statements(events, statements)
		self.assertTrue(len(statement_under_test) == 3)

