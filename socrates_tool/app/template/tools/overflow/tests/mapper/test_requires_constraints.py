from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import _requires_constraints as requires_constraints
import re

class Test_requires_constraints(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_requires_constraints_0(self):
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
		requires = inspected_obj['require_nodes']
		constraints = requires_constraints(requires)
		self.assertTrue(re.findall('bar > 5', constraints))

	def test_requires_constraints_1(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (uint foo) public pure returns (string) {
					uint bar = 5*foo;
					require(bar*5 > 5);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		requires = inspected_obj['require_nodes']
		constraints = requires_constraints(requires)
		self.assertTrue(re.findall('exp_\d+ > 5', constraints))


	def test_requires_constraints_2(self):
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
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue('bar > foo' in constraints)

	def test_requires_constraints_3(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				function testFunction (int foo) public pure returns (string) {
					int bar = 5 * foo ;
					require(bar * (6 + foo) > foo);
					require(bar * (6 + foo) != ((2 % foo) - (-((2)*foo+(3)) / 3)));
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue(re.findall('exp_\d+ > foo', constraints))
		self.assertTrue(re.findall('exp_\d+ != \(\(2 % foo\) -', constraints))

	def test_requires_constraints_4(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					require(bar * (6 + foo) > foo || foo > 9);
					require(barList.length * (6 + foo) != ((2 % foo) + (-((2)*foo+(3)) / 3)));
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue(re.findall('exp_\d+ > foo', constraints))
		self.assertTrue(re.findall('exp_\d+ != \(exp_\d+\)', constraints))

	def test_requires_constraints_5(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					bool a = true;
					require(a);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue('solver.add(a)' in constraints)

	def test_requires_constraints_6(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					bool a = true;
					require(a == (bar < 9));
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue('solver.add(a == (bar < 9))' in constraints)

	def test_requires_constraints_7(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					bool a = true;
					require(a == !(bar < 9));
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue('solver.add(a == Not((bar < 9)))' in constraints)

	def test_requires_constraints_8(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					bool a = true;
					require(!a == !(bar < 9));
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue('solver.add(Not(a) == Not((bar < 9)))' in constraints)

	def test_requires_constraints_9(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					bool a = true;
					require((bar < 9));
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue('solver.add((bar < 9))' in constraints)

	def test_requires_constraints_10(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint[] barList;
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					bool a = true;
					require(a == false);
					require(!a == true);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		self.assertTrue('solver.add(Not(a) == True)' in constraints)
		self.assertTrue('solver.add(a == False)')

	def test_requires_constraints_11(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				mapping (address => mapping (address => bool)) public map;
				uint foo;
				function testFunction (address a, address b) public returns (string) {
					uint bar = 5 * foo;
					require(map[a][b] == false);
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		print('map[a* accounts_len + b]' in constraints)


	def test_requires_constraints_no_requires(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo ;
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		accessed_state_variables = inspected_obj['require_nodes']
		constraints = requires_constraints(accessed_state_variables)
		not_empty_lines = list(filter(None, constraints.splitlines()))
		self.assertTrue(len(not_empty_lines) == 1 and not_empty_lines[0].startswith("# ==="))