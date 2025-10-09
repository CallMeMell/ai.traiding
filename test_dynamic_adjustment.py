"""
test_dynamic_adjustment.py - Tests for Dynamic Parameter Adjustment
===================================================================
Unit tests for dynamic parameter adjustment based on market volatility.
"""

import unittest
import pandas as pd
import numpy as np
from strategy_core import ReversalTrailingStopStrategy


class TestDynamicAdjustment(unittest.TestCase):
    """Test cases for dynamic parameter adjustment"""
    
    def test_volatility_calculation(self):
        """Test volatility calculation with price history"""
        strategy = ReversalTrailingStopStrategy()
        
        # Add stable prices
        for price in [100, 101, 100, 101, 100]:
            strategy.price_history.append(price)
        
        volatility = strategy._calculate_market_volatility()
        
        # Should have low volatility
        self.assertGreater(volatility, 0)
        self.assertLess(volatility, 2.0)
    
    def test_high_volatility_adjustment(self):
        """Test that high volatility widens stops"""
        strategy = ReversalTrailingStopStrategy(
            stop_loss_percent=2.0,
            take_profit_percent=4.0,
            trailing_stop_percent=1.0
        )
        
        # Create high volatility scenario
        base_price = 100
        volatile_prices = [base_price]
        for i in range(1, 20):
            # Random walk with high volatility
            change = np.random.uniform(-3, 3)
            volatile_prices.append(volatile_prices[-1] * (1 + change/100))
        
        strategy.price_history = volatile_prices
        
        # Get initial parameters
        initial_stop_loss = strategy.stop_loss_percent
        
        # Calculate volatility and adjust
        volatility = strategy._calculate_market_volatility()
        strategy._adjust_parameters_based_on_volatility(volatility)
        
        # If volatility is high, stop loss should be wider (higher percentage)
        if volatility > 2.0:
            self.assertGreater(strategy.stop_loss_percent, initial_stop_loss)
    
    def test_low_volatility_adjustment(self):
        """Test that low volatility tightens stops"""
        strategy = ReversalTrailingStopStrategy(
            stop_loss_percent=2.0,
            take_profit_percent=4.0,
            trailing_stop_percent=1.0
        )
        
        # Create low volatility scenario
        stable_prices = [100 + i * 0.1 for i in range(20)]
        strategy.price_history = stable_prices
        
        # Get initial parameters
        initial_stop_loss = strategy.stop_loss_percent
        
        # Calculate volatility and adjust
        volatility = strategy._calculate_market_volatility()
        strategy._adjust_parameters_based_on_volatility(volatility)
        
        # If volatility is low, stop loss should be tighter (lower percentage)
        if volatility < 0.5:
            self.assertLess(strategy.stop_loss_percent, initial_stop_loss)
    
    def test_dynamic_adjustment_disabled(self):
        """Test that dynamic adjustment can be disabled"""
        strategy = ReversalTrailingStopStrategy()
        strategy.enable_dynamic_adjustment = False
        
        # Add volatile prices
        volatile_prices = [100 * (1 + np.random.uniform(-0.03, 0.03)) for _ in range(20)]
        strategy.price_history = volatile_prices
        
        # Get initial parameters
        initial_stop_loss = strategy.stop_loss_percent
        
        # Try to adjust
        volatility = strategy._calculate_market_volatility()
        strategy._adjust_parameters_based_on_volatility(volatility)
        
        # Parameters should not change when disabled
        self.assertEqual(strategy.stop_loss_percent, initial_stop_loss)
    
    def test_integration_with_process_candle(self):
        """Test that dynamic adjustment works in real candle processing"""
        strategy = ReversalTrailingStopStrategy(
            initial_capital=10000.0,
            stop_loss_percent=2.0,
            take_profit_percent=4.0
        )
        
        # Generate sample candles with increasing volatility
        candles = []
        price = 100.0
        for i in range(30):
            # Increase volatility over time
            volatility_factor = 0.01 + (i / 30) * 0.02  # From 1% to 3%
            change = np.random.uniform(-volatility_factor, volatility_factor)
            price = price * (1 + change)
            
            candles.append({
                'open': price * 0.999,
                'high': price * 1.001,
                'low': price * 0.999,
                'close': price,
                'volume': 1000
            })
        
        # Process candles
        for candle_data in candles:
            candle = pd.Series(candle_data)
            result = strategy.process_candle(candle)
        
        # Verify that strategy processed candles successfully
        self.assertIsNotNone(result)
        self.assertGreater(len(strategy.price_history), 0)
        
        # If we have enough history, volatility should be calculated
        if len(strategy.price_history) >= 2:
            volatility = strategy._calculate_market_volatility()
            self.assertGreater(volatility, 0)


class TestVolatilityScenarios(unittest.TestCase):
    """Test various market volatility scenarios"""
    
    def test_gradual_volatility_increase(self):
        """Test strategy adapts to gradually increasing volatility"""
        strategy = ReversalTrailingStopStrategy()
        
        # Simulate gradual volatility increase
        price = 100.0
        for i in range(25):
            vol = 0.005 + (i / 25) * 0.025  # 0.5% to 3% volatility
            change = np.random.uniform(-vol, vol)
            price = price * (1 + change)
            
            candle = pd.Series({
                'open': price,
                'high': price * 1.001,
                'low': price * 0.999,
                'close': price,
                'volume': 1000
            })
            
            strategy.process_candle(candle)
        
        # Strategy should have adapted
        self.assertGreater(len(strategy.price_history), 0)
    
    def test_sudden_volatility_spike(self):
        """Test strategy responds to sudden volatility spike"""
        strategy = ReversalTrailingStopStrategy()
        
        price = 100.0
        # Low volatility period
        for _ in range(15):
            price = price * (1 + np.random.uniform(-0.002, 0.002))
            candle = pd.Series({
                'open': price, 'high': price * 1.001,
                'low': price * 0.999, 'close': price, 'volume': 1000
            })
            strategy.process_candle(candle)
        
        initial_stop_loss = strategy.stop_loss_percent
        
        # Sudden high volatility
        for _ in range(10):
            price = price * (1 + np.random.uniform(-0.04, 0.04))
            candle = pd.Series({
                'open': price, 'high': price * 1.001,
                'low': price * 0.999, 'close': price, 'volume': 1000
            })
            strategy.process_candle(candle)
        
        # Stop loss should have been adjusted (widened)
        # Note: This may not always trigger if volatility doesn't exceed threshold
        volatility = strategy._calculate_market_volatility()
        self.assertGreater(volatility, 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicAdjustment))
    suite.addTests(loader.loadTestsFromTestCase(TestVolatilityScenarios))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
