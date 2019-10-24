import sys, os, glob, re, csv

def get_log_cluster(folder, experiment_input_folder, number_of_experiments):
    
    results = {}

    # Get list of inputs (addr, token-name)
    inputs = []
    addresses_added = []
    solidity_sources = glob.glob(experiment_input_folder + '/*.sol')
    for source_filepath in solidity_sources:
        match = re.search(r"(0x[a-zA-Z0-9]+)-(.+)\.", source_filepath)
        addr = match.group(1)
        if addr not in addresses_added:
            addresses_added.append(addr)
            token_name = match.group(2)
            inputs.append((addr, token_name))
    
    for i in range(0, number_of_experiments):
        experiment_folder_path = "{0}/{1}".format(folder, i)
        experiment_output_folder = "{0}/{1}".format(experiment_folder_path, "output")

        if not os.path.exists(experiment_folder_path):
            print(experiment_folder_path, "does not exists => skipped")
            continue

        if not os.path.exists(experiment_output_folder):
            print(experiment_output_folder, "does not exists => skipped")
            continue
        
        
        # For each input, look at the output log (e.g. <token-addr>.log)
        for input_tuple in inputs:
            addr, token_name = input_tuple
            log_file = "{0}/{1}.log".format(experiment_output_folder, addr)

            if not os.path.exists(log_file):
                msg = "{0}: log of contract with address {1} does not exist".format(experiment_output_folder, addr)
                print(msg)
                continue
            
            with open(log_file) as logfile:
                content = logfile.read()
                if addr not in results:
                    results[addr] = {'address': addr, 'name': token_name, 'I1': 0, 'I2': 0, 'I6': 0, 'I7': 0, 'I8': 0, 'I9': 0}
                    
                results[addr]['I1'] += content.count('I1 has been')
                results[addr]['I2'] += content.count('I2 has been')
                results[addr]['I6'] += content.count('I6 has been')
                results[addr]['I7'] += content.count('I7 has been')
                results[addr]['I8'] += content.count('I8 has been')
                results[addr]['I9'] += content.count('I9 has been')
                
    return results
                

def write_csv(folder, my_dict):
    outputfile = folder + '/combined.csv'
    to_csv = [v for addr, v in list(my_dict.items())]
    keys = to_csv[0].keys()
    with open(outputfile, 'w') as ofile:
        dict_writer = csv.DictWriter(ofile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)
    print("CSV printed successfully at", outputfile)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 cluster_logs.py <test-folder> <experiment_input_folder> <number-of-runs>")
        sys.exit(-1)

    test_folder = sys.argv[1]
    experiment_input_folder = sys.argv[2]
    number_of_runs = int(sys.argv[3])

    if not os.path.exists(experiment_input_folder):
        print(experiment_input_folder, "do not exists")
        sys.exit(-1)

    my_dict = get_log_cluster(test_folder, experiment_input_folder, number_of_runs)
    write_csv(test_folder, my_dict)
