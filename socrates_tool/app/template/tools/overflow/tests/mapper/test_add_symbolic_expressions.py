from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _add_symbolic_expressions as add_symbolic_expressions
import json

"""
This function defines the symbolic expression starting from the
declaration statements inside the function.
"""

class Test_add_symbolic_expressions(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_add_symbolic_expressions_number_from_state_var(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				int stateFoo = 4;
				function testFunction () public returns (string) {
					int bar = 5*stateFoo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('bar == 5 * stateFoo' in constraints)

	def test_add_symbolic_expressions_number_from_formal_param(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint paramFoo) public returns (string) {
					uint bar = 5*paramFoo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('bar == 5 * paramFoo' in constraints)

	def test_add_symbolic_expressions_number_from_local_var(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public returns (string) {
					uint paramFoo = 4;
					uint bar = 5*paramFoo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('bar == 5 * paramFoo' in constraints)

	def test_add_symbolic_expressions_number_from_state_list(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] stateFoo;
				function testFunction () public returns (string) {
					uint paramFoo = 4;
					uint bar = 5*stateFoo[0];
					uint foo = 3*stateFoo.length; 
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('bar == 5 * stateFoo[0]' in constraints)
		self.assertTrue('foo == 3 * stateFoo_length' in constraints)
		self.assertTrue('paramFoo == 4' in constraints)

	def test_add_symbolic_expressions_complex_expression(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] stateFoo;
				function testFunction () public returns (string) {
					uint paramFoo = 4;
					uint bar = 5*stateFoo[0];
					uint foo = bar+paramFoo / 3*stateFoo.length; 
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('bar == 5 * stateFoo[0]' in constraints)
		self.assertTrue('foo == bar + paramFoo / 3 * stateFoo_length' in constraints)
		self.assertTrue('paramFoo == 4' in constraints)


	# WARNING: CASTS are IGNORED!
	def test_add_symbolic_expressions_number_cast(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public returns (string) {
					uint paramFoo = 4;
					int bar = 5*int(paramFoo);
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('bar == 5 * paramFoo' in constraints)

	def test_add_symbolic_expressions_address_cast(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public returns (string) {
					address a = address(0x0);
					uint foo = 4;
					uint bar = 5*uint(a);
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('a == null_address' in constraints)
		self.assertTrue('bar == 5 * a' in constraints) # cast are just skipped

	def test_add_symbolic_expressions_bool_cast(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public returns (string) {
					bool a = true;
					uint foo = 4;
					uint bar = 5*uint(a);
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		with self.assertRaises(Exception) as context:
			inspected_obj = self.before_test(source)
		self.assertTrue(context.exception) # solidity cannot convert bool to int

	def test_add_symbolic_expressions_special_variables(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public returns (string) {
					uint foo = msg.value;
					uint bar = 4 * foo;
					address sender = msg.sender;
					address naddress = address(0);
					address naddress2 = address(0x0);
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['local_variables']
		constraints = add_symbolic_expressions(accessed_state_variables)
		self.assertTrue('foo == msg_value' in constraints)
		self.assertTrue('sender == msg_sender' in constraints)
		self.assertTrue('bar == 4 * foo' in constraints)
		self.assertTrue('naddress == null_address' in constraints)
		self.assertTrue('naddress2 == null_address' in constraints)