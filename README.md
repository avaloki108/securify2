![securify](/img/securify-v2-5.png)

Securify v2.5
===

Securify 2.5 is a security scanner for Ethereum smart contracts supported by the
[Ethereum
Foundation](https://ethereum.github.io/blog/2018/08/17/ethereum-foundation-grants-update-wave-3/)
and [ChainSecurity](https://chainsecurity.com). The core
[research](https://files.sri.inf.ethz.ch/website/papers/ccs18-securify.pdf)
behind Securify was conducted at the [Secure, Reliable, and Intelligent Systems Lab](https://www.sri.inf.ethz.ch/) at ETH
Zurich.

It is the successor of the popular Securify security scanner (you can find the old version [here](https://github.com/eth-sri/securify)). This version (2.5) is the latest release, building upon the previous 2.0 version with enhanced features and modern Solidity support.


Features
===
- Supports 41+ vulnerabilities including Solidity 0.8.0+ specific patterns (see [table](#supported-vulnerabilities) below)
- Enhanced detection for modern Solidity versions (0.8.0 and above)
- Implements novel context-sensitive static analysis written in Datalog
- Analyzes contracts written in Solidity >= 0.5.8
- Prioritizes critical vulnerabilities relevant to current Solidity versions


Docker
===
To build the container:
```angular2
sudo docker build -t securify .
```
To run the container:
````angular2
sudo docker run -it -v <contract-dir-full-path>:/share securify /share/<contract>.sol
````
Note: to run the code via Docker with a Solidity version that is different than `0.5.12`, you will need to modify the variable `ARG SOLC=0.5.12` at the top of the `Dockerfile` to point to your version. After building with the correct version, you should not run into errors.



Install
===

## Prerequisites
The following instructions assume that a Python is already installed. In addition to that, Securify requires `solc`, `souffle` and `graphviz` to be installed on the system:

### [Solc](https://solidity.readthedocs.io/en/v0.5.10/installing-solidity.html) 
```
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install solc
```

### [Souffle](https://souffle-lang.github.io/install) 

Follow the instructions here: https://souffle-lang.github.io/download.html

*Please do not opt for the unstable version since it might break at any point.*

### [Graphviz / Dot](https://www.graphviz.org/download/)
```
sudo apt install graphviz
```

## Setting up the virtual environment

After the prerequisites have been installed, we can set up the python virtual environment from which we will run the scripts in this project. 

In the project's root folder, execute the following commands to set up and activate the virtual environment:

```
virtualenv --python=/usr/bin/python3.12 venv
source venv/bin/activate
```

Verify that the `python` version is actually `3.12` or higher (any version from 3.12 onwards is supported):

```
python --version
```

Set `LD_LIBRARY_PATH`:
```
cd <securify_root>/securify/staticanalysis/libfunctors
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`
```

Finally, install the project's dependencies by running the following commands from the `<securify_root>` folder:
```
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Now you're ready to start using the securify framework.

Remember: Before executing the framework's scripts, you'll need to activate the virtual environment with the following command:
```
source venv/bin/activate
```

Usage
===

## Analyzing a contract
Currently Securify2.5 supports only flat contracts, i.e., contracts that do not contain import statements.

To analyze a local contract simply run:
```
securify <contract_source>.sol [--use-patterns Pattern1 Pattern2 ...]
```
Or download it from the Blockchain using the Etherscan.io API:
```
securify <contract_address> --from-blockchain [--key <key-file>]
```
*Notice that you need an API-key from Etherscan.io to use this functionality.*

To analyze a contract against specific severity levels run:
```
securify <contract_source>.sol [--include-severity Severity1 Severity2]
securify <contract_source>.sol [--exclude-severity Severity1 Severity2]
```
To get all the available patterns run:
```
securify --list
```

Supported vulnerabilities
===

Securify v2.5 provides comprehensive coverage of the **[OWASP Smart Contract Top 10](https://owasp.org/www-project-smart-contract-top-10/)** vulnerabilities, ensuring your smart contracts are protected against the most critical security risks in blockchain and DeFi applications.

## OWASP Smart Contract Top 10 Coverage

| OWASP ID | Vulnerability | Securify Patterns | Severity |
|----------|---------------|-------------------|----------|
| **SC01** | **Access Control Vulnerabilities** | UnrestrictedWrite, UnrestrictedSelfdestruct, UnrestrictedDelegateCall | Critical/High |
| **SC02** | **Price Oracle Manipulation** | PriceOracleManipulation | Critical |
| **SC03** | **Logic Errors** | IncorrectEquality, Various patterns | Medium |
| **SC04** | **Lack of Input Validation** | MissingInputValidation | Medium |
| **SC05** | **Reentrancy Attacks** | DAO, ReentrancyNoETH, ReentrancyBenign | Critical/Medium/Low |
| **SC06** | **Unchecked External Calls** | UnhandledException, UnusedReturn | High/Medium |
| **SC07** | **Flash Loan Attacks** | FlashLoanAttacks | Critical |
| **SC08** | **Integer Overflow/Underflow** | UncheckedOverflow | High |
| **SC09** | **Insecure Randomness** | InsecureRandomness, Timestamp | High/Low |
| **SC10** | **Denial of Service (DoS)** | DosGasLimit | Medium |

## All Supported Patterns


| ID | Pattern name | Severity | Slither ID | SWC ID | OWASP SC | Comments |
|----|-------------| ---------|------------|--------|----------|----------|
| 1 | TODAmount | Critical | - | [SWC-114](https://swcregistry.io/docs/SWC-114) | - |
| 2 | TODReceiver| Critical | - | [SWC-114](https://swcregistry.io/docs/SWC-114)| - |
| 3 | TODTransfer | Critical | - | [SWC-114](https://swcregistry.io/docs/SWC-114) | - |
| 4 | UnrestrictedWrite | Critical | - | [SWC-124](https://swcregistry.io/docs/SWC-124) | SC01 | Access control |
| **38** | **DelegatecallStorage** | **Critical** | - | **[SWC-112](https://swcregistry.io/docs/SWC-112)** | **SC01** | **Solidity 0.8.0+ - Delegatecall with storage collision risk** |
| **42** | **PriceOracleManipulation** | **Critical** | - | - | **SC02** | **NEW - Price oracle manipulation detection** |
| **43** | **FlashLoanAttacks** | **Critical** | - | - | **SC07** | **NEW - Flash loan vulnerability detection** |
| 5 | RightToLeftOverride | High | `rtlo`| [SWC-130](https://swcregistry.io/docs/SWC-130) | - |
| 6 | ShadowedStateVariable | High | `shadowing-state`, `shadowing-abstract` | [SWC-119](https://swcregistry.io/docs/SWC-119) | - |
| 7 | UnrestrictedSelfdestruct | High | `suicidal` | [SWC-106](https://swcregistry.io/docs/SWC-106) | SC01 | Access control |
| 8 | UninitializedStateVariable | High | `uninitialized-state`| [SWC-109](https://swcregistry.io/docs/SWC-109) | - |
| 9 | UninitializedStorage | High | `uninitialized-storage`| [SWC-109](https://swcregistry.io/docs/SWC-109) | - |
| 10 | UnrestrictedDelegateCall | High | `controlled-delegatecall`| [SWC-112](https://swcregistry.io/docs/SWC-112) | SC01 | Access control |
| 11 | DAO | High | `reentrancy-eth` | [SWC-107](https://swcregistry.io/docs/SWC-107) | SC05 | Reentrancy |
| **39** | **UncheckedArithmetic** | **High** | - | - | **SC08** | **Solidity 0.8.0+ - Unchecked arithmetic blocks** |
| **40** | **StorageCollision** | **High** | - | - | - | **Solidity 0.8.0+ - Storage layout collision in upgradeable contracts** |
| **44** | **InsecureRandomness** | **High** | - | - | **SC09** | **NEW - Insecure randomness source detection** |
| 12 | ERC20Interface | Medium | `erc20-interface` | - | - |
| 13 | ERC721Interface | Medium | `erc721-interface` | - | - |
| 14 | IncorrectEquality | Medium | `incorrect-equality`| [SWC-132](https://swcregistry.io/docs/SWC-132) | SC03 | Logic errors |
| 15 | LockedEther | Medium | `locked-ether` | - | - |
| 16 | ReentrancyNoETH | Medium | `reentrancy-no-eth` | [SWC-107](https://swcregistry.io/docs/SWC-107) | SC05 | Reentrancy |
| 17 | TxOrigin | Medium |`tx-origin` | [SWC-115](https://swcregistry.io/docs/SWC-115) | - |
| 18 | UnhandledException | Medium | `unchecked-lowlevel` | - | SC06 | Unchecked calls |
| 19 | UnrestrictedEtherFlow | Medium | `unchecked-send` |[SWC-105](https://swcregistry.io/docs/SWC-105) | - |
| 20 | UninitializedLocal | Medium | `uninitialized-local` | [SWC-109](https://swcregistry.io/docs/SWC-109) | - |
| 21 | UnusedReturn | Medium | `unused-return` | [SWC-104](https://swcregistry.io/docs/SWC-104) | SC06 | Unchecked calls |
| **41** | **SolcVersion** | **Medium** | `solc-version` | **[SWC-103](https://swcregistry.io/docs/SWC-103)** | - | **Enhanced - Flags versions < 0.8.0** |
| 37 | MissingInputValidation | Medium | - | - | SC04 | Input validation |
| 45 | DosGasLimit | Medium | - | - | SC10 | DoS attacks |
| 22 | ShadowedBuiltin | Low | `shadowing-builtin` | - | - |
| 23 | ShadowedLocalVariable | Low | `shadowing-local` | - | - |
| 24 | CallToDefaultConstructor?| Low | `void-cst` | - | - |
| 25 | CallInLoop | Low | `calls-loop` | [SWC-104](https://swcregistry.io/docs/SWC-104) | - |
| 26 | ReentrancyBenign | Low | `reentrancy-benign` | [SWC-107](https://swcregistry.io/docs/SWC-107) | SC05 | Reentrancy |
| 27 | Timestamp | Low | `timestamp` | [SWC-116](https://swcregistry.io/docs/SWC-116) | SC09 | Randomness source |
| 28 | AssemblyUsage | Info | `assembly` | - | - |
| 29 | ERC20Indexed | Info | `erc20-indexed` | - | - |
| 30 | LowLevelCalls | Info | `low-level-calls` | - | - |
| 31 | NamingConvention | Info | `naming-convention` | - | - |
| 32 | UnusedStateVariable | Info | `unused-state` | - | - |
| 33 | TooManyDigits | Info | `too-many-digits` | - | - |
| 34 | ConstableStates | Info | `constable-states` | - | - |
| 35 | ExternalFunctions | Info | `external-function` | - | - | 
| 36 | StateVariablesDefaultVisibility | Info | - | [SWC-108](https://swcregistry.io/docs/SWC-108) | - |

The following Slither patterns are not checked by Securify2.5 since they are checked by the Solidity compiler (ver. 0.5.8):
- `constant-function`
- `deprecated-standards`
- `pragma`

The following SWC vulnerabilities do not apply to Solidity contracts with pragma >=5.8 and are therefore not checked by Securify2.5:

- SWC-118 (Incorrect Constructor Name)
- SWC-129 (Usage of +=)

## Solidity 0.8.0+ Specific Patterns

Securify2.5 now includes enhanced detection for Solidity 0.8.0+ specific vulnerabilities:

### Key Improvements in Solidity 0.8.0+
- **Built-in Overflow/Underflow Protection**: Arithmetic operations revert on overflow/underflow by default
- **Unchecked Blocks**: New `unchecked { }` syntax bypasses overflow protection - requires careful review
- **Custom Errors**: More gas-efficient error handling
- **ABI Coder V2**: Default, safer ABI encoding/decoding

### New Patterns for 0.8.0+
1. **UncheckedArithmetic** (High): Detects potentially unsafe unchecked arithmetic blocks
2. **StorageCollision** (High): Identifies storage layout collision risks in upgradeable contracts
3. **DelegatecallStorage** (Critical): Enhanced delegatecall detection focusing on storage safety
4. **SolcVersion** (Medium): Now flags contracts using versions < 0.8.0 for missing overflow protection

### Best Practices
- Use Solidity 0.8.0+ for new contracts to benefit from built-in overflow protection
- Only use `unchecked { }` blocks when you're certain overflow/underflow cannot occur
- Plan storage layout carefully in upgradeable contracts to avoid collisions
- Validate all delegatecall targets and ensure storage layout compatibility

## OWASP Smart Contract Top 10 Patterns

Securify2.5 v2.5 now includes comprehensive coverage of the **[OWASP Smart Contract Top 10](https://owasp.org/www-project-smart-contract-top-10/)** vulnerabilities, addressing the most critical security risks in modern blockchain and DeFi applications.

### New OWASP-Specific Patterns

1. **PriceOracleManipulation** (Critical - SC02): Detects price oracle manipulation vulnerabilities
   - Identifies oracle calls without proper validation
   - Checks for missing Time-Weighted Average Price (TWAP) usage
   - Verifies multiple oracle source validation
   - Prevents flash loan price manipulation attacks

2. **FlashLoanAttacks** (Critical - SC07): Detects flash loan attack vulnerabilities
   - Identifies functions vulnerable to flash loan manipulation
   - Checks for missing reentrancy guards
   - Verifies proper state validation before and after critical operations
   - Detects reliance on spot prices or balance checks

3. **InsecureRandomness** (High - SC09): Detects insecure randomness sources
   - Flags use of block.timestamp, block.difficulty, blockhash for randomness
   - Identifies randomness in critical operations (lotteries, winner selection, token distribution)
   - Recommends Chainlink VRF or similar secure randomness solutions

### Enhanced Existing Patterns with OWASP Tags

The following existing patterns have been tagged with their corresponding OWASP Smart Contract Top 10 categories:

- **SC01 - Access Control**: UnrestrictedWrite, UnrestrictedSelfdestruct, UnrestrictedDelegateCall
- **SC04 - Input Validation**: MissingInputValidation
- **SC05 - Reentrancy**: DAO, ReentrancyNoETH, ReentrancyBenign
- **SC06 - Unchecked Calls**: UnhandledException, UnusedReturn
- **SC08 - Integer Overflow**: UncheckedOverflow
- **SC10 - DoS Attacks**: DosGasLimit

### OWASP Best Practices

- **Oracle Security**: Always use TWAP, consult multiple oracle sources, or use decentralized oracles like Chainlink
- **Flash Loan Protection**: Implement reentrancy guards, validate state changes, avoid relying on spot prices
- **Secure Randomness**: Use Chainlink VRF or similar cryptographically secure randomness sources
- **Access Control**: Always validate msg.sender before critical state changes or asset transfers
- **Input Validation**: Sanitize and validate all external inputs before use in computations
- **Reentrancy Protection**: Use checks-effects-interactions pattern and reentrancy guards
- **Call Validation**: Always check return values from external calls
- **Overflow Protection**: Use Solidity 0.8.0+ or SafeMath for arithmetic operations


Acknowledgments
===
The following people have contributed to Securify v2.5:

- Ioannis Sachinoglou
- Lavrentios Frobeen
- Frederic Vogel
- Dimitar Dimitrov
- Petar Tsankov
