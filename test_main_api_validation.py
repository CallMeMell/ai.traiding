"""
test_main_api_validation.py - Tests für API-Key Validierung in main.py
========================================================================
Tests für die API-Key-Validierung vor dem Live-Trading Start.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the validation function
from main import validate_api_keys_for_live_trading


class TestValidateApiKeysForLiveTrading(unittest.TestCase):
    """Tests für API-Key Validierung Funktion."""
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890"
    })
    @patch('main.config')
    def test_valid_api_keys_from_env(self, mock_config):
        """Test mit gültigen API-Keys aus Environment."""
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = None
        
        success, message = validate_api_keys_for_live_trading()
        self.assertTrue(success)
        self.assertIn("validiert", message.lower())
        self.assertIn("bereit", message.lower())
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('main.config')
    def test_valid_api_keys_from_config(self, mock_config):
        """Test mit gültigen API-Keys aus Config."""
        mock_config.BINANCE_API_KEY = "valid_config_key_1234567890"
        mock_config.BINANCE_SECRET_KEY = "valid_config_secret_1234567890"
        
        success, message = validate_api_keys_for_live_trading()
        self.assertTrue(success)
        self.assertIn("validiert", message.lower())
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('main.config')
    def test_missing_api_key(self, mock_config):
        """Test ohne API-Key."""
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = "valid_test_secret_1234567890"
        
        success, message = validate_api_keys_for_live_trading()
        self.assertFalse(success)
        self.assertIn("fehlt", message.lower())
        self.assertIn("api_key", message.lower())
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('main.config')
    def test_missing_api_secret(self, mock_config):
        """Test ohne API-Secret."""
        mock_config.BINANCE_API_KEY = "valid_test_key_1234567890"
        mock_config.BINANCE_SECRET_KEY = None
        
        success, message = validate_api_keys_for_live_trading()
        self.assertFalse(success)
        self.assertIn("fehlt", message.lower())
        self.assertIn("secret", message.lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "short",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890"
    })
    @patch('main.config')
    def test_invalid_api_key_too_short(self, mock_config):
        """Test mit zu kurzem API-Key."""
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = None
        
        success, message = validate_api_keys_for_live_trading()
        self.assertFalse(success)
        self.assertIn("ungültig", message.lower())
        self.assertIn("kurz", message.lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "short"
    })
    @patch('main.config')
    def test_invalid_api_secret_too_short(self, mock_config):
        """Test mit zu kurzem API-Secret."""
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = None
        
        success, message = validate_api_keys_for_live_trading()
        self.assertFalse(success)
        self.assertIn("ungültig", message.lower())
        self.assertIn("secret", message.lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "",
        "BINANCE_API_SECRET": ""
    })
    @patch('main.config')
    def test_empty_api_keys(self, mock_config):
        """Test mit leeren API-Keys."""
        mock_config.BINANCE_API_KEY = ""
        mock_config.BINANCE_SECRET_KEY = ""
        
        success, message = validate_api_keys_for_live_trading()
        self.assertFalse(success)
        self.assertIn("fehlt", message.lower())


class TestLiveTradingBotApiValidation(unittest.TestCase):
    """Tests für API-Key Validierung im LiveTradingBot."""
    
    @patch.dict(os.environ, {
        "DRY_RUN": "false",
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890"
    })
    @patch('main.setup_logging')
    @patch('main.config')
    @patch('main.BINANCE_AVAILABLE', False)
    def test_live_mode_with_valid_keys(self, mock_config, mock_logging):
        """Test Live-Modus mit gültigen API-Keys."""
        from main import LiveTradingBot
        
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger
        
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = None
        mock_config.log_level = "INFO"
        mock_config.log_file = "test.log"
        mock_config.log_max_bytes = 10000000
        mock_config.log_backup_count = 5
        mock_config.initial_capital = 10000
        mock_config.trading_symbol = "BTC/USDT"
        mock_config.update_interval = 60
        mock_config.active_strategies = ["golden_cross"]
        mock_config.cooperation_logic = "any"
        mock_config.trades_file = "data/trades.csv"
        mock_config.to_dict = MagicMock(return_value={})
        
        # Should not raise exception - use_live_data=True, paper_trading=False, DRY_RUN=false
        bot = LiveTradingBot(use_live_data=True, paper_trading=False)
        self.assertIsNotNone(bot)
        # Verify logger was called with validation success message
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        self.assertTrue(
            any("API-Keys validiert" in str(call) for call in info_calls),
            f"Expected API-Keys validation message in logger.info calls: {info_calls}"
        )
    
    @patch.dict(os.environ, {
        "DRY_RUN": "false",
        "BINANCE_API_KEY": "",
        "BINANCE_API_SECRET": ""
    })
    @patch('main.setup_logging')
    @patch('main.config')
    @patch('main.BINANCE_AVAILABLE', False)
    def test_live_mode_without_keys_raises_exception(self, mock_config, mock_logging):
        """Test Live-Modus ohne API-Keys wirft Exception."""
        from main import LiveTradingBot
        
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger
        
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = None
        mock_config.log_level = "INFO"
        mock_config.log_file = "test.log"
        mock_config.log_max_bytes = 10000000
        mock_config.log_backup_count = 5
        mock_config.initial_capital = 10000
        mock_config.trading_symbol = "BTC/USDT"
        mock_config.update_interval = 60
        mock_config.active_strategies = ["golden_cross"]
        mock_config.cooperation_logic = "any"
        mock_config.trades_file = "data/trades.csv"
        mock_config.to_dict = MagicMock(return_value={})
        
        # Should raise exception - use_live_data=True, paper_trading=False, DRY_RUN=false
        with self.assertRaises(Exception) as context:
            LiveTradingBot(use_live_data=True, paper_trading=False)
        
        self.assertIn("api", str(context.exception).lower())
        # Verify critical logging was called
        mock_logger.critical.assert_called()
    
    @patch.dict(os.environ, {
        "DRY_RUN": "true",
        "BINANCE_API_KEY": "",
        "BINANCE_API_SECRET": ""
    })
    @patch('main.setup_logging')
    @patch('main.config')
    @patch('main.BINANCE_AVAILABLE', False)
    def test_dry_run_mode_without_keys_no_exception(self, mock_config, mock_logging):
        """Test DRY_RUN Modus ohne API-Keys wirft keine Exception."""
        from main import LiveTradingBot
        
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger
        
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = None
        mock_config.log_level = "INFO"
        mock_config.log_file = "test.log"
        mock_config.log_max_bytes = 10000000
        mock_config.log_backup_count = 5
        mock_config.initial_capital = 10000
        mock_config.trading_symbol = "BTC/USDT"
        mock_config.update_interval = 60
        mock_config.active_strategies = ["golden_cross"]
        mock_config.cooperation_logic = "any"
        mock_config.trades_file = "data/trades.csv"
        mock_config.to_dict = MagicMock(return_value={})
        
        # Should not raise exception (DRY_RUN allows missing keys)
        # use_live_data=True, paper_trading=False triggers validation check
        bot = LiveTradingBot(use_live_data=True, paper_trading=False)
        self.assertIsNotNone(bot)
        # Verify warning was logged (DRY_RUN=true with invalid keys)
        warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
        self.assertTrue(
            any("API-KEY WARNUNG" in str(call) or "API" in str(call) for call in warning_calls),
            f"Expected API warning in logger.warning calls: {warning_calls}"
        )


class TestMainWithDashboardApiValidation(unittest.TestCase):
    """Tests für API-Key Validierung in main_with_dashboard.py."""
    
    @patch.dict(os.environ, {
        "DRY_RUN": "true",
        "BINANCE_API_KEY": "",
        "BINANCE_API_SECRET": ""
    })
    @patch('main_with_dashboard.setup_logging')
    @patch('main_with_dashboard.create_dashboard')
    @patch('main_with_dashboard.config')
    def test_dashboard_displays_api_warning(self, mock_config, mock_create_dashboard, mock_logging):
        """Test Dashboard zeigt API-Key Warnung an."""
        from main_with_dashboard import LiveTradingBotWithDashboard
        
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger
        
        mock_dashboard = MagicMock()
        mock_dashboard.display_api_key_warning = MagicMock()
        mock_create_dashboard.return_value = mock_dashboard
        
        mock_config.BINANCE_API_KEY = None
        mock_config.BINANCE_SECRET_KEY = None
        mock_config.log_level = "INFO"
        mock_config.log_file = "test.log"
        mock_config.log_max_bytes = 10000000
        mock_config.log_backup_count = 5
        mock_config.initial_capital = 10000
        mock_config.trading_symbol = "BTC/USDT"
        mock_config.update_interval = 60
        mock_config.active_strategies = ["golden_cross"]
        mock_config.cooperation_logic = "any"
        mock_config.trades_file = "data/trades_test.csv"
        mock_config.to_dict = MagicMock(return_value={})
        
        # Create bot - should not raise exception in DRY_RUN
        bot = LiveTradingBotWithDashboard()
        
        # Check that dashboard is initialized
        self.assertIsNotNone(bot.dashboard)
        # Check that display_api_key_warning method exists
        self.assertTrue(hasattr(bot.dashboard, 'display_api_key_warning'))
        # Verify display_api_key_warning was called
        mock_dashboard.display_api_key_warning.assert_called_once()


if __name__ == "__main__":
    print("=" * 60)
    print("API-Key Validierung in main.py - Test Suite")
    print("=" * 60)
    print()
    
    # Run tests with verbose output
    unittest.main(verbosity=2)
