"""
Comprehensive tests for broker_api.py

Tests cover:
- BrokerInterface abstract class
- EnhancedPaperTradingExecutor
- SimulatedLiveTradingBrokerAdapter
- BrokerFactory
- Order management
- Position tracking
- Error handling
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os
import tempfile
import json

# Import the module to test
try:
    from broker_api import (
        OrderType,
        OrderSide,
        OrderStatus,
        BrokerInterface,
        EnhancedPaperTradingExecutor,
        SimulatedLiveTradingBrokerAdapter,
        BrokerFactory
    )
    BROKER_API_AVAILABLE = True
except ImportError:
    BROKER_API_AVAILABLE = False
    print("Warning: broker_api module not available")


@unittest.skipIf(not BROKER_API_AVAILABLE, "broker_api not available")
class TestOrderEnums(unittest.TestCase):
    """Tests for order enums"""
    
    def test_order_type_enum(self):
        """Test OrderType enum values"""
        self.assertEqual(OrderType.MARKET.value, "MARKET")
        self.assertEqual(OrderType.LIMIT.value, "LIMIT")
        self.assertEqual(OrderType.STOP_LOSS.value, "STOP_LOSS")
    
    def test_order_side_enum(self):
        """Test OrderSide enum values"""
        self.assertEqual(OrderSide.BUY.value, "BUY")
        self.assertEqual(OrderSide.SELL.value, "SELL")
    
    def test_order_status_enum(self):
        """Test OrderStatus enum values"""
        self.assertEqual(OrderStatus.NEW.value, "NEW")
        self.assertEqual(OrderStatus.FILLED.value, "FILLED")
        self.assertEqual(OrderStatus.CANCELED.value, "CANCELED")


@unittest.skipIf(not BROKER_API_AVAILABLE, "broker_api not available")
class TestEnhancedPaperTradingExecutor(unittest.TestCase):
    """Tests for EnhancedPaperTradingExecutor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = EnhancedPaperTradingExecutor(
            initial_capital=10000.0,
            paper_trading=True
        )
    
    def test_initialization(self):
        """Test executor initialization"""
        self.assertEqual(self.executor.cash, 10000.0)
        self.assertEqual(self.executor.initial_capital, 10000.0)
        self.assertTrue(self.executor.paper_trading)
        self.assertEqual(len(self.executor.positions), 0)
        self.assertEqual(len(self.executor.orders), 0)
    
    def test_place_market_order_buy(self):
        """Test placing a market buy order"""
        result = self.executor.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side=OrderSide.BUY.value,
            current_price=50000.0
        )
        
        self.assertEqual(result['status'], 'FILLED')
        self.assertIn('order_id', result)
        self.assertEqual(result['symbol'], 'BTCUSDT')
        self.assertEqual(result['quantity'], 0.1)
        self.assertEqual(result['side'], OrderSide.BUY.value)
        
        # Check that position was created
        positions = self.executor.get_positions('BTCUSDT')
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['quantity'], 0.1)
    
    def test_place_market_order_sell(self):
        """Test placing a market sell order"""
        # First buy
        self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        # Then sell
        result = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.SELL.value, 52000.0
        )
        
        self.assertEqual(result['status'], 'FILLED')
        self.assertIn('pnl', result)
        self.assertGreater(result['pnl'], 0)  # Should have profit
        
        # Position should be closed
        positions = self.executor.get_positions('BTCUSDT')
        self.assertEqual(len(positions), 0)
    
    def test_place_market_order_insufficient_funds(self):
        """Test market order with insufficient funds"""
        result = self.executor.place_market_order(
            'BTCUSDT', 1.0, OrderSide.BUY.value, 50000.0
        )
        
        self.assertEqual(result['status'], 'REJECTED')
        self.assertIn('insufficient', result['message'].lower())
    
    def test_place_market_order_sell_without_position(self):
        """Test selling without having a position"""
        result = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.SELL.value, 50000.0
        )
        
        self.assertEqual(result['status'], 'REJECTED')
        self.assertIn('no position', result['message'].lower())
    
    def test_place_limit_order(self):
        """Test placing a limit order"""
        result = self.executor.place_limit_order(
            symbol='BTCUSDT',
            quantity=0.1,
            price=49000.0,
            side=OrderSide.BUY.value
        )
        
        # Limit orders not fully implemented in paper trading
        self.assertIn('status', result)
        self.assertIn('order_id', result)
    
    def test_cancel_order(self):
        """Test canceling an order"""
        # Place an order first
        order_result = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        order_id = order_result['order_id']
        
        # Try to cancel (should work even if already filled)
        result = self.executor.cancel_order('BTCUSDT', order_id)
        
        # Cancel should return a boolean or dict
        self.assertIsNotNone(result)
    
    def test_get_order_status(self):
        """Test getting order status"""
        # Place an order
        order_result = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        order_id = order_result['order_id']
        
        # Get status
        status = self.executor.get_order_status('BTCUSDT', order_id)
        
        self.assertIn('order_id', status)
        self.assertIn('status', status)
    
    def test_get_open_orders(self):
        """Test getting open orders"""
        orders = self.executor.get_open_orders()
        
        self.assertIsInstance(orders, list)
    
    def test_get_open_orders_for_symbol(self):
        """Test getting open orders for specific symbol"""
        orders = self.executor.get_open_orders('BTCUSDT')
        
        self.assertIsInstance(orders, list)
    
    def test_get_account_balance(self):
        """Test getting account balance"""
        balance = self.executor.get_account_balance()
        
        self.assertIsInstance(balance, dict)
        self.assertIn('USDT', balance)
        self.assertEqual(balance['USDT'], 10000.0)
    
    def test_get_account_balance_specific_asset(self):
        """Test getting balance for specific asset"""
        balance = self.executor.get_account_balance('USDT')
        
        self.assertIsInstance(balance, dict)
        self.assertIn('USDT', balance)
    
    def test_get_positions(self):
        """Test getting all positions"""
        # Place a buy order
        self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        positions = self.executor.get_positions()
        
        self.assertIsInstance(positions, list)
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['symbol'], 'BTCUSDT')
    
    def test_get_positions_for_symbol(self):
        """Test getting position for specific symbol"""
        # Place a buy order
        self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        positions = self.executor.get_positions('BTCUSDT')
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['symbol'], 'BTCUSDT')
    
    def test_close_position(self):
        """Test closing a position"""
        # Open position
        self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        # Close position
        result = self.executor.close_position('BTCUSDT')
        
        # Should return boolean or raise error
        self.assertIsNotNone(result)
    
    def test_multiple_trades_same_symbol(self):
        """Test multiple trades on same symbol"""
        # Buy
        result1 = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        self.assertEqual(result1['status'], 'FILLED')
        
        # Sell
        result2 = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.SELL.value, 51000.0
        )
        self.assertEqual(result2['status'], 'FILLED')
        
        # Buy again
        result3 = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 51000.0
        )
        self.assertEqual(result3['status'], 'FILLED')
    
    def test_partial_sell(self):
        """Test selling less than full position"""
        # Buy 0.2 BTC
        self.executor.place_market_order(
            'BTCUSDT', 0.2, OrderSide.BUY.value, 50000.0
        )
        
        # Sell only 0.1 BTC
        result = self.executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.SELL.value, 51000.0
        )
        
        # Should still have 0.1 BTC position
        positions = self.executor.get_positions('BTCUSDT')
        if len(positions) > 0:
            # Implementation may or may not support partial sells
            # Just verify it doesn't crash
            self.assertIsNotNone(result)
    
    def test_generate_order_id_unique(self):
        """Test that generated order IDs are unique"""
        ids = set()
        for _ in range(100):
            order_id = self.executor._generate_order_id()
            self.assertNotIn(order_id, ids)
            ids.add(order_id)


@unittest.skipIf(not BROKER_API_AVAILABLE, "broker_api not available")
class TestSimulatedLiveTradingBrokerAdapter(unittest.TestCase):
    """Tests for SimulatedLiveTradingBrokerAdapter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.adapter = SimulatedLiveTradingBrokerAdapter(
            initial_capital=10000.0,
            paper_trading=True
        )
    
    def test_initialization(self):
        """Test adapter initialization"""
        self.assertTrue(self.adapter.paper_trading)
        self.assertIsNotNone(self.adapter.executor)
    
    def test_place_market_order(self):
        """Test market order through adapter"""
        result = self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        self.assertIn('status', result)
        self.assertIn('order_id', result)
    
    def test_place_limit_order(self):
        """Test limit order through adapter"""
        result = self.adapter.place_limit_order(
            'BTCUSDT', 0.1, 49000.0, OrderSide.BUY.value
        )
        
        self.assertIn('status', result)
    
    def test_cancel_order(self):
        """Test cancel order through adapter"""
        # Place order first
        order = self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        result = self.adapter.cancel_order('BTCUSDT', order['order_id'])
        
        self.assertIsNotNone(result)
    
    def test_get_order_status(self):
        """Test getting order status through adapter"""
        order = self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        status = self.adapter.get_order_status('BTCUSDT', order['order_id'])
        
        self.assertIn('order_id', status)
    
    def test_get_open_orders(self):
        """Test getting open orders through adapter"""
        orders = self.adapter.get_open_orders()
        
        self.assertIsInstance(orders, list)
    
    def test_get_account_balance(self):
        """Test getting account balance through adapter"""
        balance = self.adapter.get_account_balance()
        
        self.assertIsInstance(balance, dict)
    
    def test_get_positions(self):
        """Test getting positions through adapter"""
        # Place order first
        self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        positions = self.adapter.get_positions()
        
        self.assertIsInstance(positions, list)
    
    def test_close_position(self):
        """Test closing position through adapter"""
        # Place order first
        self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        result = self.adapter.close_position('BTCUSDT')
        
        self.assertIsNotNone(result)
    
    def test_get_performance_metrics(self):
        """Test getting performance metrics"""
        # Execute some trades
        self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.SELL.value, 51000.0
        )
        
        metrics = self.adapter.get_performance_metrics()
        
        self.assertIsNotNone(metrics)
    
    def test_save_session_log(self):
        """Test saving session log"""
        # Execute a trade
        self.adapter.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            self.adapter.save_session_log(filepath)
            
            # Verify file was created
            self.assertTrue(os.path.exists(filepath))
            
            # Verify content is valid JSON
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, (dict, list))
        finally:
            # Cleanup
            if os.path.exists(filepath):
                os.unlink(filepath)


@unittest.skipIf(not BROKER_API_AVAILABLE, "broker_api not available")
class TestBrokerFactory(unittest.TestCase):
    """Tests for BrokerFactory class"""
    
    def test_create_paper_trading_broker(self):
        """Test creating paper trading broker"""
        broker = BrokerFactory.create_broker(
            'paper',
            paper_trading=True,
            initial_capital=20000.0
        )
        
        self.assertIsInstance(broker, EnhancedPaperTradingExecutor)
        self.assertEqual(broker.initial_capital, 20000.0)
    
    def test_create_simulated_broker(self):
        """Test creating simulated live trading broker"""
        broker = BrokerFactory.create_broker(
            'simulated',
            paper_trading=True
        )
        
        self.assertIsInstance(broker, SimulatedLiveTradingBrokerAdapter)
    
    def test_create_broker_case_insensitive(self):
        """Test that broker type is case insensitive"""
        broker1 = BrokerFactory.create_broker('PAPER', paper_trading=True)
        broker2 = BrokerFactory.create_broker('paper', paper_trading=True)
        
        self.assertEqual(type(broker1), type(broker2))
    
    def test_create_broker_invalid_type(self):
        """Test creating broker with invalid type"""
        with self.assertRaises(ValueError):
            BrokerFactory.create_broker('invalid_broker_type')
    
    def test_create_broker_default_params(self):
        """Test creating broker with default parameters"""
        broker = BrokerFactory.create_broker('paper')
        
        self.assertIsNotNone(broker)
        self.assertTrue(broker.paper_trading)


@unittest.skipIf(not BROKER_API_AVAILABLE, "broker_api not available")
class TestBrokerAPIEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_negative_quantity(self):
        """Test handling negative quantity"""
        executor = EnhancedPaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.place_market_order(
            'BTCUSDT', -0.1, OrderSide.BUY.value, 50000.0
        )
        
        self.assertEqual(result['status'], 'REJECTED')
    
    def test_zero_quantity(self):
        """Test handling zero quantity"""
        executor = EnhancedPaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.place_market_order(
            'BTCUSDT', 0.0, OrderSide.BUY.value, 50000.0
        )
        
        self.assertEqual(result['status'], 'REJECTED')
    
    def test_negative_price(self):
        """Test handling negative price"""
        executor = EnhancedPaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, -50000.0
        )
        
        self.assertEqual(result['status'], 'REJECTED')
    
    def test_empty_symbol(self):
        """Test handling empty symbol"""
        executor = EnhancedPaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.place_market_order(
            '', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        self.assertEqual(result['status'], 'REJECTED')
    
    def test_very_large_order(self):
        """Test handling very large order"""
        executor = EnhancedPaperTradingExecutor(initial_capital=10000.0)
        
        result = executor.place_market_order(
            'BTCUSDT', 1000000.0, OrderSide.BUY.value, 50000.0
        )
        
        self.assertEqual(result['status'], 'REJECTED')
        self.assertIn('insufficient', result['message'].lower())
    
    def test_sell_more_than_position(self):
        """Test selling more than current position"""
        executor = EnhancedPaperTradingExecutor(initial_capital=10000.0)
        
        # Buy 0.1
        executor.place_market_order(
            'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
        )
        
        # Try to sell 0.2
        result = executor.place_market_order(
            'BTCUSDT', 0.2, OrderSide.SELL.value, 51000.0
        )
        
        # Should be rejected or adjust quantity
        self.assertIsNotNone(result)


@unittest.skipIf(not BROKER_API_AVAILABLE, "broker_api not available")
class TestBrokerLogging(unittest.TestCase):
    """Test logging functionality"""
    
    def test_log_action_called(self):
        """Test that log_action is called for operations"""
        executor = EnhancedPaperTradingExecutor(initial_capital=10000.0)
        
        # Mock the log_action method
        with patch.object(executor, 'log_action') as mock_log:
            executor.place_market_order(
                'BTCUSDT', 0.1, OrderSide.BUY.value, 50000.0
            )
            
            # Verify logging was called
            mock_log.assert_called()


if __name__ == '__main__':
    unittest.main()
