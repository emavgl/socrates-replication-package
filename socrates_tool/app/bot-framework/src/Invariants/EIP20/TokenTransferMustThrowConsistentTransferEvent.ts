import { Invariant } from '../../Types/Invariant';
import { Contract } from '../../Contract';
import { Account } from '../../Account';
import { IBigNumber } from '../../Types/BigNumber';
import { TransactionResult } from '../../Types/TransactionResult';
import { EIP20Account } from '../../EIP20/EIP20Account';
import BigNumber from 'bignumber.js';

export class TokenTransferMustThrowConsistentTransferEvent implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>

    public label: string = "I8";
    public description: string = "Every token transfer must trigger a consistent Transfer event";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    private _currentTokenBalanceMap: {[addr: string]: IBigNumber};
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this._accounts = accounts;
        this.hasBeenViolated = false;
        this._currentTokenBalanceMap = {};
        this.checkInvariant = this.checkTransferMustThrowConsistentTransferEvent;
    }

    private async getSubsetBalancesMap(accounts: string[]) : Promise<{[addr2:string]: IBigNumber}> {
        let balances: {[addr2:string]: IBigNumber} = {};
        for (const account of accounts) {
            balances[account] = await this._target.sendTransactionByName('balanceOf', [account]);
        }
        return balances;
    }

    /*
        Check if Transfer is successful
        => some tokens have been transferred
    */
    protected async isTransferSuccessful(transactionResult) : Promise<boolean> {
        if (transactionResult['successful'] == false) return false;
        let params: any = transactionResult["params"];

        let sender: string = transactionResult['address'];
        let from: string;
        let to: string;

        if (transactionResult["action"] == "transferFrom") {
            from = params[0];
            to = params[1];
        } else {
            // transfer
            from = sender;
            to = params[0];
        }

        let targets: any = [sender, from, to];

        let previousBalances = this.getPreviousBalancesMap(); // get previous map
        this._currentTokenBalanceMap = await this.getSubsetBalancesMap(targets); // get current map

        // something changed in balance of contract involved = successful transfer
        for (let i = 0; i < targets.length; i++) {
            const addr1 = targets[i];
            let b1: IBigNumber = this._currentTokenBalanceMap[addr1];
            let b2: IBigNumber = previousBalances[addr1];
            if (!b1.equals(b2)){
                return true; 
            }
        }
        return false;
    }


    /*
        Get a map: addr => tokenBalance before the transaction
    */
    private getPreviousBalancesMap() :  {[addr: string]: IBigNumber} {       
        let previousBalancesMap: {[addr: string]: IBigNumber} = {};
        for (let i = 0; i < this._accounts.length; i++) {
            const addr1 = this._accounts[i].address;
            previousBalancesMap[addr1] = (this._accounts[i] as EIP20Account).tokenBalance;
        }
        return previousBalancesMap;
    }

    /**
     * Check that the amount of money transferred is consistent
     * 
     * @param from: who pay
     * @param to: address receiver
     * @param amount: token transferred
     */
    private checkConsistentTransfer(from: string, to: string, amount: IBigNumber) : boolean {
        let previousBalances = this.getPreviousBalancesMap(); // get previous map
        let currentBalances =  this._currentTokenBalanceMap;

        let consistentFromBalance = currentBalances[from].equals(previousBalances[from].minus(amount));
        let consistentToBalance = currentBalances[to].equals(previousBalances[to].plus(amount));
        
        return consistentFromBalance && consistentToBalance;
    }

    /**
     * If the action is a "transfer" or a "transferFrom"
     * It checks that there is an associated Transfer event and
     * that that Transfer event is consistent.
     * 
     * Consistent means that:
     * - The event has the same values of the function parameters
     * - The event logs the exact amount of token transferred
     * 
     * @param transactionResult TransactionResult
     */
    protected async checkTransferMustThrowConsistentTransferEvent(transactionResult: TransactionResult) : Promise<boolean> {
        if (transactionResult == null){
            return true;
        }

        // Get action name
        let actionName: string = transactionResult["action"];

        // If successfulTransfer From (some tokens have been transferred)
        // Assert that there is a Transfer log event with consistent values
        if ((actionName == "transfer" || actionName == "transferFrom") && await this.isTransferSuccessful(transactionResult)){
            let params: any = transactionResult["params"];
            
            let from: string;
            let to: string;
            let amount: IBigNumber;

            if (actionName == "transferFrom") {
                from = params[0];
                to = params[1];
                amount = new BigNumber(params[2]);
            } else {
                // transfer
                from = transactionResult['address'];
                to = params[0];
                amount =  new BigNumber(params[1]);
            }

            let events = transactionResult['result']['logs'];        
        
            for (const event of events) {
                let name = event['event'];
                let args = event['args'] as Object;
                let argsArray = Object.keys(args).map((key) => args[key]);

                // Check consistent Transfer event
                if (name == "Transfer") {
                    let eventFrom = argsArray[0];
                    let eventTo = argsArray[1];
                    let eventAmount: IBigNumber = new BigNumber(argsArray[2]);
                    
                    // Check Transfer event is consistent with "transfer" parameters
                    let logConsistentWithTransferParams = eventFrom == from && eventTo == to && eventAmount.equals(amount);

                    // Check Transfer event is consistent with real amount of token trasferred
                    let logConsistentWithRealTokenTransferred = this.checkConsistentTransfer(eventFrom, eventTo, eventAmount);

                    return logConsistentWithTransferParams && logConsistentWithRealTokenTransferred;
                }
            }
            return false; // no event has been found
        }
        return true; // it is not a valid transfer
    }
}