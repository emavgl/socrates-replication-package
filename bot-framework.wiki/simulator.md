# Simulator

The simulator's constructor takes:

- Target contract: *Contract*
- Context: *Context*

The simulator has a method **start(duration)** to start a new simulation.
The method takes in input the parameter **duration** which is the maximum number of steps the bots can perform.

```javascript
public async start(duration: number) : Promise<void> {

    // initialize the status of the accounts
    await this.updateStatus();

    // for each round, let bots perform actions
    let bots = this._context.bots;
    for (let currentStep = 0; currentStep < duration; currentStep++){

        for (const bot of bots) {
            try {
                // perform an action
                let transactionResult = await bot.performAction();
                // check the invariants
                await this.checkInvariants(transactionResult);
            } catch (error) {
                // log error and throw
                ...
            }                
        }
    }
}
```

The method is composed of the main loop where, for each round, all the bots perform an action, one after the other.
After each bot action, the method `checkInvariants(transactionResult)` is called.

The tester should extend the class *Simulator* to implement his own invariants and check.
By default, the method has the following implementation:

```javascript
protected checkSuccessfulOverflow(transactionResult: any) {
    return  transactionResult != null &&
            transactionResult['overflow'] != null &&
            transactionResult['overflow'] == true;
}

protected async checkInvariants(transactionResult: any) : Promise<void> {
    assert(!this.checkSuccessfulOverflow(transactionResult), "Successful transaction execution with overflow");
}
```

The method *checkInvariant* has an assertion to check that the latest successful transaction execution did not make some inner expression perform an overflow.

## EIP20 Simulator

The `EIP20Simulator` re-defines the method *checkInvariant* to include also an EIP20 specific invariant (I2) that states that the sum of the users' token balances must be equal to the total supply of emitted tokens.

The method *checkInvariants* now check two invariants, the order of the checks is important.
The simulation ends when the first *assertion* is violated. In this case, we decided to check the invariant I2 first (the most significant) and then I1.

The check of the invariant I2 is implemented in the method *checkTotalBalance*.
We first sum each user token balance and then we check that the sum of all the balances is equal to the value returned by the EIP20 function `totalSupply`.

```javascript
private async checkTotalBalance() : Promise<boolean> {
    let eip20 = this._target as Contract;
    let accounts = this._context.accounts;

    // Initialize Balance to 0
    let totalBalance = new BigNumber(0);
    let tmp = new BigNumber(0);

    // Get the balances of all the accounts
    let balancesList = new Array<IBigNumber>();
    for (const account of accounts) {
        let balance = await eip20.sendTransactionByName('balanceOf', [account.address]);
        balancesList.push(balance);         
    }

    // Sum each balance to obtain the total balance
    for (const b of balancesList) {
        totalBalance = tmp.plus(b);
        tmp = totalBalance;
    }
    
    // Get totalSupply and define the assert statement
    let tSupply = await eip20.sendTransactionByName('totalSupply');


    return (tSupply as IBigNumber).equals(totalBalance);
}

protected async checkInvariants(transactionResult: any) : Promise<void> {
    try {
        const result = await this.checkTotalBalance();
        assert(result, "Total balance not equal to totalSupply");
        assert(!this.checkSuccessfulOverflow(transactionResult), "Successful transaction execution with overflow");
        } catch (error) {
        Logger.info({ "label": "assertionFail", "error": error });
        await this.updateStatus();
        this.printStatus();
        throw error;
    }
}
```
