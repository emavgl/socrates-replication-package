import { Account } from '../Account';
import { Context } from '../Context';
import { IBigNumber } from '../Types/BigNumber';
import * as ABI from '../ABI';
import BigNumber from 'bignumber.js';

export class RandomValueGenerator {

    protected _context: Context;
    protected _maxNumberOfDigits: number;
    protected _defaultConstraints: { [id: string] : ABI.Types.Constraints; }

    constructor(context: Context){
        this._context = context;
        this._maxNumberOfDigits = 77;
     
        // Set default contraints
        this._defaultConstraints = {};
        this._defaultConstraints['string'] = { minStringSize: 0, maxStringSize: 10 };
        this._defaultConstraints['[]'] = { minArraySize: 0, maxArraySize: 5 };
    }

    /**
     * Getters and Setters
     */
    public get defaultConstraints() : { [id: string] : ABI.Types.Constraints; } {
        return this._defaultConstraints;
    }

    public set defaultConstraints(v : { [id: string] : ABI.Types.Constraints; }) {
        this._defaultConstraints = v;
    }

    public get maxNumberOfDigits() : number {
        return this._maxNumberOfDigits;
    }

    public set maxNumberOfDigits(v : number) {
        this._maxNumberOfDigits = v;
    }

    /**
     * Returns a random BigNumber between 0 and maxBigNumber
     * @returns {BigNumber} random BigNumber value
     */
    protected getRandomBigNumber(min: IBigNumber, max: IBigNumber) : any {
        // Based on https://stackoverflow.com/questions/4959975/generate-random-number-between-two-numbers-in-javascript
        let randomNumber = BigNumber.random(this._maxNumberOfDigits) as IBigNumber;
        let randomNumberInInterval = randomNumber.times((max.minus(min).plus(1))); 
        return randomNumberInInterval.floor().plus(min);
    }

    /**
     * Returns a random int between min (included) and max (excluded)
     * @param  {number} min
     * @param  {number} max
     * @returns {number}
     */
    public static getRandomInt(min: number, max: number): number {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min)) + min; // min is included, max not
    }

    /**
     * Get a random element of an array
     * @param  {T[]} array
     * @returns {T}
     */
    public static getRandomElement<T>(array: T[]) : T {
        return array[this.getRandomInt(0, array.length)];
    }

    /**
     * Returns a random string of the specified size
     * @param  {number} size
     * @returns {string}
     */
    protected getRandomString(size: number) : string {
        let m = size; 
        let s = '';
        let r = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (var i=0; i < m; i++) { s += r.charAt(Math.floor(Math.random()*r.length)); }
        return s;
    };

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
            return this.getRandomBigNumber(minBigNumber, maxBigNumber);
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

    /**
     * Generate random value for the input paramater
     * @param  {ABI.Types.Parameter} param
     */
    public getRandomValue(param: ABI.Types.Parameter): any {
        let paramType = param.type;
        let paramContraints = param.constraints;

        // If no contraints are specified, paramContrains is equal to default
        if (!paramContraints) paramContraints = {};

        // Check if a default value is specified
        if (paramContraints.defaultValue){
            return paramContraints.defaultValue;
        } else if (this.defaultConstraints[paramType] && this.defaultConstraints[paramType].defaultValue) {
            return this.defaultConstraints[paramType].defaultValue;
        }

        if (paramType.includes("[]")){
            // is an array
            let elementType = paramType.replace("[]", "");
            let minSize = paramContraints.minArraySize ? paramContraints.minArraySize : this._defaultConstraints['[]'].minArraySize;
            let maxSize = paramContraints.maxArraySize ? paramContraints.maxArraySize : this._defaultConstraints['[]'].maxArraySize;
            if ((minSize == null || maxSize == null) || (maxSize === 0)) return [];
            let randomSize = RandomValueGenerator.getRandomInt(minSize, maxSize);
            let paramsArray = new Array<any>();
            for (let i = 0; i < randomSize; i++) {
                let rValue = this.newRandomValueFromType(elementType, paramContraints);
                paramsArray.push(rValue);
            }
            return paramsArray;
        } else {
            return this.newRandomValueFromType(paramType, paramContraints);
        }
    }

    /**
     * Generate a list of (constrained-)random parameters for calling the action
     * @param  {ABI.Types.Function} action
     */
    public getRandomParameters(action: ABI.Types.Function) : any[] {
        let chosenParameters: any[] = [];

        // No input parameters are required
        if (action.inputs == null){
            return chosenParameters;
        }

        // Get a random value for each of the parameter
        action.inputs.forEach((param) => {
            let assignedValue = this.getRandomValue(param);
            chosenParameters.push(assignedValue);
        });
        
        return chosenParameters;
    }
}