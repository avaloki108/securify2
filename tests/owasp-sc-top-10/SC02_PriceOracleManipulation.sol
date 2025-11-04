// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Test contract for SC02: Price Oracle Manipulation vulnerability

interface IPriceOracle {
    function getPrice(address token) external view returns (uint256);
    function latestAnswer() external view returns (uint256);
}

contract VulnerablePriceOracle {
    IPriceOracle public oracle;
    
    constructor(address _oracle) {
        oracle = IPriceOracle(_oracle);
    }
    
    // VIOLATION: Uses oracle price without validation
    function buyTokens() external payable {
        uint256 price = oracle.getPrice(address(this));
        uint256 tokensToMint = msg.value / price;
        // Mint tokens based on unvalidated oracle price
    }
    
    // VIOLATION: Single oracle source without checks
    function swapTokens(uint256 amount) external {
        uint256 price = oracle.latestAnswer();
        // Use price directly without validation
        uint256 outputAmount = amount * price;
    }
}

contract SecurePriceOracle {
    IPriceOracle public oracle1;
    IPriceOracle public oracle2;
    uint256 public constant MAX_PRICE_DIFF = 100; // 1% difference allowed
    
    constructor(address _oracle1, address _oracle2) {
        oracle1 = IPriceOracle(_oracle1);
        oracle2 = IPriceOracle(_oracle2);
    }
    
    // COMPLIANT: Uses multiple oracle sources with validation
    function buyTokensSafe() external payable {
        uint256 price1 = oracle1.getPrice(address(this));
        uint256 price2 = oracle2.getPrice(address(this));
        
        // Validate prices are within acceptable range
        require(
            price1 * 10000 / price2 < 10000 + MAX_PRICE_DIFF &&
            price2 * 10000 / price1 < 10000 + MAX_PRICE_DIFF,
            "Price discrepancy too large"
        );
        
        uint256 avgPrice = (price1 + price2) / 2;
        uint256 tokensToMint = msg.value / avgPrice;
        // Mint tokens based on validated average price
    }
}
