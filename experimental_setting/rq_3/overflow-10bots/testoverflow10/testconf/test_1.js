const { EIP20Simulator } = require('../../../bot-framework/build/EIP20/EIP20Simulator');
const { Bot } = require('../../../bot-framework/build/Bots/Bot');
const { EIP20Account } = require('../../../bot-framework/build/EIP20/EIP20Account');
const { RandomBehaviour } = require('../../../bot-framework/build/Behaviours/RandomBehaviour');
const { OverflowBehaviour } = require('../../../bot-framework/build/Behaviours/OverflowBehaviour');
const { Contract } = require('../../../bot-framework/build/Contract');
const { Context } = require('../../../bot-framework/build/Context');
const abi = require('../../../bot-framework/build/ABI');

const originalArtifacts = "original_artifacts.json";

const msTimeout = 300000;

const ContractArtifacts = artifacts.require("./<contractname>.sol");
const currentArtifacts = "./build/contracts/<contractname>.json";
contract("<contractname>", (accounts) => {

    let HST;
    
    beforeEach(async () => {
        // before each test
        // create a new instance of the contract from the accounts[0]
        HST = await ContractArtifacts.new({ from: accounts[0] });
        console.log("owner: " + accounts[0]);
        console.log("timeout in ms: ", msTimeout );
    })

    it("bottest", (done) => {        

        /**
         * =================
         * CONTEXT CREATION
         * =================
        */

        let context = new Context();
        context.accounts = accounts.map(account => new EIP20Account(account, context));
        context.addresses = accounts;
        
        let originalABI = abi.Types.importABIFromFile(originalArtifacts);
        let targetContract = new Contract(HST, originalABI, currentArtifacts);

        context.accounts.push(new EIP20Account(HST.address, context));
        context.accounts.push(new EIP20Account("0x0000000000000000000000000000000000000000", context));
        
        /**
         * ==================================
         * BOT CREATION (combined behaviour)
         * ==================================
        */

        const numberOfBots = accounts.length;
        for (let i = 0; i < numberOfBots; i++){
            let newBot = new Bot(targetContract, context.accounts[i], context);
            newBot.addBehaviour('overflow');
            context.bots.push(newBot);
        }
        
        /**
         * ===============
         * NEW SIMULATION
         * ===============
        */
        let simulator = new EIP20Simulator(targetContract, context);
        simulator.start(1000).then(() => {
            simulator.printStatus();
            console.log("Finish");
            done();
        }).catch((err) => {
            console.log(err);
            done(err);
        });
        
    }).timeout(msTimeout);

});
