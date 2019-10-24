# Socrates tool

## Build

Build the image

```bash
sudo docker-compose build
```

## Run

Run a new bash using the `socrates` image.
It will use a folder named `inputs` as a shared folder,
so that you are free to put there your smart contracts and file.

```bash
 sudo docker-compose run --entrypoint "" socrates bash
```

Once you are in the bash

```bash
 # run ganache
bash /usr/src/app/run-ganache.sh

# -s solidity source file
# -c contract name
# -t path-to-test-configuration.js
# -o output-dir
python3 run.py -s inputs/0x000-BecToken.sol -c BecToken -t inputs/test_1.js -o output/bectoken

# or

# run 5 tests for all .sol file in inputs
bash run_test_k_times.sh inputs/ inputs/test_1.js 5
```