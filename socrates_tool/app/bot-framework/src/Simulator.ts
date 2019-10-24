import { Contract } from './Contract';
import { Context } from './Context';
import { Logger } from './Logger';
import { Invariant } from './Types/Invariant';
import { OverflowInvariant } from './Invariants/OverflowInvariant';
import { TransactionResult } from './Types/TransactionResult';
import { IBigNumber } from './Types/BigNumber';

export class Simulator {
    protected _context: Context;
    protected _target: Contract;
    public invariants: Invariant[];

    /**
     * Create a new Simulator instance
     * @constructor
     * @param  {Contract} target - The contract to test
     * @param  {Context} context - The context on which the simulator has to run
     */
    constructor(target: Contract, context: Context) {
        this._context = context;
        this._target = target;
        
        // define invariants
        this.invariants = [
            new OverflowInvariant()
        ];

        this.logAddressesMap(context.addresses);
    }

    private async setCanary() : Promise<boolean> {
        try { 
            let fakeSpender: string = "0x0000000000000000000000000000000000000001";
            await this._target.sendTransactionByName('approve', [fakeSpender, 1, {from: this._context.addresses[0]}]);
            return true;
        } catch (error) {
            Logger.error(error.stack);
        }
        return false;
    }

    private async checkCanary() : Promise<boolean> {
        try { 
            let fakeSpender: string = "0x0000000000000000000000000000000000000001";
            let allowed: IBigNumber = await this._target.sendTransactionByName('allowance', [this._context.addresses[0], fakeSpender]);
            return allowed.equals(1);
        } catch (error) {
            Logger.error(error.stack);
        }
        return false;
    }
    
    /**
     * Start the simulation
     * @param  {number} duration - Number of steps to execute
     * @returns Promise
    */
   public async start(duration: number) : Promise<void> {

        // init
        await this.updateStatus();

        // set canary
        let canaryIsSet: boolean = await this.setCanary();
        if (!canaryIsSet) {
            console.log("Cannot call 'approve' to set the canary flag");
            console.log("Test will continue anyway without the canary value = cannot recognize contract selfdestruct");
        }

        // for each round, let bots perform actions
        let bots = this._context.bots;

        // starting check invariants
        await this.checkInvariants(null, -1);

        for (let currentStep = 0; currentStep < duration; currentStep++){
            
            Logger.info({"label": "step", "stepNumber": currentStep});
            console.log("Step: " + currentStep);

            for (const bot of bots) {

                let isStillAlive: boolean = await this.checkCanary();
                if (canaryIsSet == true && isStillAlive == false) {
                    console.log("The target contract is dead or cannot call 'approve'");
                    return; // exit
                }

                try {
                    // perform action
                    let transactionResult: TransactionResult = await bot.performAction();

                    // check invariants
                    await this.checkInvariants(transactionResult, currentStep);

                    // updates
                    if (transactionResult['successful'])
                        await this.updateStatus(transactionResult);
                } catch (error) {
                    let err = (error as Error);
                    if (err.message.includes("Unhandled Solidity Type") || err.message.includes("callable")){
                        Logger.debug(err.message + " during the execution of an action");
                    } else {
                        Logger.error(err.stack);
                        throw err;
                    }
                }                
            }
        }
    }

    /**
     * Check the assertions to be true
     * @returns Promise
    */
    protected async checkInvariants(transactionResult: TransactionResult | null, currentStep: number) : Promise<void> {
        // Run each invariant check
        for (const invariant of this.invariants) {
            try {
                if (invariant['hasBeenViolated']) continue;
                let isNotViolated = await invariant.checkInvariant.call(invariant, transactionResult);
                if (!isNotViolated) {
                    invariant.hasBeenViolated = true;
                    console.log("==== ", "Invariant" , invariant['label'], "has been violated at step" , currentStep, "====");
                    Logger.warn({"label": "invariant_violation", "invariant": invariant['label'], "violation_step": currentStep});
                    this.printStatus();
                }
            } catch (error) {
                Logger.error(error.stack);
                console.log("Cannot run the invariant " + invariant['label']);
            }
        }

        // Check if all the invariants have been violated
        // If so, abort the program
        let numberOfViolated = this.invariants.filter(x => x.hasBeenViolated).length;
        if (numberOfViolated == this.invariants.length){
            await this.updateStatus(transactionResult);
            throw new Error("All the invariants have been violated");
        }
    }

    /**
     * Update the status of the blockchain of each of the account
     */
    public async updateStatus(transactionResult?: any) {
        let accounts = this._context.accounts;
        for (const account of accounts) {
            // TODO: add second parameter, web3js instance
            await account.updateStatus(this._target, transactionResult);
        }        
    }

    private logAddressesMap(accounts: string[]){
        for (const account of accounts) {
            Logger.info({"label": "init", "type": "account", "address": account});
        }
        Logger.info({"label": "init", "type": "contract", "address": this._target.address});
        Logger.info({"label": "init", "type": "account", "address": "0x0000000000000000000000000000000000000000"});
    }

    /**
     * Print the status of the simulator
     * Status of the simulator is the status of all the accounts
     */
    public printStatus() : void {
        let accounts = this._context.accounts;
        for (const account of accounts) {
            account.printStatus();
        }
    }

}