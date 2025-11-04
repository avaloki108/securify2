// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Test contract for SC09: Insecure Randomness vulnerability

contract VulnerableRandomness {
    mapping(address => uint256) public tickets;
    address public lastWinner;
    
    // VIOLATION: Uses block.timestamp for randomness in lottery
    function buyTicket() external payable {
        require(msg.value >= 0.1 ether, "Ticket costs 0.1 ETH");
        
        // Insecure: block.timestamp can be manipulated by miners
        uint256 ticketNumber = uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender)));
        tickets[msg.sender] = ticketNumber;
    }
    
    // VIOLATION: Uses blockhash for winner selection
    function selectWinner() external {
        // Insecure: blockhash is predictable
        uint256 randomNumber = uint256(blockhash(block.number - 1));
        address winner = address(uint160(randomNumber));
        lastWinner = winner;
        
        payable(winner).transfer(address(this).balance);
    }
    
    // VIOLATION: Uses block.difficulty/prevrandao for randomness
    function generateRandomNumber() external view returns (uint256) {
        // Insecure: block.difficulty (prevrandao in PoS) is predictable
        return uint256(keccak256(abi.encodePacked(block.difficulty, block.timestamp)));
    }
    
    // VIOLATION: Uses msg.sender modulo for random selection
    function randomMint() external {
        // Insecure: msg.sender is known and controllable
        uint256 randomId = uint256(keccak256(abi.encodePacked(msg.sender))) % 100;
        // Mint NFT with randomId
    }
    
    // VIOLATION: Uses tx.origin for randomness
    function drawPrize() external returns (uint256) {
        // Insecure: tx.origin is predictable
        return uint256(keccak256(abi.encodePacked(tx.origin, block.number))) % 10;
    }
}

// Example of secure randomness using Chainlink VRF (simplified interface)
interface IVRFCoordinator {
    function requestRandomWords() external returns (uint256 requestId);
}

contract SecureRandomness {
    IVRFCoordinator public vrfCoordinator;
    mapping(uint256 => address) public requestIdToPlayer;
    mapping(address => uint256) public tickets;
    address public lastWinner;
    
    constructor(address _vrfCoordinator) {
        vrfCoordinator = IVRFCoordinator(_vrfCoordinator);
    }
    
    // COMPLIANT: Uses Chainlink VRF for secure randomness
    function buyTicket() external payable {
        require(msg.value >= 0.1 ether, "Ticket costs 0.1 ETH");
        
        // Request random number from Chainlink VRF
        uint256 requestId = vrfCoordinator.requestRandomWords();
        requestIdToPlayer[requestId] = msg.sender;
    }
    
    // COMPLIANT: Randomness fulfilled by trusted oracle
    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords) external {
        // This would be called by VRF Coordinator
        address player = requestIdToPlayer[requestId];
        tickets[player] = randomWords[0];
    }
}
