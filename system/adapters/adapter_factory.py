"""
adapter_factory.py - Adapter Factory
===================================
Factory for creating broker adapters.
"""

from typing import Optional, Dict, Any
import logging
from .base_adapter import BaseAdapter

logger = logging.getLogger(__name__)


class AdapterFactory:
    """Factory for creating broker adapters."""
    
    _adapters: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, adapter_class: type):
        """
        Register an adapter.
        
        Args:
            name: Adapter name (e.g., 'binance', 'alpaca')
            adapter_class: Adapter class
        """
        cls._adapters[name.lower()] = adapter_class
        logger.info(f"Registered adapter: {name}")
    
    @classmethod
    def create(cls, name: str, 
               api_key: Optional[str] = None,
               api_secret: Optional[str] = None,
               testnet: bool = True,
               **kwargs) -> BaseAdapter:
        """
        Create an adapter instance.
        
        Args:
            name: Adapter name
            api_key: API key (optional)
            api_secret: API secret (optional)
            testnet: Use testnet
            **kwargs: Additional adapter-specific arguments
            
        Returns:
            Adapter instance
            
        Raises:
            ValueError: If adapter not found
        """
        adapter_class = cls._adapters.get(name.lower())
        
        if adapter_class is None:
            available = ', '.join(cls._adapters.keys())
            raise ValueError(
                f"Adapter '{name}' not found. Available: {available}"
            )
        
        logger.info(f"Creating adapter: {name} (testnet={testnet})")
        return adapter_class(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
            **kwargs
        )
    
    @classmethod
    def list_adapters(cls) -> list:
        """
        List available adapters.
        
        Returns:
            List of adapter names
        """
        return list(cls._adapters.keys())
