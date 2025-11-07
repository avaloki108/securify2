"""
Truffle integration module for Securify 2.5
Provides support for analyzing Truffle projects
"""

import os
import subprocess
import tempfile
import re
from pathlib import Path


class TruffleProject:
    """Represents a Truffle project and provides utilities for working with it"""
    
    def __init__(self, project_path):
        """
        Initialize a Truffle project
        
        Args:
            project_path: Path to the Truffle project directory
        """
        self.project_path = Path(project_path).resolve()
        self.config_file = self._find_config_file()
        
        if not self.config_file:
            raise ValueError(f"No Truffle configuration file found in {project_path}")
    
    def _find_config_file(self):
        """Find the Truffle configuration file (truffle-config.js or truffle.js)"""
        for config_name in ['truffle-config.js', 'truffle.js']:
            config_path = self.project_path / config_name
            if config_path.exists():
                return config_path
        return None
    
    @property
    def contracts_dir(self):
        """Get the contracts directory"""
        contracts_path = self.project_path / 'contracts'
        return contracts_path if contracts_path.exists() else None
    
    @property
    def build_dir(self):
        """Get the build directory"""
        build_path = self.project_path / 'build' / 'contracts'
        return build_path if build_path.exists() else None
    
    def list_contracts(self):
        """List all Solidity contracts in the project"""
        if not self.contracts_dir:
            return []
        
        contracts = []
        for file in self.contracts_dir.glob('**/*.sol'):
            contracts.append(file)
        return contracts
    
    def flatten_contract(self, contract_path):
        """
        Flatten a Solidity contract by resolving all imports
        
        Args:
            contract_path: Path to the contract file
            
        Returns:
            Path to the flattened contract file
        """
        contract_path = Path(contract_path)
        
        # Try using truffle-flattener if available
        try:
            flattened = self._flatten_with_truffle_flattener(contract_path)
            if flattened:
                return flattened
        except Exception:
            pass
        
        # Fallback to manual flattening
        return self._flatten_manual(contract_path)
    
    def _flatten_with_truffle_flattener(self, contract_path):
        """Flatten contract using truffle-flattener tool"""
        try:
            result = subprocess.run(
                ['npx', 'truffle-flattener', str(contract_path)],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                # Save flattened contract to temp file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
                    f.write(result.stdout)
                    return f.name
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def _flatten_manual(self, contract_path):
        """
        Manually flatten a contract by resolving imports
        This is a simple implementation that handles basic imports
        """
        visited = set()
        output_lines = []
        seen_pragmas = set()
        
        def process_file(file_path):
            if file_path in visited:
                return
            visited.add(file_path)
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                stripped = line.strip()
                
                # Handle import statements
                if stripped.startswith('import'):
                    import_path = self._extract_import_path(stripped)
                    if import_path:
                        resolved_path = self._resolve_import(file_path, import_path)
                        if resolved_path and resolved_path.exists():
                            process_file(resolved_path)
                            continue
                
                # Skip duplicate pragma statements
                if stripped.startswith('pragma'):
                    if stripped in seen_pragmas:
                        continue
                    seen_pragmas.add(stripped)
                
                output_lines.append(line)
        
        process_file(Path(contract_path))
        
        # Save flattened contract to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.writelines(output_lines)
            return f.name
    
    def _extract_import_path(self, import_line):
        """Extract the file path from an import statement"""
        # Match: import "path"; or import 'path';
        match = re.search(r'import\s+["\']([^"\']+)["\']', import_line)
        if match:
            return match.group(1)
        
        # Match: import {X} from "path"; or import X from "path";
        match = re.search(r'from\s+["\']([^"\']+)["\']', import_line)
        if match:
            return match.group(1)
        
        return None
    
    def _resolve_import(self, source_file, import_path):
        """
        Resolve an import path relative to the source file
        
        Args:
            source_file: The file containing the import
            import_path: The imported path string
            
        Returns:
            Resolved Path object or None
        """
        source_dir = Path(source_file).parent
        
        # Handle relative imports
        if import_path.startswith('./') or import_path.startswith('../'):
            resolved = (source_dir / import_path).resolve()
            if resolved.exists():
                return resolved
        
        # Handle absolute imports from contracts directory
        if self.contracts_dir:
            resolved = (self.contracts_dir / import_path).resolve()
            if resolved.exists():
                return resolved
        
        # Handle node_modules imports (try common patterns)
        if not import_path.startswith('.'):
            for base_dir in [self.project_path, self.project_path / 'node_modules']:
                resolved = (base_dir / import_path).resolve()
                if resolved.exists():
                    return resolved
        
        return None


def is_truffle_project(path):
    """
    Check if a given path is a Truffle project
    
    Args:
        path: Path to check
        
    Returns:
        True if the path contains a Truffle configuration file
    """
    path = Path(path)
    
    # If it's a file, check its parent directory
    if path.is_file():
        path = path.parent
    
    # Check for Truffle config files
    for config_name in ['truffle-config.js', 'truffle.js']:
        if (path / config_name).exists():
            return True
    
    return False


def get_truffle_project_root(path):
    """
    Find the root directory of a Truffle project
    
    Args:
        path: Starting path (file or directory)
        
    Returns:
        Path to the Truffle project root or None
    """
    path = Path(path).resolve()
    
    # If it's a file, start from its parent
    if path.is_file():
        path = path.parent
    
    # Walk up the directory tree
    current = path
    while current != current.parent:
        if is_truffle_project(current):
            return current
        current = current.parent
    
    return None
