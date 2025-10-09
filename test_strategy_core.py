"""
test_strategy_core.py - Tests for Reversal-Trailing-Stop Strategy
===================================================================
Unit tests for the ReversalTrailingStopStrategy class
"""

import unittest
import pandas as pd
import numpy as np
import logging
from strategy_core import ReversalTrailingStopStrategy

# Suppress logging during tests
logging.disable(logging.CRITICAL)


class TestReversalTrailingStopStrategy(unittest.TestCase):
    """Test cases for ReversalTrailingStopStrategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.initial_capital = 10000.0
        self.strategy = ReversalTrailingStopStrategy(
            initial_capital=self.initial_capital,
            stop_loss_percent=2.0,
            take_profit_percent=4.0,
            trailing_stop_percent=1.0,
            initial_direction='LONG'
        )
    
    def test_initialization(self):
        """Test strategy initialization"""
        self.assertEqual(self.strategy.initial_capital, self.initial_capital)
        self.assertEqual(self.strategy.capital, self.initial_capital)
        self.assertEqual(self.strategy.initial_direction, 'LONG')
        self.assertTrue(self.strategy.needs_immediate_entry)
        self.assertIsNone(self.strategy.position)
        self.assertEqual(self.strategy.total_trades, 0)
    
    def test_immediate_entry(self):
        """Test immediate entry on first candle"""
        candle = pd.Series({
            'open': 30000,
            'high': 30100,
            'low': 29900,
            'close': 30000,
            'volume': 1000000
        })
        
        result = self.strategy.process_candle(candle)
        
        # Should immediately enter LONG position
        self.assertEqual(result['action'], 'BUY')
        self.assertIsNotNone(self.strategy.position)
        self.assertEqual(self.strategy.position.direction, 'LONG')
        self.assertEqual(self.strategy.position.entry_price, 30000)
        self.assertFalse(self.strategy.needs_immediate_entry)
    
    def test_stop_loss_triggers_reversal(self):
        """Test that stop-loss triggers position reversal"""
        # Enter LONG position
        entry_candle = pd.Series({
            'open': 30000,
            'high': 30100,
            'low': 29900,
            'close': 30000,
            'volume': 1000000
        })
        self.strategy.process_candle(entry_candle)
        
        # Verify initial position
        self.assertEqual(self.strategy.position.direction, 'LONG')
        initial_stop_loss = self.strategy.position.stop_loss
        
        # Price drops below stop-loss (2%)
        stop_loss_candle = pd.Series({
            'open': 29500,
            'high': 29600,
            'low': 29300,  # Below stop-loss
            'close': 29400,
            'volume': 1000000
        })
        
        result = self.strategy.process_candle(stop_loss_candle)
        
        # Should trigger reversal to SHORT
        self.assertEqual(result['action'], 'REVERSE')
        self.assertIsNotNone(result['trade_info'])
        self.assertEqual(result['trade_info']['exit_reason'], 'STOP_LOSS')
        self.assertEqual(self.strategy.position.direction, 'SHORT')
        self.assertEqual(self.strategy.total_trades, 1)
    
    def test_take_profit_triggers_reentry(self):
        """Test that take-profit triggers re-entry in same direction"""
        # Enter LONG position
        entry_candle = pd.Series({
            'open': 30000,
            'high': 30100,
            'low': 29900,
            'close': 30000,
            'volume': 1000000
        })
        self.strategy.process_candle(entry_candle)
        
        # Price rises to take-profit level (4%)
        take_profit_candle = pd.Series({
            'open': 31200,
            'high': 31300,  # Above take-profit
            'low': 31100,
            'close': 31200,
            'volume': 1000000
        })
        
        result = self.strategy.process_candle(take_profit_candle)
        
        # Should trigger re-entry in same direction (LONG)
        self.assertEqual(result['action'], 'REENTER')
        self.assertIsNotNone(result['trade_info'])
        self.assertEqual(result['trade_info']['exit_reason'], 'TAKE_PROFIT')
        self.assertEqual(self.strategy.position.direction, 'LONG')
        self.assertEqual(self.strategy.total_trades, 1)
        self.assertEqual(self.strategy.winning_trades, 1)
    
    def test_trailing_stop_updates(self):
        """Test that trailing stop updates in profit"""
        # Enter LONG position
        entry_candle = pd.Series({
            'open': 30000,
            'high': 30100,
            'low': 29900,
            'close': 30000,
            'volume': 1000000
        })
        self.strategy.process_candle(entry_candle)
        initial_stop = self.strategy.position.stop_loss
        
        # Price moves favorably (in profit)
        profitable_candle = pd.Series({
            'open': 30500,
            'high': 30600,  # New high
            'low': 30400,
            'close': 30500,
            'volume': 1000000
        })
        
        self.strategy.process_candle(profitable_candle)
        
        # Trailing stop should have moved up
        new_stop = self.strategy.position.stop_loss
        self.assertGreater(new_stop, initial_stop)
    
    def test_capital_updates_correctly(self):
        """Test that capital updates correctly after trades"""
        initial_capital = self.strategy.capital
        
        # Enter and exit with profit
        entry_candle = pd.Series({
            'open': 30000,
            'high': 30100,
            'low': 29900,
            'close': 30000,
            'volume': 1000000
        })
        self.strategy.process_candle(entry_candle)
        
        # Take profit
        profit_candle = pd.Series({
            'open': 31200,
            'high': 31300,
            'low': 31100,
            'close': 31200,
            'volume': 1000000
        })
        self.strategy.process_candle(profit_candle)
        
        # Capital should increase
        self.assertGreater(self.strategy.capital, initial_capital)
    
    def test_short_position_mechanics(self):
        """Test SHORT position entry and exit"""
        # Initialize with SHORT direction
        short_strategy = ReversalTrailingStopStrategy(
            initial_capital=10000.0,
            stop_loss_percent=2.0,
            take_profit_percent=4.0,
            trailing_stop_percent=1.0,
            initial_direction='SHORT'
        )
        
        # Enter SHORT position
        entry_candle = pd.Series({
            'open': 30000,
            'high': 30100,
            'low': 29900,
            'close': 30000,
            'volume': 1000000
        })
        
        result = short_strategy.process_candle(entry_candle)
        
        self.assertEqual(result['action'], 'SELL')
        self.assertEqual(short_strategy.position.direction, 'SHORT')
        
        # For SHORT, stop-loss is above entry
        self.assertGreater(short_strategy.position.stop_loss, 30000)
        # For SHORT, take-profit is below entry
        self.assertLess(short_strategy.position.take_profit, 30000)
    
    def test_statistics(self):
        """Test statistics calculation"""
        stats = self.strategy.get_statistics()
        
        # Initial state
        self.assertEqual(stats['total_trades'], 0)
        self.assertEqual(stats['winning_trades'], 0)
        self.assertEqual(stats['losing_trades'], 0)
        self.assertEqual(stats['win_rate'], 0.0)
        self.assertEqual(stats['total_pnl'], 0.0)
        self.assertEqual(stats['roi'], 0.0)
    
    def test_position_info(self):
        """Test position information retrieval"""
        # No position initially (after immediate entry flag is set)
        info = self.strategy._get_position_info()
        self.assertFalse(info['has_position'])
        
        # After entry
        candle = pd.Series({
            'open': 30000,
            'high': 30100,
            'low': 29900,
            'close': 30000,
            'volume': 1000000
        })
        self.strategy.process_candle(candle)
        
        info = self.strategy._get_position_info()
        self.assertTrue(info['has_position'])
        self.assertEqual(info['direction'], 'LONG')
        self.assertEqual(info['entry_price'], 30000)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for real-world scenarios"""
    
    def test_multiple_reversals(self):
        """Test multiple position reversals"""
        strategy = ReversalTrailingStopStrategy(
            initial_capital=10000.0,
            stop_loss_percent=2.0,
            take_profit_percent=4.0,
            trailing_stop_percent=1.0,
            initial_direction='LONG'
        )
        
        # Simulate price action with multiple reversals
        prices = [30000, 29300, 29800, 28900, 29400]  # Volatile moves
        
        for price in prices:
            candle = pd.Series({
                'open': price,
                'high': price + 100,
                'low': price - 100,
                'close': price,
                'volume': 1000000
            })
            strategy.process_candle(candle)
        
        # Should have executed multiple trades
        self.assertGreater(strategy.total_trades, 0)
    
    def test_trending_market(self):
        """Test strategy in trending market"""
        strategy = ReversalTrailingStopStrategy(
            initial_capital=10000.0,
            stop_loss_percent=2.0,
            take_profit_percent=4.0,
            trailing_stop_percent=1.0,
            initial_direction='LONG'
        )
        
        # Simulate uptrend
        prices = np.linspace(30000, 31500, 50)  # Steady uptrend
        
        for price in prices:
            candle = pd.Series({
                'open': price - 10,
                'high': price + 10,
                'low': price - 20,
                'close': price,
                'volume': 1000000
            })
            strategy.process_candle(candle)
        
        # Should be profitable in uptrend
        stats = strategy.get_statistics()
        self.assertGreater(stats['capital'], strategy.initial_capital)


def run_tests():
    """Run all tests"""
    # Re-enable logging for test results
    logging.disable(logging.NOTSET)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestReversalTrailingStopStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
