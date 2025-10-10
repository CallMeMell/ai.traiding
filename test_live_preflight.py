"""
test_live_preflight.py - Tests for Live Trading Preflight Checks
================================================================
Tests various scenarios for preflight checks including success and failure cases.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

import live_preflight


class TestEnvironmentCheck(unittest.TestCase):
    """Test environment variable validation."""
    
    @patch.dict(os.environ, {
        "LIVE_ACK": "I_UNDERSTAND",
        "DRY_RUN": "false",
        "LIVE_TRADING": "true",
        "BINANCE_BASE_URL": "https://api.binance.com"
    })
    def test_valid_environment(self):
        """Test with all valid environment variables."""
        success, message = live_preflight.check_environment()
        self.assertTrue(success)
        self.assertIn("validated", message.lower())
    
    @patch.dict(os.environ, {"LIVE_ACK": "wrong_value"}, clear=True)
    def test_invalid_live_ack(self):
        """Test with invalid LIVE_ACK."""
        success, message = live_preflight.check_environment()
        self.assertFalse(success)
        self.assertIn("LIVE_ACK", message)
    
    @patch.dict(os.environ, {
        "LIVE_ACK": "I_UNDERSTAND",
        "DRY_RUN": "true"
    }, clear=True)
    def test_dry_run_enabled(self):
        """Test when DRY_RUN is still true."""
        success, message = live_preflight.check_environment()
        self.assertFalse(success)
        self.assertIn("DRY_RUN", message)
    
    @patch.dict(os.environ, {
        "LIVE_ACK": "I_UNDERSTAND",
        "DRY_RUN": "false",
        "LIVE_TRADING": "false"
    }, clear=True)
    def test_live_trading_disabled(self):
        """Test when LIVE_TRADING is false."""
        success, message = live_preflight.check_environment()
        self.assertFalse(success)
        self.assertIn("LIVE_TRADING", message)


class TestCredentialsCheck(unittest.TestCase):
    """Test API credentials validation."""
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_key_1234567890",
        "BINANCE_API_SECRET": "valid_secret_1234567890"
    })
    def test_valid_credentials(self):
        """Test with valid credentials."""
        success, message = live_preflight.check_credentials()
        self.assertTrue(success)
        self.assertIn("validated", message.lower())
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test with missing API key."""
        success, message = live_preflight.check_credentials()
        self.assertFalse(success)
        self.assertIn("BINANCE_API_KEY", message)
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "short",
        "BINANCE_API_SECRET": "valid_secret_1234567890"
    }, clear=True)
    def test_invalid_api_key_length(self):
        """Test with API key that's too short."""
        success, message = live_preflight.check_credentials()
        self.assertFalse(success)
        self.assertIn("too short", message.lower())


class TestTimeSyncCheck(unittest.TestCase):
    """Test time synchronization validation."""
    
    @patch('live_preflight.requests.get')
    @patch('live_preflight.time.time')
    def test_time_sync_ok(self, mock_time, mock_get):
        """Test successful time synchronization."""
        # Mock current time (in seconds)
        mock_time.return_value = 1000.0
        
        # Mock Binance server time (in milliseconds)
        mock_response = MagicMock()
        mock_response.json.return_value = {"serverTime": 1000500}  # 500ms difference
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        success, message = live_preflight.check_time_sync()
        self.assertTrue(success)
        self.assertIn("synchronized", message.lower())
    
    @patch('live_preflight.requests.get')
    @patch('live_preflight.time.time')
    def test_time_sync_too_large(self, mock_time, mock_get):
        """Test time drift too large."""
        mock_time.return_value = 1000.0
        
        # Mock server time with large drift (2000ms)
        mock_response = MagicMock()
        mock_response.json.return_value = {"serverTime": 1002000}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        success, message = live_preflight.check_time_sync()
        self.assertFalse(success)
        self.assertIn("drift", message.lower())


class TestRiskConfigurationCheck(unittest.TestCase):
    """Test risk configuration validation."""
    
    def test_valid_risk_config(self):
        """Test with valid risk configuration."""
        config_content = """
pairs: BTCUSDT
max_risk_per_trade: 0.005
daily_loss_limit: 0.01
max_open_exposure: 0.05
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "live_risk.yaml")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            with patch('live_preflight.os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=config_content)):
                    success, message = live_preflight.check_risk_configuration()
                    self.assertTrue(success)
                    self.assertIn("validated", message.lower())
    
    def test_missing_config_file(self):
        """Test when config file is missing."""
        with patch('live_preflight.os.path.exists', return_value=False):
            success, message = live_preflight.check_risk_configuration()
            self.assertFalse(success)
            self.assertIn("not found", message.lower())
    
    def test_invalid_max_risk(self):
        """Test with invalid max_risk_per_trade."""
        config_content = """
pairs: BTCUSDT
max_risk_per_trade: 0.15
daily_loss_limit: 0.01
max_open_exposure: 0.05
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
"""
        with patch('live_preflight.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_content)):
                success, message = live_preflight.check_risk_configuration()
                self.assertFalse(success)
                self.assertIn("max_risk_per_trade", message)


class TestKillSwitchCheck(unittest.TestCase):
    """Test kill switch status reporting."""
    
    @patch.dict(os.environ, {"KILL_SWITCH": "true"})
    def test_kill_switch_enabled(self):
        """Test when kill switch is enabled."""
        success, message = live_preflight.check_kill_switch()
        self.assertTrue(success)  # Not an error, just informational
        self.assertIn("enabled", message.lower())
    
    @patch.dict(os.environ, {"KILL_SWITCH": "false"})
    def test_kill_switch_disabled(self):
        """Test when kill switch is disabled."""
        success, message = live_preflight.check_kill_switch()
        self.assertTrue(success)
        self.assertIn("disabled", message.lower())
    
    @patch.dict(os.environ, {}, clear=True)
    def test_kill_switch_not_set(self):
        """Test when kill switch is not set (defaults to false)."""
        success, message = live_preflight.check_kill_switch()
        self.assertTrue(success)
        self.assertIn("disabled", message.lower())


class TestOrderTypesCheck(unittest.TestCase):
    """Test order types support validation."""
    
    @patch('live_preflight.requests.get')
    def test_limit_only_supported(self, mock_get):
        """Test LIMIT_ONLY order type support."""
        config_content = """
pairs: BTCUSDT
max_risk_per_trade: 0.005
daily_loss_limit: 0.01
max_open_exposure: 0.05
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "orderTypes": ["LIMIT", "MARKET", "STOP_LOSS_LIMIT"]
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with patch('live_preflight.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_content)):
                success, message = live_preflight.check_order_types_support(["BTCUSDT"])
                self.assertTrue(success)
                self.assertIn("validated", message.lower())
    
    @patch('live_preflight.os.path.exists', return_value=False)
    def test_no_config_skips_check(self, mock_exists):
        """Test that check is skipped when no config exists."""
        success, message = live_preflight.check_order_types_support(["BTCUSDT"])
        self.assertTrue(success)
        self.assertIn("skipped", message.lower())


class TestExchangeInfoCheck(unittest.TestCase):
    """Test exchange information validation."""
    
    @patch('live_preflight.requests.get')
    def test_valid_symbol_with_filters(self, mock_get):
        """Test with valid symbol and all required filters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "filters": [
                        {"filterType": "PRICE_FILTER", "minPrice": "0.01"},
                        {"filterType": "LOT_SIZE", "minQty": "0.00001", "stepSize": "0.00001"},
                        {"filterType": "MIN_NOTIONAL", "minNotional": "10.0"}
                    ]
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        success, message = live_preflight.check_exchange_info(["BTCUSDT"])
        self.assertTrue(success)
        self.assertIn("validated", message.lower())
    
    @patch('live_preflight.requests.get')
    def test_symbol_not_trading(self, mock_get):
        """Test with symbol that's not in TRADING status."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "BREAK",
                    "filters": []
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        success, message = live_preflight.check_exchange_info(["BTCUSDT"])
        self.assertFalse(success)
        self.assertIn("not trading", message.lower())


class TestIntegration(unittest.TestCase):
    """Integration tests for complete preflight checks."""
    
    @patch.dict(os.environ, {
        "LIVE_ACK": "I_UNDERSTAND",
        "DRY_RUN": "false",
        "LIVE_TRADING": "true",
        "BINANCE_BASE_URL": "https://api.binance.com",
        "BINANCE_API_KEY": "valid_key_1234567890",
        "BINANCE_API_SECRET": "valid_secret_1234567890",
        "KILL_SWITCH": "false"
    })
    def test_environment_and_credentials_pass(self):
        """Test that environment and credentials checks pass together."""
        # Test environment
        env_success, env_msg = live_preflight.check_environment()
        self.assertTrue(env_success, f"Environment check failed: {env_msg}")
        
        # Test credentials
        cred_success, cred_msg = live_preflight.check_credentials()
        self.assertTrue(cred_success, f"Credentials check failed: {cred_msg}")
        
        # Test kill switch
        kill_success, kill_msg = live_preflight.check_kill_switch()
        self.assertTrue(kill_success, f"Kill switch check failed: {kill_msg}")


if __name__ == "__main__":
    print("=" * 60)
    print("Live Trading Preflight Checks - Test Suite")
    print("=" * 60)
    print()
    
    # Run tests with verbose output
    unittest.main(verbosity=2)
