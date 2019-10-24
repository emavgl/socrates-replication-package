from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _add_symbolic_constraints as add_symbolic_constraints
import json

class Test_add_symbolic_constraints(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_add_symbolic_constraints_formal_uint(self):
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
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('bar >= 0' not in constraints) # because can overflow
		self.assertTrue('bar <= max_uint(256)' not in constraints) # because can overflow
		self.assertTrue('foo >= 0' in constraints)
		self.assertTrue('foo < max_uint(256)' in constraints) # formal parameter can't be greater than max

	def test_add_symbolic_constraints_formal_uint8(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint8 foo) public pure returns (string) {
					uint8 bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('bar >= 0' not in constraints) # because can overflow
		self.assertTrue('bar <= max_uint(8)' not in constraints) # because can overflow
		self.assertTrue('foo >= 0' in constraints)
		self.assertTrue('foo < max_uint(8)' in constraints) # formal parameter can't be greater than max


	def test_add_symbolic_constraints_formal_int(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('bar >= 0' not in constraints) # because can overflow
		self.assertTrue('bar <= max_int(256)' not in constraints) # because can overflow
		self.assertTrue('foo >= min_int(256)' in constraints)
		self.assertTrue('foo < max_int(256)' in constraints) # formal parameter can't be greater than max

	def test_add_symbolic_constraints_formal_int8(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int8 foo) public pure returns (string) {
					int8 bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('bar >= 0' not in constraints) # because can overflow
		self.assertTrue('bar <= max_int(8)' not in constraints) # because can overflow
		self.assertTrue('foo >= min_int(8)' in constraints)
		self.assertTrue('foo < max_int(8)' in constraints) # formal parameter can't be greater than max


	def test_add_symbolic_constraints_formal_bool(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, bool foobar) public pure returns (string) {
					int bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('foobar' not in constraints) # WARNING: not handled values are simply ignored

	def test_add_symbolic_constraints_formal_list_uint(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, uint[] foobar) public pure returns (string) {
					int bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('foobar_length >= 0' in constraints)
		self.assertTrue('foobar_length < max_array_len' in constraints)
		self.assertTrue('x in foobar: solver.add(x < max_uint(256)' in constraints) # no lowerbound to handle length
		self.assertTrue('foobar_length == Sum([If(x >= 0, 1, 0) for x in foobar]))' in constraints)
		self.assertTrue('(args.distinct): solver.add(Distinct(foobar))' in constraints)

	def test_add_symbolic_constraints_formal_list_int(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, int[] foobar) public pure returns (string) {
					int bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('foobar_length >= 0' in constraints)
		self.assertTrue('foobar_length < max_array_len' in constraints)
		self.assertTrue('x in foobar: solver.add(x < max_int(256)' in constraints) # no lowerbound to handle length
		self.assertTrue('foobar_length == Sum([If(x >= min_int(256), 1, 0) for x in foobar]))' in constraints)
		self.assertTrue('(args.distinct): solver.add(Distinct(foobar))' in constraints)

	def test_add_symbolic_constraints_formal_list_address(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, address[] foobar) public pure returns (string) {
					int bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('foobar_length >= 0' in constraints)
		self.assertTrue('foobar_length < max_array_len' in constraints)
		self.assertTrue('x in foobar: solver.add(x < accounts_len)' in constraints) # no lowerbound to handle length
		self.assertTrue('foobar_length == Sum([If(x >= 0, 1, 0) for x in foobar]))' in constraints)
		self.assertTrue('(args.distinct): solver.add(Distinct(foobar))' in constraints)

	def test_add_symbolic_constraints_formal_list_bool(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, bool[] foobar) public pure returns (string) {
					int bar = 5*foo;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		# no other to say to unsupported types like bool
		# which constraints?
		self.assertTrue('foobar_length >= 0' in constraints)
		self.assertTrue('foobar_length < max_array_len' in constraints)


	def test_add_symbolic_constraints_without_assigned_value(self):
		"""
		Warning, local variable without initial value are not considered
		:return:
		"""
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					uint256 without;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('without' not in constraints) # no assigment would be possible


	def test_add_symbolic_constraints_using_var(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					var without = 5;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('foo >= 0' in constraints) # because formal parameters uint
		self.assertTrue('foo < max_uint(256)' in constraints) # formal parameter can't be greater than max
		# self.assertTrue('bar >= 0' in constraints) # underflow?
		# self.assertTrue('without >= 0' in constraints) # underflow?

	def test_add_symbolic_constraints_not_handled_string(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					var numLit = "5";
					var bar = foo*5;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertFalse('numLimit' in constraints)

	def test_add_symbolic_constraints_not_handled_bytes(self):
		"""
		WARNING: Parameters not handled doesn't have constraints
		but are simply ignored and doesn't raise any exception
		because the part of the function interested in the overflow
		could not interest the unhandled type.
		:return:
		"""
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo, bytes32 param) public pure returns (string) {
					var numLit = bytes32(0x01020304);
					var bar = foo*5;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		# self.assertTrue('bar >= 0' in constraints) - no because could underflow
		self.assertTrue('foo >= 0, foo < max_uint(256)' in constraints)
		self.assertFalse('numLimit' in constraints) # just skipped if not handled
		self.assertFalse('param' in constraints)
		self.assertFalse('foobar ' in constraints)

	def test_add_symbolic_constraints_bool_not_handled(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, bool mybool) public pure returns (string) {
					var bar = foo*5;
					bool mybool2 = true;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('mybool' not in constraints)

	def test_add_symbolic_constraints_local_uint(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					uint foobar = 4;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('bar >= 0' not in constraints) # because can overflow
		self.assertTrue('bar <= max_uint(256)' not in constraints) # because can overflow
		self.assertTrue('foobar' not in constraints)


	def test_add_symbolic_constraints_local_int(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					int foobar = 4;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('bar >= 0' not in constraints) # because can overflow
		self.assertTrue('bar <= max_int(256)' not in constraints) # because can overflow
		self.assertTrue('foobar' not in constraints)


	def test_add_symbolic_constraints_local_bool(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					bool foobar = true;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('foobar' not in constraints) # WARNING: not handled values are simply ignored

	def test_add_symbolic_constraints_local_list(self):
		"""
			Local list are not handled at all
		"""
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5*foo;
					uint[] foobar;
					int[] foobarInt;
					address[] addresses;
					bool[] booleans;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		local_variables = [x['declarations'][0] for x in inspected_obj['local_variables']]
		formal_parameters = inspected_obj['formal_parameters']
		constraints = add_symbolic_constraints(local_variables, formal_parameters)
		self.assertTrue('foobar_length' not in constraints)
		self.assertTrue('foobar' not in constraints)
		self.assertTrue('foobarInt_length' not in constraints)
		self.assertTrue('foobarInt' not in constraints)
		self.assertTrue('addresses_length' not in constraints)
		self.assertTrue('addresses' not in constraints)
		self.assertTrue('booleans_length' not in constraints)
		self.assertTrue('booleans' not in constraints)