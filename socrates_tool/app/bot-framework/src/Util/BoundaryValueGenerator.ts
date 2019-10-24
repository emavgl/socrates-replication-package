import { RandomValueGenerator } from './RandomValueGenerator';
import { Account } from '../Account';
import { Context } from '../Context';
import { IBigNumber } from '../Types/BigNumber';
import * as ABI from '../ABI';
import BigNumber from 'bignumber.js';

export class BoundaryValueGenerator extends RandomValueGenerator {

    protected _delta: number;

    constructor(context: Context, delta?: number){
        super(context);
        if (delta == null) delta = 10000; // default value
        this._delta = delta;
    }

    /**
     * With prob 1/10 will return the min
     * With prob 1/10 will return the max
     * With prob 1/10 will return a number close to min
     * With prob 1/10 will return a number close to max
     * With prob 6/10 will return a random number [0, delta]
     * @returns {BigNumber} random BigNumber value
    */
   protected getBoundaryBigNumber(min: IBigNumber, max: IBigNumber) : any {
        let coinFlip = RandomValueGenerator.getRandomInt(0, 10); // min included, max not
        if (coinFlip == 0) return min;
        if (coinFlip == 1) return max;
        if (coinFlip == 2) return this.getRandomBigNumber(min, min.plus(this._delta));
        if (coinFlip == 3) return this.getRandomBigNumber(max.minus(this._delta), max);
        return new BigNumber(RandomValueGenerator.getRandomInt(0, this._delta));
    }

    /**
     * Generate a random value of a specific type using the either the passed or the default constraints
     * @param  {string} paramType
     * @param  {ABI.Types.Constraints} paramContraints
     * @returns {any} random value of the requested type or throw if the type is unhandled
     */
    protected newRandomValueFromType(paramType: string, paramContraints: ABI.Types.Constraints): any {
        let accounts: Account[] = this._context.bots.map(bot => bot.account);
        let minBigNumber, maxBigNumber;

        // Random type
        // If there is no constraint, use the range of the type
        // otherwise, use the constraint defined in paramConstraints
        if (paramType.includes("int")){
            let unsigned = paramType.startsWith('uint');
            let numbersInStringType = paramType.match(/\d+/g);
            let bytes = 256;
            if (numbersInStringType) bytes = parseInt(numbersInStringType[0]);
            let minForType: IBigNumber = unsigned ? new BigNumber(0) : new BigNumber(2).pow(bytes-1).times(-1).plus(1);
            let maxForType: IBigNumber = unsigned ? new BigNumber(2).pow(bytes).minus(1) : new BigNumber(2).pow(bytes-1).minus(2);
            minBigNumber = paramContraints.minValue ? new BigNumber(paramContraints.minValue) : minForType;
            maxBigNumber = paramContraints.maxValue ? new BigNumber(paramContraints.maxValue) : maxForType;
            return this.getBoundaryBigNumber(minBigNumber, maxBigNumber); // boundary here!
        }

        // Handle other parameters
        switch (paramType) {
            case 'address':
                let randomAccount = RandomValueGenerator.getRandomElement<Account>(accounts);
                return randomAccount.address;
            case 'bool':
                let defaultBoolean = paramContraints.defaultValue;
                return defaultBoolean ? defaultBoolean : Math.random() >= 0.5;
            case 'string':
                let minSize = paramContraints.minStringSize ? paramContraints.minStringSize : this._defaultConstraints['string'].minStringSize;
                let maxSize = paramContraints.maxStringSize ? paramContraints.maxStringSize : this._defaultConstraints['string'].maxStringSize;
                if ((minSize == null || maxSize == null) || (maxSize === 0)) return [];
                let randomSize = RandomValueGenerator.getRandomInt(minSize, maxSize);
                return this.getRandomString(randomSize);
            default:
                throw new Error("Unhandled Solidity Type");
        }
    }

}