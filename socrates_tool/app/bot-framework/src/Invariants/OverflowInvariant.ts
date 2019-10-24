import { Invariant } from "../Types/Invariant";
import { TransactionResult } from "../Types/TransactionResult";

export class OverflowInvariant implements Invariant {
    public checkInvariant: (transactionResult: any) => Promise<boolean>
    public label: string = "I1";
    public description: string = "Successful transaction with overflow";
    public hasBeenViolated: boolean;

    public constructor() {
        this.hasBeenViolated = false;
        this.checkInvariant = this.checkSuccessfulOverflow;
    }

    protected async checkSuccessfulOverflow(transactionResult: TransactionResult) : Promise<boolean> {
        return Promise.resolve(
                    !(
                        transactionResult != null &&
                        transactionResult['overflow'] != null &&
                        transactionResult['overflow'] == true
                    )
                );
    }
}