# OWASP Smart Contract Top 10 Test Contracts

This directory contains test contracts demonstrating the OWASP Smart Contract Top 10 vulnerabilities that Securify2.5 can detect.

## Test Contracts

### SC02_PriceOracleManipulation.sol
Demonstrates price oracle manipulation vulnerabilities:
- **Vulnerable**: Direct use of oracle price without validation
- **Vulnerable**: Single oracle source without cross-validation
- **Secure**: Multiple oracle sources with price discrepancy checks
- **Secure**: Average price calculation from multiple sources

### SC07_FlashLoanAttacks.sol
Demonstrates flash loan attack vulnerabilities:
- **Vulnerable**: State changes without reentrancy protection
- **Vulnerable**: Balance checks vulnerable to flash loan manipulation
- **Vulnerable**: State updates after external calls
- **Secure**: Reentrancy guard implementation
- **Secure**: Proper state validation before and after external calls

### SC09_InsecureRandomness.sol
Demonstrates insecure randomness vulnerabilities:
- **Vulnerable**: Using `block.timestamp` for lottery/randomness
- **Vulnerable**: Using `blockhash` for winner selection
- **Vulnerable**: Using `block.difficulty`/`prevrandao` for randomness
- **Vulnerable**: Using `msg.sender` modulo for random selection
- **Vulnerable**: Using `tx.origin` for randomness
- **Secure**: Using Chainlink VRF for secure randomness

## Testing with Securify2.5

To test these contracts with Securify2.5, run:

```bash
# Test price oracle manipulation detection
securify tests/owasp-sc-top-10/SC02_PriceOracleManipulation.sol

# Test flash loan attack detection
securify tests/owasp-sc-top-10/SC07_FlashLoanAttacks.sol

# Test insecure randomness detection
securify tests/owasp-sc-top-10/SC09_InsecureRandomness.sol
```

## Expected Results

Each test contract should trigger the corresponding OWASP pattern detections:
- Price oracle calls without validation should be flagged
- Functions vulnerable to flash loan manipulation should be identified
- Insecure randomness sources should be detected

The secure implementations should either pass the checks or trigger fewer/lower severity warnings.

## References

- [OWASP Smart Contract Top 10](https://owasp.org/www-project-smart-contract-top-10/)
- [Securify2.5 Documentation](../README.md)
