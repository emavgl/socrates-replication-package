# Contract

A **Contract** represents the contract under test. The class Contract *extends* the class *Accounts* and defines two more functions:

```javascript
- sendTransaction(contractFunction: ABI.Types.Function, params?: any) : Promise<any>
- sendTransactionByName(functionName: string, params?: any) : Promise<any>
```

Both the functions can be used to submit a new transaction to the deployed contract via the *Web3.Js* contract instance. The functions return a **Promise** with the result of the transaction execution.

The first parameter (*ABI.Types.Function* or *string*) is a reference to the contract function to call and, the second *(optional)* parameter is an array of this form:

```typescript
[param1, param2, ... paramN, {'from': senderAddress, 'value': etherSent}]
```

At the beginning, the array contains an ordered sequence of parameters which are the arguments of the target Solidity function (*param1*, *param2*, etc.). The
last element of the array is **mandatory** object containing the fields:

- *from*: the address of sender
- *value*: the amount of Eth to send together with the transaction