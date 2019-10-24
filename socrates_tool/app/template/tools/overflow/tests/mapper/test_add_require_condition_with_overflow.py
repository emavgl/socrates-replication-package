from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _add_require_condition_with_overflow as add_require_condition_with_overflow
from modules.mapper import _requires_constraints
import re

class Test_add_require_condition_with_overflow(TestCase):



	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		inspected = visit_ast(ast_json, function_name)
		require_conditions = _requires_constraints(inspected['require_nodes'])
		return require_conditions, inspected['candidate_for_overflow']

	def test_add_require_condition_with_overflow_1(self):
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
		require_conditions, candidates = self.before_test(source)
		conditions = add_require_condition_with_overflow(require_conditions, candidates)
		self.assertTrue('bar_actual_value' in conditions)
		self.assertTrue('foo_actual_value' not in conditions)

	def test_add_require_condition_with_overflow_2(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					uint bar = 5*uint(foo);
					require(bar > uint(foo));
					return 'helloWorld';
				}
			}
		"""
		require_conditions, candidates = self.before_test(source)
		conditions = add_require_condition_with_overflow(require_conditions, candidates)
		self.assertTrue('bar_actual_value' in conditions)
		self.assertTrue('foo_actual_value' not in conditions)

	def test_add_require_condition_with_overflow_3(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction () public pure returns (string) {
					int bar = 5 * foo ;
					int foo = bar + 9;
					require(bar * (6 + foo) > foo);
					require(bar * (6 + foo) != ((2 % foo) - (-((2)*foo+(3)) / 3)));
					return 'helloWorld';
				}
			}
		"""
		require_conditions, candidates = self.before_test(source)
		conditions = add_require_condition_with_overflow(require_conditions, candidates)
		self.assertTrue(re.findall(r'exp_\d+_actual_value !=', conditions))
		self.assertTrue(re.findall(r'exp_\d+_actual_value > foo_actual_value', conditions))



	def test_add_require_condition_with_overflow_4(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					require(bar * (6 + foo) > foo);
					require(barList.length * (6 + foo) != ((2 % foo) - (-((2)*foo+(3)) / 3)));
					return 'helloWorld';
				}
			}
		"""
		require_conditions, candidates = self.before_test(source)
		conditions = add_require_condition_with_overflow(require_conditions, candidates)
		self.assertTrue(re.findall(r'exp_\d+_actual_value !=', conditions))
		self.assertFalse(re.findall(r'!= exp_\d+_actual_value', conditions))
		self.assertTrue(re.findall(r'exp_\d+_actual_value > foo', conditions))

	def test_add_require_condition_with_overflow_5(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint foo;
				function testFunction () public returns (string) {
					uint[] barList;
					uint bar = 5 * foo ;
					require(bar * (6 + foo) > foo);
					require(barList.length * (6 + foo) != ((2 % foo) - (-((2)*bar+(3)) / 3)));
					return 'helloWorld';
				}
			}
		"""
		require_conditions, candidates = self.before_test(source)
		conditions = add_require_condition_with_overflow(require_conditions, candidates)
		self.assertFalse(re.findall(r'!= exp_\d+_actual_value', conditions))
		self.assertTrue(re.findall(r'exp_\d+_actual_value != ', conditions))
		self.assertTrue(re.findall(r'exp_\d+_actual_value > foo', conditions))

	def test_add_require_condition_with_overflow_6(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint foo;
				function testFunction () public returns (string) {
					uint[] barList;
					uint bar = 5 * foo ;
					require(bar * (6 + foo) > foo);
					require(barList.length * (6 + bar) != ((2 % bar) + (-((2)*bar+(3)) / 3)));
					return 'helloWorld';
				}
			}
		"""
		require_conditions, candidates = self.before_test(source)
		conditions = add_require_condition_with_overflow(require_conditions, candidates)
		self.assertTrue(re.findall(r'!= \(exp_\d+_actual_value\)', conditions))
		self.assertTrue(re.findall(r'exp_\d+_actual_value != ', conditions))
		self.assertTrue(re.findall(r'exp_\d+_actual_value > foo', conditions))

	def test_add_require_condition_with_overflow_7(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint foo;
				function testFunction () public returns (string) {
					uint[] barList;
					uint bar = 5 * foo ;
					require(bar * (6 + foo) > foo || foo > 9);
					require(barList.length * (6 + bar) != ((2 % bar) + (-((2)*bar+(3)) / 3)));
					return 'helloWorld';
				}
			}
		"""
		require_conditions, candidates = self.before_test(source)
		conditions = add_require_condition_with_overflow(require_conditions, candidates)
		self.assertTrue(re.findall(r"Or\(exp_\d+_actual_value > foo, foo > 9\)", conditions))
		self.assertTrue(re.findall(r"exp_\d+_actual_value != \(exp_\d+_actual_value\)\)", conditions))

	def test_add_require_condition_with_overflow_no_requires(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint foo;
				function testFunction () public returns (string) {
					uint[] barList;
					uint bar = 5 * foo ;
					return 'helloWorld';
				}
			}
		"""
		require_conditions, candidates = self.before_test(source)
		constraints = add_require_condition_with_overflow(require_conditions, candidates)
		not_empty_lines = list(filter(None, constraints.splitlines()))
		self.assertTrue(len(not_empty_lines) == 1 and not_empty_lines[0].startswith("# ==="))