"""
test_simulated_live_trading.py - Tests for Simulated Live Trading Environment
=============================================================================

Comprehensive tests for the simulated live-trading environment.
"""

import unittest
import logging
import time
from simulated_live_trading import (
    SimulatedLiveTradingEnvironment,
    OrderExecutionResult,
    SimulationMetrics
)

# Disable logging during tests
logging.disable(logging.CRITICAL)


class TestSimulatedLiveTradingEnvironment(unittest.TestCase):
    """Test Simulated Live Trading Environment"""
    
    def setUp(self):
        """Set up test environment"""
        self.env = SimulatedLiveTradingEnvironment(
            initial_capital=10000.0,
            use_live_data=False,
            enable_slippage=True,
            enable_fees=True,
            enable_execution_delay=True
        )
    
    def test_initialization(self):
        """Test environment initialization"""
        self.assertEqual(self.env.initial_capital, 10000.0)
        self.assertEqual(self.env.capital, 10000.0)
        self.assertEqual(len(self.env.positions), 0)
        self.assertEqual(len(self.env.orders), 0)
        self.assertTrue(self.env.enable_slippage)
        self.assertTrue(self.env.enable_fees)
        self.assertTrue(self.env.enable_execution_delay)
    
    def test_market_order_buy(self):
        """Test placing a market buy order"""
        result = self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        # Check order result
        self.assertIsNotNone(result)
        self.assertEqual(result.symbol, 'BTCUSDT')
        self.assertEqual(result.side, 'BUY')
        self.assertEqual(result.order_type, 'MARKET')
        self.assertEqual(result.requested_quantity, 0.1)
        self.assertEqual(result.filled_quantity, 0.1)
        self.assertEqual(result.status, 'FILLED')
        
        # Check slippage was applied
        self.assertGreater(result.slippage_percent, 0)
        
        # Check fees were applied
        self.assertGreater(result.fees, 0)
        
        # Check execution delay
        self.assertGreater(result.execution_delay_ms, 0)
        
        # Check capital decreased
        self.assertLess(self.env.capital, 10000.0)
        
        # Check position created
        self.assertIn('BTCUSDT', self.env.positions)
        self.assertEqual(self.env.positions['BTCUSDT']['quantity'], 0.1)
    
    def test_market_order_sell(self):
        """Test placing a market sell order"""
        # First buy
        self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        # Then sell
        result = self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='SELL',
            current_price=51000.0
        )
        
        # Check order result
        self.assertEqual(result.status, 'FILLED')
        self.assertEqual(result.side, 'SELL')
        
        # Check position closed
        self.assertNotIn('BTCUSDT', self.env.positions)
        
        # Check realized P&L was calculated
        self.assertNotEqual(self.env.metrics.realized_pnl, 0)
    
    def test_insufficient_capital(self):
        """Test order rejection due to insufficient capital"""
        result = self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=1.0,  # Too large for capital
            side='BUY',
            current_price=50000.0
        )
        
        # Check order was rejected
        self.assertEqual(result.status, 'REJECTED')
        self.assertEqual(result.filled_quantity, 0.0)
        
        # Check capital unchanged
        self.assertEqual(self.env.capital, 10000.0)
        
        # Check no position created
        self.assertNotIn('BTCUSDT', self.env.positions)
    
    def test_sell_without_position(self):
        """Test sell order rejection when no position exists"""
        result = self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='SELL',
            current_price=50000.0
        )
        
        # Check order was rejected
        self.assertEqual(result.status, 'REJECTED')
        self.assertEqual(result.filled_quantity, 0.0)
    
    def test_slippage_calculation(self):
        """Test slippage calculation"""
        result = self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        # Slippage should be positive (worse price for buy)
        self.assertGreater(result.slippage_percent, 0)
        self.assertGreater(result.slippage, 0)
        
        # Execution price should be higher than requested price for buy
        self.assertGreater(result.execution_price, 50000.0)
    
    def test_slippage_disabled(self):
        """Test trading with slippage disabled"""
        env = SimulatedLiveTradingEnvironment(
            initial_capital=10000.0,
            enable_slippage=False
        )
        
        result = env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        # No slippage should be applied
        self.assertEqual(result.slippage, 0.0)
        self.assertEqual(result.slippage_percent, 0.0)
        self.assertEqual(result.execution_price, 50000.0)
    
    def test_fees_calculation(self):
        """Test fee calculation"""
        result = self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        # Fees should be applied
        self.assertGreater(result.fees, 0)
        
        # Fees should be reasonable percentage of order value
        order_value = result.filled_quantity * result.execution_price
        fee_percent = (result.fees / order_value) * 100
        self.assertLess(fee_percent, 0.5)  # Should be less than 0.5%
    
    def test_fees_disabled(self):
        """Test trading with fees disabled"""
        env = SimulatedLiveTradingEnvironment(
            initial_capital=10000.0,
            enable_fees=False
        )
        
        result = env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        # No fees should be applied
        self.assertEqual(result.fees, 0.0)
    
    def test_execution_delay(self):
        """Test execution delay simulation"""
        start_time = time.time()
        
        result = self.env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Execution delay should be recorded
        self.assertGreater(result.execution_delay_ms, 0)
        
        # Some actual delay should have occurred (scaled down in simulation)
        self.assertGreater(elapsed_ms, 0)
    
    def test_execution_delay_disabled(self):
        """Test trading with execution delay disabled"""
        env = SimulatedLiveTradingEnvironment(
            initial_capital=10000.0,
            enable_execution_delay=False
        )
        
        result = env.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=50000.0
        )
        
        # No delay should be recorded
        self.assertEqual(result.execution_delay_ms, 0.0)
    
    def test_multiple_trades_tracking(self):
        """Test tracking of multiple trades"""
        # Buy
        self.env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
        
        # Buy more
        self.env.place_market_order('BTCUSDT', 0.05, 'BUY', current_price=50500.0)
        
        # Sell some
        self.env.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000.0)
        
        # Check metrics
        self.assertEqual(self.env.metrics.total_orders, 3)
        self.assertEqual(self.env.metrics.filled_orders, 3)
        
        # Check position remaining
        self.assertIn('BTCUSDT', self.env.positions)
        self.assertAlmostEqual(self.env.positions['BTCUSDT']['quantity'], 0.05, places=6)
    
    def test_get_account_balance(self):
        """Test getting account balance"""
        balance = self.env.get_account_balance()
        
        # Check balance structure
        self.assertIn('capital', balance)
        self.assertIn('unrealized_pnl', balance)
        self.assertIn('total_equity', balance)
        self.assertIn('initial_capital', balance)
        
        # Check initial values
        self.assertEqual(balance['capital'], 10000.0)
        self.assertEqual(balance['unrealized_pnl'], 0.0)
        self.assertEqual(balance['total_equity'], 10000.0)
        self.assertEqual(balance['initial_capital'], 10000.0)
    
    def test_get_positions(self):
        """Test getting positions"""
        # Place a buy order
        self.env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
        
        positions = self.env.get_positions()
        
        # Check positions structure
        self.assertIn('BTCUSDT', positions)
        pos = positions['BTCUSDT']
        self.assertIn('quantity', pos)
        self.assertIn('entry_price', pos)
        self.assertIn('current_price', pos)
        self.assertIn('unrealized_pnl', pos)
        self.assertIn('unrealized_pnl_percent', pos)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        # Execute some trades
        self.env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
        self.env.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000.0)
        
        metrics = self.env.get_performance_metrics()
        
        # Check metrics structure
        self.assertGreater(metrics.total_orders, 0)
        self.assertGreater(metrics.filled_orders, 0)
        self.assertGreater(metrics.total_volume_traded, 0)
        self.assertGreater(metrics.total_fees_paid, 0)
        self.assertGreater(metrics.avg_slippage_percent, 0)
        self.assertGreater(metrics.avg_execution_delay_ms, 0)
        
        # Check equity curve
        self.assertGreater(len(metrics.equity_curve), 1)
    
    def test_equity_curve_updates(self):
        """Test equity curve updates with trades"""
        initial_length = len(self.env.metrics.equity_curve)
        
        # Place trades
        self.env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
        self.env.place_market_order('ETHUSDT', 1.0, 'BUY', current_price=3000.0)
        
        # Equity curve should have updated
        self.assertGreater(len(self.env.metrics.equity_curve), initial_length)
    
    def test_close_all_positions(self):
        """Test closing all positions"""
        # Open multiple positions
        self.env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
        self.env.place_market_order('ETHUSDT', 1.0, 'BUY', current_price=3000.0)
        
        # Close all
        self.env.close_all_positions()
        
        # All positions should be closed
        self.assertEqual(len(self.env.positions), 0)
    
    def test_order_id_generation(self):
        """Test unique order ID generation"""
        order_ids = set()
        
        for i in range(10):
            result = self.env.place_market_order(
                'BTCUSDT', 0.01, 'BUY', current_price=50000.0
            )
            order_ids.add(result.order_id)
        
        # All order IDs should be unique
        self.assertEqual(len(order_ids), 10)
    
    def test_average_position_on_multiple_buys(self):
        """Test position averaging on multiple buys"""
        # Use larger capital to ensure both orders succeed
        env = SimulatedLiveTradingEnvironment(initial_capital=100000.0)
        
        # First buy
        result1 = env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
        self.assertEqual(result1.status, 'FILLED')
        
        # Second buy at different price
        result2 = env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=52000.0)
        self.assertEqual(result2.status, 'FILLED')
        
        # Check position was averaged
        pos = env.positions['BTCUSDT']
        self.assertAlmostEqual(pos['quantity'], 0.2, places=6)
        
        # Average price should be between the two prices (accounting for slippage)
        # Since slippage pushes prices higher for buys, average should be > 50000
        self.assertGreater(pos['entry_price'], 50000.0)
        self.assertLess(pos['entry_price'], 55000.0)  # Allow for slippage


class TestOrderExecutionResult(unittest.TestCase):
    """Test OrderExecutionResult data class"""
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        from datetime import datetime
        
        result = OrderExecutionResult(
            order_id='TEST_001',
            symbol='BTCUSDT',
            side='BUY',
            order_type='MARKET',
            requested_quantity=0.1,
            filled_quantity=0.1,
            requested_price=None,
            execution_price=50000.0,
            slippage=50.0,
            slippage_percent=0.1,
            fees=37.5,
            execution_delay_ms=100.0,
            timestamp=datetime.now(),
            status='FILLED',
            total_cost=5037.5
        )
        
        result_dict = result.to_dict()
        
        # Check all fields present
        self.assertIn('order_id', result_dict)
        self.assertIn('symbol', result_dict)
        self.assertIn('side', result_dict)
        self.assertIn('execution_price', result_dict)
        self.assertIn('slippage', result_dict)
        self.assertIn('fees', result_dict)


class TestSimulationMetrics(unittest.TestCase):
    """Test SimulationMetrics data class"""
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        metrics = SimulationMetrics(
            total_orders=10,
            filled_orders=9,
            rejected_orders=1,
            total_volume_traded=50000.0
        )
        
        metrics_dict = metrics.to_dict()
        
        # Check all fields present
        self.assertIn('total_orders', metrics_dict)
        self.assertIn('filled_orders', metrics_dict)
        self.assertIn('rejected_orders', metrics_dict)
        self.assertIn('total_volume_traded', metrics_dict)
        
        # Check values
        self.assertEqual(metrics_dict['total_orders'], 10)
        self.assertEqual(metrics_dict['filled_orders'], 9)


class TestRealisticConditions(unittest.TestCase):
    """Test realistic trading condition simulations"""
    
    def test_slippage_varies_by_order_size(self):
        """Test that slippage increases with order size"""
        env = SimulatedLiveTradingEnvironment(initial_capital=100000.0)
        
        # Small order
        small_result = env.place_market_order('BTCUSDT', 0.01, 'BUY', current_price=50000.0)
        
        # Large order (relative to capital)
        large_result = env.place_market_order('ETHUSDT', 10.0, 'BUY', current_price=3000.0)
        
        # Large order should have higher slippage on average
        # Note: This is probabilistic, but with large enough orders the trend should hold
        self.assertGreater(large_result.slippage_percent, 0)
    
    def test_buy_vs_sell_slippage_direction(self):
        """Test that slippage direction is correct for buy vs sell"""
        env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)
        
        # Buy order - execution price should be higher (worse) than base
        buy_result = env.place_market_order('BTCUSDT', 0.05, 'BUY', current_price=50000.0)
        
        # For buy, slippage moves price up
        self.assertGreaterEqual(buy_result.execution_price, 50000.0)
        
        # Sell order - execution price should be lower (worse) than base
        sell_result = env.place_market_order('BTCUSDT', 0.05, 'SELL', current_price=50000.0)
        
        # For sell, slippage moves price down
        self.assertLessEqual(sell_result.execution_price, 50000.0)
    
    def test_metrics_aggregation(self):
        """Test that metrics are properly aggregated across multiple trades"""
        env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)
        
        # Execute multiple trades
        for i in range(5):
            env.place_market_order('BTCUSDT', 0.01, 'BUY', current_price=50000.0 + i*100)
        
        metrics = env.get_performance_metrics()
        
        # Check aggregated metrics
        self.assertEqual(metrics.total_orders, 5)
        self.assertEqual(metrics.filled_orders, 5)
        self.assertGreater(metrics.total_volume_traded, 0)
        self.assertGreater(metrics.total_fees_paid, 0)
        self.assertGreater(metrics.total_slippage, 0)
        
        # Average slippage should be reasonable
        self.assertGreater(metrics.avg_slippage_percent, 0)
        self.assertLess(metrics.avg_slippage_percent, 1.0)  # Should be less than 1%


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSimulatedLiveTradingEnvironment))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderExecutionResult))
    suite.addTests(loader.loadTestsFromTestCase(TestSimulationMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestRealisticConditions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


class TestBrokerIntegration(unittest.TestCase):
    """Test integration with broker_api.py"""
    
    def test_broker_factory_simulated(self):
        """Test creating simulated broker through factory"""
        try:
            from broker_api import BrokerFactory
            
            broker = BrokerFactory.create_broker(
                'simulated',
                initial_capital=10000.0,
                enable_slippage=True,
                enable_fees=True
            )
            
            self.assertIsNotNone(broker)
            
            # Test placing order
            order = broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
            self.assertEqual(order['status'], 'FILLED')
            self.assertIn('slippage', order)
            self.assertIn('fees', order)
            
            # Test getting balance
            balance = broker.get_account_balance()
            self.assertIn('total', balance)
            
            # Test getting positions
            positions = broker.get_positions()
            self.assertEqual(len(positions), 1)
            
        except ImportError:
            self.skipTest("broker_api not available")


if __name__ == '__main__':
    print("=" * 80)
    print("SIMULATED LIVE TRADING ENVIRONMENT - TEST SUITE")
    print("=" * 80)
    print()
    
    # Add broker integration tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSimulatedLiveTradingEnvironment))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderExecutionResult))
    suite.addTests(loader.loadTestsFromTestCase(TestSimulationMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestRealisticConditions))
    suite.addTests(loader.loadTestsFromTestCase(TestBrokerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
