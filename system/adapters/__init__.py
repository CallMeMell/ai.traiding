"""
adapters - Broker API Abstraction Layer
=====================================
Unified interface for different broker APIs.
"""

from .base_adapter import BaseAdapter, AdapterStatus
from .adapter_factory import AdapterFactory

__all__ = ['BaseAdapter', 'AdapterStatus', 'AdapterFactory']
