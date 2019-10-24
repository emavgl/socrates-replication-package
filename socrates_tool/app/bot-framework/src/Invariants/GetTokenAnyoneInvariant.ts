import { Invariant } from "../Types/Invariant";
import { Contract } from "../Contract";

export class GetTokenAnyoneInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "CSI6";
    public description: string = "Only the owner should be able to mint new tokens";
    public hasBeenViolated: boolean;

    private _target: Contract;
    public constructor(target: Contract) {
        this._target = target;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkOwner;
    }

    protected async checkOwner(transactionResult: any | null) : Promise<boolean> {
        let owner = await this._target.sendTransactionByName('owner');

        if (transactionResult == null) {
            // init transaction, initialization
            return true;          
        }

        if (transactionResult["successful"] && 
            transactionResult["action"] == "getToken" && 
            transactionResult['address'] != owner) {
            return false;
        }

        return true;
    }
}