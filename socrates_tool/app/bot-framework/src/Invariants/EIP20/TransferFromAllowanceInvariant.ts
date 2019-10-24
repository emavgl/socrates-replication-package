import { Invariant } from '../../Types/Invariant';
import { Contract } from '../../Contract';
import { Account } from '../../Account';
import { IBigNumber } from '../../Types/BigNumber';
import { TransactionResult } from '../../Types/TransactionResult';
import { EIP20Account } from '../../EIP20/EIP20Account';
import BigNumber from 'bignumber.js';

export class TransferFromAllowanceInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "I6";
    public description: string = "No successfully transferFrom if the user transfers more than the allowed amount";
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

    /*
    private async getAllowanceMap() : Promise<any> {
        let allowance: { [addr1:string]: {[addr2:string]: IBigNumber}; } = {};
        for (let i = 0; i < this._accounts.length; i++) {
            for (let j = 0; j < this._accounts.length; j++) {
                const addr1 = this._accounts[i].address;
                const addr2 = this._accounts[j].address;
                if (allowance[addr1] == null) allowance[addr1] = {};
                let allowed: IBigNumber = await this._target.sendTransactionByName('allowance', [addr1, addr2]) as IBigNumber;
                allowance[addr1][addr2] = allowed;
            }
        }
        return allowance;
    }
    */

    private async getSubsetBalancesMap(accounts: string[]) : Promise<{[addr2:string]: IBigNumber}> {
        let balances: {[addr2:string]: IBigNumber} = {};
        for (const account of accounts) {
            balances[account] = await this._target.sendTransactionByName('balanceOf', [account]);
        }
        return balances;
    }

    protected async isTransferFromSuccessful(transactionResult) : Promise<boolean> {
        if (transactionResult['successful'] == false) return false;
        let params: any = transactionResult["params"];

        let sender: string = transactionResult['address'];
        let from: string = params[0];
        let to: string = params[1];
        let targets: string[] = [sender, from, to];

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

    protected async checkConsistentAllowedTransferFrom(transactionResult: TransactionResult) : Promise<boolean> {
        if (transactionResult == null){
            return true;
        }

        if (transactionResult["action"] == "transferFrom" && await this.isTransferFromSuccessful(transactionResult)){
            let sender: string = transactionResult['address'];
            let params: any = transactionResult["params"];
            let from: any = params[0];
            let amount: IBigNumber =  new BigNumber(params[2]);

            // Check that our account was allowed to spend more than "amount"
            let allowedAmountOfTokens = new BigNumber(0);
            let accountIndex = this._accountsAddr.indexOf(from);
            let fromEIP20Account: EIP20Account = this._accounts[accountIndex] as EIP20Account;
            if (fromEIP20Account.allowance[sender]) allowedAmountOfTokens = fromEIP20Account.allowance[sender];                

            return allowedAmountOfTokens.greaterThanOrEqualTo(amount);
        }

        return true;
    }
}