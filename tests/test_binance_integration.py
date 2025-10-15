"""
Tests for binance_integration.py

Tests cover:
- BinanceDataProvider initialization
- Rate limiting functionality
- Historical data fetching
- Current price retrieval
- Error handling
- PaperTradingExecutor
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import time

# Import the module to test
try:
    from binance_integration import (
        BinanceDataProvider,
        PaperTradingExecutor,
        BINANCE_AVAILABLE
    )
    BINANCE_INTEGRATION_AVAILABLE = True
except ImportError:
    BINANCE_INTEGRATION_AVAILABLE = False
    print("Warning: binance_integration module not available")


@unittest.skipIf(not BINANCE_INTEGRATION_AVAILABLE, "binance_integration not available")
class TestBinanceDataProvider(unittest.TestCase):
    """Tests for BinanceDataProvider class"""
    
    @patch('binance_integration.Client')
    def test_initialization_testnet(self, mock_client):
        """Test initialization in testnet mode"""
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        self.assertEqual(provider.api_key, 'test_key')
        self.assertEqual(provider.api_secret, 'test_secret')
        self.assertTrue(provider.testnet)
        self.assertIsNotNone(provider.client)
    
    @patch('binance_integration.Client')
    def test_initialization_production(self, mock_client):
        """Test initialization in production mode"""
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=False
        )
        
        self.assertFalse(provider.testnet)
        self.assertIsNotNone(provider.client)
    
    @patch('binance_integration.Client')
    def test_rate_limit_check_enforces_delay(self, mock_client):
        """Test that rate limiter enforces minimum delay"""
        provider = BinanceDataProvider(testnet=True)
        
        # First call - should not sleep
        start_time = time.time()
        provider._rate_limit_check()
        first_call_time = time.time() - start_time
        
        # Should be very fast (no sleep)
        self.assertLess(first_call_time, 0.05)
        
        # Immediate second call - should sleep
        start_time = time.time()
        provider._rate_limit_check()
        second_call_time = time.time() - start_time
        
        # Should have slept for approximately min_request_interval
        self.assertGreaterEqual(second_call_time, provider.min_request_interval - 0.05)
    
    @patch('binance_integration.Client')
    def test_get_current_price_success(self, mock_client):
        """Test successful current price retrieval"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get_symbol_ticker.return_value = {'price': '50000.50'}
        
        provider = BinanceDataProvider(testnet=True)
        provider.last_request_time = 0  # Reset to avoid rate limit
        
        price = provider.get_current_price('BTCUSDT')
        
        self.assertEqual(price, 50000.50)
        mock_client_instance.get_symbol_ticker.assert_called_once_with(symbol='BTCUSDT')
    
    @patch('binance_integration.Client')
    @patch('binance_integration.BinanceAPIException')
    def test_get_current_price_api_error(self, mock_exception, mock_client):
        """Test handling of API error when getting price"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get_symbol_ticker.side_effect = Exception("API Error")
        
        provider = BinanceDataProvider(testnet=True)
        provider.last_request_time = 0
        
        price = provider.get_current_price('BTCUSDT')
        
        self.assertEqual(price, 0.0)  # Should return 0.0 on error
    
    @patch('binance_integration.Client')
    def test_get_historical_klines_success(self, mock_client):
        """Test successful historical klines retrieval"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock klines data
        mock_klines = [
            [1640000000000, '50000', '51000', '49000', '50500', '100', 
             1640003600000, '5000000', 1000, '50', '2500000', '0'],
            [1640003600000, '50500', '52000', '50000', '51500', '110',
             1640007200000, '5500000', 1100, '55', '2750000', '0']
        ]
        mock_client_instance.get_historical_klines.return_value = mock_klines
        
        provider = BinanceDataProvider(testnet=True)
        provider.last_request_time = 0
        
        df = provider.get_historical_klines('BTCUSDT', '1h', days_back=1)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertIn('open', df.columns)
        self.assertIn('high', df.columns)
        self.assertIn('low', df.columns)
        self.assertIn('close', df.columns)
        self.assertIn('volume', df.columns)
    
    @patch('binance_integration.Client')
    def test_test_connection_success(self, mock_client):
        """Test successful connection test"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.ping.return_value = {}
        
        provider = BinanceDataProvider(testnet=True)
        
        result = provider.test_connection()
        
        self.assertTrue(result)
    
    @patch('binance_integration.Client')
    def test_test_connection_failure(self, mock_client):
        """Test connection test failure"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.ping.side_effect = Exception("Connection failed")
        
        provider = BinanceDataProvider(testnet=True)
        
        result = provider.test_connection()
        
        self.assertFalse(result)
    
    @patch('binance_integration.Client')
    def test_get_account_balance_success(self, mock_client):
        """Test successful account balance retrieval"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get_asset_balance.return_value = {
            'asset': 'USDT',
            'free': '10000.50',
            'locked': '100.00'
        }
        
        provider = BinanceDataProvider(testnet=True)
        
        balance = provider.get_account_balance('USDT')
        
        self.assertEqual(balance, 10000.50)
    
    @patch('binance_integration.Client')
    def test_close_cleanup(self, mock_client):
        """Test that close() properly cleans up"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        provider = BinanceDataProvider(testnet=True)
        provider.close()
        
        # Should not raise any errors
        self.assertIsNone(provider.client)


@unittest.skipIf(not BINANCE_INTEGRATION_AVAILABLE, "binance_integration not available")
class TestPaperTradingExecutor(unittest.TestCase):
    """Tests for PaperTradingExecutor class"""
    
    def test_initialization(self):
        """Test executor initialization"""
        executor = PaperTradingExecutor(initial_capital=20000.0)
        
        self.assertEqual(executor.cash, 20000.0)
        self.assertEqual(executor.initial_capital, 20000.0)
        self.assertEqual(len(executor.positions), 0)
        self.assertEqual(len(executor.orders), 0)
    
    def test_buy_creates_position(self):
        """Test that buy creates a position"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.buy('BTCUSDT', 0.1, 50000.0)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('order_id', result)
        self.assertTrue(executor.has_position('BTCUSDT'))
        
        position = executor.get_position('BTCUSDT')
        self.assertEqual(position['quantity'], 0.1)
        self.assertEqual(position['entry_price'], 50000.0)
    
    def test_buy_insufficient_funds(self):
        """Test buy with insufficient funds"""
        executor = PaperTradingExecutor(initial_capital=1000.0)
        
        result = executor.buy('BTCUSDT', 1.0, 50000.0)  # Costs 50000
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('insufficient funds', result['message'].lower())
    
    def test_sell_with_position(self):
        """Test selling an existing position"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        # First buy
        executor.buy('BTCUSDT', 0.1, 50000.0)
        
        # Then sell at higher price
        result = executor.sell('BTCUSDT', 52000.0)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('pnl', result)
        self.assertGreater(result['pnl'], 0)  # Should have profit
        self.assertFalse(executor.has_position('BTCUSDT'))
    
    def test_sell_without_position(self):
        """Test selling without position"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.sell('BTCUSDT', 50000.0)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('no position', result['message'].lower())
    
    def test_get_portfolio_value(self):
        """Test portfolio value calculation"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        # Buy some assets
        executor.buy('BTCUSDT', 0.1, 50000.0)  # Costs 5000
        
        # Portfolio value with current prices
        current_prices = {'BTCUSDT': 52000.0}
        portfolio_value = executor.get_portfolio_value(current_prices)
        
        # Should be: remaining cash + position value
        # Cash: 5000, Position: 0.1 * 52000 = 5200
        expected_value = 5000.0 + 5200.0
        self.assertAlmostEqual(portfolio_value, expected_value, places=2)
    
    def test_get_performance_summary(self):
        """Test performance summary generation"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        # Execute some trades
        executor.buy('BTCUSDT', 0.1, 50000.0)
        executor.sell('BTCUSDT', 52000.0)  # Profit trade
        
        summary = executor.get_performance_summary()
        
        self.assertIn('total_trades', summary)
        self.assertIn('winning_trades', summary)
        self.assertIn('total_pnl', summary)
        self.assertIn('win_rate', summary)
        self.assertEqual(summary['total_trades'], 1)
        self.assertEqual(summary['winning_trades'], 1)
        self.assertGreater(summary['total_pnl'], 0)
    
    def test_close_position_with_profit(self):
        """Test closing position with profit"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        executor.buy('BTCUSDT', 0.1, 50000.0)
        result = executor.close_position('BTCUSDT', 55000.0)
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(result['pnl'], 0)
        self.assertGreater(result['pnl_percentage'], 0)
        self.assertFalse(executor.has_position('BTCUSDT'))
    
    def test_close_position_with_loss(self):
        """Test closing position with loss"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        executor.buy('BTCUSDT', 0.1, 50000.0)
        result = executor.close_position('BTCUSDT', 48000.0)
        
        self.assertEqual(result['status'], 'success')
        self.assertLess(result['pnl'], 0)
        self.assertLess(result['pnl_percentage'], 0)
    
    def test_get_open_orders(self):
        """Test getting open orders"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        executor.buy('BTCUSDT', 0.1, 50000.0)
        
        orders = executor.get_open_orders('BTCUSDT')
        
        self.assertIsInstance(orders, list)
        # Paper trading doesn't keep open orders after execution
        # but the method should work
    
    def test_get_account_balance(self):
        """Test getting account balance"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        balance = executor.get_account_balance('USDT')
        
        self.assertIn('free', balance)
        self.assertIn('total', balance)
        self.assertEqual(balance['free'], 10000.0)


@unittest.skipIf(not BINANCE_INTEGRATION_AVAILABLE, "binance_integration not available")
class TestPaperTradingExecutorEdgeCases(unittest.TestCase):
    """Test edge cases for PaperTradingExecutor"""
    
    def test_multiple_positions(self):
        """Test handling multiple positions"""
        executor = PaperTradingExecutor(initial_capital=50000.0)
        
        executor.buy('BTCUSDT', 0.1, 50000.0)
        executor.buy('ETHUSDT', 1.0, 3000.0)
        
        self.assertTrue(executor.has_position('BTCUSDT'))
        self.assertTrue(executor.has_position('ETHUSDT'))
        
        btc_pos = executor.get_position('BTCUSDT')
        eth_pos = executor.get_position('ETHUSDT')
        
        self.assertIsNotNone(btc_pos)
        self.assertIsNotNone(eth_pos)
    
    def test_buy_same_symbol_twice(self):
        """Test buying the same symbol twice (should reject)"""
        executor = PaperTradingExecutor(initial_capital=20000.0)
        
        # First buy
        result1 = executor.buy('BTCUSDT', 0.1, 50000.0)
        self.assertEqual(result1['status'], 'success')
        
        # Second buy of same symbol
        result2 = executor.buy('BTCUSDT', 0.1, 50000.0)
        self.assertEqual(result2['status'], 'error')
        self.assertIn('already have', result2['message'].lower())
    
    def test_sell_updates_cash_correctly(self):
        """Test that selling updates cash balance correctly"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        initial_cash = executor.cash
        
        # Buy
        executor.buy('BTCUSDT', 0.1, 50000.0)
        after_buy_cash = executor.cash
        
        self.assertEqual(after_buy_cash, initial_cash - 5000.0)
        
        # Sell at same price (no profit/loss)
        executor.sell('BTCUSDT', 50000.0)
        after_sell_cash = executor.cash
        
        # Should get back approximately the same (minus small fees if any)
        self.assertAlmostEqual(after_sell_cash, initial_cash, places=0)
    
    def test_zero_quantity_buy(self):
        """Test buying with zero quantity"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.buy('BTCUSDT', 0.0, 50000.0)
        
        self.assertEqual(result['status'], 'error')
    
    def test_negative_price(self):
        """Test handling negative price"""
        executor = PaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.buy('BTCUSDT', 0.1, -50000.0)
        
        self.assertEqual(result['status'], 'error')


@unittest.skipIf(not BINANCE_INTEGRATION_AVAILABLE, "binance_integration not available")
class TestBinanceDataProviderAdditional(unittest.TestCase):
    """Additional tests for BinanceDataProvider"""
    
    @patch('binance_integration.Client')
    def test_get_symbol_info(self, mock_client_class):
        """Test getting symbol information"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock symbol info response
        mock_client.get_symbol_info.return_value = {
            'symbol': 'BTCUSDT',
            'status': 'TRADING',
            'baseAsset': 'BTC',
            'quoteAsset': 'USDT',
            'pricePrecision': 2,
            'quantityPrecision': 6,
            'filters': [
                {
                    'filterType': 'LOT_SIZE',
                    'minQty': '0.00001',
                    'maxQty': '9000',
                    'stepSize': '0.00001'
                },
                {
                    'filterType': 'MIN_NOTIONAL',
                    'minNotional': '10.0'
                }
            ]
        }
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        info = provider.get_symbol_info('BTCUSDT')
        
        self.assertEqual(info['symbol'], 'BTCUSDT')
        self.assertEqual(info['baseAsset'], 'BTC')
        self.assertGreater(info['minQty'], 0)
    
    @patch('binance_integration.Client')
    def test_get_symbol_info_error(self, mock_client_class):
        """Test handling symbol info error"""
        from binance.exceptions import BinanceAPIException
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Simulate API error
        mock_client.get_symbol_info.side_effect = BinanceAPIException(
            response=MagicMock(status_code=400),
            status_code=400,
            text='{"code": -1121, "msg": "Invalid symbol"}'
        )
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        with self.assertRaises(Exception):
            provider.get_symbol_info('INVALID')
    
    @patch('binance_integration.Client')
    def test_get_account_balance_error(self, mock_client_class):
        """Test handling balance error"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Simulate error
        mock_client.get_asset_balance.side_effect = Exception("Connection error")
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        balance = provider.get_account_balance('USDT')
        
        # Should return 0.0 on error
        self.assertEqual(balance, 0.0)
    
    @patch('binance_integration.Client')
    def test_get_account_balance_not_found(self, mock_client_class):
        """Test getting balance for asset not in account"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Return None for asset not found
        mock_client.get_asset_balance.return_value = None
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        balance = provider.get_account_balance('UNKNOWN')
        
        # Should return 0.0 for unknown asset
        self.assertEqual(balance, 0.0)
    
    @patch('binance_integration.Client')
    def test_close_with_websocket(self, mock_client_class):
        """Test closing provider with WebSocket manager"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        # Mock WebSocket manager
        mock_ws = MagicMock()
        provider.ws_manager = mock_ws
        
        # Close provider
        provider.close()
        
        # Verify WebSocket was stopped
        mock_ws.stop.assert_called_once()
        self.assertIsNone(provider.ws_manager)
    
    @patch('binance_integration.Client')
    def test_close_without_websocket(self, mock_client_class):
        """Test closing provider without WebSocket manager"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        # Ensure ws_manager is None
        provider.ws_manager = None
        
        # Should not raise error
        provider.close()
    
    @patch('binance_integration.Client')
    def test_get_historical_klines_error_handling(self, mock_client_class):
        """Test error handling in get_historical_klines"""
        from binance.exceptions import BinanceAPIException
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Simulate API error
        mock_client.get_historical_klines.side_effect = BinanceAPIException(
            response=MagicMock(status_code=500),
            status_code=500,
            text='{"code": -1001, "msg": "Internal error"}'
        )
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        with self.assertRaises(Exception):
            provider.get_historical_klines('BTCUSDT', '1h')
    
    @patch('binance_integration.Client')
    def test_get_historical_klines_empty_result(self, mock_client_class):
        """Test handling empty klines result"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Return empty list
        mock_client.get_historical_klines.return_value = []
        
        provider = BinanceDataProvider(
            api_key='test_key',
            api_secret='test_secret',
            testnet=True
        )
        
        df = provider.get_historical_klines('BTCUSDT', '1h')
        
        # Should return empty DataFrame
        self.assertTrue(df.empty)
    
    @patch('binance_integration.Client')
    def test_initialization_without_binance(self, mock_client_class):
        """Test initialization behavior"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Test with default parameters (from env)
        provider = BinanceDataProvider()
        
        self.assertIsNotNone(provider.client)


if __name__ == '__main__':
    unittest.main()
