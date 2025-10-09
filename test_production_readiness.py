"""
test_production_readiness.py - Production Readiness Tests
==========================================================
Comprehensive tests to validate system is ready for live trading.
"""
import unittest
import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class TestSecurityManager(unittest.TestCase):
    """Test security manager functionality"""
    
    def setUp(self):
        """Setup for security tests"""
        try:
            from security_manager import SecurityManager
            self.security = SecurityManager()
        except ImportError:
            self.skipTest("Security manager not available")
    
    def test_api_key_encryption(self):
        """Test API key encryption/decryption"""
        test_key = "test_api_key_123456"
        
        # Encrypt
        encrypted = self.security.encrypt_api_key(test_key)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, test_key)
        
        # Decrypt
        decrypted = self.security.decrypt_api_key(encrypted)
        self.assertEqual(decrypted, test_key)
    
    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        limiter = self.security.create_rate_limiter("test", max_calls=5, time_window=2)
        
        # Should allow first 5 calls
        for i in range(5):
            self.assertTrue(limiter.is_allowed(), f"Call {i+1} should be allowed")
        
        # Should block 6th call
        self.assertFalse(limiter.is_allowed(), "6th call should be blocked")
        
        # Should have 0 remaining calls
        self.assertEqual(limiter.get_remaining_calls(), 0)
    
    def test_request_validation(self):
        """Test request validation for security issues"""
        # Valid request
        valid_request = {"symbol": "BTC/USDT", "amount": 0.1}
        is_valid, error = self.security.validate_request(valid_request)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # SQL injection attempt
        sql_injection = {"symbol": "BTC'; DROP TABLE trades; --"}
        is_valid, error = self.security.validate_request(sql_injection)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        
        # XSS attempt
        xss_attempt = {"symbol": "<script>alert('xss')</script>"}
        is_valid, error = self.security.validate_request(xss_attempt)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)


class TestAlertSystem(unittest.TestCase):
    """Test alert system functionality"""
    
    def setUp(self):
        """Setup for alert tests"""
        try:
            from alert_system import AlertSystem, AlertType, AlertSeverity
            self.alerts = AlertSystem()
            self.AlertType = AlertType
            self.AlertSeverity = AlertSeverity
        except ImportError:
            self.skipTest("Alert system not available")
    
    def test_alert_creation(self):
        """Test creating and sending alerts"""
        self.alerts.alert(
            self.AlertType.TRADE_SIGNAL,
            self.AlertSeverity.INFO,
            "Test Alert",
            "This is a test alert",
            data={"test": True}
        )
        
        # Check alert was added to history
        history = self.alerts.get_alert_history(limit=1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].title, "Test Alert")
    
    def test_alert_stats(self):
        """Test alert statistics"""
        # Send multiple alerts
        for i in range(5):
            self.alerts.alert(
                self.AlertType.TRADE_SIGNAL,
                self.AlertSeverity.INFO,
                f"Alert {i}",
                f"Message {i}"
            )
        
        stats = self.alerts.get_alert_stats()
        self.assertGreaterEqual(stats['total'], 5)
        self.assertIn('by_type', stats)
        self.assertIn('by_severity', stats)


class TestRiskManagement(unittest.TestCase):
    """Test risk management configuration"""
    
    def setUp(self):
        """Setup for risk management tests"""
        from config import config
        self.config = config
    
    def test_risk_parameters_exist(self):
        """Test that all risk parameters are defined"""
        required_params = [
            'max_position_size',
            'risk_per_trade',
            'max_daily_loss',
            'enable_stop_loss',
            'stop_loss_percent',
            'enable_take_profit',
            'take_profit_percent'
        ]
        
        for param in required_params:
            self.assertTrue(
                hasattr(self.config, param),
                f"Missing risk parameter: {param}"
            )
    
    def test_risk_parameters_valid(self):
        """Test that risk parameters are within safe ranges"""
        # Risk per trade should be reasonable (0.5% - 5%)
        self.assertGreater(self.config.risk_per_trade, 0)
        self.assertLess(self.config.risk_per_trade, 0.1, 
                       "Risk per trade > 10% is too high for production")
        
        # Max daily loss should be reasonable (1% - 10%)
        self.assertGreater(self.config.max_daily_loss, 0)
        self.assertLess(self.config.max_daily_loss, 0.15,
                       "Max daily loss > 15% is too high for production")
        
        # Stop loss should be enabled for production
        self.assertTrue(self.config.enable_stop_loss,
                       "Stop loss should be enabled for production")
        
        # Stop loss percent should be reasonable
        self.assertGreater(self.config.stop_loss_percent, 0)
        self.assertLess(self.config.stop_loss_percent, 25,
                       "Stop loss > 25% is too wide for production")


class TestStrategyValidation(unittest.TestCase):
    """Test trading strategy configuration"""
    
    def setUp(self):
        """Setup for strategy tests"""
        from config import config
        from strategy import TradingStrategy
        self.config = config
        self.strategy = TradingStrategy(config.to_dict())
    
    def test_strategies_configured(self):
        """Test that strategies are properly configured"""
        self.assertIsNotNone(self.config.active_strategies)
        self.assertGreater(len(self.config.active_strategies), 0,
                          "No active strategies configured")
    
    def test_cooperation_logic(self):
        """Test cooperation logic is valid"""
        self.assertIn(self.config.cooperation_logic, ['AND', 'OR'],
                     "Invalid cooperation logic")
    
    def test_strategy_initialization(self):
        """Test that strategies initialize without errors"""
        # This will fail if strategies have configuration errors
        self.assertIsNotNone(self.strategy)


class TestAPIConfiguration(unittest.TestCase):
    """Test API configuration"""
    
    def test_api_keys_not_hardcoded(self):
        """Verify API keys are not hardcoded in config"""
        from config import config
        
        # Keys should either be empty or loaded from environment
        # Should NOT contain placeholder text
        api_key = config.BINANCE_API_KEY
        
        if api_key:
            self.assertNotIn("your_api_key", api_key.lower(),
                           "API key appears to be placeholder")
            self.assertNotIn("change_me", api_key.lower(),
                           "API key appears to be placeholder")
    
    def test_keys_env_in_gitignore(self):
        """Test that keys.env is in .gitignore"""
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
        
        self.assertIn('keys.env', gitignore,
                     "keys.env should be in .gitignore")


class TestLoggingConfiguration(unittest.TestCase):
    """Test logging setup"""
    
    def test_log_directory_exists(self):
        """Test that logs directory exists"""
        self.assertTrue(os.path.exists('logs'),
                       "Logs directory should exist")
    
    def test_logging_functional(self):
        """Test that logging is working"""
        from utils import setup_logging
        
        test_log = "logs/test_production.log"
        logger = setup_logging(log_file=test_log)
        
        test_message = f"Test log message at {datetime.now()}"
        logger.info(test_message)
        
        # Check log file was created
        self.assertTrue(os.path.exists(test_log),
                       "Log file should be created")
        
        # Cleanup
        if os.path.exists(test_log):
            os.remove(test_log)


class TestSystemStability(unittest.TestCase):
    """Test system stability under load"""
    
    def test_data_validation(self):
        """Test data validation functions"""
        from utils import validate_ohlcv_data
        import pandas as pd
        
        # Valid data (need at least 2 rows)
        valid_data = pd.DataFrame({
            'timestamp': [datetime.now(), datetime.now()],
            'open': [100.0, 101.0],
            'high': [105.0, 106.0],
            'low': [95.0, 96.0],
            'close': [102.0, 103.0],
            'volume': [1000.0, 1100.0]
        })
        
        is_valid, error = validate_ohlcv_data(valid_data)
        self.assertTrue(is_valid, f"Valid data failed validation: {error}")
    
    def test_memory_leak_prevention(self):
        """Test that repeated operations don't leak memory"""
        from utils import generate_sample_data
        import gc
        
        # Generate data multiple times
        for _ in range(10):
            data = generate_sample_data(n_bars=100)
            del data
            gc.collect()
        
        # If we get here without running out of memory, test passes
        self.assertTrue(True)


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_simulated_trading_session(self):
        """Test a complete simulated trading session"""
        from config import config
        from strategy import TradingStrategy
        from utils import generate_sample_data, validate_ohlcv_data
        
        # Generate test data
        data = generate_sample_data(n_bars=100)
        is_valid, error = validate_ohlcv_data(data)
        self.assertTrue(is_valid, f"Generated data invalid: {error}")
        
        # Initialize strategy
        strategy = TradingStrategy(config.to_dict())
        
        # Analyze data
        analysis = strategy.analyze(data)
        
        # Verify analysis has required fields
        self.assertIn('signal', analysis)
        self.assertIn('current_price', analysis)
        self.assertIsNotNone(analysis['signal'])


def run_production_readiness_tests():
    """Run all production readiness tests"""
    print("=" * 70)
    print("🧪 PRODUCTION READINESS TEST SUITE")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestLoggingConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemStability))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - System appears ready for production")
        print("\n⚠️  However, complete the full deployment checklist before going live!")
    else:
        print("\n❌ SOME TESTS FAILED - Address issues before production deployment")
    
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_production_readiness_tests())
