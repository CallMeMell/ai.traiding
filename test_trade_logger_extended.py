"""
test_trade_logger_extended.py - Tests for Extended TradeLogger
===============================================================
Tests for the real-money flag and extended metrics functionality
"""
import os
import sys
import unittest
import tempfile
import shutil
import pandas as pd

from utils import TradeLogger, load_trades_from_csv


class TestTradeLoggerExtended(unittest.TestCase):
    """Test extended TradeLogger functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.trades_file = os.path.join(self.temp_dir, "test_trades.csv")
        self.logger = TradeLogger(self.trades_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_csv_headers_include_new_fields(self):
        """Test that CSV has all required headers including new fields"""
        df = pd.read_csv(self.trades_file)
        
        expected_columns = [
            'timestamp', 'symbol', 'order_type', 'price',
            'quantity', 'triggering_strategies', 'capital', 'pnl',
            'is_real_money', 'profit_factor', 'win_rate', 'sharpe_ratio'
        ]
        
        for col in expected_columns:
            self.assertIn(col, df.columns, f"Missing column: {col}")
    
    def test_log_dry_run_trade(self):
        """Test logging a dry-run trade (default)"""
        self.logger.log_trade(
            order_type='BUY',
            price=30000.0,
            quantity=0.1,
            strategies=['RSI', 'MACD'],
            capital=10000.0,
            pnl=0.0
        )
        
        trades = load_trades_from_csv(self.trades_file)
        self.assertEqual(len(trades), 1)
        
        trade = trades[0]
        # is_real_money should default to False
        self.assertIn('is_real_money', trade)
        self.assertFalse(trade['is_real_money'])
    
    def test_log_real_money_trade(self):
        """Test logging a real-money trade"""
        self.logger.log_trade(
            order_type='BUY',
            price=30000.0,
            quantity=0.1,
            strategies=['RSI', 'MACD'],
            capital=10000.0,
            pnl=0.0,
            is_real_money=True
        )
        
        trades = load_trades_from_csv(self.trades_file)
        self.assertEqual(len(trades), 1)
        
        trade = trades[0]
        self.assertIn('is_real_money', trade)
        self.assertTrue(trade['is_real_money'])
    
    def test_log_trade_with_metrics(self):
        """Test logging trade with extended metrics"""
        self.logger.log_trade(
            order_type='SELL',
            price=31000.0,
            quantity=0.1,
            strategies=['RSI'],
            capital=10500.0,
            pnl=500.0,
            is_real_money=False,
            profit_factor=1.5,
            win_rate=60.0,
            sharpe_ratio=1.2
        )
        
        trades = load_trades_from_csv(self.trades_file)
        self.assertEqual(len(trades), 1)
        
        trade = trades[0]
        self.assertEqual(float(trade['profit_factor']), 1.5)
        self.assertEqual(float(trade['win_rate']), 60.0)
        self.assertEqual(float(trade['sharpe_ratio']), 1.2)
    
    def test_multiple_trades_mixed_types(self):
        """Test logging multiple trades with mixed real-money flags"""
        # Dry-run trade
        self.logger.log_trade(
            order_type='BUY',
            price=30000.0,
            quantity=0.1,
            strategies=['RSI'],
            capital=10000.0,
            pnl=0.0,
            is_real_money=False
        )
        
        # Real-money trade
        self.logger.log_trade(
            order_type='SELL',
            price=31000.0,
            quantity=0.1,
            strategies=['MACD'],
            capital=10500.0,
            pnl=500.0,
            is_real_money=True
        )
        
        # Another dry-run trade
        self.logger.log_trade(
            order_type='BUY',
            price=30500.0,
            quantity=0.1,
            strategies=['EMA'],
            capital=10500.0,
            pnl=0.0,
            is_real_money=False
        )
        
        trades = load_trades_from_csv(self.trades_file)
        self.assertEqual(len(trades), 3)
        
        # Count real money vs dry run
        real_money_count = sum(1 for t in trades if t['is_real_money'])
        dry_run_count = sum(1 for t in trades if not t['is_real_money'])
        
        self.assertEqual(real_money_count, 1)
        self.assertEqual(dry_run_count, 2)
    
    def test_backward_compatibility(self):
        """Test that trades can still be logged without new optional parameters"""
        # Should work with just the original required parameters
        self.logger.log_trade(
            order_type='BUY',
            price=30000.0,
            quantity=0.1,
            strategies=['RSI'],
            capital=10000.0
        )
        
        trades = load_trades_from_csv(self.trades_file)
        self.assertEqual(len(trades), 1)
        
        trade = trades[0]
        # New fields should have default values
        self.assertFalse(trade['is_real_money'])
        self.assertEqual(float(trade['profit_factor']), 0.0)
        self.assertEqual(float(trade['win_rate']), 0.0)
        self.assertEqual(float(trade['sharpe_ratio']), 0.0)


if __name__ == '__main__':
    unittest.main()
