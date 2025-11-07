"""
test_reporting_export.py - Tests für Reporting und Export-Funktionen
======================================================================
Unit- und Integration-Tests für erweiterte Reporting-Funktionen,
Performance-Metriken, und Export (CSV/JSON)
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from utils import (
    calculate_roi,
    generate_comprehensive_report,
    export_report_to_csv,
    export_report_to_json,
    export_trades_to_json,
    export_trade_history_with_metrics,
    ReportingModule,
    save_trades_to_csv,
    load_trades_from_csv
)


class TestROICalculation(unittest.TestCase):
    """Test cases for ROI calculation"""
    
    def test_positive_roi(self):
        """Test ROI with profit"""
        initial = 10000.0
        final = 12000.0
        
        roi = calculate_roi(initial, final)
        
        # 20% profit
        self.assertAlmostEqual(roi, 20.0, places=2)
    
    def test_negative_roi(self):
        """Test ROI with loss"""
        initial = 10000.0
        final = 8000.0
        
        roi = calculate_roi(initial, final)
        
        # -20% loss
        self.assertAlmostEqual(roi, -20.0, places=2)
    
    def test_zero_roi(self):
        """Test ROI with no change"""
        initial = 10000.0
        final = 10000.0
        
        roi = calculate_roi(initial, final)
        
        self.assertEqual(roi, 0.0)
    
    def test_invalid_initial_capital(self):
        """Test ROI with invalid initial capital"""
        roi = calculate_roi(0.0, 10000.0)
        self.assertEqual(roi, 0.0)
        
        roi = calculate_roi(-1000.0, 10000.0)
        self.assertEqual(roi, 0.0)


class TestComprehensiveReport(unittest.TestCase):
    """Test cases for comprehensive report generation"""
    
    def setUp(self):
        """Create sample trades for testing"""
        now = datetime.now()
        self.sample_trades = [
            {
                'timestamp': now.isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': '30000.00',
                'quantity': 0.1,
                'pnl': '0.00',
                'capital': '10000.00',
                'is_real_money': False
            },
            {
                'timestamp': (now + timedelta(hours=1)).isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': '31000.00',
                'quantity': 0.1,
                'pnl': '100.00',
                'capital': '10100.00',
                'is_real_money': False
            },
            {
                'timestamp': (now + timedelta(hours=2)).isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': '30500.00',
                'quantity': 0.1,
                'pnl': '0.00',
                'capital': '10100.00',
                'is_real_money': True
            },
            {
                'timestamp': (now + timedelta(hours=3)).isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': '30000.00',
                'quantity': 0.1,
                'pnl': '-50.00',
                'capital': '10050.00',
                'is_real_money': True
            }
        ]
        
        self.equity_curve = [10000, 10100, 10050]
    
    def test_report_with_trades_and_equity(self):
        """Test report generation with trades and equity curve"""
        report = generate_comprehensive_report(
            self.sample_trades,
            self.equity_curve,
            initial_capital=10000.0
        )
        
        # Check basic metrics
        self.assertEqual(report['total_trades'], 4)
        self.assertIn('roi', report)
        self.assertIn('sharpe_ratio', report)
        self.assertIn('max_drawdown', report)
        
        # Check ROI calculation
        expected_roi = calculate_roi(10000.0, 10050.0)
        self.assertAlmostEqual(report['roi'], expected_roi, places=2)
        
        # Check capital tracking
        self.assertEqual(report['initial_capital'], 10000.0)
        self.assertEqual(report['final_capital'], 10050.0)
    
    def test_report_with_trades_only(self):
        """Test report generation with only trades (no equity curve)"""
        report = generate_comprehensive_report(
            self.sample_trades,
            equity_curve=None,
            initial_capital=10000.0
        )
        
        # Should still calculate metrics
        self.assertEqual(report['total_trades'], 4)
        self.assertIn('roi', report)
        self.assertIn('total_pnl', report)
        
        # ROI should be calculated from PnL
        expected_pnl = 100.0 - 50.0  # Net 50
        expected_roi = calculate_roi(10000.0, 10000.0 + expected_pnl)
        self.assertAlmostEqual(report['roi'], expected_roi, places=2)
    
    def test_report_metadata(self):
        """Test report includes metadata"""
        report = generate_comprehensive_report(
            self.sample_trades,
            self.equity_curve,
            initial_capital=10000.0
        )
        
        # Check metadata
        self.assertIn('report_generated_at', report)
        self.assertIn('total_real_money_trades', report)
        self.assertIn('total_dry_run_trades', report)
        
        # Check counts
        self.assertEqual(report['total_real_money_trades'], 2)
        self.assertEqual(report['total_dry_run_trades'], 2)
    
    def test_empty_trades_report(self):
        """Test report with empty trades"""
        report = generate_comprehensive_report(
            [],
            equity_curve=None,
            initial_capital=10000.0
        )
        
        # Should return default values
        self.assertEqual(report['total_trades'], 0)
        self.assertEqual(report['total_pnl'], 0.0)
        self.assertEqual(report['roi'], 0.0)


class TestExportFunctions(unittest.TestCase):
    """Test cases for export functions"""
    
    def setUp(self):
        """Create temporary directory for test exports"""
        self.test_dir = tempfile.mkdtemp()
        
        # Sample data
        self.sample_report = {
            'total_trades': 10,
            'total_pnl': 500.0,
            'roi': 5.0,
            'win_rate': 60.0,
            'sharpe_ratio': 1.5,
            'report_generated_at': datetime.now().isoformat()
        }
        
        self.sample_trades = [
            {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': 30000.0,
                'quantity': 0.1,
                'pnl': 0.0
            },
            {
                'timestamp': (datetime.now() + timedelta(hours=1)).isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': 31000.0,
                'quantity': 0.1,
                'pnl': 100.0
            }
        ]
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_export_report_to_csv(self):
        """Test exporting report to CSV"""
        filepath = os.path.join(self.test_dir, 'report.csv')
        
        result = export_report_to_csv(self.sample_report, filepath)
        
        # Check file was created
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        import pandas as pd
        df = pd.read_csv(filepath)
        self.assertGreater(len(df), 0)
        self.assertIn('metric', df.columns)
        self.assertIn('value', df.columns)
    
    def test_export_report_to_json(self):
        """Test exporting report to JSON"""
        filepath = os.path.join(self.test_dir, 'report.json')
        
        result = export_report_to_json(self.sample_report, filepath)
        
        # Check file was created
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data['total_trades'], 10)
        self.assertEqual(data['roi'], 5.0)
    
    def test_export_trades_to_json(self):
        """Test exporting trades to JSON"""
        filepath = os.path.join(self.test_dir, 'trades.json')
        
        result = export_trades_to_json(self.sample_trades, filepath)
        
        # Check file was created
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['symbol'], 'BTC/USDT')
    
    def test_export_trade_history_with_metrics(self):
        """Test exporting detailed trade history"""
        filepath = os.path.join(self.test_dir, 'trade_history.csv')
        
        result = export_trade_history_with_metrics(self.sample_trades, filepath)
        
        # Check file was created
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        import pandas as pd
        df = pd.read_csv(filepath)
        self.assertEqual(len(df), 2)
        self.assertIn('trade_number', df.columns)
        self.assertIn('cumulative_pnl', df.columns)
        
        # Check cumulative PnL calculation
        self.assertEqual(df.iloc[0]['cumulative_pnl'], 0.0)
        self.assertEqual(df.iloc[1]['cumulative_pnl'], 100.0)
    
    def test_export_empty_data(self):
        """Test exporting empty data"""
        filepath = os.path.join(self.test_dir, 'empty.json')
        
        # Export empty trades
        result = export_trades_to_json([], filepath)
        self.assertIsNone(result)
        
        # Export empty report
        result = export_report_to_json({}, filepath)
        self.assertIsNone(result)


class TestReportingModule(unittest.TestCase):
    """Integration tests for ReportingModule"""
    
    def setUp(self):
        """Create temporary directory and sample trades file"""
        self.test_dir = tempfile.mkdtemp()
        self.trades_file = os.path.join(self.test_dir, 'trades.csv')
        
        # Create sample trades
        now = datetime.now()
        self.sample_trades = [
            {
                'timestamp': now.isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': '30000.00',
                'quantity': 0.1,
                'pnl': '0.00',
                'capital': '10000.00',
                'is_real_money': False,
                'triggering_strategies': 'RSI',
                'profit_factor': '0.00',
                'win_rate': '0.00',
                'sharpe_ratio': '0.00'
            },
            {
                'timestamp': (now + timedelta(hours=1)).isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': '31000.00',
                'quantity': 0.1,
                'pnl': '100.00',
                'capital': '10100.00',
                'is_real_money': False,
                'triggering_strategies': 'MACD',
                'profit_factor': '2.0',
                'win_rate': '100.0',
                'sharpe_ratio': '1.5'
            }
        ]
        
        # Save to CSV
        save_trades_to_csv(self.sample_trades, self.trades_file)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_load_trades(self):
        """Test loading trades from CSV"""
        module = ReportingModule(self.trades_file)
        trades = module.load_trades()
        
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[0]['symbol'], 'BTC/USDT')
    
    def test_calculate_equity_curve(self):
        """Test equity curve calculation"""
        module = ReportingModule(self.trades_file)
        module.load_trades()
        
        equity_curve = module.calculate_equity_curve(initial_capital=10000.0)
        
        # Should have initial + one per trade
        self.assertEqual(len(equity_curve), 3)
        self.assertEqual(equity_curve[0], 10000.0)
        self.assertEqual(equity_curve[-1], 10100.0)
    
    def test_generate_report(self):
        """Test report generation"""
        module = ReportingModule(self.trades_file)
        report = module.generate_report(initial_capital=10000.0)
        
        # Check report contains all metrics
        self.assertIn('total_trades', report)
        self.assertIn('roi', report)
        self.assertIn('sharpe_ratio', report)
        self.assertIn('total_real_money_trades', report)
        
        # Verify values
        self.assertEqual(report['total_trades'], 2)
        self.assertGreater(report['roi'], 0)  # Profitable
    
    def test_export_all(self):
        """Test exporting all reports"""
        output_dir = os.path.join(self.test_dir, 'reports')
        
        module = ReportingModule(self.trades_file)
        exported_files = module.export_all(output_dir=output_dir, prefix="test")
        
        # Check all files were created
        self.assertIn('report_csv', exported_files)
        self.assertIn('report_json', exported_files)
        self.assertIn('trades_csv', exported_files)
        self.assertIn('trades_json', exported_files)
        self.assertIn('trade_history_detailed', exported_files)
        
        # Verify files exist
        for key, filepath in exported_files.items():
            if filepath:
                self.assertTrue(os.path.exists(filepath), f"File not found: {filepath}")
    
    def test_print_report_summary(self):
        """Test printing report summary (basic smoke test)"""
        module = ReportingModule(self.trades_file)
        
        # Should not raise any exceptions
        try:
            module.print_report_summary()
        except Exception as e:
            self.fail(f"print_report_summary raised exception: {e}")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for real-world scenarios"""
    
    def setUp(self):
        """Create temporary directory"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_full_reporting_workflow(self):
        """Test complete reporting workflow from trades to exports"""
        # Create sample trades
        trades_file = os.path.join(self.test_dir, 'trades.csv')
        
        now = datetime.now()
        trades = []
        capital = 10000.0
        
        # Generate realistic trading scenario
        for i in range(10):
            # Buy
            trades.append({
                'timestamp': (now + timedelta(hours=i*2)).isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'BUY',
                'price': f"{30000 + i*100:.2f}",
                'quantity': 0.1,
                'pnl': '0.00',
                'capital': f"{capital:.2f}",
                'is_real_money': i % 2 == 0,  # Alternate real/dry-run
                'triggering_strategies': 'RSI, MACD',
                'profit_factor': '0.00',
                'win_rate': '0.00',
                'sharpe_ratio': '0.00'
            })
            
            # Sell with profit or loss
            pnl = 100.0 if i % 3 != 0 else -50.0
            capital += pnl
            
            trades.append({
                'timestamp': (now + timedelta(hours=i*2 + 1)).isoformat(),
                'symbol': 'BTC/USDT',
                'order_type': 'SELL',
                'price': f"{30000 + i*100 + 100:.2f}",
                'quantity': 0.1,
                'pnl': f"{pnl:.2f}",
                'capital': f"{capital:.2f}",
                'is_real_money': i % 2 == 0,
                'triggering_strategies': 'MACD',
                'profit_factor': '2.5',
                'win_rate': '70.0',
                'sharpe_ratio': '1.8'
            })
        
        # Save trades
        save_trades_to_csv(trades, trades_file)
        
        # Create reporting module and process
        module = ReportingModule(trades_file)
        report = module.generate_report(initial_capital=10000.0)
        
        # Verify report quality
        self.assertEqual(report['total_trades'], 20)
        self.assertGreater(report['win_rate'], 0)
        self.assertLess(report['win_rate'], 100)
        
        # Export all reports
        output_dir = os.path.join(self.test_dir, 'reports')
        exported_files = module.export_all(output_dir=output_dir)
        
        # Verify all exports
        for filepath in exported_files.values():
            if filepath:
                self.assertTrue(os.path.exists(filepath))
                self.assertGreater(os.path.getsize(filepath), 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestROICalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestComprehensiveReport))
    suite.addTests(loader.loadTestsFromTestCase(TestExportFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestReportingModule))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
