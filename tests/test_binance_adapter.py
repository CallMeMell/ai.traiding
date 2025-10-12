"""
test_binance_adapter.py - Binance Testnet Adapter Tests
======================================================
Tests for Binance Testnet adapter functionality.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.adapters.base_adapter import AdapterStatus, OrderSide, OrderType
from automation.brokers.binance import BinanceTestnetClient


class TestBinanceTestnetClient:
    """Test BinanceTestnetClient adapter."""
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        adapter = BinanceTestnetClient()
        
        assert adapter.testnet is True  # Should always be testnet
        assert adapter.status == AdapterStatus.DISCONNECTED
        assert adapter._client is None
    
    def test_adapter_forces_testnet(self):
        """Test that adapter always uses testnet mode."""
        # Even if we try to set testnet=False, it should force True
        adapter = BinanceTestnetClient(testnet=False)
        assert adapter.testnet is True
    
    def test_api_key_loading_from_env(self, test_env):
        """Test API key loading from environment."""
        os.environ['BINANCE_TESTNET_API_KEY'] = 'test_key'
        os.environ['BINANCE_TESTNET_SECRET_KEY'] = 'test_secret'
        
        adapter = BinanceTestnetClient()
        
        assert adapter.api_key == 'test_key'
        assert adapter.api_secret == 'test_secret'
    
    @patch('automation.brokers.binance.Client')
    def test_connect_success(self, mock_client_class):
        """Test successful connection."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        result = adapter.connect()
        
        assert result is True
        assert adapter.status == AdapterStatus.CONNECTED
        assert adapter._client is not None
        
        # Verify client was initialized with testnet=True
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs['testnet'] is True
    
    @patch('automation.brokers.binance.Client')
    def test_connect_with_api_key_validation(self, mock_client_class):
        """Test connection with API key validation."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_account.return_value = {'accountType': 'SPOT'}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient(api_key='test_key', api_secret='test_secret')
        result = adapter.connect()
        
        assert result is True
        mock_client.get_account.assert_called_once()
    
    @patch('automation.brokers.binance.Client')
    def test_connect_failure(self, mock_client_class):
        """Test connection failure."""
        mock_client_class.side_effect = Exception("Connection failed")
        
        adapter = BinanceTestnetClient()
        result = adapter.connect()
        
        assert result is False
        assert adapter.status == AdapterStatus.ERROR
    
    @patch('automation.brokers.binance.Client')
    def test_disconnect(self, mock_client_class):
        """Test disconnection."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        result = adapter.disconnect()
        
        assert result is True
        assert adapter.status == AdapterStatus.DISCONNECTED
        assert adapter._client is None
    
    @patch('automation.brokers.binance.Client')
    def test_health_check_success(self, mock_client_class):
        """Test successful health check."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_system_status.return_value = {'status': 0}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        result = adapter.health_check()
        
        assert result is True
        mock_client.ping.assert_called()
        mock_client.get_system_status.assert_called_once()
    
    @patch('automation.brokers.binance.Client')
    def test_health_check_not_connected(self, mock_client_class):
        """Test health check when not connected."""
        adapter = BinanceTestnetClient()
        
        result = adapter.health_check()
        
        assert result is False
    
    @patch('automation.brokers.binance.Client')
    def test_health_check_system_status_abnormal(self, mock_client_class):
        """Test health check with abnormal system status."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_system_status.return_value = {'status': 1}  # Abnormal
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        result = adapter.health_check()
        
        assert result is False
    
    @patch('automation.brokers.binance.Client')
    def test_get_account_balance(self, mock_client_class):
        """Test getting account balance."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_account.return_value = {
            'balances': [
                {'asset': 'USDT', 'free': '1000.00', 'locked': '100.00'},
                {'asset': 'BTC', 'free': '0.5', 'locked': '0.0'}
            ]
        }
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        balance = adapter.get_account_balance()
        
        assert 'total' in balance
        assert 'available' in balance
        assert balance['total'] == 1100.0
        assert balance['available'] == 1000.0
        assert balance['currency'] == 'USDT'
    
    @patch('automation.brokers.binance.Client')
    def test_get_market_price(self, mock_client_class):
        """Test getting market price."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_symbol_ticker.return_value = {'price': '50000.50'}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        price = adapter.get_market_price('BTCUSDT')
        
        assert price == 50000.50
        mock_client.get_symbol_ticker.assert_called_once_with(symbol='BTCUSDT')
    
    @patch('automation.brokers.binance.Client')
    def test_place_order_dry_run(self, mock_client_class, test_env):
        """Test placing order in dry-run mode."""
        os.environ['DRY_RUN'] = 'true'
        
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_symbol_ticker.return_value = {'price': '50000.00'}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        order = adapter.place_order(
            'BTCUSDT',
            OrderSide.BUY,
            OrderType.MARKET,
            0.001
        )
        
        assert 'order_id' in order
        assert order['order_id'].startswith('DRY_RUN_')
        assert order['status'] == 'filled'
        assert order['dry_run'] is True
        assert order['symbol'] == 'BTCUSDT'
        assert order['side'] == 'buy'
        assert order['quantity'] == 0.001
    
    @patch('automation.brokers.binance.Client')
    def test_place_order_real_mode_blocked(self, mock_client_class, test_env):
        """Test that real order placement is blocked."""
        os.environ['DRY_RUN'] = 'false'
        
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        order = adapter.place_order(
            'BTCUSDT',
            OrderSide.BUY,
            OrderType.MARKET,
            0.001
        )
        
        assert 'error' in order
        assert order['status'] == 'failed'
    
    @patch('automation.brokers.binance.Client')
    def test_get_order_status_dry_run(self, mock_client_class):
        """Test getting order status for dry-run order."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        status = adapter.get_order_status('DRY_RUN_20231010120000')
        
        assert status['order_id'] == 'DRY_RUN_20231010120000'
        assert status['status'] == 'filled'
        assert status['dry_run'] is True
    
    @patch('automation.brokers.binance.Client')
    def test_cancel_order_dry_run(self, mock_client_class):
        """Test cancelling dry-run order."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        result = adapter.cancel_order('DRY_RUN_20231010120000')
        
        assert result is True
    
    @patch('automation.brokers.binance.Client')
    def test_get_open_orders(self, mock_client_class):
        """Test getting open orders (empty in dry-run)."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        orders = adapter.get_open_orders('BTCUSDT')
        
        assert orders == []
    
    @patch('automation.brokers.binance.Client')
    def test_get_historical_data(self, mock_client_class):
        """Test getting historical data."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_klines.return_value = [
            [1633046400000, '50000', '51000', '49000', '50500', '100'],
            [1633050000000, '50500', '51500', '50000', '51000', '150']
        ]
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        data = adapter.get_historical_data('BTCUSDT', '1h', limit=2)
        
        assert len(data) == 2
        assert 'timestamp' in data[0]
        assert 'open' in data[0]
        assert 'high' in data[0]
        assert 'low' in data[0]
        assert 'close' in data[0]
        assert 'volume' in data[0]
    
    @patch('automation.brokers.binance.Client')
    def test_adapter_info(self, mock_client_class):
        """Test getting adapter information."""
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        adapter.connect()
        
        info = adapter.get_adapter_info()
        
        assert info['name'] == 'BinanceTestnetClient'
        assert info['status'] == 'connected'
        assert info['testnet'] is True
        assert info['connected'] is True


class TestBinanceAdapterIntegration:
    """Integration tests for Binance adapter."""
    
    @patch('automation.brokers.binance.Client')
    def test_full_workflow(self, mock_client_class, test_env):
        """Test complete workflow: connect, check health, place order, disconnect."""
        os.environ['DRY_RUN'] = 'true'
        
        mock_client = Mock()
        mock_client.ping.return_value = {}
        mock_client.get_system_status.return_value = {'status': 0}
        mock_client.get_symbol_ticker.return_value = {'price': '50000.00'}
        mock_client_class.return_value = mock_client
        
        adapter = BinanceTestnetClient()
        
        # Connect
        assert adapter.connect() is True
        
        # Health check
        assert adapter.health_check() is True
        
        # Place order
        order = adapter.place_order('BTCUSDT', OrderSide.BUY, OrderType.MARKET, 0.001)
        assert order['status'] == 'filled'
        assert order['dry_run'] is True
        
        # Disconnect
        assert adapter.disconnect() is True
    
    def test_no_api_keys_required_for_initialization(self):
        """Test that adapter can be initialized without API keys."""
        adapter = BinanceTestnetClient()
        assert adapter is not None
        assert adapter.status == AdapterStatus.DISCONNECTED
