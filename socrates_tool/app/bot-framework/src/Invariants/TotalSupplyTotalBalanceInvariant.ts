import { Invariant } from "../Types/Invariant";
import { IBigNumber } from '../Types/BigNumber';
import { Contract } from '../Contract';
import BigNumber from 'bignumber.js';
import { Account } from '../Account';

export class TotalSupplyTotalBalanceInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "I2";
    public description: string = "TotalSupply must be equal to the sum of the balances";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this._accounts = accounts;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkTotalBalance;
    }

    protected async checkTotalBalance(transactionResult: any) : Promise<boolean> {
        let eip20 = this._target;
        let accounts = this._accounts;

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
}