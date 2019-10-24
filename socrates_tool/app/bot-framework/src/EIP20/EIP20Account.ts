import { Logger } from "../Logger";
import { Account } from '../Account';
import { Contract } from "../Contract";
import { IBigNumber } from "../Types/BigNumber";
import BigNumber from 'bignumber.js';

export class EIP20Account extends Account {
    /**
     * Status of the Bot = What the Bot knows
     * State is initialized by the bot through the method `initialize`
     * State of the account can be useful for the Bot to choose the action to perform and its parameters
     */
    protected _tokenBalance: any = new BigNumber(0);
    protected _allowance: {[addr: string]: IBigNumber} = {};

    
    public get tokenBalance() : IBigNumber {
        return this._tokenBalance;
    }
    
    public set tokenBalance(v : IBigNumber) {
        this._tokenBalance = v;
    }

    public get allowance() : {[addr: string]: IBigNumber} {
        return this._allowance;
    }

    
    public set allowance(v : {[addr: string]: IBigNumber}) {
        this._allowance = v;
    }

    private async updateAllowance(eip20Contract: Contract, transactionResult: any) {

        // If there is an event Approval
        // We use that one
        let actionName: string = transactionResult["action"];
        let events = transactionResult['result']['logs'];        
        
        for (const event of events) {
            let name = event['event'];
            let args = event['args'] as Object;
            let argsArray = Object.keys(args).map((key) => args[key]);
            if (name == "Approval") {
                let sender = argsArray[0];
                let spender = argsArray[1];
                let amount = new BigNumber(argsArray[2]);
                if (sender == this._address)
                    this._allowance[spender] = amount;
                return;
            }
        }

        // What if there is no an Approval event?
        // It is not safe to use the value directly from "approve" or "transferFrom"
        // Includes the methods es. increaseApproval, increaseAllowance etc.
        if (
            (actionName == "approve" || actionName.toLowerCase().includes("allowance") || actionName.toLowerCase().includes("approv"))
            && transactionResult['address'] == this._address){
            let params: any = transactionResult["params"];
            let spender: string = params[0]; // or "spender" or "from"
            this._allowance[spender] = await eip20Contract.sendTransactionByName('allowance', [this._address, spender]) as IBigNumber;
            return;
        }

        // TrasferFrom decrease the allowance but the implementation could have some bug
        // es. https://github.com/sec-bit/awesome-buggy-erc20-tokens/blob/master/ERC20_token_issue_list.md#a21-check-effect-inconsistency
        // => Get from the blockchain
        if (actionName == "transferFrom" )
        {
            let params: any = transactionResult["params"];
            let from: string = params[0]; // or "spender" or "from"
            let sender: string = transactionResult["address"];
            if (from == this._address) {
                this._allowance[sender] = await eip20Contract.sendTransactionByName('allowance', [this._address, sender]) as IBigNumber;
                return;
            }
        }
    }
    
    /**
     * Update the status of the account
     * @returns Promise
     */
    public async updateStatus(eip20Contract: Contract, transactionResult: any): Promise<void> {
        this.tokenBalance = await eip20Contract.sendTransactionByName('balanceOf', [this._address]);

        // can't do anything else
        if (transactionResult) {
            try {
                await this.updateAllowance(eip20Contract, transactionResult);                
            } catch (error) {
                console.error("Cannot set the allowance", error);
            }
        }
    }
    
    /**
     * Print the status of the bot
     * @override
     */
    public printStatus(): void {
        Logger.info({'label': 'status', 'address': this.address, 'tokenBalance': this._tokenBalance})
    }
}