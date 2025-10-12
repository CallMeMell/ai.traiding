"""
adapters - Broker API Abstraction Layer
=====================================
Unified interface for different broker APIs.
"""

from .base_adapter import BaseAdapter, AdapterStatus, OrderSide, OrderType
from .adapter_factory import AdapterFactory

# Register Binance adapter
try:
    from automation.brokers.binance import BinanceTestnetClient
    AdapterFactory.register('binance', BinanceTestnetClient)
except ImportError:
    pass  # Binance adapter not available

__all__ = ['BaseAdapter', 'AdapterStatus', 'OrderSide', 'OrderType', 'AdapterFactory']
