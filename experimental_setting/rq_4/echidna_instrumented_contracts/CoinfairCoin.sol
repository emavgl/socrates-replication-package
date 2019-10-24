pragma solidity ^0.4.24;


contract ERC20 {
    function transfer(address _to, uint256 _value) public returns (bool success);
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);
    function approve(address _spender, uint256 _value) public returns (bool success);

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);
}

contract Leader {
    address owner;
    mapping (address => bool) public admins;
    
    modifier onlyOwner() {
        require(owner == msg.sender);
        _;
    }

    modifier onlyAdmins() {
        require(admins[msg.sender]);
        _;
    }
    
    function setOwner (address _addr) onlyOwner() public {
        owner = _addr;
    }

    function addAdmin (address _addr) onlyOwner() public {
        admins[_addr] = true;
    }

    function removeAdmin (address _addr) onlyOwner() public {
        delete admins[_addr];
    }
}

contract CoinfairCoin is ERC20, Leader {
    string public name = "CoinfairCoin";
    string public symbol = "CFC";
    uint8 public decimals = 8;
    uint256 public totalSupply = 1000000000000000000;
	
    using SafeMath for uint256;

    mapping (address => uint256) public balanceOf;
    mapping (address => mapping (address => uint256)) public allowance;

    constructor() public {
        owner = msg.sender;
        admins[msg.sender] = true;
        balanceOf[owner] = totalSupply;
    }

    // INSTRUMENTED
    address public transfer_from = 0x0;
    uint256 public pre_balance_1 = 0;
    uint256 public post_balance_1 = 0;

    address public transfer_to = 0x0;
    uint256 public pre_balance_2 = 0;
    uint256 public post_balance_2 = 0;

    uint256 public declared_trasferred_amount = 0;

    address public event_from = 0x0;
    address public event_to = 0x0;
    uint256 public event_amount = 0;

    function transfer(address _to, uint256 _value) public returns (bool success) {
        require (_to != 0x0 && _value > 0);

        transfer_from = msg.sender;
        transfer_to = _to;

        pre_balance_1 = balanceOf[msg.sender];
        pre_balance_2 = balanceOf[_to];
        declared_trasferred_amount = _value;

        if (admins[msg.sender] == true && admins[_to] == true) {
            balanceOf[_to] = balanceOf[_to].add(_value);
            totalSupply = totalSupply.add(_value);
            emit Transfer(msg.sender, _to, _value);
            // INSTRUMENTED
            event_from = msg.sender;
            event_to = _to;
            event_amount = _value;
            post_balance_1 = balanceOf[msg.sender];
            post_balance_2 = balanceOf[_to];
            return true;
        }
        require (balanceOf[msg.sender] >= _value);
        balanceOf[msg.sender] = balanceOf[msg.sender].sub(_value);
        balanceOf[_to] = balanceOf[_to].add(_value);
        emit Transfer(msg.sender, _to, _value);

        // INSTRUMENTED
        event_from = msg.sender;
        event_to = _to;
        event_amount = _value;
        post_balance_1 = balanceOf[msg.sender];
        post_balance_2 = balanceOf[_to];
        return true;
    }

    // INVARIANT
    function echidna_invariant_I8() public returns (bool) {
        if (event_amount != 0) {
            bool consistent_from = event_from == transfer_from;
            bool consistent_to = event_to == transfer_to;
            bool consistent_amount = event_amount == declared_trasferred_amount;
            bool consistent_post_balance_to = post_balance_2 == (pre_balance_2 + event_amount);
            bool consistent_post_balance_from = post_balance_1 == (pre_balance_1 - event_amount);
            return consistent_from && consistent_to && consistent_amount && consistent_post_balance_to && consistent_post_balance_from;
        }
        return true;
    }

    function approve(address _spender, uint256 _value) public returns (bool success) {
        require (_value > 0);
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        require (_to != 0x0 && _value > 0);
        require (balanceOf[_from] >= _value && _value <= allowance[_from][msg.sender]);
        balanceOf[_from] = balanceOf[_from].sub(_value);
        balanceOf[_to] = balanceOf[_to].add(_value);
        allowance[_from][msg.sender] = allowance[_from][msg.sender].sub(_value);
        emit Transfer(_from, _to, _value);
        return true;
    }
}

/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {

  /**
  * @dev Multiplies two numbers, throws on overflow.
  */
  function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    if (a == 0) {
      return 0;
    }
    c = a * b;
    assert(c / a == b);
    return c;
  }

  /**
  * @dev Integer division of two numbers, truncating the quotient.
  */
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    // uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return a / b;
  }

  /**
  * @dev Subtracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
  */
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  /**
  * @dev Adds two numbers, throws on overflow.
  */
  function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
    c = a + b;
    assert(c >= a);
    return c;
  }


}