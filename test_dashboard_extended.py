"""
test_dashboard_extended.py - Tests for Extended Dashboard Metrics
=================================================================
Tests for the dashboard's display of real-money flag and extended metrics
"""
import os
import sys
import unittest
import tempfile
import shutil

from dashboard import VisualDashboard, DashboardConfig, create_dashboard
from utils import save_trades_to_csv


class TestDashboardExtended(unittest.TestCase):
    """Test extended dashboard functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.trades_file = os.path.join(self.temp_dir, "trades.csv")
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        # Create sample trades with new fields
        sample_trades = [
            {
                'timestamp': '2024-01-01T10:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': '30000.00',
                'quantity': '0.1',
                'triggering_strategies': 'RSI, MACD',
                'capital': '10000.00',
                'pnl': '0.00',
                'is_real_money': False,
                'profit_factor': '0.00',
                'win_rate': '0.00',
                'sharpe_ratio': '0.00'
            },
            {
                'timestamp': '2024-01-01T12:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': '31000.00',
                'quantity': '0.1',
                'triggering_strategies': 'RSI',
                'capital': '10500.00',
                'pnl': '500.00',
                'is_real_money': True,
                'profit_factor': '1.50',
                'win_rate': '100.00',
                'sharpe_ratio': '1.20'
            },
            {
                'timestamp': '2024-01-01T14:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': '30500.00',
                'quantity': '0.1',
                'triggering_strategies': 'MACD',
                'capital': '10500.00',
                'pnl': '0.00',
                'is_real_money': False,
                'profit_factor': '1.50',
                'win_rate': '50.00',
                'sharpe_ratio': '0.80'
            },
            {
                'timestamp': '2024-01-01T16:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': '30200.00',
                'quantity': '0.1',
                'triggering_strategies': 'EMA',
                'capital': '10470.00',
                'pnl': '-30.00',
                'is_real_money': False,
                'profit_factor': '1.20',
                'win_rate': '50.00',
                'sharpe_ratio': '0.70'
            }
        ]
        
        save_trades_to_csv(sample_trades, self.trades_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_config_includes_new_metrics(self):
        """Test that default config includes new metrics"""
        config = DashboardConfig(self.config_file)
        
        self.assertIn('profit_factor', config.metrics)
        self.assertIn('sharpe_ratio', config.metrics)
        self.assertIn('real_money_trades', config.metrics)
        self.assertIn('dry_run_trades', config.metrics)
    
    def test_get_metrics_includes_trade_counts(self):
        """Test that get_metrics returns real money and dry run counts"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        metrics = dashboard.get_metrics()
        
        self.assertIn('real_money_trades', metrics)
        self.assertIn('dry_run_trades', metrics)
        
        # Should have 1 real money trade and 3 dry run trades
        self.assertEqual(metrics['real_money_trades'], 1)
        self.assertEqual(metrics['dry_run_trades'], 3)
    
    def test_metrics_filtering_works(self):
        """Test that only configured metrics are returned"""
        # Create custom config with limited metrics
        config = DashboardConfig(self.config_file)
        config.metrics = ['real_money_trades', 'dry_run_trades', 'profit_factor']
        config.save_config()
        
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        metrics = dashboard.get_metrics()
        
        # Should only have the 3 configured metrics
        self.assertEqual(len(metrics), 3)
        self.assertIn('real_money_trades', metrics)
        self.assertIn('dry_run_trades', metrics)
        self.assertIn('profit_factor', metrics)
    
    def test_console_display_runs(self):
        """Test that console display works without errors"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        
        # Should not raise any exceptions
        try:
            dashboard.display_metrics_console()
            success = True
        except Exception as e:
            print(f"Console display failed: {e}")
            success = False
        
        self.assertTrue(success)
    
    def test_html_export_includes_new_metrics(self):
        """Test that HTML export includes new metrics"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        output_file = os.path.join(self.temp_dir, "dashboard.html")
        
        dashboard.export_dashboard_html(output_file)
        
        self.assertTrue(os.path.exists(output_file))
        
        # Read HTML and check for new metrics
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check that real money and dry run indicators are present
        self.assertIn('💰', html_content)  # Real money emoji
        self.assertIn('🧪', html_content)  # Dry run emoji
    
    def test_create_dashboard_factory(self):
        """Test that factory function works with extended functionality"""
        # This should use default file paths, but we can verify it creates
        dashboard = create_dashboard()
        
        self.assertIsInstance(dashboard, VisualDashboard)
        self.assertIsNotNone(dashboard.config)
        
        # Verify new metrics are in default config
        self.assertIn('profit_factor', dashboard.config.metrics)
        self.assertIn('real_money_trades', dashboard.config.metrics)


if __name__ == '__main__':
    unittest.main()
