import { IBigNumber } from "./BigNumber";

export interface TransactionParams {
    sender?: string,
    value?: IBigNumber
}