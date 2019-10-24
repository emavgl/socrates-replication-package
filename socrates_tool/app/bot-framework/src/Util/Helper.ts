export class Helper {
    private static sortAlphaNum(a: string, b: string) {
        var reA = /[^a-zA-Z]/g;
        var reN = /[^0-9]/g;
        var aA = a.replace(reA, "");
        var bA = b.replace(reA, "");
        if(aA === bA) {
            var aN = parseInt(a.replace(reN, ""), 10);
            var bN = parseInt(b.replace(reN, ""), 10);
            return aN === bN ? 0 : aN > bN ? 1 : -1;
        } else {
            return aA > bA ? 1 : -1;
        }         
    }

    public static extractInputs(variables: any){
        let arrays = {};
        let parsedVariables = {};

        for (const variable of variables) {
            let name: string = variable['name'];
            let value: string = variable['value'];
    
            if (name.includes("__")){
                // Is part of IntVector
                let base_name = name.split("__")[0];
                if (!arrays[base_name]){
                    arrays[base_name] = new Array<any>();
                }

                if (!value.includes("-") && !name.includes("__length")){
                    // Valid value for an array member
                    arrays[base_name].push(value);    
                }
            } else {
                parsedVariables[name] = value;
            }
        }

        for (const [key, value] of Object.entries(arrays)) {
            (value as string[]).sort((a, b) => this.sortAlphaNum(a, b));
        }

        return {...arrays, ...parsedVariables}
    }
}