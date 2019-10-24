import { Account } from "./Account";
import * as ABI from "./ABI";

export class Contract extends Account {
    protected _web3Instance: any;
    protected _abi: ABI.Types.NameToFunctionMap;
    protected _artifactsPath: string;

    /**
     * @param  {any} web3Instance - Web3JS instance of the contract
     * @param  {Function[]} abi - List of ABI.Function imported using importABIFromFile
     * @param  {any} artifactsPath - Path to Truffle artifacts
     */
    constructor(web3Instance: any, abi: ABI.Types.NameToFunctionMap, artifactsPath: string) {
        super(web3Instance.address);
        this._web3Instance = web3Instance;
        this._abi = abi;
        this._artifactsPath = artifactsPath;
    }

    /**
     * Returns the list of actions that can be invoked 
     * @returns Action[]
     */
    public get artifactsPath() : string {
        return this._artifactsPath;
    }
    
    /**
     * Returns the list of actions that can be invoked 
     * @returns Action[]
     */
    public get abi() : ABI.Types.NameToFunctionMap {
        return this._abi;
    }

    /**
     * @param  {ABI.Types.Function} contractFunction
     * @param  {any} functionParams (optional)
     * @returns {Promise<any>} Promise with result of the function execution
     */
    public sendTransaction(contractFunction: ABI.Types.Function, params?: any) : Promise<any> {
        let functionName: string = contractFunction.name;
        let functionParams = params ? params: [];
        return this._web3Instance[functionName](...functionParams);
    }

        /**
     * @param  {string} functionName
     * @param  {any} functionParams (optional)
     * @returns {Promise<any>} Promise with result of the function execution
     */
    public sendTransactionByName(functionName: string, params?: any) : Promise<any> {
        let functionParams = params ? params: [];
        return this._web3Instance[functionName](...functionParams);
    }
    
}
