"""
test_adapters.py - Adapter System Tests
======================================
Tests for broker adapter system.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.adapters.base_adapter import BaseAdapter, AdapterStatus, OrderSide, OrderType
from system.adapters.adapter_factory import AdapterFactory


class TestBaseAdapter:
    """Test BaseAdapter class."""
    
    def test_adapter_status_enum(self):
        """Test AdapterStatus enum."""
        assert AdapterStatus.DISCONNECTED.value == "disconnected"
        assert AdapterStatus.CONNECTING.value == "connecting"
        assert AdapterStatus.CONNECTED.value == "connected"
        assert AdapterStatus.ERROR.value == "error"
    
    def test_order_type_enum(self):
        """Test OrderType enum."""
        assert OrderType.MARKET.value == "market"
        assert OrderType.LIMIT.value == "limit"
        assert OrderType.STOP.value == "stop"
        assert OrderType.STOP_LIMIT.value == "stop_limit"
    
    def test_order_side_enum(self):
        """Test OrderSide enum."""
        assert OrderSide.BUY.value == "buy"
        assert OrderSide.SELL.value == "sell"
    
    def test_mock_adapter(self, mock_adapter):
        """Test mock adapter functionality."""
        # Connect
        assert mock_adapter.connect() is True
        assert mock_adapter.status == AdapterStatus.CONNECTED
        
        # Get balance
        balance = mock_adapter.get_account_balance()
        assert 'total' in balance
        assert balance['total'] > 0
        
        # Get price
        price = mock_adapter.get_market_price('BTCUSDT')
        assert price > 0
        
        # Place order
        order = mock_adapter.place_order(
            'BTCUSDT',
            OrderSide.BUY,
            OrderType.MARKET,
            0.001
        )
        assert 'order_id' in order
        assert order['status'] == 'filled'
        
        # Disconnect
        assert mock_adapter.disconnect() is True
        assert mock_adapter.status == AdapterStatus.DISCONNECTED
    
    def test_adapter_info(self, mock_adapter):
        """Test adapter info."""
        mock_adapter.connect()
        info = mock_adapter.get_adapter_info()
        
        assert 'name' in info
        assert 'status' in info
        assert 'testnet' in info
        assert 'connected' in info
        assert info['connected'] is True


class TestAdapterFactory:
    """Test AdapterFactory class."""
    
    def test_register_adapter(self, mock_adapter):
        """Test adapter registration."""
        AdapterFactory.register('mock', mock_adapter.__class__)
        
        adapters = AdapterFactory.list_adapters()
        assert 'mock' in adapters
    
    def test_create_adapter(self, mock_adapter):
        """Test adapter creation."""
        AdapterFactory.register('mock', mock_adapter.__class__)
        
        adapter = AdapterFactory.create('mock', testnet=True)
        assert isinstance(adapter, BaseAdapter)
        assert adapter.testnet is True
    
    def test_create_unknown_adapter(self):
        """Test creating unknown adapter raises error."""
        with pytest.raises(ValueError, match="Adapter 'unknown' not found"):
            AdapterFactory.create('unknown')
    
    def test_list_adapters(self, mock_adapter):
        """Test listing adapters."""
        AdapterFactory.register('mock', mock_adapter.__class__)
        
        adapters = AdapterFactory.list_adapters()
        assert isinstance(adapters, list)
        assert 'mock' in adapters
