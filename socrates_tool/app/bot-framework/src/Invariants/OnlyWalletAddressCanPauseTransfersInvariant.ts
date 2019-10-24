import { Invariant } from "../Types/Invariant";
import { Contract } from "../Contract";

export class OnlyWalletAddressCanPauseTransfersInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "CSI4";
    public description: string = "Only walletAddress can successfully pause/restart token transfer";
    public hasBeenViolated: boolean;

    private _target: Contract;
    private _walletAddress: string | null;
    public constructor(target: Contract) {
        this._target = target;
        this._walletAddress = null;
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkOwner;
    }

    protected async checkOwner(transactionResult: any | null) : Promise<boolean> {
        let walletAddress = await this._target.sendTransactionByName('walletAddress');

        if (transactionResult == null) {
            // init transaction, initialization
            this._walletAddress = walletAddress;
            return true;          
        }

        if (transactionResult["successful"] && 
            (transactionResult["action"] == "enableTokenTransfer" || transactionResult["action"] == "disableTokenTransfer") && 
            transactionResult['address'] != this._walletAddress) {
            return false;
        }

        return true;
    }
}