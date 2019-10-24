import { Invariant } from '../../Types/Invariant';
import { Contract } from '../../Contract';
import { Account } from '../../Account';
import { IBigNumber } from '../../Types/BigNumber';
import { TransactionResult } from '../../Types/TransactionResult';
import BigNumber from 'bignumber.js';
import { EIP20Account } from '../../EIP20/EIP20Account';

export class ApproveMustThrowApprovalEvent implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "I9";
    public description: string = "Every 'approve' must trigger a consistent Approval event";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    private _accountsAddr: string[];
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkConsistentApprovalLog;
        this._accounts = accounts;
        this._accountsAddr = this._accounts.map(acc => acc.address);
    }

    protected async approvalHasChanged(transactionResult) : Promise<boolean> {
        if (transactionResult['successful'] == false) return false;
        let params: any = transactionResult["params"];
        let owner: string = transactionResult['address'];
        let spender: any = params[0];

        let ownerIndex = this._accountsAddr.indexOf(owner);
        let oldApprovalAmount: IBigNumber = (this._accounts[ownerIndex] as EIP20Account).allowance[spender];
        if (!oldApprovalAmount) oldApprovalAmount = new BigNumber(0);
        
        let currentAmount: IBigNumber = await this._target.sendTransactionByName('allowance', [owner, spender]) as IBigNumber;

        return !currentAmount.equals(oldApprovalAmount);
    }

    protected async isCurrentApprovalConsistent(transactionResult) : Promise<boolean> {
        let params: any = transactionResult["params"];
        let owner: string = transactionResult['address'];

        let spender: any = params[0];

        let typeMax = new BigNumber(2).pow(256); // unit256
        let expectedAmount: IBigNumber = new BigNumber(params[1]).modulo(typeMax); // prevent error from overflow-boundary-behaviour
        let currentAmount: IBigNumber = await this._target.sendTransactionByName('allowance', [owner, spender]) as IBigNumber;

        return expectedAmount.equals(currentAmount);
    }

    protected async checkConsistentApprovalLog(transactionResult: TransactionResult) : Promise<boolean> {
        if (transactionResult == null){
            return true;
        }

        // Get action name
        let actionName: string = transactionResult["action"];

        if (actionName == "approve" && await this.approvalHasChanged(transactionResult)){
            let owner: string = transactionResult['address'];
            let params: any = transactionResult["params"];
            let spender: string = params[0];
            let amount: IBigNumber =  new BigNumber(params[1]);

            let events = transactionResult['result']['logs'];        
        
            for (const event of events) {
                let name = event['event'];
                let args = event['args'] as Object;
                let argsArray = Object.keys(args).map((key) => args[key]);

                // Check consistent Approval event
                if (name == "Approval") {
                    let eventOwner = argsArray[0];
                    let eventSpender = argsArray[1];
                    let eventAmount: IBigNumber = new BigNumber(argsArray[2]);
                    let logConsistent = eventOwner == owner && eventSpender == spender && eventAmount.equals(amount);
                    let approvalConsistent = await this.isCurrentApprovalConsistent(transactionResult);
                    return logConsistent && approvalConsistent;
                }
            }
            return false; // no event has been found
        }
        return true;
    }
}