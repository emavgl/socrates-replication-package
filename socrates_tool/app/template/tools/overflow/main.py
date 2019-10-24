import sys, argparse
import logging
from modules import asthelper
from modules import astvisitor
from modules import mapper
from modules import filewriter

def main(args):
    functions_under_test = []

    # Parsing Args
    contract_path, output_folder, contract_name = (args.source, args.output, args.contract)

    if args.function:
        functions_under_test.append(args.function)
    elif args.contract:
        filewriter.create_dir(output_folder)
        output_folder = '{}/{}'.format(output_folder, args.contract)
        abi = asthelper.get_abi(contract_path, args.contract)
        functions_under_test = [x['name'] for x in abi if 'name' in x]

    logging.info("Compiling and extracting json" + contract_path)

    # Compile, Generate AST
    ast_json = asthelper.compile(contract_path)

    for function_name in functions_under_test:

        try:
            # Visit
            inspected_function = astvisitor.visit_ast(ast_json, function_name)

            # Map to Z3
            z3_generated_code = mapper.ast_to_z3(inspected_function)

            # Write On File
            output_file_path = filewriter.write_z3_script(output_folder, function_name, z3_generated_code)

            logging.info("Output file " + output_file_path)

        except Exception as e:
            if e.args[0] in ['AstVisitErr', 'Z3MapperErr']:
                msg = "function '{0}' raise a {1}: {2}".format(function_name, e.args[0], e.args[1])
                logging.warning(msg)
            elif e.args[0] in ['AstCompileErr']:
                logging.error("Cannot compile with solc")
                logging.error(e.args[1])
            else:
                logging.error(e)

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Generate function constraint for Z3 overflow solver')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-s', '--source', help='Solidity source file path (es. BecToken_example.sol)', required=True)
    requiredNamed.add_argument('-c', '--contract', help='Name of the contract under test (es. BecToken_example)', required=True)
    requiredNamed.add_argument('-f', '--function', help='(Optional) Specify the name of single function to test (es. batchTransfer)', required=False)
    requiredNamed.add_argument('-o', '--output', help='Output folder', required=True)

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(-1)

    # Run
    main(args)

    sys.exit()
