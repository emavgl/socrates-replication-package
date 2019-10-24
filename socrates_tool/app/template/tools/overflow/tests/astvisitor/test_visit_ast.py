from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast

"""
	visit_ast
	
	Given the AST of the complete solidity source file and
	the function name of the function under test, visit_ast
	checks if the function has a list of valid statements
	which precede the last require statements (using the
	sub-function filter_statements) and collect information
	for later analysis such as the candidate variables
	for an overflow, variable declarations, accessed state
	variables and the require expressions.
"""

class TestVisit_ast(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return ast_json, function_name

	def test_visit_ast_re_assigment(self):
		"""
		Check that does not raise an exception
		:return:
		"""
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					foo = 4;
					require(foo*5 > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)

	def test_visit_ast_not_requires(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint bar) public pure returns (string) {
					uint foo = 5*bar;
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		candidate_for_overflow = collected_obj['candidate_for_overflow']
		candidate_for_overflow_name = [x.dic['name'] for x in candidate_for_overflow]
		self.assertFalse(collected_obj['require_nodes'])
		self.assertTrue('foo' in candidate_for_overflow_name)
		self.assertFalse('bar' in candidate_for_overflow_name)

	def test_visit_ast_not_candidate_overflow(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					bool bar = true && false;
					uint foobar = 42 / 2;
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		with self.assertRaises(Exception) as context:
			collected_obj = visit_ast(ast_json, function_name)
		self.assertTrue('No variable is a good candidate for overflow' in str(context.exception))

	def test_visit_ast_not_candidate_overflow_unary(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					uint bar = foo++;
					uint foobar = 42 / 2;
					require(foo > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		with self.assertRaises(Exception) as context:
			collected_obj = visit_ast(ast_json, function_name)
		self.assertTrue('Unary' in str(context.exception))

	def test_visit_ast_candidate_overflow(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					uint bar = 5*foo;
					uint foobar = foo + bar;
					uint fooexp = foo**2;
					uint foominu = foo - 3;
					uint fooexpress = (foo + 4) / fooexp;
					uint fooexpress2 = (foo + 4) * fooexp;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		candidate_for_overflow = collected_obj['candidate_for_overflow']
		candidate_for_overflow_name = [x.dic['name'] for x in candidate_for_overflow]
		self.assertTrue('bar' in candidate_for_overflow_name)
		self.assertTrue('foobar' in candidate_for_overflow_name)
		self.assertTrue('fooexp' in candidate_for_overflow_name)
		self.assertTrue('foominu' not in candidate_for_overflow_name)
		self.assertTrue('fooexpress'  not in candidate_for_overflow_name)
		self.assertTrue('fooexpress2' in candidate_for_overflow_name)

	def test_visit_ast_candidate_overflow_with_cast(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					uint bar = uint8(5*foo);
					uint foobar = uint8(5*foo) + bar;
					uint fooexp = foo**2;
					require(fooexp > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		candidate_for_overflow = collected_obj['candidate_for_overflow']
		self.assertTrue(len(candidate_for_overflow) == 2)

	def test_visit_ast_variable_declaration(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					uint bar = 5*foo;
					uint foobar;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		variable_declaration = collected_obj['local_variables']
		variable_declaration_name = [x['declarations'][0]['name'] for x in variable_declaration]
		self.assertTrue('foo' in variable_declaration_name)
		self.assertTrue('bar' in variable_declaration_name)
		self.assertTrue('foobar' not in variable_declaration_name) # declaration without initial value do not handled

	def test_visit_ast_no_formal_parameters(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					uint foo = 5;
					uint bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		formal_parameters = collected_obj['formal_parameters']
		self.assertTrue(len(formal_parameters) == 0)


	def test_visit_ast_formal_parameters(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		formal_parameters = collected_obj['formal_parameters']
		formal_parameters_names = [x['name'] for x in formal_parameters]
		self.assertTrue(len(formal_parameters) == 1)
		self.assertTrue('foo' in formal_parameters_names)

	def test_visit_ast_no_accessed_state_variables(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		accessed_state_variables = collected_obj['accessed_state_variables']
		self.assertTrue(len(accessed_state_variables) == 0)

	def test_visit_ast_accessed_state_variables(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint myStateVariable;
				uint myNotAccessedStateVariable;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*myStateVariable;
					uint foobar = foo*myStateVariable;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		accessed_state_variables = collected_obj['accessed_state_variables']
		accessed_state_variables_names = [x['name'] for x in accessed_state_variables]
		self.assertTrue(len(accessed_state_variables) == 1)
		self.assertTrue('myStateVariable' in accessed_state_variables_names)
		self.assertFalse('myNotAccessedStateVariable' in accessed_state_variables_names)

	def test_visit_ast_accessed_state_variables_2(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				address stateFoo = 4;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					address a = stateFoo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		accessed_state_variables = collected_obj['accessed_state_variables']
		accessed_state_variables_names = [x['name'] for x in accessed_state_variables]
		self.assertTrue(len(accessed_state_variables) == 1)
		self.assertTrue('stateFoo' in accessed_state_variables_names)

	def test_visit_ast_requires(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint myStateVariable;
				uint myNotAccessedStateVariable;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*myStateVariable;
					require(bar > 5);
					require(myStateVariable > 3);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		requires = collected_obj['require_nodes']
		self.assertTrue(len(requires) == 2)

	def test_visit_ast_compile_error(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					require(bar > 5)
					require(myStateVariable > 3);
					return 'helloWorld';
				}
			}
		"""
		with self.assertRaises(Exception) as context:
			ast_json, function_name = self.before_test(source)
		self.assertTrue('AstCompileErr' in str(context.exception))


	def test_visit_ast_candidate_in_require_expression(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint foo;
				function testFunction () public returns (string) {
					uint bar = foo + 5;
					require(6 + foo > 5 * foo);
					return 'helloWorld';
				}
			}
		"""
		ast_json, function_name = self.before_test(source)
		collected_obj = visit_ast(ast_json, function_name)
		self.assertTrue(len(collected_obj['require_expression_map']) == 2)



