from typing import List

from securify.analyses.patterns.abstract_pattern import Severity, PatternMatch, MatchComment
from securify.analyses.patterns.ast.abstract_ast_pattern import AbstractAstPattern
from securify.analyses.patterns.ast.declaration_utils import DeclarationUtils
from securify.solidity.v_0_5_x.solidity_grammar_core import ContractDefinition, InheritanceSpecifier, VariableDeclaration


class StorageCollisionPattern(DeclarationUtils, AbstractAstPattern):
    name = "Storage Collision Risk"

    description = "In contracts using inheritance or proxy patterns, storage layout collisions can occur. Ensure proper storage gap or layout planning in upgradeable contracts."

    severity = Severity.HIGH
    tags = {"solidity_version": "0.8.0+", "category": "storage", "upgradeable": "true"}
    
    # Storage gap pattern used in upgradeable contracts (e.g., OpenZeppelin)
    STORAGE_GAP_PATTERN = '__gap'

    def find_matches(self) -> List[PatternMatch]:
        ast_root = self.get_ast_root()
        contracts = ast_root.find_descendants_of_type(ContractDefinition)
        
        for contract in contracts:
            # Check if contract uses inheritance
            inheritance_list = []
            try:
                if hasattr(contract, 'baseContracts') and contract.baseContracts:
                    inheritance_list = contract.baseContracts
            except AttributeError:
                continue
            
            # If contract uses inheritance, check for storage variables
            if len(inheritance_list) > 0:
                state_vars = contract.find_descendants_of_type(VariableDeclaration)
                
                # Check if contract has any state variables
                has_state_vars = False
                has_gap = False
                
                for var in state_vars:
                    has_state_vars = True
                    if hasattr(var, 'name') and self.STORAGE_GAP_PATTERN in str(var.name).lower():
                        has_gap = True
                        break
                
                # If contract has state variables and multiple inheritance but no storage gap, flag it
                if has_state_vars and not has_gap and len(inheritance_list) > 1:
                    yield self.match_warning().with_info(
                        MatchComment(f"Contract {contract.name} uses multiple inheritance without storage gap - potential storage collision in upgradeable contracts"),
                        *self.ast_node_info(contract)
                    )
