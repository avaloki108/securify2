from typing import List

from securify.analyses.patterns.abstract_pattern import Severity, PatternMatch, MatchComment
from securify.analyses.patterns.ast.abstract_ast_pattern import AbstractAstPattern
from securify.analyses.patterns.ast.declaration_utils import DeclarationUtils
from securify.solidity.v_0_5_x.solidity_grammar_core import PragmaDirective
import re


class SolcVersionPattern(DeclarationUtils, AbstractAstPattern):
    name = "Solidity pragma directives"

    description = "Avoid complex solidity version pragma statements and use Solidity 0.8.0+ for built-in overflow protection."

    # Needs to be changed to informational
    severity = Severity.MEDIUM
    tags = {}

    def find_matches(self) -> List[PatternMatch]:
        ast_root = self.get_ast_root()
        nodes = ast_root.find_descendants_of_type(PragmaDirective)
        for node in nodes:
            # Check for complex version pragma
            if re.compile(r"[<>^]").search(node.src_code):
                yield self.match_violation().with_info(
                    MatchComment(f"{node.src_code} is complex"),
                    *self.ast_node_info(node)
                )
            
            # Check for outdated Solidity versions (< 0.8.0)
            # Extract version from pragma
            version_match = re.search(r'(\d+)\.(\d+)\.(\d+)', node.src_code)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                
                # Flag versions before 0.8.0 as they lack built-in overflow protection
                if major == 0 and minor < 8:
                    yield self.match_warning().with_info(
                        MatchComment(f"{node.src_code} - Consider upgrading to Solidity 0.8.0+ for built-in overflow/underflow protection"),
                        *self.ast_node_info(node)
                    )
