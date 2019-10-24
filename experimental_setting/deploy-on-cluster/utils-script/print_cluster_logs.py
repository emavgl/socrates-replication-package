import sys, os, glob, re, csv

def get_log_cluster(folder, number_of_experiments):
    
    results = {}
    
    for i in range(0, number_of_experiments):
        experiment_folder_path = "{0}/{1}".format(folder, i)
        experiment_input_folder = "{0}/{1}".format(experiment_folder_path, "inputs")
        experiment_output_folder = "{0}/{1}".format(experiment_folder_path, "output")
        
        if not os.path.exists(experiment_input_folder):
            print(experiment_input_folder, "do not exists")
            
        if not os.path.exists(experiment_output_folder):
            print(experiment_output_folder, "do not exists")
        
        solidity_sources = glob.glob(experiment_input_folder + '/*.sol')
        
        inputs = []
        for source_filepath in solidity_sources:
            match = re.search(r"([a-zA-Z0-9]+)-(.+)\.", source_filepath)
            addr = match.group(1)
            token_name = match.group(2)
            inputs.append((addr, token_name))
        
        for input_tuple in inputs:
            addr, token_name = input_tuple
            log_file = "{0}/{1}.log".format(experiment_output_folder, addr)
            
            with open(log_file) as logfile:
                content = logfile.read()
                if addr not in results:
                    results[addr] = {'address': addr, 'name': token_name, 'I1': 0, 'I2': 0, 'I6': 0, 'I7': 0, 'I8': 0, 'I9': 0}
                    
                results[addr]['I1'] += content.count('I1')
                results[addr]['I2'] += content.count('I2')
                results[addr]['I6'] += content.count('I6')
                results[addr]['I7'] += content.count('I7')
                results[addr]['I8'] += content.count('I8')
                results[addr]['I9'] += content.count('I9')

                
    return results
                

def write_csv(folder, my_dict):
    outputfile = folder + '/combined.csv'
    to_csv = [v for addr, v in list(my_dict.items())]
    keys = to_csv[0].keys()
    with open(outputfile, 'w') as ofile:
        dict_writer = csv.DictWriter(ofile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)
        

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 cluster_logs.py testfolder number_of_runs")
        sys.exit(-1)

    folder = sys.argv[1]
    number_of_runs = int(sys.argv[2])
    my_dict = get_log_cluster(folder, number_of_runs)
    write_csv(folder, my_dict)
