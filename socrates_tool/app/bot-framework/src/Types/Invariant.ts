export interface Invariant {
    checkInvariant: (transactionResult: any | null) => Promise<boolean>;
    label: string,
    description?: string,
    hasBeenViolated: boolean
}