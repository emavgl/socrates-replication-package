import os
import sys
from glob import glob

if len(sys.argv) != 3:
    help_msg = "Usage: python3 find.py <contract-address> <invariants1>-<invariant2>...\n"
    print(help_msg)
    sys.exit(-1)

addr = sys.argv[1]
vulnerabilities = sys.argv[2].split('-')

dirs = glob("./*/")
for dir in dirs:
    file_path = dir + 'output/' + '{0}.log'.format(addr)
    if os.path.isfile(file_path):
        with open(file_path) as f:
            content = f.read()
            found = True
            for v in vulnerabilities:
                if v not in content:
                    found = False
                    break

            if found:
                print("Found all vulnerabilities in:")
                print(file_path)