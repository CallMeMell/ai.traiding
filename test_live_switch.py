"""
test_live_switch.py - Tests for Live Trading Mode Switcher
==========================================================
Tests für die Live-Umschaltung Funktionalität.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation import live_switch


class TestCheckApiKey(unittest.TestCase):
    """Tests für API-Key Validierung."""
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890"
    })
    def test_valid_api_keys(self):
        """Test mit gültigen API-Keys."""
        success, message = live_switch.check_api_key()
        self.assertTrue(success)
        self.assertIn("gültig", message.lower())
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test ohne API-Key."""
        success, message = live_switch.check_api_key()
        self.assertFalse(success)
        self.assertIn("fehlt", message.lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890"
    }, clear=True)
    def test_missing_api_secret(self):
        """Test ohne API-Secret."""
        success, message = live_switch.check_api_key()
        self.assertFalse(success)
        self.assertIn("fehlt", message.lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "short",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890"
    })
    def test_invalid_api_key_too_short(self):
        """Test mit zu kurzem API-Key."""
        success, message = live_switch.check_api_key()
        self.assertFalse(success)
        self.assertIn("ungültig", message.lower())


class TestCheckEnvironmentReady(unittest.TestCase):
    """Tests für Umgebungs-Validierung."""
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890",
        "BINANCE_BASE_URL": "https://api.binance.com",
        "KILL_SWITCH": "false"
    })
    def test_environment_ready(self):
        """Test mit bereiter Umgebung."""
        success, message = live_switch.check_environment_ready()
        self.assertTrue(success)
        self.assertIn("bereit", message.lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890",
        "BINANCE_BASE_URL": "https://testnet.binance.vision",
        "KILL_SWITCH": "false"
    })
    def test_wrong_base_url(self):
        """Test mit falschem Base-URL (Testnet statt Production)."""
        success, message = live_switch.check_environment_ready()
        self.assertFalse(success)
        self.assertIn("production", message.lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890",
        "KILL_SWITCH": "true"
    })
    def test_kill_switch_active(self):
        """Test mit aktivem KILL_SWITCH."""
        success, message = live_switch.check_environment_ready()
        self.assertFalse(success)
        self.assertIn("kill_switch", message.lower())


class TestConfirmLiveSwitch(unittest.TestCase):
    """Tests für Bestätigungs-Dialog."""
    
    def test_force_confirmation(self):
        """Test mit force=True (keine Bestätigung erforderlich)."""
        result = live_switch.confirm_live_switch(force=True)
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='LIVE_TRADING_BESTÄTIGT')
    def test_correct_confirmation(self, mock_input):
        """Test mit korrekter Bestätigung."""
        result = live_switch.confirm_live_switch(force=False)
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='wrong_input')
    def test_wrong_confirmation(self, mock_input):
        """Test mit falscher Bestätigung."""
        result = live_switch.confirm_live_switch(force=False)
        self.assertFalse(result)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt(self, mock_input):
        """Test mit Keyboard-Interrupt."""
        result = live_switch.confirm_live_switch(force=False)
        self.assertFalse(result)


class TestSwitchToLive(unittest.TestCase):
    """Tests für Umschaltung zu Live-Modus."""
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890",
        "KILL_SWITCH": "false"
    })
    @patch('automation.live_switch.confirm_live_switch', return_value=True)
    @patch('automation.live_switch.run_preflight_checks', return_value=(True, "Checks passed"))
    def test_switch_to_live_success(self, mock_preflight, mock_confirm):
        """Test erfolgreiche Umschaltung zu Live-Modus."""
        result = live_switch.switch_to_live(force=True, skip_preflight=False)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["mode"], "LIVE")
        self.assertFalse(result["dry_run"])
        self.assertTrue(result["live_trading"])
        self.assertEqual(result["base_url"], "https://api.binance.com")
        
        # Prüfe Environment-Variablen
        self.assertEqual(os.getenv("DRY_RUN"), "false")
        self.assertEqual(os.getenv("LIVE_TRADING"), "true")
        self.assertEqual(os.getenv("BINANCE_BASE_URL"), "https://api.binance.com")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_switch_to_live_missing_api_key(self):
        """Test Umschaltung ohne API-Key (sollte Exception werfen)."""
        with self.assertRaises(Exception) as context:
            live_switch.switch_to_live(force=True, skip_preflight=True)
        
        self.assertIn("fehlt", str(context.exception).lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890",
        "KILL_SWITCH": "false"
    })
    @patch('automation.live_switch.confirm_live_switch', return_value=False)
    def test_switch_to_live_no_confirmation(self, mock_confirm):
        """Test Umschaltung ohne Bestätigung."""
        result = live_switch.switch_to_live(force=False, skip_preflight=True)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["mode"], "DRY_RUN")
        self.assertIn("verweigert", result["reason"].lower())
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890",
        "KILL_SWITCH": "true"
    })
    def test_switch_to_live_kill_switch_active(self):
        """Test Umschaltung mit aktivem KILL_SWITCH."""
        with self.assertRaises(Exception) as context:
            live_switch.switch_to_live(force=True, skip_preflight=True)
        
        self.assertIn("kill_switch", str(context.exception).lower())


class TestSwitchToDryRun(unittest.TestCase):
    """Tests für Umschaltung zu DRY_RUN Modus."""
    
    @patch.dict(os.environ, {
        "DRY_RUN": "false",
        "LIVE_TRADING": "true"
    })
    def test_switch_to_dry_run(self):
        """Test Umschaltung zu DRY_RUN."""
        result = live_switch.switch_to_dry_run()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["mode"], "DRY_RUN")
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["live_trading"])
        self.assertIn("testnet", result["base_url"].lower())
        
        # Prüfe Environment-Variablen
        self.assertEqual(os.getenv("DRY_RUN"), "true")
        self.assertEqual(os.getenv("LIVE_TRADING"), "false")


class TestGetCurrentMode(unittest.TestCase):
    """Tests für aktuellen Modus abrufen."""
    
    @patch.dict(os.environ, {
        "DRY_RUN": "false",
        "LIVE_TRADING": "true",
        "BINANCE_BASE_URL": "https://api.binance.com",
        "KILL_SWITCH": "false",
        "LIVE_ACK": "I_UNDERSTAND"
    })
    def test_get_current_mode_live(self):
        """Test get_current_mode im LIVE Modus."""
        status = live_switch.get_current_mode()
        
        self.assertEqual(status["mode"], "LIVE")
        self.assertFalse(status["dry_run"])
        self.assertTrue(status["live_trading"])
        self.assertEqual(status["base_url"], "https://api.binance.com")
        self.assertFalse(status["kill_switch"])
        self.assertEqual(status["live_ack"], "I_UNDERSTAND")
        self.assertFalse(status["is_safe_mode"])
    
    @patch.dict(os.environ, {
        "DRY_RUN": "true",
        "LIVE_TRADING": "false",
        "BINANCE_BASE_URL": "https://testnet.binance.vision",
        "KILL_SWITCH": "false",
        "LIVE_ACK": ""
    })
    def test_get_current_mode_dry_run(self):
        """Test get_current_mode im DRY_RUN Modus."""
        status = live_switch.get_current_mode()
        
        self.assertEqual(status["mode"], "DRY_RUN")
        self.assertTrue(status["dry_run"])
        self.assertFalse(status["live_trading"])
        self.assertIn("testnet", status["base_url"].lower())
        self.assertFalse(status["kill_switch"])
        self.assertEqual(status["live_ack"], "")
        self.assertTrue(status["is_safe_mode"])
    
    @patch.dict(os.environ, {
        "DRY_RUN": "false",
        "LIVE_TRADING": "true",
        "KILL_SWITCH": "true"
    })
    def test_get_current_mode_kill_switch(self):
        """Test get_current_mode mit KILL_SWITCH."""
        status = live_switch.get_current_mode()
        
        self.assertTrue(status["kill_switch"])
        self.assertTrue(status["is_safe_mode"])  # KILL_SWITCH aktiviert Safe Mode


class TestIntegration(unittest.TestCase):
    """Integrationstests für komplette Workflows."""
    
    @patch.dict(os.environ, {
        "BINANCE_API_KEY": "valid_test_key_1234567890",
        "BINANCE_API_SECRET": "valid_test_secret_1234567890",
        "DRY_RUN": "true",
        "LIVE_TRADING": "false",
        "KILL_SWITCH": "false"
    })
    @patch('automation.live_switch.confirm_live_switch', return_value=True)
    @patch('automation.live_switch.run_preflight_checks', return_value=(True, "All checks passed"))
    def test_full_workflow_dry_to_live(self, mock_preflight, mock_confirm):
        """Test kompletter Workflow von DRY_RUN zu LIVE."""
        # Start im DRY_RUN Modus
        initial_status = live_switch.get_current_mode()
        self.assertEqual(initial_status["mode"], "DRY_RUN")
        
        # Wechsel zu LIVE
        result = live_switch.switch_to_live(force=True, skip_preflight=False)
        self.assertTrue(result["success"])
        
        # Prüfe neuen Status
        new_status = live_switch.get_current_mode()
        self.assertEqual(new_status["mode"], "LIVE")
        self.assertFalse(new_status["dry_run"])
        self.assertTrue(new_status["live_trading"])
    
    @patch.dict(os.environ, {
        "DRY_RUN": "false",
        "LIVE_TRADING": "true"
    })
    def test_full_workflow_live_to_dry(self):
        """Test kompletter Workflow von LIVE zu DRY_RUN."""
        # Start im LIVE Modus
        initial_status = live_switch.get_current_mode()
        self.assertEqual(initial_status["mode"], "LIVE")
        
        # Wechsel zu DRY_RUN
        result = live_switch.switch_to_dry_run()
        self.assertTrue(result["success"])
        
        # Prüfe neuen Status
        new_status = live_switch.get_current_mode()
        self.assertEqual(new_status["mode"], "DRY_RUN")
        self.assertTrue(new_status["dry_run"])
        self.assertFalse(new_status["live_trading"])


if __name__ == "__main__":
    print("=" * 60)
    print("Live Trading Mode Switcher - Test Suite")
    print("=" * 60)
    print()
    
    # Run tests with verbose output
    unittest.main(verbosity=2)
