import { Account } from './Account';
import { Bot } from './Bots/Bot';

/**
 * A context class contains a list of accounts[]
 * Moreover, contains a list of getter methods to easily get the bots[] and the contracts[]
 */
export class Context {
    protected _accounts: Account[] = [];
    protected _bots: Bot[] = [];
    protected _addresses: string[] = [];

    // Getter and setter for accounts list
    public get accounts() : Account[] {
        return this._accounts;
    }
    
    public set accounts(v : Account[]) {
        this._accounts = v;
    }

    public get bots() : Bot[] {
        return this._bots;
    }
    
    public set bots(v : Bot[]) {
        this._bots = v;
    }

    public get addresses() : string[] {
        return this._addresses;
    }
    
    public set addresses(v : string[]) {
        this._addresses = v;
    }

}