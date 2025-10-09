"""
test_dashboard.py - Tests for Visual Dashboard
==============================================
Unit tests for dashboard functionality
"""
import os
import sys
import unittest
import json
import tempfile
import shutil
from unittest.mock import patch

from dashboard import (
    DashboardConfig, VisualDashboard, DashboardModal,
    create_dashboard
)
from utils import save_trades_to_csv


class TestDashboardConfig(unittest.TestCase):
    """Test DashboardConfig class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_default_metrics(self):
        """Test default metrics are loaded"""
        config = DashboardConfig(self.config_file)
        self.assertGreater(len(config.metrics), 0)
        self.assertIn('total_pnl', config.metrics)
        self.assertIn('win_rate', config.metrics)
    
    def test_default_charts(self):
        """Test default charts are loaded"""
        config = DashboardConfig(self.config_file)
        self.assertGreater(len(config.charts), 0)
        self.assertTrue(all('type' in c for c in config.charts))
        self.assertTrue(all('title' in c for c in config.charts))
    
    def test_add_metric(self):
        """Test adding a metric"""
        config = DashboardConfig(self.config_file)
        initial_count = len(config.metrics)
        config.add_metric('test_metric')
        self.assertEqual(len(config.metrics), initial_count + 1)
        self.assertIn('test_metric', config.metrics)
    
    def test_remove_metric(self):
        """Test removing a metric"""
        config = DashboardConfig(self.config_file)
        config.add_metric('test_metric')
        config.remove_metric('test_metric')
        self.assertNotIn('test_metric', config.metrics)
    
    def test_add_chart(self):
        """Test adding a chart"""
        config = DashboardConfig(self.config_file)
        initial_count = len(config.charts)
        config.add_chart('bar', 'Test Chart', 'test_data')
        self.assertEqual(len(config.charts), initial_count + 1)
        self.assertTrue(any(c['title'] == 'Test Chart' for c in config.charts))
    
    def test_remove_chart(self):
        """Test removing a chart"""
        config = DashboardConfig(self.config_file)
        config.add_chart('bar', 'Test Chart', 'test_data')
        config.remove_chart('Test Chart')
        self.assertFalse(any(c['title'] == 'Test Chart' for c in config.charts))
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        config = DashboardConfig(self.config_file)
        config.add_metric('custom_metric')
        config.save_config()
        
        # Load in new instance
        new_config = DashboardConfig(self.config_file)
        self.assertIn('custom_metric', new_config.metrics)


class TestVisualDashboard(unittest.TestCase):
    """Test VisualDashboard class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.trades_file = os.path.join(self.temp_dir, "trades.csv")
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        # Create sample trades
        sample_trades = [
            {
                'timestamp': '2024-01-01T10:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': '30000.00',
                'quantity': 100,
                'triggering_strategies': 'rsi, ema',
                'capital': '10000.00',
                'pnl': '0.00'
            },
            {
                'timestamp': '2024-01-01T11:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': '30500.00',
                'quantity': 100,
                'triggering_strategies': 'rsi, ema',
                'capital': '10500.00',
                'pnl': '500.00'
            },
            {
                'timestamp': '2024-01-01T12:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': '30300.00',
                'quantity': 100,
                'triggering_strategies': 'rsi',
                'capital': '10500.00',
                'pnl': '0.00'
            },
            {
                'timestamp': '2024-01-01T13:00:00',
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': '30100.00',
                'quantity': 100,
                'triggering_strategies': 'rsi',
                'capital': '10300.00',
                'pnl': '-200.00'
            }
        ]
        save_trades_to_csv(sample_trades, self.trades_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test dashboard initialization"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        self.assertIsNotNone(dashboard)
        self.assertEqual(dashboard.trades_file, self.trades_file)
    
    def test_get_metrics(self):
        """Test getting metrics"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        metrics = dashboard.get_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_pnl', metrics)
        self.assertIn('win_rate', metrics)
        self.assertIn('total_trades', metrics)
    
    def test_get_pnl_history(self):
        """Test getting P&L history"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        data = dashboard.get_chart_data('pnl_history')
        
        self.assertIn('timestamps', data)
        self.assertIn('pnl', data)
        self.assertGreater(len(data['pnl']), 0)
    
    def test_get_strategy_stats(self):
        """Test getting strategy statistics"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        data = dashboard.get_chart_data('strategy_stats')
        
        self.assertIn('strategies', data)
        self.assertIn('counts', data)
        self.assertGreater(len(data['strategies']), 0)
    
    def test_get_win_loss_distribution(self):
        """Test getting win/loss distribution"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        data = dashboard.get_chart_data('win_loss')
        
        self.assertIn('labels', data)
        self.assertIn('values', data)
        self.assertEqual(len(data['labels']), 2)
        self.assertEqual(len(data['values']), 2)
    
    def test_export_dashboard_html(self):
        """Test exporting dashboard to HTML"""
        dashboard = VisualDashboard(self.trades_file, self.config_file)
        output_file = os.path.join(self.temp_dir, "dashboard.html")
        
        dashboard.export_dashboard_html(output_file)
        
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Trading Bot Dashboard', content)
            self.assertIn('Total Pnl', content)


class TestDashboardModal(unittest.TestCase):
    """Test DashboardModal class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.trades_file = os.path.join(self.temp_dir, "trades.csv")
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        # Create empty trades file
        save_trades_to_csv([], self.trades_file)
        
        self.dashboard = VisualDashboard(self.trades_file, self.config_file)
        self.modal = DashboardModal(self.dashboard)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_modal_open_close(self):
        """Test modal open and close"""
        self.assertFalse(self.modal.is_open)
        self.modal.open()
        self.assertTrue(self.modal.is_open)
        self.modal.close()
        self.assertFalse(self.modal.is_open)
    
    def test_add_metric_when_open(self):
        """Test adding metric when modal is open"""
        self.modal.open()
        result = self.modal.add_metric('test_metric')
        self.assertTrue(result)
        self.assertIn('test_metric', self.dashboard.config.metrics)
    
    def test_add_metric_when_closed(self):
        """Test adding metric when modal is closed"""
        result = self.modal.add_metric('test_metric')
        self.assertFalse(result)
        self.assertNotIn('test_metric', self.dashboard.config.metrics)
    
    def test_remove_metric_when_open(self):
        """Test removing metric when modal is open"""
        self.modal.open()
        self.modal.add_metric('test_metric')
        result = self.modal.remove_metric('test_metric')
        self.assertTrue(result)
        self.assertNotIn('test_metric', self.dashboard.config.metrics)
    
    def test_add_chart_when_open(self):
        """Test adding chart when modal is open"""
        self.modal.open()
        result = self.modal.add_chart('bar', 'Test Chart', 'test_data')
        self.assertTrue(result)
        self.assertTrue(any(c['title'] == 'Test Chart' 
                          for c in self.dashboard.config.charts))
    
    def test_get_available_metrics(self):
        """Test getting available metrics"""
        metrics = self.modal.get_available_metrics()
        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)
    
    def test_get_available_chart_types(self):
        """Test getting available chart types"""
        chart_types = self.modal.get_available_chart_types()
        self.assertIsInstance(chart_types, list)
        self.assertIn('line', chart_types)
        self.assertIn('bar', chart_types)
        self.assertIn('pie', chart_types)
    
    def test_get_available_data_sources(self):
        """Test getting available data sources"""
        sources = self.modal.get_available_data_sources()
        self.assertIsInstance(sources, list)
        self.assertIn('pnl_history', sources)
        self.assertIn('strategy_stats', sources)


class TestFactoryFunction(unittest.TestCase):
    """Test factory function"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.trades_file = os.path.join(self.temp_dir, "trades.csv")
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        # Create empty trades file
        save_trades_to_csv([], self.trades_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_dashboard(self):
        """Test factory function"""
        dashboard = create_dashboard(self.trades_file, self.config_file)
        self.assertIsInstance(dashboard, VisualDashboard)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
