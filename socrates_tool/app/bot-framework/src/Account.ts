import { Contract } from './Contract';
import { Logger } from './Logger';
import { IBigNumber } from "./Types/BigNumber";
import BigNumber from 'bignumber.js';

export class Account {

    protected _address: string;
    protected _balance: IBigNumber;

    /**
     * Create a new account instance
     * @constructor
     * @param  {string} address - address of the account
     */
    constructor(address: string, balance?: IBigNumber | number | null) {
        this._address = address;
        this._balance = new BigNumber(0); // TODO
    }
    
    /**
     * @returns string - Address of the account
     */
    public get address() : string {
        return this._address;
    }
    
    /**
     * Returns account's balance (wei)
     * @param balance: IBigNumber
     * @returns void
    */
    public get balance(): IBigNumber {
        return this.balance;
    }

    /**
     * Update the status of the account
     * To update Ethereum Balance you need a Web3JS instance connected to the blockchain
     * @returns Promise
     */
    public async updateStatus(contract: Contract, transactionResult?: any, web3jsInstance?: any): Promise<void> {
    }

    /**
     * Log the current state of the account
     */
    public printStatus() : void {
        Logger.info({"label": "status", "address": this.address})
    }

}