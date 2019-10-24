import { Invariant } from '../../Types/Invariant';
import { Contract } from '../../Contract';
import { Account } from '../../Account';
import { IBigNumber } from '../../Types/BigNumber';
import { TransactionResult } from "../../Types/TransactionResult";
import BigNumber from 'bignumber.js';

export class AllocationLimitInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "CSI5";
    public description: string = "Token allocation must never exceed allocation limits";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this._accounts = accounts;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkAllocationLimit;
    }

    protected async checkAllocationLimit(transactionResult: TransactionResult) : Promise<boolean> {
        // Define token limits
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
    }
}