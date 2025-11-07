import unittest
import tempfile
import shutil
from pathlib import Path
from securify.utils.truffle_integration import (
    is_truffle_project, 
    get_truffle_project_root, 
    TruffleProject
)


class TestTruffleDetection(unittest.TestCase):
    """Test Truffle project detection functionality"""
    
    def setUp(self):
        """Create temporary test directories"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_is_truffle_project_with_config(self):
        """Test detection with truffle-config.js"""
        config_file = self.test_path / 'truffle-config.js'
        config_file.write_text('module.exports = {};')
        
        self.assertTrue(is_truffle_project(self.test_path))
    
    def test_is_truffle_project_with_old_config(self):
        """Test detection with truffle.js"""
        config_file = self.test_path / 'truffle.js'
        config_file.write_text('module.exports = {};')
        
        self.assertTrue(is_truffle_project(self.test_path))
    
    def test_is_not_truffle_project(self):
        """Test detection without config files"""
        self.assertFalse(is_truffle_project(self.test_path))
    
    def test_get_truffle_project_root(self):
        """Test finding Truffle project root"""
        config_file = self.test_path / 'truffle-config.js'
        config_file.write_text('module.exports = {};')
        
        # Create a subdirectory
        subdir = self.test_path / 'contracts'
        subdir.mkdir()
        
        # Should find root from subdirectory
        root = get_truffle_project_root(subdir)
        self.assertEqual(root, self.test_path)
    
    def test_get_truffle_project_root_not_found(self):
        """Test when no Truffle project exists"""
        root = get_truffle_project_root(self.test_path)
        self.assertIsNone(root)


class TestTruffleProject(unittest.TestCase):
    """Test TruffleProject class functionality"""
    
    def setUp(self):
        """Create a sample Truffle project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create truffle config
        config_file = self.test_path / 'truffle-config.js'
        config_file.write_text('module.exports = {};')
        
        # Create contracts directory
        self.contracts_dir = self.test_path / 'contracts'
        self.contracts_dir.mkdir()
        
        # Create sample contracts
        (self.contracts_dir / 'Contract1.sol').write_text(
            'pragma solidity ^0.8.0;\ncontract Contract1 {}'
        )
        (self.contracts_dir / 'Contract2.sol').write_text(
            'pragma solidity ^0.8.0;\ncontract Contract2 {}'
        )
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_truffle_project_initialization(self):
        """Test TruffleProject initialization"""
        project = TruffleProject(self.test_path)
        
        self.assertEqual(project.project_path, self.test_path)
        self.assertIsNotNone(project.config_file)
        self.assertEqual(project.contracts_dir, self.contracts_dir)
    
    def test_truffle_project_no_config_error(self):
        """Test error when no config file exists"""
        empty_dir = tempfile.mkdtemp()
        try:
            with self.assertRaises(ValueError):
                TruffleProject(empty_dir)
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)
    
    def test_list_contracts(self):
        """Test listing contracts in project"""
        project = TruffleProject(self.test_path)
        contracts = project.list_contracts()
        
        self.assertEqual(len(contracts), 2)
        contract_names = [c.name for c in contracts]
        self.assertIn('Contract1.sol', contract_names)
        self.assertIn('Contract2.sol', contract_names)
    
    def test_list_contracts_empty(self):
        """Test listing contracts when directory is empty"""
        # Remove all contracts
        for contract in self.contracts_dir.glob('*.sol'):
            contract.unlink()
        
        project = TruffleProject(self.test_path)
        contracts = project.list_contracts()
        
        self.assertEqual(len(contracts), 0)


class TestContractFlattening(unittest.TestCase):
    """Test contract flattening functionality"""
    
    def setUp(self):
        """Create a sample Truffle project with imports"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create truffle config
        config_file = self.test_path / 'truffle-config.js'
        config_file.write_text('module.exports = {};')
        
        # Create contracts directory
        self.contracts_dir = self.test_path / 'contracts'
        self.contracts_dir.mkdir()
        
        # Create a base contract
        (self.contracts_dir / 'Base.sol').write_text(
            '// SPDX-License-Identifier: MIT\n'
            'pragma solidity ^0.8.0;\n\n'
            'contract Base {\n'
            '    uint256 public value;\n'
            '}\n'
        )
        
        # Create a derived contract with import
        (self.contracts_dir / 'Derived.sol').write_text(
            '// SPDX-License-Identifier: MIT\n'
            'pragma solidity ^0.8.0;\n\n'
            'import "./Base.sol";\n\n'
            'contract Derived is Base {\n'
            '    function setValue(uint256 _value) public {\n'
            '        value = _value;\n'
            '    }\n'
            '}\n'
        )
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_flatten_contract_with_imports(self):
        """Test flattening a contract with imports"""
        project = TruffleProject(self.test_path)
        derived_contract = self.contracts_dir / 'Derived.sol'
        
        flattened_path = project.flatten_contract(derived_contract)
        
        # Check that flattened file exists
        self.assertTrue(Path(flattened_path).exists())
        
        # Check that flattened content includes both contracts
        with open(flattened_path, 'r') as f:
            content = f.read()
            self.assertIn('contract Base', content)
            self.assertIn('contract Derived', content)
        
        # Clean up temporary flattened file
        Path(flattened_path).unlink()
    
    def test_flatten_contract_without_imports(self):
        """Test flattening a contract without imports"""
        project = TruffleProject(self.test_path)
        base_contract = self.contracts_dir / 'Base.sol'
        
        flattened_path = project.flatten_contract(base_contract)
        
        # Check that flattened file exists
        self.assertTrue(Path(flattened_path).exists())
        
        # Check that content is preserved
        with open(flattened_path, 'r') as f:
            content = f.read()
            self.assertIn('contract Base', content)
        
        # Clean up temporary flattened file
        Path(flattened_path).unlink()


if __name__ == '__main__':
    unittest.main()
