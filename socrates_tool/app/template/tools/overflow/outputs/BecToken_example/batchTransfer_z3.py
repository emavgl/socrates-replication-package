import json
import web3
from z3 import *
from web3 import Web3, HTTPProvider, TestRPCProvider
import itertools
import argparse

"""
  Source:

  function batchTransfer(address[] _receivers, uint256 _value) public whenNotPaused returns (bool) {
    uint cnt = _receivers.length;

    uint256 amount = uint256(cnt) * _value;

    require(cnt > 0 && cnt <= 20);
    require(_value > 0 && balances[msg.sender] >= amount);

    balances[msg.sender] = balances[msg.sender].sub(amount);
    for (uint i = 0; i < cnt; i++) {
        balances[_receivers[i]] = balances[_receivers[i]].add(_value);
        Transfer(msg.sender, _receivers[i], _value);
    }
    return true;
  }
"""

# === CONSTANTS ===
max_array_len = 32

# === HELPER FUNCTIONS
def max_uint(bits):
    return 2**bits

def max_int(bits):
    return 2**(bits-1) - 1

def min_int(bits):
    return - 2**(bits-1)

def u_is_overflow(value, numberOfBits):
    return Or(value > (2**numberOfBits) - 1, value < 0)

def u_overflow_value(value, numberOfBits):
    return value % 2**numberOfBits

def is_overflow(value, numberOfBits):
    return Or(value > 2**(numberOfBits-1) - 1, value < - 2**(numberOfBits-1))

def overflow_value(value, numberOfBits):
    return (value + 2**(numberOfBits-1)) % 2**numberOfBits - 2**(numberOfBits-1)


def get_state_variable(contract_instance, base, *args):
    f = contract_instance.get_function_by_name(base)
    return f(*args).call()

def get_contract_instance(w3, contract_address, contract_abi):
    return w3.eth.contract(
        address=contract_address,
        abi=contract_abi,
)

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description='Run Z3 Solver')
parser.add_argument('-d', '--distinct', type=str2bool, help='Force distinct values for IntVectors', default=0, choices=[0,1])
parser.add_argument('-n', '--nulladdress', type=str2bool, help='Allow null address 0x0', default=0, choices=[0,1])
parser.add_argument('-b', '--blockchain', help='Blockchain address', default="http://127.0.0.1:8545")
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-c', '--contract', help='Target contract address', required=True)
requiredNamed.add_argument('-a', '--account', help='Account address', required=True)
requiredNamed.add_argument('-ta', '--artifacts', help="Contract's Truffle artifacts path", required=True)

try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(-1)

try:
    w3 = Web3(Web3.HTTPProvider(args.blockchain))
    accounts_concrete = w3.eth.accounts
except:
    print("Error while connecting to the blockchain at ", args.blockchain)
    exit(-1)

artifacts_path = args.artifacts
contract_address = Web3.toChecksumAddress(args.contract)
user_address = Web3.toChecksumAddress(args.account)
null_address = Web3.toChecksumAddress("0x0000000000000000000000000000000000000000")
accounts_concrete = [null_address] + accounts_concrete
null_address_index = 0

try:
    user_address_index = accounts_concrete.index(user_address)
except ValueError:
    print("specified user address", args.account," is not in the list of the accounts")
    print(accounts_concrete)
    exit(-1)

with open(artifacts_path, 'r') as r:
    artifacts = r.read()
    contract_abi = json.loads(artifacts)['abi']

# Initialize contract
contract_instance = get_contract_instance(w3, contract_address, contract_abi)

accounts_len = len(accounts_concrete)
solver = Solver()

msg_sender, msg_value, msg_gas = Ints('msg_sender msg_value msg_gas')
solver.add(msg_value >= 0)
solver.add(msg_gas >= 0)
solver.add(msg_sender >= 0, msg_sender < accounts_len)

# ===========
# =========== AUTOMATICALLY GENERATED CODE
# ===========


# === SYMBOLIC STATE VARIABLES INITIALIZATION ===
accounts_list = [accounts_concrete]*1
balances_concrete = [get_state_variable(contract_instance, 'balances', *x) for x in list(itertools.product(*accounts_list))]
balances = Array('balances', IntSort(), IntSort())
i = 0
for value in balances_concrete:
    balances = Store(balances, i, value); i = i + 1




# === FORMAL PARAMETERS AND LOCAL VARIABLES ===
cnt, amount, _value = Ints('cnt amount _value')

_receivers = IntVector('_receivers', max_array_len)
_receivers_length = Int('_receivers_length')



# === SYM VARIABLES CONSTRAINTS ===
solver.add(_receivers_length >= 0, _receivers_length < max_array_len)
if not args.nulladdress:
    for x in _receivers: solver.add(x < accounts_len, x != 0)
else:
    for x in _receivers: solver.add(x < accounts_len)
solver.add(_receivers_length == Sum([If(x >= 0, 1, 0) for x in _receivers]))
if (args.distinct): solver.add(Distinct(_receivers))
solver.add(_value >= 0, _value < max_uint(256))
solver.add(msg_sender == user_address_index)



# === SYMBOLIC VARIABLES INITIALIZATION ===
solver.add(cnt == _receivers_length)
solver.add(amount == cnt * _value)



# === SYMBOLIC REQUIRE-OVERFLOW-EXPRESSION ===

# === OVERFLOW CONSTRAINTS ===
solver.add(Or(u_is_overflow(amount, 256) == True))
amount_actual_value = Int('amount_actual_value')
solver.add(amount_actual_value >= 0)
solver.add(amount_actual_value == If(u_is_overflow(amount, 256), u_overflow_value(amount, 256), amount))



# === REQUIRES CONSTRAINTS ===
solver.add(And(cnt > 0, cnt <= 20))
solver.add(And(_value > 0, balances[msg_sender] >= amount_actual_value))





# ===========
# =========== END OF AUTOMATICALLY GENERATED CODE
# ===========


def preprocess(z3result_dic):
    variables = z3result_dic['variables']

    arrays = {}
    parsedVariables = {}

    for variable in variables:
        name = variable['name']
        value = variable['value']

        if '__' in name:
            # is part of IntVector
            base_name = name.split('__')[0]

            if base_name not in arrays:
                arrays[base_name] = []

            # invalid values not skipped here
            arrays[base_name].append((name, value))
        else:
            parsedVariables[name] = value

    for key, l in arrays.items():
        ordered_list_by_number = sorted(l, key = lambda tup: int(tup[0].split('__')[1]))
        arrays[key] = [x[1] for x in ordered_list_by_number]

    return {'sat': z3result_dic['sat'], **arrays, **parsedVariables}

if solver.check():
    m = solver.model()
    vs = [(v,m[v]) for v in m]
    body = '\n'.join(['\t\t{{"name": "{}", "value": "{}"}},'.format(k,v) for (k,v) in vs])[:-1]
    all_dic = '{{\n\t"sat": true,\n\t"variables":[\n{}\n\t]\n}}'.format(body)
else:
    all_dic = '{{\n\t"sat": false,\n\t"variables":[]\n}}'

json_result = json.loads(all_dic)
output_dic = preprocess(json_result)
print(json.dumps(output_dic))