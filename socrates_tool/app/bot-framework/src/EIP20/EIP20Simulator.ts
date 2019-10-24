import { Simulator } from '../Simulator';
import { Contract } from '../Contract';
import { Invariant } from '../Types/Invariant';
import { Context } from '../Context';
import { TotalSupplyTotalBalanceInvariant } from '../Invariants/EIP20/TotalSupplyTotalBalanceInvariant';
import { TransferFromAllowanceInvariant } from '../Invariants/EIP20/TransferFromAllowanceInvariant';
import { ConsistentAllowanceAfterTransferFromInvariant } from '../Invariants/EIP20/ConsistentAllowanceAfterTransferFromInvariant';

import { TokenTransferMustThrowConsistentTransferEvent } from '../Invariants/EIP20/TokenTransferMustThrowConsistentTransferEvent';
import { ApproveMustThrowApprovalEvent } from '../Invariants/EIP20/ApproveMustThrowApprovalEvent';


// Invariants import

export class EIP20Simulator extends Simulator {  

    constructor(target: Contract, context: Context) {
        super(target, context); // includes invariant I1
        
        // Invariant declaration
        let I2Invariant: Invariant = new TotalSupplyTotalBalanceInvariant(target, context.accounts); 
        let I6Invariant: Invariant = new TransferFromAllowanceInvariant(target, context.accounts); 
        let I7Invariant: Invariant = new ConsistentAllowanceAfterTransferFromInvariant(target, context.accounts); 

        let I8Invariant: Invariant = new TokenTransferMustThrowConsistentTransferEvent(target, context.accounts); 
        let I9Invariant: Invariant = new ApproveMustThrowApprovalEvent(target, context.accounts); 

        // Adding invariants to the list of invariants
        this.invariants.push(I2Invariant);
        this.invariants.push(I6Invariant);
        this.invariants.push(I7Invariant);
        this.invariants.push(I8Invariant);
        this.invariants.push(I9Invariant);
    }
}
