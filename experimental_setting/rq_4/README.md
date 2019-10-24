# Test contracts using Echidna
 
## Config file

I edited the config file to specify a list of addresses:

```yaml
#Contract's address in the EVM
contractAddr: "0x00a329c0648769a73afac7f9381e08fb43dbea72"
#Sender's address in the EVM
sender: "0x00a329c0648769a73afac7f9381e08fb43dbea70"
#List of addresses that will be used in all tests
addrList: ["0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000002", "0x0000000000000000000000000000000000000004", "0x0000000000000000000000000000000000000005", "0x0000000000000000000000000000000000000006", "0x0000000000000000000000000000000000000007", "0x0000000000000000000000000000000000000008", "0x0000000000000000000000000000000000000009"]
```

## Invariants

### I1 (successful transaction with overflow)

The contract needs additional instrumentation to store as contract variables the operands of each operations.
Those operands are read from inside the invariant definition `echidna_*`.

For instance, suppose you have a sum operation:

```
    function ... () {
        ...
        uint256 c = a + b;
        ...
    }
```

it needs to be converted in

```
    uint256 public add_1;
    uint256 public add_2;
    uint256 public add_result;
    
    function ... () {
        ...
        add_1 = a;
        add_2 = b;
        uint256 c = a + b;
        add_result = c;
        ...
    }
```

Then the invariant can be defined as follows:

```
    function echidna_invariant_I1() public returns (bool) {
        return (add_result >= add_1);
    }
```

You can re-use the condition inside the library *SafeMath* to ensure that the operations did not overflow.
You need to define an invariant for each *unsafe* operation.

### I2 (totalBalance = sum(balances))

Since we have a limited number of addresses. We can write the echidna's invariant as follow:

```
address address_1 = 0x00a329c0648769a73afac7f9381e08fb43dbea72; // contract
address address_2 = 0x00a329c0648769a73afac7f9381e08fb43dbea70; // sender
address address_3 = 0x0000000000000000000000000000000000000010; // addr_1
address address_4 = 0x0000000000000000000000000000000000000001; // addr_2
address address_5 = 0x0000000000000000000000000000000000000002; // addr_3
address address_6 = 0x0000000000000000000000000000000000000003; // ...
address address_7 = 0x0000000000000000000000000000000000000004; // ...
address address_8 = 0x0000000000000000000000000000000000000005; // ...
address address_9 = 0x0000000000000000000000000000000000000006; // ...
address address_10 = 0x0000000000000000000000000000000000000007; // ...
address address_11 = 0x0000000000000000000000000000000000000008; // ...
address address_12 = 0x0000000000000000000000000000000000000009;

function echidna_invariant_I2() public returns (bool) {

    uint256 sumBalances =   balances[address_1] +
                            balances[address_2] +
                            balances[address_3] +
                            balances[address_4] +
                            balances[address_5] +
                            balances[address_6] + 
                            balances[address_7] +
                            balances[address_8] +
                            balances[address_9] +
                            balances[address_10] +
                            balances[address_11] +
                            balances[address_12];
                            
    return totalSupply == sumBalances;
}
```

Note: The sender of the transaction is always `address_2` due to echidna limitation.

## Command

To run the tests:

```
/home/eviglianisi/.local/bin/echidna-test ./0x3495ffcee09012ab7d827abf3e3b3ae428a38443-BecToken.sol BecToken --config="config.yaml"
```


### Docker

If you want to use docker instead you need to open a bash inside a new container 

```
sudo docker run -v `pwd`:/src -it trailofbits/echidna  /bin/bash 
```

and 

```
export LC_ALL=C.UTF-8
```

then you can run `echidna_test`.


## Common questions without trivial answers

### Who is the contract deployer?

Since the initial amount of money is often set to the balance of the contract owner, I made the invariant definition return `return (currentSupply == balanceOf[address_1]);`. As expected the invariant is never violated.  
I tried instead with `return (currentSupply == balanceOf[address_2]);` and the invariant failed after the first iteration.

Result:

The contract deployer is the **contract itself**.
The msg.sender inside the constructor refers to the contract address specified in the configuration file.

Open issue: https://github.com/trailofbits/echidna/issues/146

NOTE.

Since the contract ownes all the tokens. And the contract address never makes calls. We are forced to set the transaction sender == contract.address in the configuration file.

## Limitations

- Do not manage correctly the keyword "this" (address of the contract)