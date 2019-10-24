# Sol-Overflow-Solver

Tool for automatic generation of Z3 constraints to obtain the concrete input values for a solidity function. Such values will make some local variables overflow and pass the requires anyway.

## Requirements

- Python3
- Z3, PyZ3 Solver (pip install -r requirements.txt)
- [Solc](http://solidity.readthedocs.io/en/v0.4.24/installing-solidity.html#binary-packages)

# How to use

1. The script requires to read all the state variables of the program, so these variables must be public. To do so, run the script:

    ```
        python3 utils/all_public.py source.sol dest.sol
    ```

2. Run and deploy `dest.sol`

3. Run the main script to generate automatically the z3 scripts for the function under test.

    ```
        python3 main.py path/to/Contract.sol functionName
    ```

    Program will output a python script `functionName_z3.py`.

4. Then, to obtain the concrete formal parameters to trigger a variable overflow run

    ```
        python3 functionName_z3.py contract_artifact.json contract_address user_address
    ```