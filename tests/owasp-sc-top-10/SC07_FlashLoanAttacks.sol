// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Test contract for SC07: Flash Loan Attack vulnerability

interface IFlashLoanReceiver {
    function onFlashLoan(uint256 amount) external;
}

contract VulnerableFlashLoan {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    // VIOLATION: State changes can be manipulated in single transaction
    function deposit() external payable {
        balances[msg.sender] += msg.value;
        totalSupply += msg.value;
    }
    
    // VIOLATION: Uses balance check vulnerable to flash loan manipulation
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: Relies on balance state that can be manipulated
        uint256 sharePercent = (balances[msg.sender] * 100) / totalSupply;
        
        balances[msg.sender] -= amount;
        totalSupply -= amount;
        payable(msg.sender).transfer(amount);
    }
    
    // VIOLATION: Unprotected state update after external call
    function executeFlashLoan(address receiver, uint256 amount) external {
        uint256 balanceBefore = address(this).balance;
        
        payable(receiver).transfer(amount);
        IFlashLoanReceiver(receiver).onFlashLoan(amount);
        
        // State updated after external call - vulnerable to manipulation
        require(address(this).balance >= balanceBefore, "Flash loan not repaid");
    }
}

contract SecureFlashLoan {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    bool private locked;
    
    modifier noReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
    
    // COMPLIANT: Has reentrancy guard
    function deposit() external payable noReentrant {
        balances[msg.sender] += msg.value;
        totalSupply += msg.value;
    }
    
    // COMPLIANT: Protected with reentrancy guard
    function withdraw(uint256 amount) external noReentrant {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        totalSupply -= amount;
        
        payable(msg.sender).transfer(amount);
    }
    
    // COMPLIANT: Has proper state validation before and after
    function executeFlashLoan(address receiver, uint256 amount) external noReentrant {
        uint256 balanceBefore = address(this).balance;
        require(balanceBefore >= amount, "Insufficient liquidity");
        
        payable(receiver).transfer(amount);
        IFlashLoanReceiver(receiver).onFlashLoan(amount);
        
        uint256 balanceAfter = address(this).balance;
        require(balanceAfter >= balanceBefore, "Flash loan not repaid");
    }
}
