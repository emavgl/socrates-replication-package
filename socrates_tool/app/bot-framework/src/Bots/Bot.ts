import { Context } from '../Context';
import { Contract } from "../Contract";
import { Account } from "../Account";
import { Behaviour } from '../Behaviours/Behaviour';
import { RandomValueGenerator } from '../Util/RandomValueGenerator';
import { RandomBehaviour } from '../Behaviours/RandomBehaviour';
import { OverflowBehaviour } from '../Behaviours/OverflowBehaviour';
import { BoundaryValueGenerator } from '../Util/BoundaryValueGenerator';
import { BoundaryBehaviour } from '../Behaviours/BoundaryBehaviour';
import { TransactionResult } from '../Types/TransactionResult';


export class Bot {

    protected _target: Contract;
    protected _account: Account;
    protected _context: Context;
    protected _behaviours: Behaviour[]; 

    /**
     * Create a new Bot instance
     * @constructor
     * @param  {Contract} target - Contract under test
     * @param  {string} account -  Account associated to the bot
     * @param  {Context} context - Context in which the bots runs
     */
    constructor(target: Contract, account: Account, context: Context) {
        this._target = target;
        this._account = account;
        this._context = context;
        this._behaviours = new Array<Behaviour>();
    }
    
    /**
     * @returns Account
     */
    public get account() : Account {
        return this._account;
    }

    /**
     * Add a new behaviour to the bot
     * @param Behaviour behaviour to add
     */
    public addBehaviour(v: string) : void {
        let behaviour: Behaviour;
        switch (v) {
            case "overflow":
                behaviour = new OverflowBehaviour(this._target, this._account, this._context);
                break;
            case "random":
                behaviour = new RandomBehaviour(this._target, this._account, this._context);
                break;
            case "boundary":
                behaviour = new BoundaryBehaviour(this._target, this._account, this._context);
                break;
            default:
                behaviour = new RandomBehaviour(this._target, this._account, this._context);
                break;
        }
        this._behaviours.push(behaviour);
    }

    /**
     * Select a random behaviour between the list of behaviours
     * and calls performAction on it, then returns the result.
     */
    public async performAction() : Promise<TransactionResult> {
        let selectedBehaviour: Behaviour = RandomValueGenerator.getRandomElement(this._behaviours);
        return await selectedBehaviour.performAction();
    }
}