from typing import List

from securify.analyses.patterns.abstract_pattern import Severity, PatternMatch, MatchComment
from securify.analyses.patterns.ast.abstract_ast_pattern import AbstractAstPattern
from securify.analyses.patterns.ast.declaration_utils import DeclarationUtils
import re


class UncheckedArithmeticPattern(DeclarationUtils, AbstractAstPattern):
    name = "Unchecked Arithmetic"

    description = "Solidity 0.8.0+ unchecked blocks bypass overflow/underflow protection. Ensure arithmetic operations in unchecked blocks cannot overflow or underflow."

    severity = Severity.HIGH
    tags = {"solidity_version": "0.8.0+", "category": "arithmetic"}

    def find_matches(self) -> List[PatternMatch]:
        # Since UncheckedBlock is not in the grammar (Solidity 0.8.0+ feature),
        # we'll search through the source code for unchecked blocks
        source_code = self.analysis_context.source_code
        
        if not source_code:
            return []
        
        # Search for unchecked blocks in the source code
        pattern = re.compile(r'\bunchecked\s*\{', re.MULTILINE)
        matches = pattern.finditer(source_code)
        
        for match in matches:
            # Calculate line number
            line_num = source_code[:match.start()].count('\n') + 1
            
            # Create a warning for each unchecked block found
            # We can't provide exact AST node info since unchecked isn't in the grammar
            # So we'll create a generic match comment
            yield self.match_warning().with_info(
                MatchComment(f"Unchecked block detected at line {line_num} - ensure arithmetic operations cannot overflow/underflow")
            )
