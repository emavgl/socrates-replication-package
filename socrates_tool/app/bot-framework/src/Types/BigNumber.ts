export interface IBigNumber {
    equals(n: number|string|IBigNumber, base?: number): boolean;
    greaterThan(n: number|string|IBigNumber, base?: number): boolean;
    greaterThanOrEqualTo(n: number|string|IBigNumber, base?: number): boolean;
    lessThan(n: number|string|IBigNumber, base?: number): boolean;
    lessThanOrEqualTo(n: number|string|IBigNumber, base?: number): boolean;
    plus(n: number|string|IBigNumber, base?: number): IBigNumber;
    times(n: number|string|IBigNumber, base?: number): IBigNumber;
    minus(n: number|string|IBigNumber, base?: number): IBigNumber;
    modulo(n: number|string|IBigNumber, base?: number): IBigNumber;
    pow(n: number): IBigNumber;
    comparedTo(n: number|string|IBigNumber, base?: number): number;
    floor() : IBigNumber;
    toNumber(): number;
}