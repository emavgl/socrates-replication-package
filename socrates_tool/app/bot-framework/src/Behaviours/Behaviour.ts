import { Context } from '../Context';
import { Contract } from "../Contract";
import { Account } from "../Account";
import { TransactionResult } from '../Types/TransactionResult';

export abstract class Behaviour {

    protected _target: Contract;
    protected _account: Account;
    protected _context: Context;
    protected _label: string;
    protected _counter: number;

    /**
     * Istantiate new Behaviour
     * @constructor
     * @param  {Contract} target - Contract under test
     * @param  {string} account -  Account associated to the bot
     * @param  {Context} context - Context in which the bots runs
     */
    constructor(target: Contract, account: Account, context: Context) {
        this._target = target;
        this._account = account;
        this._context = context;
        this._label = "Behaviour";
        this._counter = 0;
    }

    /**
     * Make the account perform an action
     * @returns Promise
    */
    public async performAction() : Promise<any> {
        this._counter += 1;
    }
}