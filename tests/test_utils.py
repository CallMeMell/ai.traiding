"""
test_utils.py - Tests for utils.py
==================================
Comprehensive tests for utility functions.
"""

import unittest
import os
import tempfile
import shutil
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Import functions to test
from utils import (
    setup_logging,
    validate_ohlcv_data,
    format_currency,
    format_percentage,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_current_drawdown,
    calculate_calmar_ratio,
    calculate_volatility,
    TradeLogger,
    generate_sample_data
)


class TestSetupLogging(unittest.TestCase):
    """Tests for logging setup"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, "test.log")
    
    def _cleanup_logging_handlers(self):
        """Close all logging handlers to avoid PermissionError on Windows."""
        # Get root logger and all other loggers
        loggers = [logging.getLogger()] + [
            logging.getLogger(name) for name in logging.root.manager.loggerDict
        ]
        
        for logger in loggers:
            # Close and remove all handlers
            for handler in logger.handlers[:]:  # Use slice to avoid modification during iteration
                try:
                    handler.close()
                except Exception:
                    pass  # Ignore errors during cleanup
                try:
                    logger.removeHandler(handler)
                except Exception:
                    pass  # Ignore errors during cleanup
        
        # Clear handler list completely
        logging.getLogger().handlers.clear()
    
    def tearDown(self):
        """Clean up test environment"""
        # Close handlers BEFORE deleting files to prevent PermissionError on Windows
        # See: WINDOWS_PERMISSION_ERROR_FIX.md
        self._cleanup_logging_handlers()
        
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_setup_logging_creates_logger(self):
        """Test that setup_logging creates a logger"""
        logger = setup_logging(log_file=self.log_file)
        
        self.assertIsNotNone(logger)
    
    def test_setup_logging_creates_log_directory(self):
        """Test that log directory is created"""
        log_file = os.path.join(self.test_dir, "subdir", "test.log")
        setup_logging(log_file=log_file)
        
        self.assertTrue(os.path.exists(os.path.dirname(log_file)))
    
    def test_setup_logging_creates_log_file(self):
        """Test that log file is created"""
        logger = setup_logging(log_file=self.log_file)
        logger.info("Test message")
        
        self.assertTrue(os.path.exists(self.log_file))
    
    def test_setup_logging_respects_log_level(self):
        """Test that log level is respected"""
        logger = setup_logging(log_level="ERROR", log_file=self.log_file)
        
        self.assertEqual(logger.level, 40)  # ERROR level


class TestValidateOHLCVData(unittest.TestCase):
    """Tests for OHLCV data validation"""
    
    def test_valid_ohlcv_data(self):
        """Test validation of valid OHLCV data"""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [102, 103, 104],
            'volume': [1000, 1100, 1200]
        })
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_missing_column(self):
        """Test validation fails with missing column"""
        df = pd.DataFrame({
            'open': [100, 101],
            'high': [105, 106],
            'low': [95, 96],
            'close': [102, 103]
            # Missing 'volume'
        })
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn('volume', error.lower())
    
    def test_non_numeric_data(self):
        """Test validation fails with non-numeric data"""
        df = pd.DataFrame({
            'open': ['100', '101'],
            'high': ['105', '106'],
            'low': ['95', '96'],
            'close': ['102', '103'],
            'volume': ['1000', '1100']
        })
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn('numerisch', error.lower())
    
    def test_nan_values(self):
        """Test validation fails with NaN values"""
        df = pd.DataFrame({
            'open': [100, np.nan, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [102, 103, 104],
            'volume': [1000, 1100, 1200]
        })
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn('NaN', error)
    
    def test_negative_values(self):
        """Test validation fails with negative values"""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, -97],
            'close': [102, 103, 104],
            'volume': [1000, 1100, 1200]
        })
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn('negativ', error.lower())
    
    def test_invalid_ohlc_logic_high_less_than_low(self):
        """Test validation fails when high < low"""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 96, 107],  # Second high < low
            'low': [95, 100, 97],
            'close': [102, 103, 104],
            'volume': [1000, 1100, 1200]
        })
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn('High < Low', error)
    
    def test_too_few_rows(self):
        """Test validation fails with too few rows"""
        df = pd.DataFrame({
            'open': [100],
            'high': [105],
            'low': [95],
            'close': [102],
            'volume': [1000]
        })
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn('Zu wenig', error)


class TestFormatting(unittest.TestCase):
    """Tests for formatting functions"""
    
    def test_format_currency(self):
        """Test currency formatting"""
        result = format_currency(1234.56)
        
        self.assertIn('1,234.56', result)
        self.assertIn('$', result)
    
    def test_format_currency_large_amount(self):
        """Test formatting large amounts"""
        result = format_currency(1234567.89)
        
        self.assertIn('1,234,567.89', result)
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        result = format_percentage(12.3456)
        
        self.assertEqual(result, '12.35%')
    
    def test_format_percentage_negative(self):
        """Test formatting negative percentage"""
        result = format_percentage(-5.67)
        
        self.assertEqual(result, '-5.67%')


class TestSharpeRatio(unittest.TestCase):
    """Tests for Sharpe ratio calculation"""
    
    def test_sharpe_ratio_positive_returns(self):
        """Test Sharpe ratio with positive returns"""
        returns = [0.01, 0.02, 0.015, 0.01, 0.02]
        
        sharpe = calculate_sharpe_ratio(returns)
        
        self.assertIsInstance(sharpe, float)
        self.assertGreater(sharpe, 0)
    
    def test_sharpe_ratio_empty_list(self):
        """Test Sharpe ratio with empty list"""
        returns = []
        
        sharpe = calculate_sharpe_ratio(returns)
        
        self.assertEqual(sharpe, 0.0)
    
    def test_sharpe_ratio_single_return(self):
        """Test Sharpe ratio with single return"""
        returns = [0.01]
        
        sharpe = calculate_sharpe_ratio(returns)
        
        self.assertEqual(sharpe, 0.0)
    
    def test_sharpe_ratio_zero_std(self):
        """Test Sharpe ratio when all returns are identical"""
        returns = [0.01, 0.01, 0.01, 0.01]
        
        sharpe = calculate_sharpe_ratio(returns)
        
        self.assertEqual(sharpe, 0.0)


class TestMaxDrawdown(unittest.TestCase):
    """Tests for maximum drawdown calculation"""
    
    def test_max_drawdown_with_decline(self):
        """Test max drawdown with declining equity"""
        equity_curve = [10000, 11000, 9000, 8000, 10000]
        
        max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(equity_curve)
        
        self.assertLess(max_dd_pct, 0)  # Should be negative
        self.assertLess(max_dd_val, 0)  # Should be negative
        self.assertEqual(peak_val, 11000)
        self.assertEqual(trough_val, 8000)
    
    def test_max_drawdown_no_decline(self):
        """Test max drawdown with only increasing equity"""
        equity_curve = [10000, 11000, 12000, 13000]
        
        max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(equity_curve)
        
        self.assertEqual(max_dd_pct, 0.0)
    
    def test_max_drawdown_empty_list(self):
        """Test max drawdown with empty list"""
        equity_curve = []
        
        max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(equity_curve)
        
        self.assertEqual(max_dd_pct, 0.0)
        self.assertEqual(max_dd_val, 0.0)
    
    def test_max_drawdown_single_value(self):
        """Test max drawdown with single value"""
        equity_curve = [10000]
        
        max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(equity_curve)
        
        self.assertEqual(max_dd_pct, 0.0)


class TestCurrentDrawdown(unittest.TestCase):
    """Tests for current drawdown calculation"""
    
    def test_current_drawdown_at_peak(self):
        """Test current drawdown when at peak"""
        equity_curve = [10000, 11000, 12000]
        
        dd = calculate_current_drawdown(equity_curve)
        
        self.assertEqual(dd, 0.0)
    
    def test_current_drawdown_below_peak(self):
        """Test current drawdown when below peak"""
        equity_curve = [10000, 12000, 11000]  # Peak at 12000, current 11000
        
        dd = calculate_current_drawdown(equity_curve)
        
        self.assertLess(dd, 0)
        self.assertAlmostEqual(dd, -8.333, places=2)
    
    def test_current_drawdown_empty_list(self):
        """Test current drawdown with empty list"""
        equity_curve = []
        
        dd = calculate_current_drawdown(equity_curve)
        
        self.assertEqual(dd, 0.0)


class TestCalmarRatio(unittest.TestCase):
    """Tests for Calmar ratio calculation"""
    
    def test_calmar_ratio_positive(self):
        """Test Calmar ratio with positive return and drawdown"""
        total_return = 20.0  # 20% return
        max_drawdown = -10.0  # -10% drawdown
        
        calmar = calculate_calmar_ratio(total_return, max_drawdown)
        
        self.assertEqual(calmar, 2.0)
    
    def test_calmar_ratio_zero_drawdown(self):
        """Test Calmar ratio with zero drawdown"""
        total_return = 20.0
        max_drawdown = 0.0
        
        calmar = calculate_calmar_ratio(total_return, max_drawdown)
        
        self.assertEqual(calmar, 0.0)
    
    def test_calmar_ratio_positive_drawdown(self):
        """Test Calmar ratio with positive drawdown (invalid)"""
        total_return = 20.0
        max_drawdown = 10.0  # Should be negative
        
        calmar = calculate_calmar_ratio(total_return, max_drawdown)
        
        self.assertEqual(calmar, 0.0)


class TestVolatility(unittest.TestCase):
    """Tests for volatility calculation"""
    
    def test_volatility_calculation(self):
        """Test volatility calculation"""
        equity_curve = [10000, 10100, 9900, 10200, 10000]
        
        vol = calculate_volatility(equity_curve)
        
        self.assertIsInstance(vol, float)
        self.assertGreater(vol, 0)
    
    def test_volatility_constant_equity(self):
        """Test volatility with constant equity"""
        equity_curve = [10000, 10000, 10000, 10000]
        
        vol = calculate_volatility(equity_curve)
        
        self.assertEqual(vol, 0.0)
    
    def test_volatility_empty_list(self):
        """Test volatility with empty list"""
        equity_curve = []
        
        vol = calculate_volatility(equity_curve)
        
        self.assertEqual(vol, 0.0)


class TestTradeLogger(unittest.TestCase):
    """Tests for TradeLogger class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.trades_file = os.path.join(self.test_dir, "trades.jsonl")
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_trade_logger_initialization(self):
        """Test TradeLogger initializes correctly"""
        logger = TradeLogger(self.trades_file)
        
        self.assertIsNotNone(logger)
        self.assertTrue(os.path.exists(os.path.dirname(self.trades_file)))
    
    def test_log_trade_creates_file(self):
        """Test logging trade creates file"""
        logger = TradeLogger(self.trades_file)
        
        logger.log_trade(
            order_type='BUY',
            price=30000,
            quantity=0.1,
            strategies=['test'],
            capital=10000,
            symbol='BTC/USDT'
        )
        
        self.assertTrue(os.path.exists(self.trades_file))
    
    def test_log_trade_with_pnl(self):
        """Test logging trade with P&L"""
        logger = TradeLogger(self.trades_file)
        
        logger.log_trade(
            order_type='SELL',
            price=31000,
            quantity=0.1,
            strategies=['test'],
            capital=11000,
            symbol='BTC/USDT',
            pnl=100
        )
        
        trades = logger.get_all_trades()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]['pnl'], 100)
    
    def test_get_all_trades(self):
        """Test getting all trades"""
        logger = TradeLogger(self.trades_file)
        
        # Log multiple trades
        logger.log_trade(
            order_type='BUY',
            price=30000,
            quantity=0.1,
            strategies=['test'],
            capital=10000,
            symbol='BTC/USDT'
        )
        logger.log_trade(
            order_type='SELL',
            price=31000,
            quantity=0.1,
            strategies=['test'],
            capital=11000,
            symbol='BTC/USDT',
            pnl=100
        )
        
        trades = logger.get_all_trades()
        
        self.assertEqual(len(trades), 2)
    
    def test_clear_trades_method_exists(self):
        """Test that clear_trades method exists and is callable"""
        logger = TradeLogger(self.trades_file)
        
        # Log a trade
        logger.log_trade(
            order_type='BUY',
            price=30000,
            quantity=0.1,
            strategies=['test'],
            capital=10000,
            symbol='BTC/USDT'
        )
        
        # Verify clear_trades is callable
        self.assertTrue(callable(logger.clear_trades))
        
        # Call clear_trades - should not raise exception
        try:
            logger.clear_trades()
        except Exception as e:
            self.fail(f"clear_trades raised unexpected exception: {e}")


class TestGenerateSampleData(unittest.TestCase):
    """Tests for sample data generation"""
    
    def test_generate_sample_data_default(self):
        """Test generating sample data with defaults"""
        df = generate_sample_data()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertIn('close', df.columns)
    
    def test_generate_sample_data_custom_params(self):
        """Test generating sample data with custom parameters"""
        df = generate_sample_data(n_bars=100, start_price=50000)
        
        self.assertEqual(len(df), 100)
        self.assertAlmostEqual(df['close'].iloc[0], 50000, delta=100)
    
    def test_generate_sample_data_has_all_columns(self):
        """Test generated data has all required columns"""
        df = generate_sample_data()
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            self.assertIn(col, df.columns)
    
    def test_generate_sample_data_valid_ohlcv(self):
        """Test generated data passes validation"""
        df = generate_sample_data()
        
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertTrue(is_valid, f"Generated data failed validation: {error}")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSetupLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestValidateOHLCVData))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestSharpeRatio))
    suite.addTests(loader.loadTestsFromTestCase(TestMaxDrawdown))
    suite.addTests(loader.loadTestsFromTestCase(TestCurrentDrawdown))
    suite.addTests(loader.loadTestsFromTestCase(TestCalmarRatio))
    suite.addTests(loader.loadTestsFromTestCase(TestVolatility))
    suite.addTests(loader.loadTestsFromTestCase(TestTradeLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateSampleData))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.exit(0 if run_tests() else 1)
