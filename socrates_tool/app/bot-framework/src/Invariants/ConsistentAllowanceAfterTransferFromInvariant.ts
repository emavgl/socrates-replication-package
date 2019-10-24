import { Invariant } from "../Types/Invariant";
import { Contract } from "../Contract";
import { IBigNumber } from "../Types/BigNumber";
import { Account } from '../Account';
import BigNumber from 'bignumber.js';

export class ConsistentAllowanceAfterTransferFromInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "I7";
    public description: string = "Trasferred amount of money should be subtracted from the from address";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    private _allowance: any;
    private _balances: any;
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this._accounts = accounts;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkConsistentAllowedTransferFrom;
        this._allowance = null;
        this._balances = null;
    }

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

    private async getBalancesMap() : Promise<{[addr2:string]: IBigNumber}> {
        let balances: {[addr2:string]: IBigNumber} = {};
        for (let i = 0; i < this._accounts.length; i++) {
            const addr1 = this._accounts[i].address;
            balances[addr1] = await this._target.sendTransactionByName('balanceOf', [addr1]);
        }
        return balances;
    }


    protected async isTransferFromSuccessful(transactionResult) : Promise<boolean> {
        if (transactionResult['successful'] == false) return false;
        let currentBalances = await this.getBalancesMap();
        for (let i = 0; i < this._accounts.length; i++) {
            const addr1 = this._accounts[i].address;
            let b1: IBigNumber = currentBalances[addr1];
            let b2: IBigNumber = this._balances[addr1];
            if (!b1.equals(b2)){
                return true; 
            }
        }
        return false;
    }

    private async updateMaps() {
        this._allowance = await this.getAllowanceMap();
        this._balances = await this.getBalancesMap();
    }

    protected async checkConsistentAllowedTransferFrom(transactionResult: any) : Promise<boolean> {
        if (transactionResult == null){
            try {
                await this.updateMaps();                
            } catch (error) {
                // There is some interface inconsistency
                return false;
            }
            return true;
        }

        let allowanceBeforeTransaction = this._allowance as { [addr1:string]: {[addr2:string]: IBigNumber}; };
        let allowanceAfterTransaction = await this.getAllowanceMap();

        if (transactionResult["action"] == "transferFrom" && await this.isTransferFromSuccessful(transactionResult)){
            let sender: string = transactionResult['address'];
            let params: any = transactionResult["params"];
            let from: any = params[0];
            let transferredAmount: IBigNumber =  new BigNumber(params[2]);

            let allowedBeforeTransaction = allowanceBeforeTransaction[from][sender];
            let allowedAfterTransaction = allowanceAfterTransaction[from][sender];

            let expectedAllowedAfterTransaction = allowedBeforeTransaction.minus(transferredAmount);
            let toReturn: boolean = allowedAfterTransaction.equals(expectedAllowedAfterTransaction);

            await this.updateMaps();     
            return toReturn;
        }

        await this.updateMaps();
        return true;
    }
}