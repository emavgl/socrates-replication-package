import { Invariant } from "../Types/Invariant";
import { Contract } from "../Contract";

export class LegitOwnerChangeInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "CSI1";
    public description: string = "No one can change the owner except the owner itself";
    public hasBeenViolated: boolean;

    private _ownerAddr: string;
    private _target: Contract;

    public constructor(target: Contract, ownerAddr: string) {
        this._ownerAddr = ownerAddr;
        this._target = target;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkOwner;
    }

    protected async checkOwner(transactionResult: any | null) : Promise<boolean> {
        // it works because due to instrumentation all the variables are public
        let currentOwner = await this._target.sendTransactionByName('owner');

        if (transactionResult == null) {
            return currentOwner == this._ownerAddr;            
        }

        if (currentOwner != this._ownerAddr && transactionResult["successful"] && transactionResult['address'] != this._ownerAddr) {
            return false;
        }

        this._ownerAddr = currentOwner;
        return true;
    }
}