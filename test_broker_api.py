"""
test_broker_api.py - Tests for Broker API Integration
=====================================================

Tests for the unified broker API interface and implementations.
"""

import unittest
import logging
from datetime import datetime
from broker_api import (
    BrokerFactory, 
    EnhancedPaperTradingExecutor, 
    OrderType, 
    OrderSide,
    OrderStatus
)

# Disable logging during tests
logging.disable(logging.CRITICAL)


class TestBrokerFactory(unittest.TestCase):
    """Test BrokerFactory"""
    
    def test_create_paper_broker(self):
        """Test creating paper trading broker"""
        broker = BrokerFactory.create_broker('paper', initial_capital=5000)
        self.assertIsNotNone(broker)
        self.assertIsInstance(broker, EnhancedPaperTradingExecutor)
        self.assertEqual(broker.capital, 5000)
    
    def test_invalid_broker_type(self):
        """Test creating invalid broker type"""
        with self.assertRaises(ValueError):
            BrokerFactory.create_broker('invalid_broker')


class TestPaperTradingExecutor(unittest.TestCase):
    """Test Enhanced Paper Trading Executor"""
    
    def setUp(self):
        """Set up test broker"""
        self.broker = EnhancedPaperTradingExecutor(initial_capital=10000)
    
    def test_initialization(self):
        """Test broker initialization"""
        self.assertEqual(self.broker.capital, 10000)
        self.assertEqual(self.broker.initial_capital, 10000)
        self.assertEqual(len(self.broker.positions), 0)
        self.assertEqual(len(self.broker.orders), 0)
    
    def test_place_market_buy_order(self):
        """Test placing a market buy order"""
        order = self.broker.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000
        )
        
        self.assertIsNotNone(order)
        self.assertEqual(order['symbol'], 'BTCUSDT')
        self.assertEqual(order['quantity'], 0.1)
        self.assertEqual(order['side'], 'BUY')
        self.assertEqual(order['status'], 'FILLED')
        
        # Check capital decreased
        self.assertEqual(self.broker.capital, 10000 - (0.1 * 50000))
        
        # Check position created
        self.assertIn('BTCUSDT', self.broker.positions)
        self.assertEqual(self.broker.positions['BTCUSDT']['quantity'], 0.1)
    
    def test_place_market_sell_order(self):
        """Test placing a market sell order"""
        # First buy
        self.broker.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000
        )
        
        # Then sell
        order = self.broker.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='SELL',
            current_price=51000
        )
        
        self.assertIsNotNone(order)
        self.assertEqual(order['side'], 'SELL')
        self.assertEqual(order['status'], 'FILLED')
        
        # Check position closed
        self.assertNotIn('BTCUSDT', self.broker.positions)
        
        # Check profit
        expected_capital = 10000 + (0.1 * (51000 - 50000))
        self.assertAlmostEqual(self.broker.capital, expected_capital, places=2)
    
    def test_insufficient_capital(self):
        """Test placing order with insufficient capital"""
        with self.assertRaises(ValueError):
            self.broker.place_market_order(
                symbol='BTCUSDT',
                quantity=1.0,  # Too much
                side='BUY',
                current_price=50000
            )
    
    def test_sell_without_position(self):
        """Test selling without having a position"""
        with self.assertRaises(ValueError):
            self.broker.place_market_order(
                symbol='BTCUSDT',
                quantity=0.1,
                side='SELL',
                current_price=50000
            )
    
    def test_place_limit_order(self):
        """Test placing a limit order"""
        order = self.broker.place_limit_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            price=49000
        )
        
        self.assertIsNotNone(order)
        self.assertEqual(order['type'], 'LIMIT')
        self.assertEqual(order['status'], 'NEW')
        self.assertEqual(order['price'], 49000)
        
        # Check order is tracked
        self.assertIn(order['order_id'], self.broker.orders)
    
    def test_cancel_order(self):
        """Test canceling an order"""
        # Place limit order
        order = self.broker.place_limit_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            price=49000
        )
        
        order_id = order['order_id']
        
        # Cancel it
        result = self.broker.cancel_order('BTCUSDT', order_id)
        self.assertTrue(result)
        
        # Check status updated
        order_status = self.broker.get_order_status('BTCUSDT', order_id)
        self.assertEqual(order_status['status'], 'CANCELED')
    
    def test_get_order_status(self):
        """Test getting order status"""
        # Place order
        order = self.broker.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000
        )
        
        # Get status
        status = self.broker.get_order_status('BTCUSDT', order['order_id'])
        self.assertIsNotNone(status)
        self.assertEqual(status['status'], 'FILLED')
    
    def test_get_open_orders(self):
        """Test getting open orders"""
        # Place limit orders
        self.broker.place_limit_order('BTCUSDT', 0.1, 'BUY', 49000)
        self.broker.place_limit_order('ETHUSDT', 1.0, 'BUY', 2900)
        
        # Get all open orders
        open_orders = self.broker.get_open_orders()
        self.assertEqual(len(open_orders), 2)
        
        # Get open orders for specific symbol
        btc_orders = self.broker.get_open_orders('BTCUSDT')
        self.assertEqual(len(btc_orders), 1)
        self.assertEqual(btc_orders[0]['symbol'], 'BTCUSDT')
    
    def test_get_account_balance(self):
        """Test getting account balance"""
        balance = self.broker.get_account_balance('USDT')
        
        self.assertIsNotNone(balance)
        self.assertEqual(balance['total'], 10000)
        self.assertEqual(balance['free'], 10000)
        self.assertEqual(balance['locked'], 0)
    
    def test_get_positions(self):
        """Test getting positions"""
        # No positions initially
        positions = self.broker.get_positions()
        self.assertEqual(len(positions), 0)
        
        # Buy and check position
        self.broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000)
        positions = self.broker.get_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['symbol'], 'BTCUSDT')
        self.assertEqual(positions[0]['quantity'], 0.1)
        
        # Get specific position
        btc_positions = self.broker.get_positions('BTCUSDT')
        self.assertEqual(len(btc_positions), 1)
    
    def test_close_position(self):
        """Test closing a position"""
        # Buy
        self.broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000)
        
        # Close position
        result = self.broker.close_position('BTCUSDT')
        self.assertTrue(result)
        
        # Check position is closed
        positions = self.broker.get_positions('BTCUSDT')
        self.assertEqual(len(positions), 0)
    
    def test_multiple_trades_tracking(self):
        """Test tracking multiple trades"""
        # Execute multiple trades
        self.broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000)
        self.broker.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000)
        
        self.broker.place_market_order('ETHUSDT', 1.0, 'BUY', current_price=3000)
        self.broker.place_market_order('ETHUSDT', 1.0, 'SELL', current_price=3100)
        
        # Check trade history
        self.assertEqual(len(self.broker.trade_history), 2)
        
        # Check capital changed
        expected_pnl = (0.1 * (51000 - 50000)) + (1.0 * (3100 - 3000))
        expected_capital = 10000 + expected_pnl
        self.assertAlmostEqual(self.broker.capital, expected_capital, places=2)


class TestBrokerLogging(unittest.TestCase):
    """Test broker action logging"""
    
    def setUp(self):
        """Set up test broker"""
        # Re-enable logging for this test
        logging.disable(logging.NOTSET)
        self.broker = EnhancedPaperTradingExecutor(initial_capital=10000)
    
    def tearDown(self):
        """Disable logging after test"""
        logging.disable(logging.CRITICAL)
    
    def test_logging_enabled(self):
        """Test that logging is working"""
        # This test just ensures logging doesn't cause errors
        order = self.broker.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000
        )
        self.assertIsNotNone(order)


class TestOrderEnums(unittest.TestCase):
    """Test order enumerations"""
    
    def test_order_type_enum(self):
        """Test OrderType enum"""
        self.assertEqual(OrderType.MARKET.value, "MARKET")
        self.assertEqual(OrderType.LIMIT.value, "LIMIT")
    
    def test_order_side_enum(self):
        """Test OrderSide enum"""
        self.assertEqual(OrderSide.BUY.value, "BUY")
        self.assertEqual(OrderSide.SELL.value, "SELL")
    
    def test_order_status_enum(self):
        """Test OrderStatus enum"""
        self.assertEqual(OrderStatus.NEW.value, "NEW")
        self.assertEqual(OrderStatus.FILLED.value, "FILLED")
        self.assertEqual(OrderStatus.CANCELED.value, "CANCELED")


def run_tests():
    """Run all tests"""
    # Re-enable logging
    logging.disable(logging.NOTSET)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
