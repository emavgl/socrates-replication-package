import subprocess, json
from models import variable, astnode
import uuid
import os
import glob
import re

def compile(filename):
    """
    Compiles the solidity source code and import the json
    :param filename: path of the file containing the source code
    :return: List of object, one for sources (the first one is the one specified in filename)
    """
    try:
        #], stderr=subprocess.DEVNULL
        result = subprocess.run(['solc', '--ast-compact-json', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout
        stderr = result.stderr

        if not stdout and stderr:
            raise Exception('AstCompileErr', stderr.decode('utf8'))

        # Remove headers from solc output
        result = stdout.decode('utf8')
        blocks = result.split('=======')

        # remove header
        blocks = blocks[1:]

        # 0 -  filename1
        # 1 - json_file_1
        # 2 -  filename2
        # 3 - json_file_2
        # ...

        # odd indexes are the json blocks
        # even are the name of the files

        return [json.loads(block) for i, block in enumerate(blocks) if i % 2 != 0]

    except subprocess.CalledProcessError as exc:
        raise Exception("Status : FAIL", exc.returncode, exc.stderr)

def get_abi(filename, contract_name):
    """
    Compiles the solidity source code and import the json
    :param filename: path of the file containing the source code
    :return: List of object, one for sources (the first one is the one specified in filename)
    """
    try:
        # ], stderr=subprocess.DEVNULL
        result = subprocess.run(['solc', '--abi', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout
        stderr = result.stderr

        if not stdout and stderr:
            raise Exception('AstCompileErr', stderr.decode('utf8'))

        # Remove headers from solc output
        result = stdout.decode('utf8')
        blocks = result.split('=======')

        # remove header
        blocks = blocks[1:]

        # 0 -  filename1
        # 1 - json_file_1
        # 2 -  filename2
        # 3 - json_file_2
        # ...

        # odd indexes are the json blocks
        # even are the name of the files

        abi_list =  [blocks[i+1] for i, block in enumerate(blocks) if ":" + contract_name in block]
        abi_str = abi_list[0].split('\n')[2]
        return json.loads(abi_str)

    except subprocess.CalledProcessError as exc:
        raise Exception("Status : FAIL", exc.returncode, exc.stderr)


def compile_from_source(source: str):
    # remove existing files in tmp

    import os
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    files = glob.glob('./tmp/*')
    for f in files:
        os.remove(f)

    # create a new tmp file copying the source code
    temporary_file_path = './tmp/{}'.format(uuid.uuid4().hex)
    with open(temporary_file_path, 'w') as f:
        f.write(source)

    # call compile specifing the created file path
    return compile(temporary_file_path)


def match_function(function_ast, expected_function):

    name = expected_function['name']
    implemented = expected_function['implemented']
    expected_parameters = expected_function['parameters']
    expected_return_parameters = expected_function['returnParameters']

    if function_ast['name'] != name or function_ast['implemented'] != implemented:
        return False

    parameters = function_ast['parameters'].get('parameters')
    return_parameters = function_ast['returnParameters'].get('parameters')

    if len(parameters) != len(expected_parameters) or len(return_parameters) != len(expected_return_parameters):
        return False

    # IMPORTANT: Order matter in expected parameters matter
    for param, expected in zip(parameters, expected_parameters):
        if not variable.Variable(param).match(expected):
            return False

    for param, expected in zip(return_parameters, expected_return_parameters):
        if not variable.Variable(param).match(expected):
            return False

    return True


def _is_a_match(node, properties):
    if type(node) is not dict:
        return False

    for property, value in properties.items():

        if property not in node:
            return False

        # boolean or int
        # check specific value
        if isinstance(value, int) and node[property] != value:
            return False

        if not isinstance(value, int) and len(re.findall(value, str(node[property]))) == 0:
           return False

    return True


def _find_node(parent, ast, properties):
    """
    Find and return the first node that match the properties
    :param ast: object representing the AST
    :param properties: dictionary of the property to search (for example, {'name': 'transfer'})
    """

    if _is_a_match(ast, properties):
        return astnode.AstNode(parent, ast)

    if type(ast) is list:
        for element in ast:
            new_parent = astnode.AstNode(parent, ast)
            found = _find_node(new_parent, element, properties)
            if found:
                return found

    elif type(ast) is dict:
        for key, value in ast.items():
            if type(value) is dict or type(value) is list:
                new_parent = astnode.AstNode(parent, ast)
                found = _find_node(new_parent, value, properties)
                if found:
                    return found

    return False


def find_node(ast, properties):
    return _find_node(None, ast, properties)

def find_parent(node: astnode.AstNode, properties: dict):
    my_parent = node.parent
    while my_parent != None and not _is_a_match(my_parent.dic, properties):
        my_parent = my_parent.parent
    return my_parent

def _find_all_nodes(parent, ast, properties, outputs):

    # Add to the list if it is matching
    if _is_a_match(ast, properties):
        outputs.append(astnode.AstNode(parent, ast))

    # Call find_all_nodes on its childs
    if type(ast) is list:
        for element in ast:
            new_parent = astnode.AstNode(parent, ast)
            _find_all_nodes(new_parent, element, properties, outputs)

    elif type(ast) is dict:
        for key, value in ast.items():
            if type(value) is dict or type(value) is list:
                new_parent = astnode.AstNode(parent, ast)
                _find_all_nodes(new_parent, value, properties, outputs)

    # At the end, the element on the top will return the list
    return outputs


def find_all_nodes(ast, properties):
    """
    Find and return the first node that match the properties
    :param ast: object representing the AST
    :param properties: dictionary of the property to search (for example, {'name': 'transfer'})
    """
    return _find_all_nodes(None, ast, properties, [])


def write_on_file(asts_json):
    """
    Write AST as a json
    :param asts_json:
    :return:
    """
    with open('resources/ast.json', 'w') as outfile:
        json.dump(asts_json, outfile)


def isERC20(main_ast: str):
    """
    Takes in input the AST of the Solidity code
    Checks if it is a valid ERC20 contract
    :param main_ast: the root ast

    Example:
        asts_json = compile(filename)
        erc20 = isERC20(asts_json[1])
    """

    # We need to check that at least one contract of the file implements the ERC20 interface
    contracts = find_all_nodes(main_ast, {'nodeType': 'ContractDefinition'})

    erc_20_interface = [
        {
            'name': 'transfer',
            'implemented': True,
            'parameters': [ {'type': 'address'}, {'type': 'uint256'}],
            'returnParameters': [ { 'type': 'bool' }]
        },
        {
            'name': 'transferFrom',
            'implemented': True,
            'parameters': [{'type': 'address'}, {'type': 'address'}, {'type': 'uint256'}],
            'returnParameters': [{'type': 'bool'}]
        },
        {
            'name': 'approve',
            'implemented': True,
            'parameters': [{'type': 'address'}, {'type': 'uint256'}],
            'returnParameters': [{'type': 'bool'}]
        },
        {
            'name': 'balanceOf',
            'implemented': True,
            'parameters': [{'type': 'address'}],
            'returnParameters': [{'type': 'uint256' }]
        },
        {
            'name': 'allowance',
            'implemented': True,
            'parameters': [{'type': 'address'}, {'type': 'address'}],
            'returnParameters': [{'type': 'uint256'}]
        }
    ]

    for contract in contracts:
        print("contract", contract['name'])
        functions = find_all_nodes(contract, {'nodeType': 'FunctionDefinition'})

        matching_contract = None
        for expected_function in erc_20_interface:

            found = None
            for function in functions:
                if match_function(function, expected_function):
                    found = function
                    break

            if not found:
                # I have no match for the expected_function in this contract
                # break and skip the contract
                matching_contract = False
                break

        if matching_contract == None:
            # I'm here because I found a contract which implements the ERC20 interface
            return contract

