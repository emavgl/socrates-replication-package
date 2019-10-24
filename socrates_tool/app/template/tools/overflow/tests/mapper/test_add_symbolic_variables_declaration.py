from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _add_symbolic_variables_declaration as add_symbolic_variables_declaration
import json

class Test_add_symbolic_variables_declaration(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_add_symbolic_variables_declaration_uint(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					uint8 bar2 = 3;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_variables_declaration(local_variables, formal_parameters)
		self.assertTrue('bar' in constraints)
		self.assertTrue('bar2' in constraints)
		self.assertTrue('foo' in constraints)

	def test_add_symbolic_variables_declaration_int(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					int8 bar2 = int8(3*foo);
					require(bar2 > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_variables_declaration(local_variables, formal_parameters)
		self.assertTrue('bar' in constraints)
		self.assertTrue('bar2' in constraints)
		self.assertTrue('foo' in constraints)

	def test_add_symbolic_variables_declaration_bool(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					bool foobar = true;
					bool foobar2;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_variables_declaration(local_variables, formal_parameters)
		self.assertTrue('= Bool(' in constraints)
		self.assertTrue('foobar' in constraints)
		self.assertTrue('foobar2' not in constraints) # no initialization

	def test_add_symbolic_variables_declaration_bool_list(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					bool foobar = true;
					bool[] foobar2;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_variables_declaration(local_variables, formal_parameters)
		self.assertTrue('= Bool(' in constraints)
		self.assertTrue('foobar2 = BoolVector(' not in constraints) # no initialization
		self.assertTrue('foobar2_length = Int(' not in constraints) # no initialization
		self.assertTrue('foobar' in constraints)

	def test_add_symbolic_variables_declaration_address(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, address foobar) public pure returns (string) {
					int bar = 5*foo;
					address foobar2;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_variables_declaration(local_variables, formal_parameters)
		self.assertTrue('foobar' in constraints)
		self.assertTrue('foobar2' not in constraints) # no initialization, no variable

	def test_add_symbolic_variables_declaration_list(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, int[] foobar) public pure returns (string) {
					int bar = 5*foo;
					uint[] foobar2;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_variables_declaration(local_variables, formal_parameters)
		self.assertTrue('foobar2 = IntVector' not in constraints) # do not consider because no initialvalue
		self.assertTrue('foobar2_length = Int' not in constraints)
		self.assertTrue('foobar = IntVector' in constraints)
		self.assertTrue('foobar_length = Int' in constraints)

	def test_add_symbolic_variables_declaration_string(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, int[] foobar) public pure returns (string) {
					int bar = 5*foo;
					var a = "4";
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		with self.assertRaises(Exception) as context:
			constraints = add_symbolic_variables_declaration(local_variables, formal_parameters)
		self.assertTrue('Not handled' in str(context.exception))
