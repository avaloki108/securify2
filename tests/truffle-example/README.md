# Truffle Example Project

This is a sample Truffle project for testing Securify 2.5's Truffle integration.

## Structure

- `truffle-config.js` - Truffle configuration file
- `contracts/` - Solidity contracts
  - `SafeMath.sol` - Math operations library
  - `Token.sol` - Simple ERC20-like token that imports SafeMath

## Testing the Integration

To analyze this Truffle project with Securify 2.5:

```bash
# Analyze all contracts in the project
securify tests/truffle-example --truffle-project

# Analyze a specific contract
securify tests/truffle-example --truffle-project --contract-name Token
```

## Expected Behavior

Securify should:
1. Detect the Truffle project structure
2. Find both contract files
3. Flatten Token.sol to resolve the SafeMath import
4. Analyze both contracts for vulnerabilities
