import os
import sys
import argparse
import shutil
import subprocess

# to use the module ast_helper
sys.path.append("./tools/overflow/")

def exec_command(command, showstdout=False):
    
    p = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    output = ""
    
    if showstdout:
        while p.poll() is None:
            o = p.stdout.readline().decode("utf-8").replace('\n', '')
            output += o
            print(o)
    
    stdout, stderr = p.communicate()
        
    if stdout is not None: stdout = stdout.decode("utf-8")
    else: stdout = ""
    if stderr is not None: stderr = stderr.decode("utf-8")
    else: stderr = ""
    
    if showstdout and (stdout or stderr):
        print(stdout + stderr)
    
    output += stdout + stderr
    
    if p.returncode != 0:
        
        if 'AssertionError' in output:
            return output
        
        print("stdout: ", stdout )
        print("stderr: ", stderr )
        
        raise Exception("Error when executing: " + command)
    
    return output

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def clean():
    shutil.rmtree('./tmp')
    os.remove('./tmp.sol')
    os.remove('./contract_tmp.sol')

def main(args):
    
    # === Create new folder
    # it will delete and re-create the folder if it already exists
    print("creating new folder")
    project_folder_name = args.outputfolder
    
    if os.path.exists(project_folder_name):
        shutil.rmtree(project_folder_name)
    
    os.makedirs(project_folder_name)

    # === Copy Template
    print("copying the template")
    try:
        exec_command('cp -r ./template/* {}/'.format(project_folder_name))
    except:
        print("WARNING: no template folder found")
        sys.exit(-1)
        
    
    if args.testconfig and os.path.exists(args.testconfig):
        print("copying the test script ", args.testconfig )
        exec_command('cp {} {}/test/test_1.js'.format(args.testconfig, project_folder_name))
    
    exec_command('cp {} {}/contract_tmp.sol'.format(args.source, project_folder_name))
    
    os.chdir(project_folder_name)
    
    try:
    
        # Change the fallback function
        instrumentation_command = 'python3 ./tools/overflow/utils/instrumentation.py '
        instrumentation_command += '-s contract_tmp.sol -o ./contracts/{}.sol '.format(args.contract)
        instrumentation_command += '-p="0" -g="0" -t="0" -if="0" -r="0" -a="0" -f="1"'
        exec_command(instrumentation_command)
    
        # Compile and save Artifacts of the original code
        exec_command('truffle compile')
        exec_command('mv ./build/contracts/{}.json original_artifacts.json'.format(args.contract))
        exec_command('rm -rf ./build')

        # Instrument the original code to use it then together with z3 scripts (getters, public variables etc)
        print("instrumenting and copy the contract to deploy")
        instrumentation_command = 'python3 ./tools/overflow/utils/instrumentation.py '
        instrumentation_command += '-s contract_tmp.sol -o ./contracts/{}.sol '.format(args.contract)
        instrumentation_command += '-p="1" -g="1" -t="0" -if="0" -r="0" -a="0" -f="1"'
        exec_command(instrumentation_command)
    
        # === Run Z3 static analysis to generate the z3 scripts
        print("running z3 analysis")

        if args.instrument:
            instrumentation_command = "python3 ./tools/overflow/utils/instrumentation.py -o tmp.sol -s contract_tmp.sol"
            exec_command(instrumentation_command)
            exec_command("python3 ./tools/overflow/main.py -s tmp.sol -o outputs -c " + args.contract)
        else:
            exec_command("python3 ./tools/overflow/main.py -s {} -o outputs -c {}".format(args.source, args.contract))
            
        # Change name to 'generated'
        try:
            exec_command('cp ./outputs/{}/*_z3.py ./outputs/'.format(args.contract))
            exec_command('mv outputs generated')
        except:
            print("WARNING: no output folder found, overflow behaviour cannot apply")
    
        # === Add Migrations
        print("adding migrations")
        
        with open('./migrations/2_deploy_contracts.js', 'r') as migrationfile:
            content = migrationfile.read()
        
        with open('./migrations/2_deploy_contracts.js', 'w') as migrationfile:
            content = content.replace('<contractname>', args.contract)
            migrationfile.write(content)
        
        # === Add test
        print("adding test")
        
        with open('./test/test_1.js', 'r') as testfile:
            content = testfile.read()
            
        with open('./test/test_1.js', 'w') as testfile:
            testfile.truncate(0)
            content = content.replace('<contractname>', args.contract)
            testfile.write(content)
            
        # === Truffle Compile
        print("truffle compile...")
        exec_command('truffle compile')
        
        # === Truffle migrate
        print('truffle migrate...')
        exec_command('truffle migrate')
    
        # === Run tests
        print('running tests...')
        out = exec_command('truffle test', showstdout=True)

        print("\n======================")
        print("Name: ", args.contract)

        if 'AssertionError' not in out:
            print("The framework DOES NOT report an error")
        else:
            print("The framework reports an AssertionError:" )
            
            if 'totalSupply' in out:
                print("I2 violated")
            else:
                print("I1 violated")

    except Exception as e:
        # delete the project_folder_name
        os.chdir('..')
        #shutil.rmtree(project_folder_name)
        raise e
        
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automatic test')

    parser.add_argument('-i', '--instrument', type=str2bool, help='Instrument for Z3 analysis',
                        default=1, choices=[False, True])
    
    
    requiredNamed = parser.add_argument_group('Required arguments')
    requiredNamed.add_argument('-s', '--source', help='Source file (solidity)', required=True)
    requiredNamed.add_argument('-c', '--contract', help='Contract name', required=True)
    requiredNamed.add_argument('-t', '--testconfig', help='Test configuration file', required=False)
    requiredNamed.add_argument('-o', '--outputfolder', help='Output folder', required=True)
    
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(-1)

    # Run
    main(args)
    
    try:
        clean()
    except:
        pass

    sys.exit()
