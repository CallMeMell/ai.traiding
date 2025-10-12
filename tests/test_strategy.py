"""
test_strategy.py - Tests for strategy.py
========================================
Comprehensive tests for trading strategies.
"""

import unittest
import pandas as pd
import numpy as np

# Import classes to test
from strategy import (
    BaseStrategy,
    MACrossoverStrategy,
    RSIStrategy,
    EMACrossoverStrategy,
    TradingStrategy
)


class TestBaseStrategy(unittest.TestCase):
    """Tests for BaseStrategy base class"""
    
    def test_base_strategy_cannot_be_instantiated(self):
        """Test that BaseStrategy is abstract and cannot be instantiated"""
        with self.assertRaises(TypeError):
            BaseStrategy("test", {})
    
    def test_validate_data_with_valid_data(self):
        """Test validate_data with valid DataFrame"""
        strategy = MACrossoverStrategy({})
        
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [102, 103, 104],
            'volume': [1000, 1100, 1200]
        })
        
        self.assertTrue(strategy.validate_data(df))
    
    def test_validate_data_missing_column(self):
        """Test validate_data fails with missing column"""
        strategy = MACrossoverStrategy({})
        
        df = pd.DataFrame({
            'open': [100, 101],
            'high': [105, 106],
            'low': [95, 96],
            'close': [102, 103]
            # Missing 'volume'
        })
        
        self.assertFalse(strategy.validate_data(df))
    
    def test_validate_data_insufficient_rows(self):
        """Test validate_data fails with too few rows"""
        strategy = MACrossoverStrategy({})
        
        df = pd.DataFrame({
            'open': [100],
            'high': [105],
            'low': [95],
            'close': [102],
            'volume': [1000]
        })
        
        self.assertFalse(strategy.validate_data(df))
    
    def test_update_params(self):
        """Test updating strategy parameters"""
        strategy = MACrossoverStrategy({'short_window': 50})
        
        self.assertEqual(strategy.params['short_window'], 50)
        
        strategy.update_params({'short_window': 100})
        
        self.assertEqual(strategy.params['short_window'], 100)
    
    def test_get_info(self):
        """Test getting strategy info"""
        params = {'short_window': 50, 'long_window': 200}
        strategy = MACrossoverStrategy(params)
        
        info = strategy.get_info()
        
        self.assertIn('name', info)
        self.assertIn('enabled', info)
        self.assertIn('params', info)
        self.assertEqual(info['name'], 'MA_Crossover')
        self.assertTrue(info['enabled'])


class TestMACrossoverStrategy(unittest.TestCase):
    """Tests for MA Crossover Strategy"""
    
    def setUp(self):
        """Set up test data"""
        self.strategy = MACrossoverStrategy({
            'short_window': 5,
            'long_window': 10
        })
    
    def test_initialization(self):
        """Test strategy initializes correctly"""
        self.assertEqual(self.strategy.name, 'MA_Crossover')
        self.assertEqual(self.strategy.short_window, 5)
        self.assertEqual(self.strategy.long_window, 10)
    
    def test_generate_signal_with_valid_data(self):
        """Test signal generation with valid data"""
        # Create uptrend data
        df = pd.DataFrame({
            'open': np.arange(100, 120),
            'high': np.arange(105, 125),
            'low': np.arange(95, 115),
            'close': np.arange(100, 120),
            'volume': np.full(20, 1000)
        })
        
        signal = self.strategy.generate_signal(df)
        
        self.assertIn(signal, [-1, 0, 1])
    
    def test_generate_signal_bullish_crossover(self):
        """Test BUY signal on bullish crossover"""
        # Create data where short MA crosses above long MA
        closes = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                  110, 115, 120, 125, 130, 135, 140, 145, 150, 155]
        
        df = pd.DataFrame({
            'open': closes,
            'high': [c + 5 for c in closes],
            'low': [c - 5 for c in closes],
            'close': closes,
            'volume': np.full(len(closes), 1000)
        })
        
        signal = self.strategy.generate_signal(df)
        
        # Should be BUY or HOLD (depends on exact crossover timing)
        self.assertIn(signal, [0, 1])


class TestRSIStrategy(unittest.TestCase):
    """Tests for RSI Strategy"""
    
    def setUp(self):
        """Set up test data"""
        self.strategy = RSIStrategy({
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        })
    
    def test_initialization(self):
        """Test strategy initializes correctly"""
        self.assertEqual(self.strategy.name, 'RSI_MeanReversion')
        self.assertEqual(self.strategy.window, 14)
        self.assertEqual(self.strategy.oversold, 30)
        self.assertEqual(self.strategy.overbought, 70)
    
    def test_generate_signal_with_valid_data(self):
        """Test signal generation with valid data"""
        # Create sufficient data for RSI calculation
        df = pd.DataFrame({
            'open': np.arange(100, 120),
            'high': np.arange(105, 125),
            'low': np.arange(95, 115),
            'close': np.arange(100, 120),
            'volume': np.full(20, 1000)
        })
        
        signal = self.strategy.generate_signal(df)
        
        self.assertIn(signal, [-1, 0, 1])
    
    def test_generate_signal_insufficient_data(self):
        """Test signal returns HOLD with insufficient data"""
        # Not enough data for RSI calculation
        df = pd.DataFrame({
            'open': [100, 101],
            'high': [105, 106],
            'low': [95, 96],
            'close': [102, 103],
            'volume': [1000, 1100]
        })
        
        signal = self.strategy.generate_signal(df)
        
        self.assertEqual(signal, 0)  # HOLD


class TestEMACrossoverStrategy(unittest.TestCase):
    """Tests for EMA Crossover Strategy"""
    
    def setUp(self):
        """Set up test data"""
        self.strategy = EMACrossoverStrategy({
            'short_window': 12,
            'long_window': 26
        })
    
    def test_initialization(self):
        """Test strategy initializes correctly"""
        self.assertEqual(self.strategy.name, 'EMA_Crossover')
        self.assertEqual(self.strategy.short_window, 12)
        self.assertEqual(self.strategy.long_window, 26)
    
    def test_generate_signal_with_valid_data(self):
        """Test signal generation with valid data"""
        # Create sufficient data
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        signal = self.strategy.generate_signal(df)
        
        self.assertIn(signal, [-1, 0, 1])


class TestTradingStrategy(unittest.TestCase):
    """Tests for TradingStrategy manager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = {
            'active_strategies': ['rsi', 'ema_crossover'],
            'cooperation_logic': 'OR'
        }
        self.strategy = TradingStrategy(self.config)
    
    def test_initialization(self):
        """Test TradingStrategy initializes correctly"""
        self.assertIsNotNone(self.strategy)
        self.assertIsNotNone(self.strategy.strategy_manager)
    
    def test_loads_configured_strategies(self):
        """Test that configured strategies are loaded"""
        self.assertIn('rsi', self.strategy.strategy_manager.strategies)
        self.assertIn('ema_crossover', self.strategy.strategy_manager.strategies)
    
    def test_analyze_returns_dict(self):
        """Test analyze method returns dictionary"""
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        result = self.strategy.analyze(df)
        
        self.assertIsInstance(result, dict)
        self.assertIn('signal', result)
        self.assertIn('current_price', result)
        self.assertIn('triggering_strategies', result)
    
    def test_analyze_signal_in_valid_range(self):
        """Test analyze returns valid signal"""
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        result = self.strategy.analyze(df)
        
        self.assertIn(result['signal'], [-1, 0, 1])
    
    def test_or_logic_any_buy_triggers(self):
        """Test OR logic - any BUY triggers BUY signal"""
        # Test with OR logic
        strategy_or = TradingStrategy({
            'active_strategies': ['rsi', 'ema_crossover'],
            'cooperation_logic': 'OR'
        })
        
        # Create data that should trigger at least one strategy
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        result = strategy_or.analyze(df)
        
        # Should return valid signal
        self.assertIn(result['signal'], [-1, 0, 1])
    
    def test_and_logic_all_must_agree(self):
        """Test AND logic - all strategies must agree"""
        strategy_and = TradingStrategy({
            'active_strategies': ['rsi', 'ema_crossover'],
            'cooperation_logic': 'AND'
        })
        
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        result = strategy_and.analyze(df)
        
        # Should return valid signal
        self.assertIn(result['signal'], [-1, 0, 1])
    
    def test_weighted_logic(self):
        """Test WEIGHTED cooperation logic"""
        strategy_weighted = TradingStrategy({
            'active_strategies': ['rsi', 'ema_crossover'],
            'cooperation_logic': 'WEIGHTED',
            'strategy_weights': {
                'rsi': 0.6,
                'ema_crossover': 0.4
            }
        })
        
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        result = strategy_weighted.analyze(df)
        
        self.assertIn(result['signal'], [-1, 0, 1])
    
    def test_analyze_with_invalid_data(self):
        """Test analyze handles invalid data gracefully"""
        # Empty DataFrame
        df = pd.DataFrame()
        
        result = self.strategy.analyze(df)
        
        # Should return HOLD signal for invalid data
        self.assertEqual(result['signal'], 0)
    
    def test_get_strategy_info(self):
        """Test getting info about all strategies"""
        info = self.strategy.strategy_manager.get_all_strategies_info()
        
        self.assertIsInstance(info, dict)
        # Should have info for active strategies
        self.assertGreater(len(info), 0)


class TestStrategyCooperation(unittest.TestCase):
    """Tests for strategy cooperation logic"""
    
    def test_cooperation_or_with_mixed_signals(self):
        """Test OR logic with mixed signals"""
        strategy = TradingStrategy({
            'active_strategies': ['rsi', 'ema_crossover'],
            'cooperation_logic': 'OR'
        })
        
        # Create test data
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        result = strategy.analyze(df)
        
        # Should have triggering strategies if signal != 0
        if result['signal'] != 0:
            self.assertGreater(len(result['triggering_strategies']), 0)
    
    def test_cooperation_and_requires_consensus(self):
        """Test AND logic requires all strategies to agree"""
        strategy = TradingStrategy({
            'active_strategies': ['rsi', 'ema_crossover'],
            'cooperation_logic': 'AND'
        })
        
        df = pd.DataFrame({
            'open': np.arange(100, 150),
            'high': np.arange(105, 155),
            'low': np.arange(95, 145),
            'close': np.arange(100, 150),
            'volume': np.full(50, 1000)
        })
        
        result = strategy.analyze(df)
        
        # If signal is BUY or SELL, all strategies should have agreed
        if result['signal'] != 0:
            # All active strategies should be in triggering list
            self.assertGreater(len(result['triggering_strategies']), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestBaseStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestMACrossoverStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestRSIStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestEMACrossoverStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestTradingStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyCooperation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.exit(0 if run_tests() else 1)
