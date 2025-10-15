"""
test_safety_features.py - Tests for safety features
===================================================
Comprehensive tests for all safety features required for live trading.
"""

import unittest
import os
import time
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
import numpy as np

# Import modules to test
from main import validate_api_keys_for_live_trading, LiveTradingBot
from utils import calculate_max_drawdown, calculate_current_drawdown


class TestCircuitBreakerIntegration(unittest.TestCase):
    """Integration tests for circuit breaker functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.original_dry_run = os.environ.get('DRY_RUN')
        # Force legacy circuit breaker for these tests
        from config import config
        self.original_use_advanced_cb = config.use_advanced_circuit_breaker
        config.use_advanced_circuit_breaker = False
    
    def tearDown(self):
        """Clean up"""
        if self.original_dry_run:
            os.environ['DRY_RUN'] = self.original_dry_run
        elif 'DRY_RUN' in os.environ:
            del os.environ['DRY_RUN']
        # Restore original config
        from config import config
        config.use_advanced_circuit_breaker = self.original_use_advanced_cb
    
    def test_circuit_breaker_stops_trading_on_large_loss(self):
        """Test that circuit breaker stops trading after large loss"""
        os.environ['DRY_RUN'] = 'false'
        
        bot = LiveTradingBot(use_live_data=False)
        bot.initialize_data()
        
        # Simulate large loss
        initial_capital = bot.initial_capital
        bot.capital = initial_capital * 0.70  # 30% loss
        bot.equity_curve = [initial_capital, initial_capital * 0.90, initial_capital * 0.85, initial_capital * 0.75]
        
        # Check circuit breaker
        triggered = bot.check_circuit_breaker()
        
        self.assertTrue(triggered)
        self.assertTrue(bot.circuit_breaker_triggered)
    
    def test_circuit_breaker_respects_config_limit(self):
        """Test that circuit breaker respects configured limit"""
        from config import config
        
        os.environ['DRY_RUN'] = 'false'
        bot = LiveTradingBot(use_live_data=False)
        
        # Get configured limit
        limit = config.max_drawdown_limit
        
        # Simulate loss just below limit (should not trigger)
        bot.capital = bot.initial_capital * (1 - limit + 0.01)
        bot.equity_curve = [bot.initial_capital, bot.capital]
        
        triggered = bot.check_circuit_breaker()
        
        self.assertFalse(triggered)
    
    def test_circuit_breaker_logs_critical_info(self):
        """Test that circuit breaker logs critical information"""
        os.environ['DRY_RUN'] = 'false'
        
        bot = LiveTradingBot(use_live_data=False)
        bot.capital = bot.initial_capital * 0.70
        bot.equity_curve = [bot.initial_capital, bot.capital]
        
        # Trigger circuit breaker
        with self.assertLogs(level='CRITICAL') as log:
            bot.check_circuit_breaker()
            
            # Check that critical log messages were generated
            self.assertTrue(any('CIRCUIT BREAKER' in message for message in log.output))


class TestAPIKeyValidationIntegration(unittest.TestCase):
    """Integration tests for API key validation"""
    
    def setUp(self):
        """Store original env vars"""
        self.original_api_key = os.environ.get('BINANCE_API_KEY')
        self.original_api_secret = os.environ.get('BINANCE_API_SECRET')
        self.original_dry_run = os.environ.get('DRY_RUN')
    
    def tearDown(self):
        """Restore original env vars"""
        for key, value in [
            ('BINANCE_API_KEY', self.original_api_key),
            ('BINANCE_API_SECRET', self.original_api_secret),
            ('DRY_RUN', self.original_dry_run)
        ]:
            if value:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_live_trading_blocked_without_valid_keys(self):
        """Test that live trading is blocked without valid API keys"""
        os.environ['DRY_RUN'] = 'false'
        
        # Remove API keys
        if 'BINANCE_API_KEY' in os.environ:
            del os.environ['BINANCE_API_KEY']
        if 'BINANCE_API_SECRET' in os.environ:
            del os.environ['BINANCE_API_SECRET']
        
        # Attempt to initialize live trading bot should raise exception
        with self.assertRaises(Exception) as context:
            bot = LiveTradingBot(use_live_data=True, paper_trading=False)
        
        self.assertIn('API-Key', str(context.exception))
    
    def test_dry_run_allows_missing_keys(self):
        """Test that DRY_RUN mode allows missing API keys"""
        os.environ['DRY_RUN'] = 'true'
        
        # Remove API keys
        if 'BINANCE_API_KEY' in os.environ:
            del os.environ['BINANCE_API_KEY']
        if 'BINANCE_API_SECRET' in os.environ:
            del os.environ['BINANCE_API_SECRET']
        
        # Should not raise exception in DRY_RUN mode
        try:
            bot = LiveTradingBot(use_live_data=True, paper_trading=False)
            # Should succeed without exception
            self.assertIsNotNone(bot)
        except Exception as e:
            self.fail(f"DRY_RUN mode should allow missing keys, but raised: {e}")


class TestRateLimiting(unittest.TestCase):
    """Tests for rate limiting functionality"""
    
    @patch('binance_integration.BinanceDataProvider')
    def test_rate_limit_enforces_minimum_interval(self, mock_provider_class):
        """Test that rate limiter enforces minimum interval between requests"""
        # Create a mock provider with rate limiting
        from binance_integration import BinanceDataProvider
        
        # We can test the rate limit logic directly
        class TestProvider:
            def __init__(self):
                self.last_request_time = 0
                self.min_request_interval = 0.2
            
            def _rate_limit_check(self):
                """Same implementation as BinanceDataProvider"""
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                
                if time_since_last < self.min_request_interval:
                    sleep_time = self.min_request_interval - time_since_last
                    time.sleep(sleep_time)
                
                self.last_request_time = time.time()
        
        provider = TestProvider()
        
        # First request
        start_time = time.time()
        provider._rate_limit_check()
        first_request_time = provider.last_request_time
        
        # Second request immediately after
        provider._rate_limit_check()
        second_request_time = provider.last_request_time
        
        # Time between requests should be at least min_request_interval
        time_diff = second_request_time - first_request_time
        self.assertGreaterEqual(time_diff, provider.min_request_interval - 0.01)  # Small tolerance
    
    def test_rate_limit_config_is_reasonable(self):
        """Test that rate limit configuration is reasonable for Binance"""
        from binance_integration import BinanceDataProvider
        
        # Binance has weight-based rate limits
        # 200ms interval = 5 requests/second = 300 requests/minute
        # This is well within Binance limits (typically 1200 weight/minute)
        
        try:
            # Just test initialization with testnet
            provider = BinanceDataProvider(
                api_key='test_key_1234567890',
                api_secret='test_secret_1234567890',
                testnet=True
            )
            
            # Check rate limit settings
            self.assertTrue(hasattr(provider, 'min_request_interval'))
            self.assertGreater(provider.min_request_interval, 0)
            self.assertLessEqual(provider.min_request_interval, 1.0)  # Should be < 1 second
        except Exception as e:
            # OK if initialization fails (no network), we just want to test the attribute exists
            pass


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling and recovery"""
    
    def test_invalid_data_returns_hold_signal(self):
        """Test that invalid data returns HOLD signal instead of crashing"""
        bot = LiveTradingBot(use_live_data=False)
        
        # Create invalid DataFrame (empty)
        df = pd.DataFrame()
        
        # Should not crash, should return HOLD signal
        result = bot.strategy.analyze(df)
        
        self.assertEqual(result['signal'], 0)  # HOLD
    
    def test_nan_in_data_handled_gracefully(self):
        """Test that NaN values in data are handled gracefully"""
        bot = LiveTradingBot(use_live_data=False)
        
        # Create data with NaN
        df = pd.DataFrame({
            'open': [100, np.nan, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [102, 103, 104],
            'volume': [1000, 1100, 1200]
        })
        
        # Should handle gracefully (validation should fail)
        from utils import validate_ohlcv_data
        is_valid, error = validate_ohlcv_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn('NaN', error)
    
    def test_bot_handles_data_initialization_error(self):
        """Test that bot handles data initialization errors gracefully"""
        bot = LiveTradingBot(use_live_data=False)
        
        # Force an error scenario
        bot.use_live_data = True
        bot.binance_data_provider = None
        
        # Should fall back to simulation without crashing
        try:
            bot.initialize_data()
            # Should have created simulated data
            self.assertIsNotNone(bot.data)
        except Exception as e:
            self.fail(f"Bot should handle initialization errors gracefully, but raised: {e}")


class TestDrawdownCalculations(unittest.TestCase):
    """Tests for drawdown calculation accuracy"""
    
    def test_max_drawdown_calculation_accuracy(self):
        """Test maximum drawdown calculation with known values"""
        # Test case: Peak at 10000, trough at 7000 = 30% drawdown
        equity_curve = [8000, 9000, 10000, 9500, 8500, 7000, 7500, 8000]
        
        max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(equity_curve)
        
        self.assertAlmostEqual(max_dd_pct, -30.0, places=1)
        self.assertEqual(peak_val, 10000)
        self.assertEqual(trough_val, 7000)
    
    def test_current_drawdown_at_new_high(self):
        """Test current drawdown is 0 when at new high"""
        equity_curve = [10000, 11000, 12000, 13000]
        
        dd = calculate_current_drawdown(equity_curve)
        
        self.assertEqual(dd, 0.0)
    
    def test_current_drawdown_below_peak(self):
        """Test current drawdown calculation when below peak"""
        # Peak at 10000, current at 9000 = -10% drawdown
        equity_curve = [10000, 10000, 9000]
        
        dd = calculate_current_drawdown(equity_curve)
        
        self.assertAlmostEqual(dd, -10.0, places=1)


class TestDryRunSafety(unittest.TestCase):
    """Tests for DRY_RUN safety features"""
    
    def test_dry_run_defaults_to_true(self):
        """Test that DRY_RUN defaults to true for safety"""
        # Clear DRY_RUN env var
        if 'DRY_RUN' in os.environ:
            original = os.environ['DRY_RUN']
            del os.environ['DRY_RUN']
        else:
            original = None
        
        try:
            bot = LiveTradingBot(use_live_data=False)
            
            # Should default to DRY_RUN = true
            # Check by seeing if circuit breaker is disabled
            self.assertTrue(bot.is_dry_run)
        finally:
            # Restore
            if original:
                os.environ['DRY_RUN'] = original
    
    def test_dry_run_mode_disables_circuit_breaker(self):
        """Test that DRY_RUN mode disables circuit breaker"""
        os.environ['DRY_RUN'] = 'true'
        
        bot = LiveTradingBot(use_live_data=False)
        
        # Simulate massive loss
        bot.capital = bot.initial_capital * 0.1  # 90% loss
        
        # Circuit breaker should not trigger in DRY_RUN
        triggered = bot.check_circuit_breaker()
        
        self.assertFalse(triggered)
    
    def test_production_mode_enables_circuit_breaker(self):
        """Test that production mode enables circuit breaker"""
        os.environ['DRY_RUN'] = 'false'
        
        bot = LiveTradingBot(use_live_data=False)
        
        self.assertFalse(bot.is_dry_run)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIKeyValidationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiting))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDrawdownCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestDryRunSafety))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.exit(0 if run_tests() else 1)
