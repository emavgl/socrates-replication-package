import { Contract } from '../Contract';
import { Context } from '../Context';
import { Account } from '../Account';
import { RandomBehaviour } from './RandomBehaviour';
import { BoundaryValueGenerator } from '../Util/BoundaryValueGenerator';

export class BoundaryBehaviour extends RandomBehaviour {    
    constructor(target: Contract, account: Account, context: Context) {
        super(target, account, context);
        this._randomValueGenerator = new BoundaryValueGenerator(context);
        this._label = "BoundaryBehaviour";
    }
}