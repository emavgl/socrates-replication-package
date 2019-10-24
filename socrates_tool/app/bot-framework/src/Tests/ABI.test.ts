
import * as abi from '../ABI';
import * as mocha from 'mocha';
import * as chai from 'chai';
import { RandomValueGenerator } from '../Util/RandomValueGenerator';
import { Context } from '../Context';
import { Account } from '../Account';
import { IBigNumber } from '../Types/BigNumber';
import { AssertionError } from 'assert';


const assert = chai.assert;
describe('ABI library', () => {

  it('should be able to import abi from file' , () => {
      const filePath = './src/Tests/resources/EIP20.abi.json';
      let importedABI = abi.Types.importABIFromFile(filePath);
      let assertion = Object.keys(importedABI).length > 0;
      assert(assertion, "imported abi map should not be empty");
  });

  it('should import map and constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let inputWithConstraints = importedABI['transferFrom'].inputs[2];
    assert(inputWithConstraints.constraints != null, "does not contain constraints");
  });

  function createMockContext(){
    // Create mock context and accounts
    let context = new Context();
    let accounts = new Array<Account>();
    for (let i = 0; i < 10; i++) {
      accounts.push(new Account('address' + i.toString()));
    }
    context.accounts = accounts;
    return context;
  }

  function checkTypeConstraints(type: string, value: any, constraints: abi.Types.Constraints | undefined, defaultConstraints: any){

      type = type.replace("[]", "");
      if (!constraints) constraints = defaultConstraints[type] as abi.Types.Constraints;

      // Check for a BigNumber assertion
      if (type.includes("uint")){
        //console.log("I'm checking a bignumber", (value as IBigNumber).toString())
        let minValue = constraints.minValue;
        let maxValue = constraints.maxValue;
        if (minValue != null && maxValue != null){
          assert((value as IBigNumber).greaterThanOrEqualTo(minValue), "value is not greater or equal to minValue");
          assert((value as IBigNumber).lessThanOrEqualTo(maxValue), "value is not less than or equal to maxValue");
        }
        if (constraints.defaultValue){
          assert((value as IBigNumber).equals(constraints.defaultValue), "value is not equal to defaultValue");
        }
      }

      // Check string assertion
      if (type.includes("string")){
        // is an array
        let lengthString = (value as string).length;
        // console.log("checking a string of size", lengthString)

        if (constraints.minStringSize)
          assert(lengthString >= constraints.minStringSize, "value is not greater or equal to minStringSize");

        if (constraints.maxStringSize)
          assert(lengthString <= constraints.maxStringSize, "value is not less than maxStringSize");
      }

      if (type.includes("bool")){
        assert(typeof(value) === 'boolean', "value is not a boolean");
      }
  }

  function checkConstraints(funct: abi.Types.Function, parameters: any[], defaultConstraints: any){
      for (let i = 0; i < funct.inputs.length; i++) {
        let constraints = funct.inputs[i].constraints;
        const type = funct.inputs[i].type;
        const value = parameters[i];
        
        if (type.includes("address")){
          continue;
        }

        if (type.includes("[]")){
            // is an array
            assert(Array.isArray(value), "value should be an array");
            let lengthArray = (value as Array<any>).length;
            // console.log("is an array of size", lengthArray);

            let arrayConstraints = constraints;
            if (!arrayConstraints){
              // using the default contraints for array
              console.log("using the default constraints for array");
              arrayConstraints = defaultConstraints['[]'] as abi.Types.Constraints;
            }

            if (arrayConstraints.minArraySize)
              assert(lengthArray >= arrayConstraints.minArraySize, "should be greater or equal than minArraySize ");

            if (arrayConstraints.maxArraySize)
              assert(lengthArray < arrayConstraints.maxArraySize, "should be less than maxArraySize");

            value.forEach(element => {
              checkTypeConstraints(type, element, constraints, defaultConstraints);
            });

        } else {
          checkTypeConstraints(type, value, constraints, defaultConstraints);
        }
      }
  }
 
  it('generate random bigNumber with constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);
    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(importedABI['transferFrom']);
      checkConstraints(importedABI['transferFrom'], parameters, rvg.defaultConstraints);
    }
  });

  it('generate random string with constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);

    let mockFunction = importedABI['transferFrom'];
    mockFunction.inputs[2].type = 'string';

    if (mockFunction.inputs[2].constraints != null){
      mockFunction.inputs[2].constraints!.minStringSize = 3;
      mockFunction.inputs[2].constraints!.maxStringSize = 10;
    }

    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(mockFunction);
      checkConstraints(mockFunction, parameters, rvg.defaultConstraints);
    }
  });

  it('generate random bigNumber array with constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);

    let mockFunction = importedABI['transferFrom'];
    mockFunction.inputs[2].type = 'uint256[]';

    if (mockFunction.inputs[2].constraints != null){
      mockFunction.inputs[2].constraints!.minArraySize = 3;
      mockFunction.inputs[2].constraints!.maxArraySize = 10;
    }

    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(mockFunction);
      checkConstraints(mockFunction, parameters, rvg.defaultConstraints);
    }
  });

  it('generate random string array with constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);

    let mockFunction = importedABI['transferFrom'];
    mockFunction.inputs[2].type = 'string[]';

    if (mockFunction.inputs[2].constraints != null){
      mockFunction.inputs[2].constraints!.minArraySize = 3;
      mockFunction.inputs[2].constraints!.maxArraySize = 10;
      mockFunction.inputs[2].constraints!.minStringSize = 3;
      mockFunction.inputs[2].constraints!.maxStringSize = 10;
    }

    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(mockFunction);
      checkConstraints(mockFunction, parameters, rvg.defaultConstraints);
    }
  });


  it('generate random bignumber with default constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);

    let mockFunction = importedABI['transferFrom'];
    mockFunction.inputs[2].type = 'uint256';

    if (mockFunction.inputs[2].constraints != null){
      mockFunction.inputs[2].constraints = {};
    }

    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(mockFunction);
      checkConstraints(mockFunction, parameters, rvg.defaultConstraints);
    }
  });


  it('generate random bigNumber array with default constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);

    let mockFunction = importedABI['transferFrom'];
    mockFunction.inputs[2].type = 'uint256[]';
    mockFunction.inputs[2].constraints = {}

    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(mockFunction);
      checkConstraints(mockFunction, parameters, rvg.defaultConstraints);
    }
  });

  it('generate random string array with default constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);

    let mockFunction = importedABI['transferFrom'];
    mockFunction.inputs[2].type = 'string[]';
    mockFunction.inputs[2].constraints = {}

    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(mockFunction);
      checkConstraints(mockFunction, parameters, rvg.defaultConstraints);
    }
  });


  it('generate random boolean array without constraints' , () => {
    const filePath = './src/Tests/resources/EIP20WithContraints.abi.json';
    let importedABI = abi.Types.importABIFromFile(filePath);
    let context: Context = createMockContext();
    let rvg = new RandomValueGenerator(context);

    let mockFunction = importedABI['transferFrom'];
    mockFunction.inputs[2].type = 'bool[]';
    mockFunction.inputs[2].constraints = {}

    for (let i = 0; i < 10000; i++) {
      let parameters = rvg.getRandomParameters(mockFunction);
      checkConstraints(mockFunction, parameters, rvg.defaultConstraints);
    }
  });


});



