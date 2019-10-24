import { Invariant } from "../Types/Invariant";
import { Contract } from "../Contract";
import { IBigNumber } from "../Types/BigNumber";

export class TotalSupplyMustNeverDecreaseInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "CSI2";
    public description: string = "TotalSupply amount must never decrease change";
    public hasBeenViolated: boolean;

    private _totalSupply: IBigNumber | null;
    private _target: Contract;
    public constructor(target: Contract) {
        this._totalSupply = null;
        this._target = target;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkTotalSupply;
    }

    protected async checkTotalSupply(transactionResult: any) : Promise<boolean> {
        let currentTotalSupply: IBigNumber = await this._target.sendTransactionByName('totalSupply') as IBigNumber;
        if (this._totalSupply == null) {
            // first call, set initial totalSupply
            this._totalSupply = currentTotalSupply;
        }
        if (currentTotalSupply.lessThan(this._totalSupply)){
            return false;
        }
        this._totalSupply = currentTotalSupply;
        return true;
    }
}