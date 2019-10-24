var fs = require('fs');

export module Types {

    export interface Constraints {
        minValue?: string;
        maxValue?: string;
        defaultValue?: any;
        minArraySize?: number;
        maxArraySize?: number;
        minStringSize?: number;
        maxStringSize?: number;
    }

    export interface Parameter {
        name: string;
        type: string;
        constraints?: Constraints;
    }

    export interface Function {
        constant: boolean;
        inputs: Parameter[];
        name: string;
        outputs: Parameter[];
        payable: boolean;
        stateMutability: string;
        type: string;
        anonymous?: boolean;
        functionInstance?: any;
    }

    export interface NameToFunctionMap {
        [functionName: string]: Function;
    }

    /**
     * @param  {string} jsonPath
     * @returns {NameToFunctionMap} dictionary functionName -> abi
     */
    export function importABIFromFile(jsonPath: string) : NameToFunctionMap {
        let inputJson = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

        if (inputJson.abi != null){
            inputJson = inputJson.abi;
        }
        
        let abi = inputJson as Function[];
        let map: NameToFunctionMap = { };
        abi.forEach(functionABI => {
            map[functionABI.name] = functionABI;
        });
        return map;
    }
}