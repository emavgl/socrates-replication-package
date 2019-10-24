import { Contract } from '../Contract';
import { Context } from '../Context';
import { Account } from '../Account';
import * as ABI from '../ABI';
import { IBigNumber } from '../Types/BigNumber';

const util = require('util');
const glob = util.promisify(require('glob'));
const exec = util.promisify(require('child_process').exec);
const stat = util.promisify(require('fs').stat);

import { RandomValueGenerator } from '../Util/RandomValueGenerator';
import { Logger } from "../Logger";
import { TransactionParams } from '../Types/TransactionParams';
import { Behaviour } from './Behaviour';

import BigNumber from 'bignumber.js';
import { TransactionResult } from '../Types/TransactionResult';

export class OverflowBehaviour extends Behaviour {

    protected _randomValueGenerator: RandomValueGenerator;
    constructor(target: Contract, account: Account, context: Context) {
        super(target, account, context);
        this._randomValueGenerator = new RandomValueGenerator(context);
        this._label = "OverflowBehaviour";
    }

    private getFunctionParams(targetFunction: ABI.Types.Function, resultsZ3: any) : any[] {
        let chosenParameters = this.getConcreteValues(resultsZ3, targetFunction);
        let msg_value = this.getConcreteValue(resultsZ3['msg_value'], 'uint256');

        let transactionParameters = {
                                    from: this._account.address,
                                    value: msg_value
                                }

        let functionParams = new Array<any>();
        functionParams = functionParams.concat(chosenParameters);
        functionParams.push(transactionParameters as TransactionParams);
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
        return {
            "label": "action",
            "successful": successful,
            "overflow": successful,
            "address": this._account.address,
            "action": targetFunction.name,
            "behaviour": this._label,
            "behaviourCounter": this._counter,
            "params": params,
            "result": result
        };
    }

    /**
     * Find the value which make the fitness equal to 0 and apply it
     * @returns Promise: result
     * @override
     */
    public async performAction(): Promise<TransactionResult> {
        super.performAction();
        let contract: Contract = this._target as Contract;
        let abi: ABI.Types.NameToFunctionMap = this._target.abi;

        // Get all the callable actions
        let listOfFiles: [string] = await glob('./generated/*_z3.py');
        let callableFunctions: ABI.Types.Function[] = new Array<ABI.Types.Function>();
        for (const [ key, value ] of Object.entries(abi)) {
            let expectedPath = "./generated/" + key + "_z3.py";
            if (['view', 'pure'].includes(value['stateMutability']) == false && listOfFiles.includes(expectedPath)) {
                callableFunctions.push(value);
            }
        }

        if (callableFunctions.length == 0) {
            throw new Error("No callable function");
        }

        // Choose a random action with random parameters
        let chosenAction = RandomValueGenerator.getRandomElement<ABI.Types.Function>(callableFunctions);

        let distinctOption: number = RandomValueGenerator.getRandomElement([0, 1]);
        let results = await this.callZ3Solver(chosenAction.name, this._target, this._target.artifactsPath, distinctOption);

        let functionParams: any = [];
        let actionResult: any;

        if (results && results.sat){
            functionParams = this.getFunctionParams(chosenAction, results);
            actionResult = await this.execTransaction(contract, chosenAction, functionParams);
            if (actionResult.successful) {
                Logger.info(actionResult);
                return actionResult;
            }
        } else if (results.sat == false) {
            // console.log("not sat");
            Logger.debug(chosenAction.name + ": not sat");
        }

        return {
            "label": "action",
            "successful": false,
            "overflow": false,
            "address": this._account.address,
            "action": chosenAction.name,
            "behaviour": this._label,
            "behaviourCounter": this._counter,
            "params": [],
            "result": "unsat"
        };
    }


    private async callZ3Solver(functionName: String, target: Contract, artifacts: string, distinctOption: number) {

        let scriptPath = "./generated/" + functionName + "_z3.py";

        // null if exist
        try {
            await stat(scriptPath);
        } catch (error) {
            return [];
        }

        let command = `timeout 10 python3 ${scriptPath} -ta ${artifacts}`
        command += ` -c ${target.address} -a ${this._account.address} -d ${distinctOption} -bn ${this._context.bots.length}`;

        Logger.debug(command);
        //console.log(command);

        try {
            const { stdout, stderr } = await exec(command);
            if (stderr) {
                console.error(`error: ${stderr}`);
                return {'sat': false};
            }
            let data = stdout.toString('utf8');
            Logger.debug(command);
            return JSON.parse(data);
        } catch (error) {
            return {'sat': false};
        }
    }

    private checkTypeConsistency(value: string, type: string) : boolean {
        if ((type.includes('address') || type.includes('uint')) && value.includes('-')) return false;
        if (type.startsWith('int')){
            let bigInt: IBigNumber = new BigNumber(value);
            
            let bits: number = 256;
            let numbersInType = type.match(/\d+/);
            if (numbersInType) bits = parseInt(numbersInType[0]);
            
            let minInt: IBigNumber = (new BigNumber(2) as IBigNumber).pow(bits-1).times(-1);
            if (bigInt.lessThan(minInt)) return false;
        }

        return true;
    }

    /**
     * Check type validity
     * Z3 output will consider values outside the typerange
     * as not valid values, which will not be part of the final
     * arrays.
     * @param  {} z3value
     * @param  {} type
     */
    private getConcreteValue(z3value: string, type: string) : any | null {

        let isConsistent: boolean =  this.checkTypeConsistency(z3value, type);
        if (!isConsistent) return null;

        // value is consistent
        if (type.includes('address')){
            // Array of index of address accounts
            const addressId = parseInt(z3value);
            return this._context.accounts[addressId].address;
        } else {
            return new BigNumber(z3value);
        }
    }

    /**
     * Given the output of the solver, get the corresponding parameters
     * for the function call.
     * @param  {any} z3variables
     * @param  {ABI.Types.Function} action
     */
    private getConcreteValues(z3variables: any, action: ABI.Types.Function) : any {
        const functionInputs = action.inputs;
        let parameters = new Array<any>();
        let randomValues = this._randomValueGenerator.getRandomParameters(action);
        for (let i = 0; i < functionInputs.length; i++) {
            const input = functionInputs[i];
            const inputName = input.name;
            const inputType = input.type;
            const z3Value = z3variables[inputName];
            if (z3Value) {
                // There is matching with a z3 variables
                if (Array.isArray(z3Value)){
                    // is an array
                    let concreteValues = new Array<any>();
                    for (const value of z3Value) {
                        let concreteValue = this.getConcreteValue(value, inputType)
                        if (concreteValue != null) concreteValues.push(concreteValue);
                    }
                    parameters.push(concreteValues);
                } else {
                    // z3Value is a single value
                    let concreteValue = this.getConcreteValue(z3Value, inputType)
                    if (concreteValue != null) parameters.push(concreteValue);
                }
            } else {
                // I don't have a z3 value for this input
                // Get the random generated for this position
                parameters.push(randomValues[i]);
            }     
        }
        return parameters;
    }
}
