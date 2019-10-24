import sys
import argparse
import json
from web3 import Web3

def create_mapper(logpath) -> dict:
	mapper = {}

	with open(logpath) as logfile:

		content = logfile.read()
		lines = content.splitlines()

	for i, line in enumerate(lines):
		line = json.loads(line)
		if line['message']['label'] == 'init' and line['message']['type'] == 'account':
			mapper[line['message']['address']] = "accounts[{}]".format(str(i))
		elif line['message']['label'] == 'init' and line['message']['type'] == 'contract':
			mapper[line['message']['address']] = "HST.address"
			break
		else:
			break

	mapper['0x0000000000000000000000000000000000000000'] = "null_address"

	return mapper


def parse_logs(log_path: str):
	parsed = []
	with open(log_path) as logfile:
		content = logfile.read()
		lines = content.splitlines()
		for line in lines:
			line = json.loads(line)['message']
			try:
				if line['label'] == 'action':
					sent_from = line['address']
					action = line['action']
					params = line['params']
					parsed.append({'type': 'action', 'content': (sent_from, action, params)})
				if line['label'] == 'invariant_violation':
					invariant = {'type': 'violation', 'content': line['invariant']}
					parsed.append(invariant)
			except Exception:
				pass
	return parsed


def is_number(s):
	# works even with scientific notation
	try:
		float(s)
		return True
	except ValueError:
		return False

def convert_param(param, mapper):
    param_str = ''
    if isinstance(param, bool):
        param_str += '{}, '.format(str(param).lower())
    elif is_number(param):
        param_str += 'web3.toBigNumber("{}")'.format(param)
    elif Web3.isAddress(param):
        param_str += '{}'.format(mapper[param])
    else:
        param_str += '"{}"'.format(param)
    return param_str

def parsedLogsToJS(parsedLogs, mapper):
	base_str = "        await HST['{0}']({1});"

	actions_str = []
	for log in parsedLogs:
		if log['type'] == 'action':
			sent_from, action_name, params = log['content']
			params_str = ""

			for param in params[:-1]:
				if isinstance(param, list):
					params_str += '['
					for p in param:
						params_str += convert_param(p, mapper) + ', '
					params_str = params_str[:-2] # remove last ,
					params_str += '], '
				else:
					params_str += convert_param(param, mapper) + ', '

			transaction_options = params[-1]
			value_str = 'web3.toBigNumber("{}")'.format(transaction_options['value'])
			from_str = mapper[transaction_options['from']]
			params_str += '{{ from: {0}, value: {1} }}'.format(from_str, value_str)

			action_str = base_str.format(action_name, params_str)
			actions_str.append(action_str)
		
		if log['type'] == 'violation':
			actions_str.append("\n        console.log('ERROR: ', '{}');\n".format(log['content']))

	return '\n'.join(actions_str)


def write_on_truffle_test(actions_js_str: str, contract_name: str, outputfile: str):
	with open('template.js') as template_file:
		truffle_template = template_file.read()

	truffle_template = truffle_template.replace('<contractname>', contract_name)
	truffle_template = truffle_template.replace('<codehere>', actions_js_str)

	with open(outputfile, 'w') as output_file:
		output_file.write(truffle_template)


def load_artifacts(artifacts_path: str) -> dict:
	with open(artifacts_path) as artifactfile:
		return json.loads(artifactfile.read())


def get_read_state_code(accounts):
	base_str = '        console.log("{0}", (await HST["balanceOf"]({0})).toString());\n'
	code_js = "\n\n"
	code_js += '        console.log("\\n\\nCONTRACT STATE");\n'
	for a in sorted(accounts):
		code_js += base_str.format(a)

	code_js += '        console.log("totalSupply", (await HST["totalSupply"]()).toString());\n'

	return code_js


def main(args):
	mapper = create_mapper(args.log)
	contract_name = args.contractname
	parsed = parse_logs(args.log)
	to_write = parsedLogsToJS(parsed, mapper)
	code_for_print_state = get_read_state_code(list(mapper.values()))
	all_code = to_write + code_for_print_state
	write_on_truffle_test(all_code, contract_name, args.outputfile)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='log2test')
	requiredNamed = parser.add_argument_group('Required arguments')
	requiredNamed.add_argument('-l', '--log', help='logs', required=True)
	requiredNamed.add_argument('-c', '--contractname', help='Contract name', required=True)
	requiredNamed.add_argument('-o', '--outputfile', help='Output file', required=True)


	try:
		args = parser.parse_args()
	except:
		parser.print_help()
		sys.exit(-1)

	# Run
	main(args)

	sys.exit()

