import { Invariant } from "../Types/Invariant";
import { Contract } from "../Contract";
import { IBigNumber } from "../Types/BigNumber";
import { Account } from '../Account';
import BigNumber from 'bignumber.js';

export class TotalBalanceLessThanTokenLimit implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "CSI3";
    public description: string = "Sum of balances must be always lower or equal than tokenLimit";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this._accounts = accounts;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkTokenLimit;
    }

    protected async checkTokenLimit(transactionResult: any) : Promise<boolean> {
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
    }
}