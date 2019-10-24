#! /bin/bash
cd /usr/src/app
ganache-cli -p "8545" -h "0.0.0.0" -u "0" --noVMErrorsOnRPCResponse -e "100000000000" --gasLimit "9999999999" > output/out 2> output/error &
APP_PID=$!
sleep 10