from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _add_overflow_constraints as add_overflow_constraints

class Test_add_overflow_constraints(TestCase):

	"""
	Description: Test the function _add_overflow_constraints
	the function should accept as parameter the list
	of parameters that could overflow. The function
	will output a string representing the automatic generated Z3
	conditions.

	All the variables that are candidate to overflow are put
	in a Z3 Or condition, meaning that at least 1 should overflow.
	actual_value symbolic variable contains the exact value of the
	variable, either it overflows or not. This is done using
	the If statement in Z3.
	"""

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_add_overflow_single_uint_candidate(self):
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
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue('bar_actual_value = Int(' in constraints)
		self.assertTrue('bar_actual_value >= 0' in constraints)
		self.assertTrue('bar_actual_value == If(u_is_overflow(bar, 256), u_overflow_value(bar, 256), bar)' in constraints)
		self.assertTrue('u_is_overflow(bar, 256) == True' in constraints)

	def test_add_overflow_single_uint8_candidate(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint8 bar = 5*uint8(foo);
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue('bar_actual_value = Int(' in constraints)
		self.assertTrue('bar_actual_value >= 0' in constraints)
		self.assertTrue('bar_actual_value == If(u_is_overflow(bar, 8), u_overflow_value(bar, 8), bar)' in constraints)
		self.assertTrue('u_is_overflow(bar, 8) == True' in constraints)


	def test_add_overflow_single_int_candidate(self):
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
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue('bar_actual_value = Int(' in constraints)
		self.assertTrue('bar_actual_value >= 0' not in constraints)
		self.assertTrue('bar_actual_value == If(is_overflow(bar, 256), overflow_value(bar, 256), bar)' in constraints)
		self.assertTrue('is_overflow(bar, 256) == True' in constraints)

	def test_add_overflow_single_int8_candidate(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int8 bar = 5*int8(foo);
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue('bar_actual_value = Int(' in constraints)
		self.assertTrue('bar_actual_value >= 0' not in constraints)
		self.assertTrue('bar_actual_value == If(is_overflow(bar, 8), overflow_value(bar, 8), bar)' in constraints)
		self.assertTrue('is_overflow(bar, 8) == True' in constraints)


	def test_add_overflow_single_multi_uint_candidates(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo, uint8 foo8) public pure returns (string) {
					uint bar = 5*foo;
					uint8 foobar = foo8 + 42;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue('bar_actual_value = Int(' in constraints)
		self.assertTrue('foobar_actual_value = Int(' in constraints)
		self.assertTrue('bar_actual_value >= 0' in constraints)
		self.assertTrue('foobar_actual_value >= 0' in constraints)
		self.assertTrue('bar_actual_value == If(u_is_overflow(bar, 256), u_overflow_value(bar, 256), bar)' in constraints)
		self.assertTrue('u_is_overflow(bar, 256) == True' in constraints)
		self.assertTrue('foobar_actual_value == If(u_is_overflow(foobar, 8), u_overflow_value(foobar, 8), foobar)' in constraints)
		self.assertTrue('u_is_overflow(foobar, 8) == True' in constraints)


	def test_add_overflow_single_multi_int_candidates(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, int8 foo8) public pure returns (string) {
					int bar = 5*foo;
					int8 foobar = foo8 + 42;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue('bar_actual_value = Int(' in constraints)
		self.assertTrue('foobar_actual_value = Int(' in constraints)
		self.assertTrue('bar_actual_value >= 0' not in constraints)
		self.assertTrue('foobar_actual_value >= 0' not in constraints)
		self.assertTrue('bar_actual_value == If(is_overflow(bar, 256), overflow_value(bar, 256), bar)' in constraints)
		self.assertTrue('is_overflow(bar, 256) == True' in constraints)
		self.assertTrue('foobar_actual_value == If(is_overflow(foobar, 8), overflow_value(foobar, 8), foobar)' in constraints)
		self.assertTrue('is_overflow(foobar, 8) == True' in constraints)

	def test_add_overflow_single_multi_mix_candidates(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, uint8 foo8) public pure returns (string) {
					int bar = 5*foo;
					uint8 foobar = foo8 + 42;
					require(bar > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue('Or(is_overflow(bar, 256) == True,u_is_overflow(foobar, 8)' in constraints)


	def test_add_overflow_single_multi_mix_candidates_2(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo, uint8 foo8) public pure returns (string) {
					uint8 foobar = foo8 + 42;
					require(5*foo > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['candidate_for_overflow']
		constraints = add_overflow_constraints(accessed_state_variables)
		self.assertTrue("Int('foobar_actual_value" in constraints)
		self.assertTrue("Int('exp_19_actual_value" in constraints)
		self.assertTrue('Or(u_is_overflow(foobar, 8) == True,is_overflow(exp_19, 256)' in constraints)
		self.assertTrue("If(is_overflow(exp_19, 256), overflow_value(exp_19, 256), exp_19))" in constraints)

