from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _add_symbolic_require_expressions as add_symbolic_require_expressions
import re

class Test_add_symbolic_require_expressions(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_add_symbolic_require_expressions_no_expression(self):
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
		accessed_state_variables = inspected_obj['require_expression_map']
		constraints = add_symbolic_require_expressions(accessed_state_variables)
		not_empty_lines = list(filter(None, constraints.splitlines()))
		self.assertTrue(len(not_empty_lines) == 1 and not_empty_lines[0].startswith("# ==="))

	def test_add_symbolic_require_expressions_1(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					require(bar > 5);
					require(foo + 9 > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_expression_map']
		constraints = add_symbolic_require_expressions(accessed_state_variables)
		not_empty_lines = list(filter(None, constraints.splitlines()))
		self.assertFalse(len(not_empty_lines) == 1 and not_empty_lines[0].startswith("# ===")) # not empty
		self.assertTrue(re.findall(r"exp_\d+ = Int\('exp_\d+'\)", constraints))
		self.assertTrue(re.findall(r"exp_\d+ == foo \+ 9", constraints))

	def test_add_symbolic_require_expressions_2(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					require(bar > 5);
					require(foo + 9 > (bar * 9));
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_expression_map']
		constraints = add_symbolic_require_expressions(accessed_state_variables)
		not_empty_lines = list(filter(None, constraints.splitlines()))
		self.assertFalse(len(not_empty_lines) == 1 and not_empty_lines[0].startswith("# ===")) # not empty
		self.assertTrue(re.findall(r"exp_\d+ = Int\('exp_\d+ exp_\d+'\)", constraints))
		self.assertTrue(re.findall(r"exp_\d+ == foo \+ 9", constraints))
		self.assertTrue(re.findall(r"exp_\d+ == bar \* 9", constraints))

	def test_add_symbolic_require_expressions_3(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					require(bar > 5);
					require(foo + 9 > (bar * 9) + 9);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_expression_map']
		constraints = add_symbolic_require_expressions(accessed_state_variables)
		not_empty_lines = list(filter(None, constraints.splitlines()))
		self.assertFalse(len(not_empty_lines) == 1 and not_empty_lines[0].startswith("# ===")) # not empty
		self.assertTrue(re.findall(r"exp_\d+ = Int\('exp_\d+ exp_\d+'\)", constraints))
		self.assertTrue(re.findall(r"exp_\d+ == foo \+ 9", constraints))
		self.assertTrue(re.findall(r"exp_\d+ == \(bar \* 9\) \+ 9", constraints))


	def test_add_symbolic_require_expressions_4(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					require(bar > 5);
					require(foo + 9 > (bar * 9) + 9 && foo + 9 > 3);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_expression_map']
		constraints = add_symbolic_require_expressions(accessed_state_variables)
		not_empty_lines = list(filter(None, constraints.splitlines()))
		self.assertFalse(len(not_empty_lines) == 1 and not_empty_lines[0].startswith("# ===")) # not empty
		self.assertTrue(re.findall(r"exp_\d+ = Int\('exp_\d+ exp_\d+ exp_\d+'\)", constraints))
		self.assertTrue(len(re.findall(r"exp_\d+ == foo \+ 9", constraints)) == 2)
		self.assertTrue(re.findall(r"exp_\d+ == \(bar \* 9\) \+ 9", constraints))