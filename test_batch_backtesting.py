"""
test_batch_backtesting.py - Tests for Batch Backtesting
========================================================
Comprehensive tests for batch backtesting and visualization features
"""
import unittest
import os
import sys
import tempfile
import shutil
import pandas as pd

from batch_backtester import BatchBacktester
from backtester import Backtester
from utils import (
    generate_sample_data,
    generate_equity_curve_chart,
    generate_drawdown_chart,
    generate_pnl_distribution_chart
)
from strategy import (
    MACrossoverStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    EMACrossoverStrategy
)


class TestVisualizationFunctions(unittest.TestCase):
    """Test visualization functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test equity curve
        self.equity_curve = [
            {'timestamp': i, 'capital': 10000 + i * 50} 
            for i in range(100)
        ]
        
        # Create test trades
        self.trades = [
            {'pnl': 100.0 if i % 2 == 0 else -50.0}
            for i in range(20)
        ]
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_equity_curve_matplotlib(self):
        """Test equity curve generation with Matplotlib"""
        output_file = os.path.join(self.test_dir, 'equity_test.png')
        result = generate_equity_curve_chart(
            self.equity_curve,
            output_file,
            use_plotly=False
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_equity_curve_plotly(self):
        """Test equity curve generation with Plotly"""
        output_file = os.path.join(self.test_dir, 'equity_test.html')
        result = generate_equity_curve_chart(
            self.equity_curve,
            output_file,
            use_plotly=True
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_equity_curve_simple_list(self):
        """Test equity curve with simple list of values"""
        simple_curve = [10000 + i * 50 for i in range(100)]
        output_file = os.path.join(self.test_dir, 'equity_simple.png')
        result = generate_equity_curve_chart(
            simple_curve,
            output_file,
            use_plotly=False
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(output_file))
    
    def test_drawdown_chart_matplotlib(self):
        """Test drawdown chart generation with Matplotlib"""
        output_file = os.path.join(self.test_dir, 'drawdown_test.png')
        result = generate_drawdown_chart(
            self.equity_curve,
            output_file,
            use_plotly=False
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_drawdown_chart_plotly(self):
        """Test drawdown chart generation with Plotly"""
        output_file = os.path.join(self.test_dir, 'drawdown_test.html')
        result = generate_drawdown_chart(
            self.equity_curve,
            output_file,
            use_plotly=True
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_pnl_distribution_matplotlib(self):
        """Test P&L distribution with Matplotlib"""
        output_file = os.path.join(self.test_dir, 'pnl_test.png')
        result = generate_pnl_distribution_chart(
            self.trades,
            output_file,
            use_plotly=False
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_pnl_distribution_plotly(self):
        """Test P&L distribution with Plotly"""
        output_file = os.path.join(self.test_dir, 'pnl_test.html')
        result = generate_pnl_distribution_chart(
            self.trades,
            output_file,
            use_plotly=True
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_empty_equity_curve(self):
        """Test handling of empty equity curve"""
        result = generate_equity_curve_chart(
            [],
            os.path.join(self.test_dir, 'empty.png'),
            use_plotly=False
        )
        self.assertIsNone(result)
    
    def test_empty_trades(self):
        """Test handling of empty trades"""
        result = generate_pnl_distribution_chart(
            [],
            os.path.join(self.test_dir, 'empty.png'),
            use_plotly=False
        )
        self.assertIsNone(result)


class TestBacktesterVisualization(unittest.TestCase):
    """Test Backtester visualization integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.backtester = Backtester(initial_capital=10000.0)
        self.data = generate_sample_data(n_bars=300, start_price=30000)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_visualize_results(self):
        """Test visualization generation from backtester"""
        # Run backtest
        self.backtester.run(self.data)
        
        # Generate visualizations
        charts = self.backtester.visualize_results(
            output_dir=self.test_dir,
            use_plotly=False
        )
        
        # Verify charts were generated
        self.assertIsInstance(charts, dict)
        self.assertGreater(len(charts), 0)
        
        # Check that files exist
        for chart_type, path in charts.items():
            self.assertTrue(os.path.exists(path), f"{chart_type} chart not found")
            self.assertGreater(os.path.getsize(path), 0, f"{chart_type} chart is empty")
    
    def test_visualize_with_plotly(self):
        """Test visualization with Plotly"""
        self.backtester.run(self.data)
        
        charts = self.backtester.visualize_results(
            output_dir=self.test_dir,
            use_plotly=True
        )
        
        self.assertIsInstance(charts, dict)
        for chart_type, path in charts.items():
            self.assertTrue(path.endswith('.html'))
            self.assertTrue(os.path.exists(path))


class TestBatchBacktester(unittest.TestCase):
    """Test BatchBacktester functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.batch_tester = BatchBacktester(initial_capital=10000.0, trade_size=100.0)
        self.data = generate_sample_data(n_bars=300, start_price=30000)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_add_strategy(self):
        """Test adding strategies to batch tester"""
        strategy = MACrossoverStrategy({'short_window': 20, 'long_window': 50})
        self.batch_tester.add_strategy('MA Test', strategy)
        
        self.assertEqual(len(self.batch_tester.strategies), 1)
        self.assertIn('MA Test', self.batch_tester.strategies)
    
    def test_run_batch_single_strategy(self):
        """Test running batch backtest with single strategy"""
        strategy = MACrossoverStrategy({'short_window': 20, 'long_window': 50})
        self.batch_tester.add_strategy('MA Test', strategy)
        
        self.batch_tester.run_batch(self.data)
        
        self.assertEqual(len(self.batch_tester.results), 1)
        self.assertIn('MA Test', self.batch_tester.results)
        
        result = self.batch_tester.results['MA Test']
        self.assertIn('metrics', result)
        self.assertIn('trades', result)
        self.assertIn('equity_curve', result)
    
    def test_run_batch_multiple_strategies(self):
        """Test running batch backtest with multiple strategies"""
        strategies = [
            ('MA Crossover', MACrossoverStrategy({'short_window': 20, 'long_window': 50})),
            ('RSI', RSIStrategy({'window': 14, 'oversold_threshold': 35, 'overbought_threshold': 65})),
            ('EMA', EMACrossoverStrategy({'short_window': 9, 'long_window': 21}))
        ]
        
        for name, strategy in strategies:
            self.batch_tester.add_strategy(name, strategy)
        
        self.batch_tester.run_batch(self.data)
        
        self.assertEqual(len(self.batch_tester.results), 3)
        
        # Verify all results have proper structure
        for name, result in self.batch_tester.results.items():
            self.assertIn('metrics', result)
            self.assertIn('trades', result)
            self.assertIn('equity_curve', result)
            
            metrics = result['metrics']
            self.assertIn('strategy_name', metrics)
            self.assertIn('total_trades', metrics)
            self.assertIn('roi', metrics)
    
    def test_export_results(self):
        """Test exporting batch backtest results"""
        strategy = MACrossoverStrategy({'short_window': 20, 'long_window': 50})
        self.batch_tester.add_strategy('MA Test', strategy)
        
        self.batch_tester.run_batch(self.data)
        self.batch_tester.export_results(output_dir=self.test_dir)
        
        # Check summary file
        summary_file = os.path.join(self.test_dir, 'batch_backtest_summary.csv')
        self.assertTrue(os.path.exists(summary_file))
        
        # Verify summary can be read
        df = pd.read_csv(summary_file)
        self.assertGreater(len(df), 0)
        self.assertIn('strategy_name', df.columns)
        self.assertIn('roi', df.columns)
    
    def test_visualize_results(self):
        """Test batch visualization generation"""
        strategies = [
            ('MA Crossover', MACrossoverStrategy({'short_window': 20, 'long_window': 50})),
            ('RSI', RSIStrategy({'window': 14, 'oversold_threshold': 35, 'overbought_threshold': 65}))
        ]
        
        for name, strategy in strategies:
            self.batch_tester.add_strategy(name, strategy)
        
        self.batch_tester.run_batch(self.data)
        charts = self.batch_tester.visualize_results(
            output_dir=self.test_dir,
            use_plotly=False
        )
        
        # Verify charts were generated for each strategy
        self.assertIsInstance(charts, dict)
        
        for strategy_name, strategy_charts in charts.items():
            self.assertIsInstance(strategy_charts, dict)
            # Check that at least equity chart exists
            self.assertIn('equity', strategy_charts)
            self.assertTrue(os.path.exists(strategy_charts['equity']))
    
    def test_performance_comparison(self):
        """Test that performance metrics are calculated correctly"""
        strategy = MACrossoverStrategy({'short_window': 20, 'long_window': 50})
        self.batch_tester.add_strategy('MA Test', strategy)
        
        self.batch_tester.run_batch(self.data)
        
        result = self.batch_tester.results['MA Test']
        metrics = result['metrics']
        
        # Verify metrics structure
        required_metrics = [
            'strategy_name', 'total_trades', 'total_pnl', 'roi',
            'win_rate', 'best_trade', 'worst_trade', 'avg_trade',
            'final_capital', 'sharpe_ratio', 'max_drawdown'
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, metrics, f"Missing metric: {metric}")
        
        # Verify metrics make sense
        self.assertEqual(metrics['strategy_name'], 'MA Test')
        self.assertIsInstance(metrics['total_trades'], int)
        self.assertIsInstance(metrics['roi'], (int, float))
        self.assertIsInstance(metrics['final_capital'], (int, float))


class TestBatchBacktesterEdgeCases(unittest.TestCase):
    """Test edge cases for batch backtester"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.batch_tester = BatchBacktester(initial_capital=10000.0, trade_size=100.0)
        self.data = generate_sample_data(n_bars=300, start_price=30000)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_no_strategies(self):
        """Test running batch backtest with no strategies"""
        # Should handle gracefully
        self.batch_tester.run_batch(self.data)
        self.assertEqual(len(self.batch_tester.results), 0)
    
    def test_strategy_with_no_trades(self):
        """Test strategy that generates no trades"""
        # Use a strategy with very tight parameters
        strategy = BollingerBandsStrategy({'window': 200, 'std_dev': 5.0})
        self.batch_tester.add_strategy('No Trades', strategy)
        
        self.batch_tester.run_batch(self.data)
        
        result = self.batch_tester.results['No Trades']
        metrics = result['metrics']
        
        self.assertEqual(metrics['total_trades'], 0)
        self.assertEqual(metrics['roi'], 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVisualizationFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktesterVisualization))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchBacktester))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchBacktesterEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
