"""
env_helpers.py - Environment Variable and API Key Helpers
========================================================
Helpers to load API keys from environment variables.
No plain-text secrets should be committed.
"""

import os
from typing import Optional, Dict, Any


class EnvHelper:
    """Helper to load and validate environment variables."""
    
    @staticmethod
    def load_from_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Load value from environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Value or default
        """
        return os.environ.get(key, default)
    
    @staticmethod
    def load_api_keys() -> Dict[str, Optional[str]]:
        """
        Load API keys from environment variables.
        
        Returns:
            Dictionary with API keys
        """
        keys = {
            'binance_api_key': EnvHelper.load_from_env('BINANCE_API_KEY'),
            'binance_api_secret': EnvHelper.load_from_env('BINANCE_API_SECRET'),
            'alpaca_api_key': EnvHelper.load_from_env('ALPACA_API_KEY'),
            'alpaca_api_secret': EnvHelper.load_from_env('ALPACA_API_SECRET'),
        }
        return keys
    
    @staticmethod
    def validate_api_keys(required_keys: list) -> Dict[str, Any]:
        """
        Validate that required API keys are present.
        
        Args:
            required_keys: List of required key names
            
        Returns:
            Dictionary with validation results
        """
        all_keys = EnvHelper.load_api_keys()
        results = {
            'valid': True,
            'missing': [],
            'present': []
        }
        
        for key in required_keys:
            if key in all_keys and all_keys[key]:
                results['present'].append(key)
            else:
                results['missing'].append(key)
                results['valid'] = False
        
        return results
    
    @staticmethod
    def dry_run_connectivity_check() -> Dict[str, Any]:
        """
        Dry-run connectivity check (stub for now).
        In production, this would test API connectivity without making trades.
        
        Returns:
            Dictionary with connectivity status
        """
        # This is a placeholder for actual connectivity checks
        keys = EnvHelper.load_api_keys()
        
        results = {
            'binance': {
                'configured': bool(keys.get('binance_api_key')),
                'status': 'not_tested'
            },
            'alpaca': {
                'configured': bool(keys.get('alpaca_api_key')),
                'status': 'not_tested'
            }
        }
        
        return results
    
    @staticmethod
    def load_dotenv_if_available() -> bool:
        """
        Load .env file if python-dotenv is available.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return True
        except ImportError:
            return False
