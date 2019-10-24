from unittest import TestCase
from modules import asthelper
from modules.astvisitor import visit_ast
from modules.mapper import ast_to_z3


class TestAst_to_z3(TestCase):

	def before_test(self, source):
		ast_json = asthelper.compile_from_source(source)
		function_name = 'testFunction'
		return visit_ast(ast_json, function_name)

	def test_ast_to_z3_no_requires(self):
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
		all_constraints = ast_to_z3(inspected_obj)
		# unit test should not raise an exception

	def test_ast_to_z3_overflow_in_require(self):
		source = """
			pragma solidity ^0.4.22;
			contract testContract {
				uint foo;
				function testFunction () public returns (string) {
					uint bar = 5 * foo;
					require( 5 * foo > 10 );
					return 'helloWorld';
				}
			}
		"""
		inspected_obj = self.before_test(source)
		all_constraints = ast_to_z3(inspected_obj)
		# unit test should not raise an exception