export interface TransactionResult {
    label: string,
    successful: boolean,
    overflow: boolean,
    address: string,
    action: string,
    behaviour: string,
    behaviourCounter: number,
    params: Array<any>,
    result: any
}