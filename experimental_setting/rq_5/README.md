 # Contract Specific Invariants

 | Label | Formula                                                                                       |
|-------|-----------------------------------------------------------------------------------------------|
| CS1   | Owner1 -> Owner2; only if Sender(T) == Owner1                                                 |
| CS2   | totalSupply\_before\_T <= totalSupply\_after\_T                                               |
| CS3   | Sum(balances) <= tokenLimit                                                                   |
| CS4   | successful(enableTokenTransfer | disableTokenTransfer) only if Sender(T) == walletAddress     |
| CS5   | totalAllocatedTokens <= (ADVISORS_AMOUNT + FOUNDERS_AMOUNT + HOLDERS_AMOUNT + RESERVE_AMOUNT) |
| CS6   | successful(getToken) only if Sender(T) == owner                                               |

 ## CSI1

**Target contract**: FansChainToken
**Vulnerability**: constructor of contract Owned mismatch (lowercase)
**Description**: No one can change the owner except the owner itself
**Formula**: Owner1 -> Owner2; only if Sender(T) == Owner1

Invariant Implementation

```javascript
    protected async checkOwner(transactionResult: TransactionResult | null) : Promise<boolean> {
        let currentOwner = await this._target.sendTransactionByName('owner');

        if (
            currentOwner != this._ownerAddr &&
            transactionResult["successful"] &&
            transactionResult['address'] != this._ownerAddr) {
            return false;
        }

        this._ownerAddr = currentOwner;
        return true;
    }
```

## CSI2

**Target contract**: PKT
**Vulnerability**:  overflow inside require(totalSupply + _value <= tokenLimit)
**Description**: TotalSupply amount must never be decreased
**Formula**: totalSupply_before_T <= totalSupply_after_T

Invariant Implementation

```javascript
    protected async checkTotalSupply(transactionResult: TransactionResult) : Promise<boolean> {
        let currentTotalSupply = await this._target.sendTransactionByName('totalSupply');

        if (currentTotalSupply.lessThan(this.oldTotalSupply)){
            return false;
        }

        this.oldTotalSupply = currentTotalSupply;
        return true;
    }
```

### CSI3

**Target contract**: PKT
**Vulnerability**:  overflow inside require(totalSupply + _value <= tokenLimit)
**Description**: Sum of balances must be always lower or equal than tokenLimit
**Formula**: Sum(balances) <= tokenLimit

Invariant Implementation

```javascript
    let tokenLimit: IBigNumber = await this._target.sendTransactionByName('tokenLimit') as IBigNumber;

    let eip20 = this._target;
    let accounts = this._accounts;

    // Initialize Balance to 0
    let totalBalance: IBigNumber = new BigNumber(0);
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
    return totalBalance.lessThanOrEqualTo(tokenLimit);
```

###  CSI4

**Target contract**: IcxToken
**Vulnerability**:  Wrong require condition in onlyFromWallet modifier  causes everyone call owner specific functions
**Description**: Only walletAddress can successfully pause/restart token transfer
**Formula**: successful(enableTokenTransfer) or successful(disableTokenTransfer) only if Sender(T) == walletAddress

Invariant Implementation

```javascript
    protected async checkOwner(transactionResult: TransactionResult | null) : Promise<boolean> {
        let walletAddress = await this._target.sendTransactionByName('walletAddress');

        if (transactionResult["successful"] && 
            (transactionResult["action"] == "enableTokenTransfer" || transactionResult["action"] == "disableTokenTransfer") && 
            transactionResult['address'] != this._walletAddress) {
            return false;
        }

        return true;
    }
```

### CSI5

**Target contract**: Legolas
**Vulnerability**:  Overflow inside require may causes token allocation to overflow the maximum allocation limit
**Description**: Token allocation must never exceed allocation limits
**Formula**: totalAllocatedTokens <=  ADVISORS_AMOUNT + FOUNDERS_AMOUNT + HOLDERS_AMOUNT + RESERVE_AMOUNT

Invariant Implementation

```javascript
    let ADVISORS_AMOUNT: IBigNumber = await this._target.sendTransactionByName('ADVISORS_AMOUNT') as IBigNumber;
    let FOUNDERS_AMOUNT: IBigNumber = await this._target.sendTransactionByName('FOUNDERS_AMOUNT') as IBigNumber;
    let HOLDERS_AMOUNT: IBigNumber = await this._target.sendTransactionByName('HOLDERS_AMOUNT') as IBigNumber;
    let RESERVE_AMOUNT: IBigNumber = await this._target.sendTransactionByName('RESERVE_AMOUNT') as IBigNumber;
    let totalSupply: IBigNumber = await this._target.sendTransactionByName('totalSupply') as IBigNumber;
    let tokenLimit: IBigNumber = ADVISORS_AMOUNT.plus(FOUNDERS_AMOUNT).plus(HOLDERS_AMOUNT).plus(RESERVE_AMOUNT);

    let eip20 = this._target;
    let accounts = this._accounts;

    // Initialize Balance to 0
    let totalBalance: IBigNumber = new BigNumber(0);
    let tmp: IBigNumber = new BigNumber(0);

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

    let totalAllocatedTokens: IBigNumber = totalBalance.minus(totalSupply);

    // Get totalSupply and define the assert statement
    return totalAllocatedTokens.lessThanOrEqualTo(tokenLimit);
```

### CSI6

**Target contract**: Amorcoin
**Vulnerability**: Function getToken has not modifier onlyOwner
**Description**: Only the owner should be able to mint new tokens
**Formula**: successful(getToken) only if Sender(T) == owner

Invariant Implementation

```javascript
    protected async checkOwner(transactionResult: TransactionResult | null) : Promise<boolean> {
        let owner = await this._target.sendTransactionByName('owner');

        if (transactionResult["successful"] && 
            transactionResult["action"] == "getToken" && 
            transactionResult['address'] != owner) {
            return false;
        }

        return true;
    }
```
