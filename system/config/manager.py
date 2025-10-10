"""
manager.py - Configuration Manager
=================================
Centralized configuration management with validation.
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """
    Manage system configuration.
    
    Loads configuration from multiple sources:
    1. Environment variables
    2. .env file
    3. JSON configuration files
    4. Windows Credential Manager (for sensitive data)
    """
    
    DEFAULT_CONFIG = {
        'DRY_RUN': True,
        'BROKER_NAME': 'binance',
        'BINANCE_BASE_URL': 'https://testnet.binance.vision',
        'LOG_LEVEL': 'INFO',
        'LOG_DIR': 'logs',
        'DATA_DIR': 'data',
        'SESSION_DIR': 'data/session',
        'MAX_LOG_SIZE_MB': 10,
        'LOG_BACKUP_COUNT': 5,
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to JSON config file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            self.config.update(file_config)
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        for key in self.config.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                # Convert boolean strings
                if env_value.lower() in ('true', 'false'):
                    self.config[key] = env_value.lower() == 'true'
                # Convert numeric strings
                elif env_value.isdigit():
                    self.config[key] = int(env_value)
                else:
                    self.config[key] = env_value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def save(self, config_file: str) -> None:
        """
        Save configuration to file.
        
        Args:
            config_file: Path to save configuration
        """
        # Create directory if needed
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if valid, False otherwise
        """
        # Check required directories exist or can be created
        for dir_key in ['LOG_DIR', 'DATA_DIR', 'SESSION_DIR']:
            dir_path = self.get(dir_key)
            if dir_path:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception:
                    return False
        
        # Validate DRY_RUN is boolean
        if not isinstance(self.get('DRY_RUN'), bool):
            return False
        
        return True
