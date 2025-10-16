"""
test_config_root.py - Tests for root config.py
==============================================
Tests for the TradingConfig dataclass.
"""

import unittest
import os
import tempfile
import shutil
import json
from unittest.mock import patch

# Import config
from config import TradingConfig


class TestTradingConfig(unittest.TestCase):
    """Tests for TradingConfig class"""
    
    def test_config_initialization(self):
        """Test config initialization with defaults"""
        config = TradingConfig()
        
        self.assertIsInstance(config.initial_capital, float)
        self.assertEqual(config.trading_symbol, "BTC/USDT")
        self.assertEqual(config.timeframe, "15m")
    
    def test_validate_valid_config(self):
        """Test validate with valid configuration"""
        config = TradingConfig()
        
        is_valid, error = config.validate()
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_invalid_initial_capital(self):
        """Test validate with invalid initial capital"""
        config = TradingConfig()
        config.initial_capital = -100
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("initial_capital", error.lower())
    
    def test_validate_invalid_initial_capital_zero(self):
        """Test validate with zero initial capital"""
        config = TradingConfig()
        config.initial_capital = 0
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("initial_capital", error.lower())
    
    def test_validate_invalid_risk_per_trade_negative(self):
        """Test validate with negative risk per trade"""
        config = TradingConfig()
        config.risk_per_trade = -0.1
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("risk_per_trade", error.lower())
    
    def test_validate_invalid_risk_per_trade_over_one(self):
        """Test validate with risk_per_trade > 1"""
        config = TradingConfig()
        config.risk_per_trade = 1.5
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("risk_per_trade", error.lower())
    
    def test_validate_invalid_cooperation_logic(self):
        """Test validate with invalid cooperation logic"""
        config = TradingConfig()
        config.cooperation_logic = "INVALID"
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("cooperation_logic", error.lower())
    
    def test_validate_invalid_stop_loss_percent_negative(self):
        """Test validate with negative stop loss percent"""
        config = TradingConfig()
        config.enable_stop_loss = True
        config.stop_loss_percent = -5
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("stop_loss_percent", error.lower())
    
    def test_validate_invalid_stop_loss_percent_over_fifty(self):
        """Test validate with stop_loss_percent > 50"""
        config = TradingConfig()
        config.enable_stop_loss = True
        config.stop_loss_percent = 60
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("stop_loss_percent", error.lower())
    
    def test_validate_invalid_max_drawdown_negative(self):
        """Test validate with negative max drawdown"""
        config = TradingConfig()
        config.max_drawdown_limit = -0.1
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("max_drawdown_limit", error.lower())
    
    def test_validate_invalid_max_drawdown_over_one(self):
        """Test validate with max_drawdown_limit > 1"""
        config = TradingConfig()
        config.max_drawdown_limit = 1.5
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("max_drawdown_limit", error.lower())
    
    def test_validate_kelly_criterion_invalid_fraction_negative(self):
        """Test validate with invalid kelly fraction (negative)"""
        config = TradingConfig()
        config.enable_kelly_criterion = True
        config.kelly_fraction = -0.1
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("kelly_fraction", error.lower())
    
    def test_validate_kelly_criterion_invalid_fraction_over_one(self):
        """Test validate with invalid kelly fraction (> 1)"""
        config = TradingConfig()
        config.enable_kelly_criterion = True
        config.kelly_fraction = 1.5
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("kelly_fraction", error.lower())
    
    def test_validate_kelly_criterion_invalid_max_position_negative(self):
        """Test validate with invalid kelly max position (negative)"""
        config = TradingConfig()
        config.enable_kelly_criterion = True
        config.kelly_max_position_pct = -0.1
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("kelly_max_position_pct", error.lower())
    
    def test_validate_kelly_criterion_invalid_max_position_over_one(self):
        """Test validate with invalid kelly max position (> 1)"""
        config = TradingConfig()
        config.enable_kelly_criterion = True
        config.kelly_max_position_pct = 1.5
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("kelly_max_position_pct", error.lower())
    
    def test_validate_kelly_criterion_invalid_lookback_trades(self):
        """Test validate with invalid kelly lookback trades (< 5)"""
        config = TradingConfig()
        config.enable_kelly_criterion = True
        config.kelly_lookback_trades = 3
        
        is_valid, error = config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("kelly_lookback_trades", error.lower())
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        config = TradingConfig()
        
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('initial_capital', config_dict)
        self.assertIn('trading_symbol', config_dict)
    
    def test_save_to_file(self):
        """Test saving config to file"""
        test_dir = tempfile.mkdtemp()
        try:
            config = TradingConfig()
            config.initial_capital = 20000.0
            filepath = os.path.join(test_dir, "config", "test_config.json")
            
            config.save_to_file(filepath)
            
            self.assertTrue(os.path.exists(filepath))
            
            # Verify content
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(data['initial_capital'], 20000.0)
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def test_load_from_file_existing(self):
        """Test loading config from existing file"""
        test_dir = tempfile.mkdtemp()
        try:
            # Create test config file
            config_data = {
                'initial_capital': 15000.0,
                'trading_symbol': 'ETH/USDT',
                'timeframe': '1h'
            }
            filepath = os.path.join(test_dir, "test_config.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f)
            
            # Load config
            config = TradingConfig.load_from_file(filepath)
            
            self.assertEqual(config.initial_capital, 15000.0)
            self.assertEqual(config.trading_symbol, 'ETH/USDT')
            self.assertEqual(config.timeframe, '1h')
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def test_load_from_file_nonexistent(self):
        """Test loading config from non-existent file returns defaults"""
        config = TradingConfig.load_from_file("nonexistent_file.json")
        
        # Should return default config
        self.assertEqual(config.trading_symbol, "BTC/USDT")
        self.assertEqual(config.timeframe, "15m")


if __name__ == '__main__':
    unittest.main()
