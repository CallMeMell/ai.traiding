"""
test_config.py - Configuration Manager Tests
==========================================
Tests for configuration management system.
"""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.config.manager import ConfigManager


class TestConfigManager:
    """Test configuration manager."""
    
    def test_config_manager_initialization(self):
        """Test config manager initialization."""
        manager = ConfigManager()
        
        assert manager.get('DRY_RUN') is True  # Default value
        assert manager.get('BROKER_NAME') == 'binance'
    
    def test_get_default_value(self):
        """Test getting with default value."""
        manager = ConfigManager()
        
        value = manager.get('NONEXISTENT', default='default_value')
        
        assert value == 'default_value'
    
    def test_set_value(self):
        """Test setting a value."""
        manager = ConfigManager()
        
        manager.set('NEW_KEY', 'new_value')
        
        assert manager.get('NEW_KEY') == 'new_value'
    
    def test_get_all(self):
        """Test getting all configuration."""
        manager = ConfigManager()
        
        all_config = manager.get_all()
        
        assert isinstance(all_config, dict)
        assert 'DRY_RUN' in all_config
        assert 'BROKER_NAME' in all_config
    
    def test_load_from_env(self, test_env):
        """Test loading from environment variables."""
        # Set test environment variable
        os.environ['TEST_CONFIG'] = 'test_value'
        
        manager = ConfigManager()
        manager.config['TEST_CONFIG'] = None  # Add to config keys
        manager._load_from_env()
        
        assert manager.get('TEST_CONFIG') == 'test_value'
    
    def test_load_from_file(self, temp_dir):
        """Test loading from JSON file."""
        # Create temp config file
        config_file = os.path.join(temp_dir, 'test_config.json')
        config_data = {
            'TEST_KEY': 'test_value',
            'TEST_NUMBER': 42
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        manager = ConfigManager(config_file=config_file)
        
        assert manager.get('TEST_KEY') == 'test_value'
        assert manager.get('TEST_NUMBER') == 42
    
    def test_save_config(self, temp_dir):
        """Test saving configuration."""
        manager = ConfigManager()
        manager.set('TEST_KEY', 'test_value')
        
        config_file = os.path.join(temp_dir, 'saved_config.json')
        manager.save(config_file)
        
        # Verify file exists and can be loaded
        assert os.path.exists(config_file)
        
        with open(config_file, 'r') as f:
            loaded = json.load(f)
            assert loaded['TEST_KEY'] == 'test_value'
    
    def test_validate_config(self):
        """Test configuration validation."""
        manager = ConfigManager()
        
        is_valid = manager.validate()
        
        assert is_valid is True
    
    def test_boolean_env_conversion(self, test_env):
        """Test boolean environment variable conversion."""
        os.environ['BOOL_TRUE'] = 'true'
        os.environ['BOOL_FALSE'] = 'false'
        
        manager = ConfigManager()
        manager.config['BOOL_TRUE'] = None
        manager.config['BOOL_FALSE'] = None
        manager._load_from_env()
        
        assert manager.get('BOOL_TRUE') is True
        assert manager.get('BOOL_FALSE') is False
    
    def test_numeric_env_conversion(self, test_env):
        """Test numeric environment variable conversion."""
        os.environ['NUMBER'] = '42'
        
        manager = ConfigManager()
        manager.config['NUMBER'] = None
        manager._load_from_env()
        
        assert manager.get('NUMBER') == 42
        assert isinstance(manager.get('NUMBER'), int)
