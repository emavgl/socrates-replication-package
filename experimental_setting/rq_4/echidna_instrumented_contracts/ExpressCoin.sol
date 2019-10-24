pragma solidity ^0.4.16;
contract owned {
    address public owner;
    constructor() public {
        owner = msg.sender;
    }
    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }
    function transferOwnership(address newOwner) onlyOwner public {
        owner = newOwner;
    }
}
contract ExpressCoin is owned {
    string public constant name = "ExpressCoin";
    string public constant symbol = "XPC";
    uint public constant decimals = 8;
    uint constant ONETOKEN = 10 ** uint(decimals);
    uint constant MILLION = 1000000; 
    uint public totalSupply;
    constructor() public {
        totalSupply = 88 * MILLION * ONETOKEN;                        
        balanceOf[msg.sender] = totalSupply;                            
    }
    mapping (address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Burn(address indexed from, uint256 value);
    
    function transfer(address _to, uint256 _value) public {
        _transferXToken(msg.sender, _to, _value);
    }
    function _transferXToken(address _from, address _to, uint _value) internal {
        require(_to != 0x0);
        require(balanceOf[_from] >= _value);
        require(balanceOf[_to] + _value > balanceOf[_to]);
        uint previousBalances = balanceOf[_from] + balanceOf[_to];
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(_from, _to, _value);
        assert(balanceOf[_from] + balanceOf[_to] == previousBalances);
    }
    function() payable public { }

    function withdrawEther() onlyOwner public{
        owner.transfer(this.balance);
    }

    // INSTRUMENTED
    uint256 internal add1_1;
    uint256 internal add1_2;
    uint256 internal add1_result;


    // INSTRUMENTED
    uint256 internal add2_1;
    uint256 internal add2_2;
    uint256 internal add2_result;

    function mint(address target, uint256 token) onlyOwner public {

        // INSTRUMENTED
        add1_1 = balanceOf[target];
        add1_2 = token;
        balanceOf[target] += token; // original
        add1_result = balanceOf[target];

        add2_1 = totalSupply;
        add2_2 = token;
        totalSupply += token;       // original
        add2_result = totalSupply;

        emit Transfer(0, this, token);
        emit Transfer(this, target, token);
    }

    function burn(uint256 _value) public returns (bool success) {
        require(balanceOf[msg.sender] >= _value);   
        balanceOf[msg.sender] -= _value;            
        totalSupply -= _value;
        emit Burn(msg.sender, _value);
        return true;
    }

    // INVARIANTS
    function echidna_invariant_I1() public returns (bool) {
        bool op1 = add1_result >= add1_1;
        bool op2 = add2_result >= add2_1;
        return (op1 && op2); // if one of the two is false -> overflow
    }

}