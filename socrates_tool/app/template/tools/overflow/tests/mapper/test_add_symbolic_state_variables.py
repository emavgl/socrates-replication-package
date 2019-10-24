from unittest import TestCase
from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _add_symbolic_state_variables as add_symbolic_state_variables
import json

class Test_add_symbolic_state_variables(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_add_symbolic_state_variables_int(self):
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
		accessed_state_variables = inspected_obj['accessed_state_variables']
		constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('stateFoo = Int' in constraints)
		self.assertTrue('stateFoo >= 0' not in constraints)
		self.assertTrue('stateFoo_concrete' in constraints)
		self.assertTrue('stateFoo == stateFoo_concrete' in constraints)

	def test_add_symbolic_state_variables_uint(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint stateFoo = 4;
				function testFunction () public returns (string) {
					uint bar = 5*stateFoo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('stateFoo = Int' in constraints)
		self.assertTrue('stateFoo >= 0' in constraints)
		self.assertTrue('stateFoo_concrete' in constraints)
		self.assertTrue('stateFoo == stateFoo_concrete' in constraints)

	def test_add_symbolic_state_variables_address(self):
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
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('stateFoo = Int' in constraints)
		self.assertTrue('stateFoo >= 0' in constraints)
		self.assertTrue('stateFoo < accounts_len' in constraints)
		self.assertTrue('stateFoo_concrete' in constraints)
		self.assertTrue('stateFoo == stateFoo_concrete' in constraints)

	def test_add_symbolic_state_variables_bool(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				bool stateFoo = true;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					bool a = stateFoo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('stateFoo = Bool' in constraints)
		self.assertTrue('stateFoo_concrete' in constraints)
		self.assertTrue('stateFoo == stateFoo_concrete' in constraints)

	def test_add_symbolic_state_variables_bytes(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				byte stateFoo;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					byte a = stateFoo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		with self.assertRaises(Exception) as context:
			constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('not handled' in str(context.exception))

	def test_add_symbolic_state_variables_list(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint8[4] stateFoo;
				uint8[] stateFoo2;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					uint a = stateFoo[0];
					uint b = stateFoo2.length;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('stateFoo_length' in constraints) # not symbolic
		self.assertTrue('stateFoo_concrete' in constraints) # not symbolic py list
		self.assertTrue('stateFoo = Array(' in constraints) # z3 array
		self.assertTrue('stateFoo2_length' in constraints) # not symbolic
		self.assertTrue('stateFoo2_concrete' in constraints) # not symbolic py list
		self.assertTrue('stateFoo2 = Array(' in constraints) # z3 array

	def test_add_symbolic_state_variables_not_number_list(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				bytes32[] stateFoo2;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					uint b = stateFoo2.length;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		with self.assertRaises(Exception) as context:
			constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('not handled' in str(context.exception))

	def test_add_symbolic_state_variables_address_map(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				mapping (address => uint) public balances;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					uint b = balances[address(0)];
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('balances_concrete' in constraints) # not symbolic py list
		self.assertTrue('balances = Array(' in constraints) # z3 array


	def test_add_symbolic_state_variables_not_address_map(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				mapping (uint => uint) public balances;
				function testFunction (uint foo) public returns (string) {
					uint bar = 5*foo;
					uint b = balances[0];
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['accessed_state_variables']
		with self.assertRaises(Exception) as context:
			constraints = add_symbolic_state_variables(accessed_state_variables)
		self.assertTrue('not handled' in str(context.exception))