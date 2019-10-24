import { Invariant } from "../Types/Invariant";
import { Contract } from "../Contract";

export class SuccessfullBuyInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "CSI7";
    public description: string = "Sell operation must increase my ethereum balance";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _accounts: Account[];
    private _allowance: any;
    public constructor(target: Contract, accounts: Account[]) {
        this._target = target;
        this._accounts = accounts;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkBuyWorks;
        this._allowance = null;
    }

    protected async checkBuyWorks(transactionResult: any | null) : Promise<boolean> {
        if (transactionResult == null) return true;

        if (transactionResult["action"] == "setPrices" && transactionResult['successful'] == true){// && transactionResult['successfull']) {
            let a = 4;
        }

        if (transactionResult["action"] == "buy") {
            let b = 4;
            if (transactionResult['successful']) {
                let c = 5;
            }
        }

        return true;
    }
}