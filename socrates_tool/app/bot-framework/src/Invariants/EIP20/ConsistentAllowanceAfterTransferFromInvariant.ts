import BigNumber from 'bignumber.js';
import { Invariant } from '../../Types/Invariant';
import { Contract } from '../../Contract';
import { Account } from '../../Account';
import { IBigNumber } from '../../Types/BigNumber';
import { TransactionResult } from '../../Types/TransactionResult';
import { EIP20Account } from '../../EIP20/EIP20Account';

export class ConsistentAllowanceAfterTransferFromInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "I7";
    public description: string = "Trasferred amount of money should be subtracted from the allowance of the 'from' address";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    private _accountsAddr: string[];
    private _balances: {[addr: string]: IBigNumber};
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this._accounts = accounts;
        this._accountsAddr = this._accounts.map(acc => acc.address);
        this.hasBeenViolated = false;
        this._balances = {};
        this.checkInvariant = this.checkConsistentAllowedTransferFrom;
    }

    private async getSubsetBalancesMap(accounts: string[]) : Promise<{[addr2:string]: IBigNumber}> {
        let balances: {[addr2:string]: IBigNumber} = {};
        for (const account of accounts) {
            balances[account] = await this._target.sendTransactionByName('balanceOf', [account]);
        }
        return balances;
    }

    protected async isTransferFromSuccessful(transactionResult: TransactionResult) : Promise<boolean> {
        if (transactionResult['successful'] == false) return false;
        let params: any = transactionResult["params"];

        let sender: string = transactionResult['address'];
        let from: any = params[0];
        let to: any = params[1];
        let targets: any = [sender, from, to];

        this.getPreviousBalancesMap(); // get previous map
        let currentBalances = await this.getSubsetBalancesMap(targets); // get current map
        
        // something changed in balance of contract involved = successful transfer
        for (let i = 0; i < targets.length; i++) {
            const addr1 = targets[i];
            let b1: IBigNumber = currentBalances[addr1];
            let b2: IBigNumber = this._balances[addr1];
            if (!b1.equals(b2)){
                return true; 
            }
        }
        return false;
    }

    private getPreviousBalancesMap() {       
        // get previous balances map
        for (let i = 0; i < this._accounts.length; i++) {
            const addr1 = this._accounts[i].address;
            this._balances[addr1] = (this._accounts[i] as EIP20Account).tokenBalance;
        }
    }

    protected async checkConsistentAllowedTransferFrom(transactionResult: any) : Promise<boolean> {
        if (transactionResult == null) return true;

        if (transactionResult["action"] == "transferFrom" && await this.isTransferFromSuccessful(transactionResult)){
            let sender: string = transactionResult['address'];
            let params: string = transactionResult["params"];
            let from: string = params[0];
            let transferredAmount: IBigNumber =  new BigNumber(params[2]);

            // Get the allowance [from][msg.sender] before the transaction
            let allowedBeforeTransaction = new BigNumber(0);
            let accountIndex = this._accountsAddr.indexOf(from);
            let fromEIP20Account: EIP20Account = this._accounts[accountIndex] as EIP20Account;
            if (fromEIP20Account.allowance[sender]) allowedBeforeTransaction = fromEIP20Account.allowance[sender];   

            // Check the expected allowance after the transaction
            let allowedAfterTransaction: IBigNumber = await this._target.sendTransactionByName('allowance', [from, sender]) as IBigNumber;
            let expectedAllowedAfterTransaction = allowedBeforeTransaction.minus(transferredAmount);
            return allowedAfterTransaction.equals(expectedAllowedAfterTransaction);
        }

        return true;
    }
}