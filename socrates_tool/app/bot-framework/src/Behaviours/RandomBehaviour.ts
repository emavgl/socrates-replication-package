import { Contract } from '../Contract';
import { Context } from '../Context';
import { Account } from '../Account';
import { RandomValueGenerator } from '../Util/RandomValueGenerator';
import { Logger } from "../Logger";
import { Behaviour } from './Behaviour';
import * as ABI from '../ABI';
import { TransactionResult } from '../Types/TransactionResult';

export class RandomBehaviour extends Behaviour {

    protected _randomValueGenerator: RandomValueGenerator;
    
    constructor(target: Contract, account: Account, context: Context) {
        super(target, account, context);
        this._randomValueGenerator = new RandomValueGenerator(context);
        this._label = "RandomBehaviour";
    }

    public get randomValueGenerator() : RandomValueGenerator {
        return this._randomValueGenerator;
    }

    private getFunctionParams(targetFunction: ABI.Types.Function) : any[] {
        let chosenParameters = this._randomValueGenerator.getRandomParameters(targetFunction);

        // Insert the bot address (sender of the message) as last parameter
        let valueConstraints: ABI.Types.Constraints = { defaultValue: '0' }
        if (targetFunction.payable) {
            // Set 1 ETH
            valueConstraints = { defaultValue: '1000000000000000000' }
        }
        let valueParam: ABI.Types.Parameter = { name: 'value', type: 'uint256', constraints: valueConstraints}
        let transactionParameters = {from: this._account.address,
                                    value: this._randomValueGenerator.getRandomValue(valueParam)}

        let functionParams = new Array<any>();
        functionParams = functionParams.concat(chosenParameters);
        functionParams.push(transactionParameters);
        return functionParams;
    }

    private async execTransaction(contract: Contract, targetFunction: ABI.Types.Function, params: any[]) : Promise<TransactionResult> {
        // Apply function and save the result
        let successful: boolean = false;
        let actionResult: any = null;
        let result: any;
        
        try {
            result = await contract.sendTransaction(targetFunction, params);
            successful = true;
        } catch (error) {
            // Catch if the action has thrown a Revert Exception
            let err = error as Error;
            if (err.name === "StatusError"){
                result = "revert";
            }
        }

        // Log the action and the results
        actionResult = {
                        "label": "action",
                        "successful": successful,
                        "overflow": false,
                        "address": this._account.address,
                        "action": targetFunction.name,
                        "behaviour": this._label,
                        "behaviourCounter": this._counter,
                        "params": params,
                        "result": result
                    };

        return actionResult;
    }

    /**
     * Perform a random action
     * @returns Promise
     * @override
     */
    public async performAction(): Promise<TransactionResult> {
        super.performAction();
        let contract: Contract = this._target as Contract;
        let abi: ABI.Types.NameToFunctionMap = this._target.abi;

        // Get all the callable actions
        let callableFunctions: ABI.Types.Function[] = new Array<ABI.Types.Function>();
        for (const [ key, value ] of Object.entries(abi)) {
            if (['view', 'pure'].includes(value['stateMutability']) == false && value["type"] == "function" && !value.name.includes("freeze")) {
                callableFunctions.push(value);
            }
        }

        if (callableFunctions.length == 0) {
            throw new Error("No callable function");
        }

        // Choose a random action with random parameters
        let chosenAction = RandomValueGenerator.getRandomElement<ABI.Types.Function>(callableFunctions);

        let functionParams: any[] = [];
        let actionResult: any;

        for (let attempt = 0; attempt < 5; attempt++) {
            functionParams = this.getFunctionParams(chosenAction);
            actionResult = await this.execTransaction(contract, chosenAction, functionParams);
            if (actionResult.successful) {
                Logger.info(actionResult);
                return actionResult;
            }
        }

        return actionResult;
    }
}