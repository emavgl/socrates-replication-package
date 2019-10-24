import sys
import argparse
import re

# to use the module ast_helper
sys.path.append("..")
sys.path.append("./tools/overflow")

from modules import asthelper

# ==============
# === GETTER ===
# ==============


def _inject_getter_function(source, list_name):
    before_index = source.index(list_name) + source[source.index(list_name):].index('\n')
    before = source[:before_index]
    after = source[before_index:]
    middle = " function get_{0}_len() public constant returns(uint count) {{  return {0}.length;  }}".format(list_name)
    return before + middle + after


def inject_getter_functions(source: str):
    """
    Create getters for array's length member
    :param source: original source code
    :return: edited source code
    """
    ast = asthelper.compile_from_source(source)

    state_variables = \
        [x for x in asthelper.find_all_nodes(ast, {'nodeType': 'VariableDeclaration', 'stateVariable': True})]

    state_variables_list = [x for x in state_variables if 't_array' in x['typeDescriptions']['typeIdentifier']]
    state_variables_names = [x['name'] for x in state_variables_list]

    edited_source = source
    for state_variable in state_variables_names:
        edited_source = _inject_getter_function(edited_source, state_variable)

    return edited_source


# ===========================
# === PUBLIC DECLARATIONS ===
# ===========================

def all_declarations_public(source: str) -> str:
    """
    Using a regex it makes public all the variable inside source
    :param source:
    :param ast:
    :return: edited_source: str
    """

    ast = asthelper.compile_from_source(source)

    nodes = asthelper.find_all_nodes(ast, {'nodeType': 'VariableDeclaration', 'stateVariable': True})
    destination = source

    declaration_re = re.compile(r"(address|string|bool|bytes?\d*|u?int\d*|mapping.*\))(\[\d*\]|)?\s*(public|private|internal|external|)?\s+(\w+)\s*(;|=)")

    for n in nodes:
        start, length, _ = n['src'].split(':')
        start = int(start); length = int(length)
        line = source[start:start+length+1]
    #    print("before: ", line)
        left, right = tuple(destination.split(line, 1))
        middle = declaration_re.sub(r"\g<1>\g<2> public \g<4> \g<5>", line)
        destination = left + middle + right
    #    print("after: ", middle)

    return destination


# ===================================
# === CONVERT IF-REVERT TO REQUIRE ==
# ===================================

def ifrevert2require(source: str) -> str:
    """
    Conver the assigment to newly created declarations
    :param source:
    :return:
    """
    ast = asthelper.compile_from_source(source)
    if_nodes = asthelper.find_all_nodes(ast, {'nodeType': '^IfStatement$'})

    edited_source = source

    for node in if_nodes:

        try:
            reverts = asthelper.find_node(node['trueBody'], {'nodeType': '^Identifier$', 'name': '^revert$'})

            # Check for return false
            return_false = False
            if 'statements' in node['trueBody']:
                if_statements = node['trueBody']['statements']
                if len(if_statements) == 1:
                    return_statement = asthelper.find_node(node['trueBody'], {'nodeType': '^Return$'})
                    if return_statement and asthelper.find_node(node['trueBody'], {'nodeType': '^Literal$', 'value': '^false$'}):
                        return_false = True
            elif 'expression' in node['trueBody']:
                return_statement = asthelper.find_node(node['trueBody'], {'nodeType': '^Return$'})
                if return_statement and asthelper.find_node(node['trueBody'], {'nodeType': '^Literal$', 'value': '^false$'}):
                    return_false = True

            if reverts or return_false:
                start, length, _ = node['src'].split(':')
                start = int(start)
                length = int(length)
                line = source[start:start + length + 1]
                left, right = tuple(edited_source.split(line, 1))

                # other way
                # new_line = line.replace('if', 'require')
                # sa = new_line.split(')')
                # new_line = ')'.join(sa[:-2]) # remove the portion after the last if closed bracket

                if_condition = asthelper.astnode.AstNode(None, node['condition']).to_sol_string()
                require_statement = 'require(({}) == false);\n'.format(if_condition)
                edited_source = left + require_statement + right
        except Exception as e:
            # an error while editing some if, maybe contains a function
            # just skip
            continue

    return edited_source


def throw2revert(source: str) -> str:
    """
    Convert the throw keyword into a revert call
    :param source:
    :return:
    """
    regex = r"\s?throw\s*;"
    subst = " revert();"
    return re.sub(regex, subst, source)


# ===========================================
# === GIVE A NAME TO THE FALLBACK FUNCTION ==
# ===========================================

def convert_fallback_function(source: str) -> str:
    """
    Convert the signature of a fallback function
    and create a new function called fallbackFunction
    """
    regex = r"function\s+\(\)\s*(payable)?\s*(internal|public|private|external)?\s*(payable)?"
    subst = "function fallbackFunction() payable public "
    return re.sub(regex, subst, source)


# ========================================================
# === ASSIGN TO A NEW VARIABLE INSTEAD OF RE-ASSIGNMENT ==
# ========================================================

def convert_reassignment(source: str) -> str:
    regex = r"^[\s|\t]*([^\s]+)\s+(\+|\-|\*)?=\s+([^;]*)"
    ast = asthelper.compile_from_source(source)
    assigment_nodes = asthelper.find_all_nodes(ast, {'nodeType': '^Assignment$'})

    edited_source = source

    for node in assigment_nodes:
        start, length, _ = node['src'].split(':')
        start = int(start)
        length = int(length)
        line = source[start:start + length + 1]
        line_rgx = r'^[\s|\t]*' + re.escape(line)
        pieces = re.compile(line_rgx, re.M).split(edited_source, 1)

        if len(pieces) != 2:
            # not exact "LINE" match found
            continue

        left, right = tuple(pieces)
        name = 'var nvar_{1}'.format(node['typeDescriptions']['typeString'], node['id'])

        new_line = line
        matches = re.search(regex, line, re.M)
        if matches and matches.group(2) is None:
            subst = name + ' = \g<3>'
            new_line = re.sub(regex, subst, new_line, re.M)
        elif matches and matches.group(2):
            subst = name + ' = \g<1> \g<2> \g<3>'
            new_line = re.sub(regex, subst, new_line, re.M)

        edited_source = left + new_line + right

    return edited_source


def main(args):
    """
    Entry point of the program
    :param args:
    :return:
    """

    # read original source code
    with open(args.source) as r:
        edited_source_code = r.read()

    # apply operations
    if args.allpublic:
        # convert all variable declaration to public
        edited_source_code = all_declarations_public(edited_source_code)

    if args.getters:
        # creates getters for array length
        edited_source_code = inject_getter_functions(edited_source_code)

    if args.throwrevert:
        edited_source_code = throw2revert(edited_source_code)

    if args.ifrevert:
        edited_source_code = ifrevert2require(edited_source_code)

    if args.asserts:
        edited_source_code = edited_source_code.replace('assert(', 'require(')

    if args.fallback:
        edited_source_code = convert_fallback_function(edited_source_code)

    if args.reassigment:
        # convert 	balanceOf[target] += mintedAmount; to
        # to        var_something = balanceOf[target] + mintedAmount;
        edited_source_code = convert_reassignment(edited_source_code)

    # Check if compile or raise an exception
    asthelper.compile_from_source(edited_source_code)

    # write on output files
    with open(args.output, 'w') as w:
        w.write(edited_source_code)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tools for pre-processing')

    parser.add_argument('-p', '--allpublic', type=str2bool, help='Convert each variable declaration into public',
                        default=1, choices=[False, True])
    parser.add_argument('-g', '--getters', type=str2bool, help='Create Getter functions for length',
                        default=1, choices=[False, True])
    parser.add_argument('-t', '--throwrevert', type=str2bool, help='Convert throw to revert',
                        default=1, choices=[False, True])
    parser.add_argument('-if', '--ifrevert', type=str2bool, help='Convert if-revert into require',
                        default=1, choices=[False, True])
    parser.add_argument('-a', '--asserts', type=str2bool, help='Convert assert into require',
                        default=1, choices=[False, True])
    parser.add_argument('-f', '--fallback', type=str2bool, help='Convert fallback into new function',
                        default=1, choices=[False, True])
    parser.add_argument('-r', '--reassigment', type=str2bool, help='Convert re-assigment to newly created variables',
                        default=1, choices=[False, True])

    requiredNamed = parser.add_argument_group('Required arguments')
    requiredNamed.add_argument('-s', '--source', help='Source file (solidity)', required=True)
    requiredNamed.add_argument('-o', '--output', help='Output destination', required=True)

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(-1)

    # Run
    main(args)

    sys.exit()

