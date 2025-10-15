"""
test_main.py - Tests for main.py (LiveTradingBot)
=================================================
Comprehensive tests for the LiveTradingBot class and related functions.
"""

import unittest
import os
import tempfile
import shutil
import logging
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
import numpy as np

# Import functions and classes to test
from main import (
    validate_api_keys_for_live_trading,
    LiveTradingBot,
    signal_handler
)
from config import TradingConfig


class TestValidateApiKeysForLiveTrading(unittest.TestCase):
    """Tests for API key validation function"""
    
    def setUp(self):
        """Store original env vars"""
        self.original_api_key = os.environ.get('BINANCE_API_KEY')
        self.original_api_secret = os.environ.get('BINANCE_API_SECRET')
    
    def tearDown(self):
        """Restore original env vars"""
        if self.original_api_key:
            os.environ['BINANCE_API_KEY'] = self.original_api_key
        elif 'BINANCE_API_KEY' in os.environ:
            del os.environ['BINANCE_API_KEY']
            
        if self.original_api_secret:
            os.environ['BINANCE_API_SECRET'] = self.original_api_secret
        elif 'BINANCE_API_SECRET' in os.environ:
            del os.environ['BINANCE_API_SECRET']
    
    def test_valid_api_keys_from_env(self):
        """Test validation with valid API keys from environment"""
        os.environ['BINANCE_API_KEY'] = 'test_api_key_1234567890'
        os.environ['BINANCE_API_SECRET'] = 'test_api_secret_1234567890'
        
        success, message = validate_api_keys_for_live_trading()
        
        self.assertTrue(success)
        self.assertIn('validiert', message.lower())
    
    def test_missing_api_key(self):
        """Test validation fails when API key is missing"""
        if 'BINANCE_API_KEY' in os.environ:
            del os.environ['BINANCE_API_KEY']
        os.environ['BINANCE_API_SECRET'] = 'test_api_secret_1234567890'
        
        success, message = validate_api_keys_for_live_trading()
        
        self.assertFalse(success)
        self.assertIn('API_KEY fehlt', message)
    
    def test_missing_api_secret(self):
        """Test validation fails when API secret is missing"""
        os.environ['BINANCE_API_KEY'] = 'test_api_key_1234567890'
        if 'BINANCE_API_SECRET' in os.environ:
            del os.environ['BINANCE_API_SECRET']
        
        success, message = validate_api_keys_for_live_trading()
        
        self.assertFalse(success)
        self.assertIn('API_SECRET fehlt', message)
    
    def test_api_key_too_short(self):
        """Test validation fails when API key is too short"""
        os.environ['BINANCE_API_KEY'] = 'short'
        os.environ['BINANCE_API_SECRET'] = 'test_api_secret_1234567890'
        
        success, message = validate_api_keys_for_live_trading()
        
        self.assertFalse(success)
        self.assertIn('zu kurz', message)
    
    def test_api_secret_too_short(self):
        """Test validation fails when API secret is too short"""
        os.environ['BINANCE_API_KEY'] = 'test_api_key_1234567890'
        os.environ['BINANCE_API_SECRET'] = 'short'
        
        success, message = validate_api_keys_for_live_trading()
        
        self.assertFalse(success)
        self.assertIn('zu kurz', message)


class TestLiveTradingBotInitialization(unittest.TestCase):
    """Tests for LiveTradingBot initialization"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dry_run = os.environ.get('DRY_RUN')
        os.environ['DRY_RUN'] = 'true'
        
        # Clear API keys for safe testing
        self.original_api_key = os.environ.get('BINANCE_API_KEY')
        self.original_api_secret = os.environ.get('BINANCE_API_SECRET')
        if 'BINANCE_API_KEY' in os.environ:
            del os.environ['BINANCE_API_KEY']
        if 'BINANCE_API_SECRET' in os.environ:
            del os.environ['BINANCE_API_SECRET']
    
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
        
        # Clear root logger handler list
        logging.getLogger().handlers.clear()
    
    def tearDown(self):
        """Clean up test environment"""
        # Close handlers BEFORE deleting files to prevent PermissionError on Windows
        self._cleanup_logging_handlers()
        
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
        
        if self.original_dry_run:
            os.environ['DRY_RUN'] = self.original_dry_run
        elif 'DRY_RUN' in os.environ:
            del os.environ['DRY_RUN']
            
        if self.original_api_key:
            os.environ['BINANCE_API_KEY'] = self.original_api_key
        if self.original_api_secret:
            os.environ['BINANCE_API_SECRET'] = self.original_api_secret
    
    def test_initialization_simulation_mode(self):
        """Test bot initializes correctly in simulation mode"""
        bot = LiveTradingBot(use_live_data=False)
        
        self.assertIsNotNone(bot)
        self.assertIsNotNone(bot.strategy)
        self.assertIsNotNone(bot.trade_logger)
        self.assertEqual(bot.current_position, 0)
        self.assertGreater(bot.capital, 0)
        self.assertEqual(bot.capital, bot.initial_capital)
        self.assertFalse(bot.use_live_data)
        self.assertTrue(bot.is_dry_run)
    
    def test_initialization_sets_circuit_breaker_state(self):
        """Test circuit breaker is initialized correctly"""
        bot = LiveTradingBot(use_live_data=False)
        
        self.assertFalse(bot.circuit_breaker_triggered)
        self.assertIsInstance(bot.equity_curve, list)
        self.assertEqual(len(bot.equity_curve), 1)
        self.assertEqual(bot.equity_curve[0], bot.initial_capital)
    
    @patch('main.BINANCE_AVAILABLE', False)
    def test_initialization_binance_not_available(self):
        """Test bot handles missing Binance integration gracefully"""
        bot = LiveTradingBot(use_live_data=True)
        
        # Should fall back to simulation mode
        self.assertFalse(bot.use_live_data)
        self.assertIsNone(bot.binance_data_provider)
    
    def test_initialization_paper_trading_mode(self):
        """Test bot initializes in paper trading mode"""
        bot = LiveTradingBot(use_live_data=False, paper_trading=True)
        
        self.assertTrue(bot.paper_trading)
        self.assertIsNotNone(bot)


class TestCircuitBreaker(unittest.TestCase):
    """Tests for circuit breaker functionality"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['DRY_RUN'] = 'false'  # Enable circuit breaker
        # Force legacy circuit breaker for these tests
        from config import config
        self.original_use_advanced_cb = config.use_advanced_circuit_breaker
        config.use_advanced_circuit_breaker = False
        self.bot = LiveTradingBot(use_live_data=False)
    
    def tearDown(self):
        """Clean up"""
        os.environ['DRY_RUN'] = 'true'
        # Restore original config
        from config import config
        config.use_advanced_circuit_breaker = self.original_use_advanced_cb
    
    def test_circuit_breaker_not_triggered_within_limit(self):
        """Test circuit breaker doesn't trigger when within drawdown limit"""
        # Simulate small loss
        self.bot.capital = self.bot.initial_capital * 0.95  # 5% loss
        
        triggered = self.bot.check_circuit_breaker()
        
        self.assertFalse(triggered)
        self.assertFalse(self.bot.circuit_breaker_triggered)
    
    def test_circuit_breaker_triggered_exceeds_limit(self):
        """Test circuit breaker triggers when drawdown limit exceeded"""
        # Simulate large loss (>20% default limit)
        self.bot.capital = self.bot.initial_capital * 0.75  # 25% loss
        
        # Add some history to equity curve
        self.bot.equity_curve = [self.bot.initial_capital, 
                                 self.bot.initial_capital * 0.95,
                                 self.bot.initial_capital * 0.90]
        
        triggered = self.bot.check_circuit_breaker()
        
        self.assertTrue(triggered)
        self.assertTrue(self.bot.circuit_breaker_triggered)
    
    def test_circuit_breaker_disabled_in_dry_run(self):
        """Test circuit breaker is disabled in DRY_RUN mode"""
        os.environ['DRY_RUN'] = 'true'
        bot = LiveTradingBot(use_live_data=False)
        
        # Simulate large loss
        bot.capital = bot.initial_capital * 0.50  # 50% loss
        
        triggered = bot.check_circuit_breaker()
        
        self.assertFalse(triggered)
        self.assertFalse(bot.circuit_breaker_triggered)


class TestDataInitialization(unittest.TestCase):
    """Tests for data initialization"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['DRY_RUN'] = 'true'
        self.bot = LiveTradingBot(use_live_data=False)
    
    def test_initialize_data_simulation_mode(self):
        """Test data initialization in simulation mode"""
        self.bot.initialize_data()
        
        self.assertIsNotNone(self.bot.data)
        self.assertIsInstance(self.bot.data, pd.DataFrame)
        self.assertGreater(len(self.bot.data), 0)
        self.assertIn('close', self.bot.data.columns)
        self.assertIn('open', self.bot.data.columns)
        self.assertIn('high', self.bot.data.columns)
        self.assertIn('low', self.bot.data.columns)
        self.assertIn('volume', self.bot.data.columns)
    
    def test_initialize_data_sets_current_index(self):
        """Test current_index is set correctly after initialization"""
        self.bot.initialize_data()
        
        self.assertEqual(self.bot.current_index, len(self.bot.data) - 1)


class TestCandleGeneration(unittest.TestCase):
    """Tests for candle generation"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['DRY_RUN'] = 'true'
        self.bot = LiveTradingBot(use_live_data=False)
        self.bot.initialize_data()
        self.initial_length = len(self.bot.data)
    
    def test_add_new_candle_increases_data_length(self):
        """Test adding new candle increases data length"""
        self.bot.add_new_candle()
        
        self.assertEqual(len(self.bot.data), self.initial_length + 1)
    
    def test_add_new_candle_updates_current_index(self):
        """Test current_index updates when new candle added"""
        old_index = self.bot.current_index
        
        self.bot.add_new_candle()
        
        self.assertEqual(self.bot.current_index, old_index + 1)
        self.assertEqual(self.bot.current_index, len(self.bot.data) - 1)
    
    def test_add_new_candle_creates_valid_ohlcv(self):
        """Test new candle has valid OHLCV structure"""
        self.bot.add_new_candle()
        
        last_candle = self.bot.data.iloc[-1]
        
        self.assertGreater(last_candle['close'], 0)
        self.assertGreater(last_candle['high'], 0)
        self.assertGreater(last_candle['low'], 0)
        self.assertGreaterEqual(last_candle['high'], last_candle['close'])
        self.assertLessEqual(last_candle['low'], last_candle['close'])


class TestSignalProcessing(unittest.TestCase):
    """Tests for signal processing"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['DRY_RUN'] = 'true'
        self.bot = LiveTradingBot(use_live_data=False)
        self.bot.initialize_data()
    
    def test_process_buy_signal_opens_position(self):
        """Test buy signal opens long position"""
        analysis = {
            'signal': 1,  # BUY
            'current_price': 30000,
            'triggering_strategies': ['test_strategy']
        }
        
        self.bot.process_signal(analysis)
        
        self.assertEqual(self.bot.current_position, 1)
        self.assertEqual(self.bot.entry_price, 30000)
    
    def test_process_sell_signal_closes_position(self):
        """Test sell signal closes long position"""
        # First open a position
        self.bot.current_position = 1
        self.bot.entry_price = 30000
        
        # Then sell
        analysis = {
            'signal': -1,  # SELL
            'current_price': 31000,
            'triggering_strategies': ['test_strategy']
        }
        
        initial_capital = self.bot.capital
        self.bot.process_signal(analysis)
        
        self.assertEqual(self.bot.current_position, 0)
        self.assertGreater(self.bot.capital, initial_capital)  # Profitable trade
    
    def test_process_signal_calculates_pnl_correctly(self):
        """Test P&L calculation is correct"""
        from config import config
        
        # Open position
        self.bot.current_position = 1
        self.bot.entry_price = 30000
        initial_capital = self.bot.capital
        
        # Close with profit
        exit_price = 31000
        expected_pnl = (exit_price - 30000) * config.trade_size
        
        analysis = {
            'signal': -1,  # SELL
            'current_price': exit_price,
            'triggering_strategies': ['test_strategy']
        }
        
        self.bot.process_signal(analysis)
        
        self.assertAlmostEqual(self.bot.capital, initial_capital + expected_pnl, places=2)
    
    def test_process_signal_respects_circuit_breaker(self):
        """Test signals are ignored when circuit breaker is triggered"""
        # Disable DRY_RUN to enable circuit breaker
        os.environ['DRY_RUN'] = 'false'
        # Force legacy circuit breaker for this test
        from config import config
        original_use_advanced_cb = config.use_advanced_circuit_breaker
        config.use_advanced_circuit_breaker = False
        
        bot = LiveTradingBot(use_live_data=False)
        bot.initialize_data()
        
        # Simulate large loss to trigger circuit breaker
        bot.capital = bot.initial_capital * 0.70  # 30% loss
        bot.equity_curve = [bot.initial_capital, bot.initial_capital * 0.90, bot.initial_capital * 0.80]
        
        initial_position = bot.current_position
        
        analysis = {
            'signal': 1,  # BUY
            'current_price': 30000,
            'triggering_strategies': ['test_strategy']
        }
        
        bot.process_signal(analysis)
        
        # Circuit breaker should have been triggered during check
        self.assertTrue(bot.circuit_breaker_triggered)
        # Position should not change because circuit breaker returns early
        self.assertEqual(bot.current_position, initial_position)
        
        # Clean up
        os.environ['DRY_RUN'] = 'true'
        config.use_advanced_circuit_breaker = original_use_advanced_cb


class TestShutdown(unittest.TestCase):
    """Tests for shutdown functionality"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['DRY_RUN'] = 'true'
        self.bot = LiveTradingBot(use_live_data=False)
        self.bot.initialize_data()
    
    def test_shutdown_calculates_final_stats(self):
        """Test shutdown calculates final statistics"""
        # Simulate some trading
        self.bot.capital = self.bot.initial_capital * 1.1  # 10% profit
        
        # Shutdown should complete without error
        self.bot.shutdown()
        
        # Bot should still have valid state
        self.assertIsNotNone(self.bot.capital)
        self.assertIsNotNone(self.bot.initial_capital)


class TestSignalHandler(unittest.TestCase):
    """Tests for signal handler"""
    
    def test_signal_handler_exists(self):
        """Test signal handler function exists"""
        self.assertTrue(callable(signal_handler))
    
    def test_signal_handler_accepts_parameters(self):
        """Test signal handler accepts signal and frame parameters"""
        # Should not raise exception
        try:
            signal_handler(None, None)
        except Exception as e:
            self.fail(f"signal_handler raised unexpected exception: {e}")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestValidateApiKeysForLiveTrading))
    suite.addTests(loader.loadTestsFromTestCase(TestLiveTradingBotInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreaker))
    suite.addTests(loader.loadTestsFromTestCase(TestDataInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestCandleGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestSignalProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestShutdown))
    suite.addTests(loader.loadTestsFromTestCase(TestSignalHandler))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.exit(0 if run_tests() else 1)
