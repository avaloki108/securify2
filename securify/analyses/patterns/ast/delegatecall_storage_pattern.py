from typing import List

from securify.analyses.patterns.abstract_pattern import Severity, PatternMatch, MatchComment
from securify.analyses.patterns.ast.abstract_ast_pattern import AbstractAstPattern
from securify.analyses.patterns.ast.declaration_utils import DeclarationUtils
from securify.solidity.v_0_5_x.solidity_grammar_core import FunctionCall, MemberAccess


class DelegatecallStoragePattern(DeclarationUtils, AbstractAstPattern):
    name = "Delegatecall Storage Safety"

    description = "Delegatecall executes code in the context of the calling contract. In Solidity 0.8.0+, ensure storage layouts match between caller and callee to prevent storage corruption."

    severity = Severity.CRITICAL
    tags = {"solidity_version": "0.8.0+", "category": "delegatecall", "storage": "true"}

    def find_matches(self) -> List[PatternMatch]:
        ast_root = self.get_ast_root()
        
        # Find all function calls
        function_calls = ast_root.find_descendants_of_type(FunctionCall)
        
        for call in function_calls:
            # Check if this is a delegatecall
            try:
                # delegatecall can appear as address.delegatecall(...)
                if hasattr(call, 'expression'):
                    expr = call.expression
                    if isinstance(expr, MemberAccess):
                        if hasattr(expr, 'memberName') and str(expr.memberName) == 'delegatecall':
                            yield self.match_violation().with_info(
                                MatchComment("Delegatecall detected - ensure storage layout compatibility and validate target address"),
                                *self.ast_node_info(call)
                            )
                    # Also check for direct delegatecall references
                    elif hasattr(expr, 'name') and 'delegatecall' in str(expr.name).lower():
                        yield self.match_violation().with_info(
                            MatchComment("Delegatecall detected - ensure storage layout compatibility and validate target address"),
                            *self.ast_node_info(call)
                        )
            except AttributeError:
                # Expected when node doesn't have required attributes
                continue
