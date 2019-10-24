var Web3 = require('web3');
const ContractArtifacts = artifacts.require("./<contractname>.sol");
contract("<contractname>", (accounts) => {

    let HST;

    beforeEach(async () => {
        // before each test
        // create a new instance of the contract from the accounts[0]
        HST = await ContractArtifacts.new({ from: accounts[0] });
        console.log("owner: " + accounts[0]);
    });

    it("test", async () => {
        let null_address = "0x0000000000000000000000000000000000000000";
        let web3 = new Web3();

<codehere>
    });

});
