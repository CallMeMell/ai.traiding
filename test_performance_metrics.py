"""
test_performance_metrics.py - Tests for Performance Metrics
===========================================================
Unit tests for Sharpe Ratio, Maximum Drawdown, and enhanced
performance metrics calculations.
"""

import unittest
import numpy as np
from datetime import datetime, timedelta
from utils import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_performance_metrics,
    calculate_calmar_ratio,
    calculate_volatility,
    calculate_avg_trade_duration,
    calculate_profit_factor
)


class TestSharpeRatio(unittest.TestCase):
    """Test cases for Sharpe Ratio calculation"""
    
    def test_positive_returns(self):
        """Test Sharpe ratio with positive returns"""
        returns = [0.01, 0.02, 0.015, 0.012, 0.018]
        sharpe = calculate_sharpe_ratio(returns)
        
        # Should be positive for positive returns
        self.assertGreater(sharpe, 0)
    
    def test_negative_returns(self):
        """Test Sharpe ratio with negative returns"""
        returns = [-0.01, -0.02, -0.015, -0.012, -0.018]
        sharpe = calculate_sharpe_ratio(returns)
        
        # Should be negative for negative returns
        self.assertLess(sharpe, 0)
    
    def test_mixed_returns(self):
        """Test Sharpe ratio with mixed returns"""
        returns = [0.02, -0.01, 0.015, -0.005, 0.01]
        sharpe = calculate_sharpe_ratio(returns)
        
        # Should handle mixed returns
        self.assertIsInstance(sharpe, (int, float))
    
    def test_zero_volatility(self):
        """Test Sharpe ratio with zero volatility (constant returns)"""
        returns = [0.01, 0.01, 0.01, 0.01, 0.01]
        sharpe = calculate_sharpe_ratio(returns)
        
        # Should return 0 for zero volatility
        self.assertEqual(sharpe, 0.0)
    
    def test_insufficient_data(self):
        """Test Sharpe ratio with insufficient data"""
        # Empty list
        sharpe = calculate_sharpe_ratio([])
        self.assertEqual(sharpe, 0.0)
        
        # Single value
        sharpe = calculate_sharpe_ratio([0.01])
        self.assertEqual(sharpe, 0.0)
    
    def test_risk_free_rate(self):
        """Test Sharpe ratio with non-zero risk-free rate"""
        returns = [0.05, 0.06, 0.055, 0.052, 0.058]
        risk_free_rate = 0.02
        
        sharpe_with_rf = calculate_sharpe_ratio(returns, risk_free_rate)
        sharpe_without_rf = calculate_sharpe_ratio(returns, 0.0)
        
        # Sharpe with risk-free rate should be different
        self.assertNotEqual(sharpe_with_rf, sharpe_without_rf)


class TestMaximumDrawdown(unittest.TestCase):
    """Test cases for Maximum Drawdown calculation"""
    
    def test_monotonic_increase(self):
        """Test drawdown with constantly increasing equity"""
        equity = [10000, 10100, 10200, 10300, 10400]
        max_dd_pct, max_dd_val, peak, trough = calculate_max_drawdown(equity)
        
        # No drawdown for monotonic increase
        self.assertLessEqual(max_dd_pct, 0)
        self.assertLessEqual(max_dd_val, 0)
    
    def test_simple_drawdown(self):
        """Test drawdown with simple peak-trough pattern"""
        equity = [10000, 11000, 10500, 10000, 10500]
        max_dd_pct, max_dd_val, peak, trough = calculate_max_drawdown(equity)
        
        # Should detect the drawdown from 11000 to 10000
        self.assertLess(max_dd_pct, 0)
        self.assertEqual(peak, 11000)
        self.assertEqual(trough, 10000)
        self.assertAlmostEqual(max_dd_val, -1000, places=0)
    
    def test_multiple_drawdowns(self):
        """Test with multiple drawdown periods"""
        equity = [10000, 11000, 10500, 12000, 10000, 11000]
        max_dd_pct, max_dd_val, peak, trough = calculate_max_drawdown(equity)
        
        # Should find the maximum drawdown (12000 to 10000)
        self.assertEqual(peak, 12000)
        self.assertEqual(trough, 10000)
        self.assertLess(max_dd_pct, 0)
    
    def test_complete_loss(self):
        """Test with severe drawdown"""
        equity = [10000, 12000, 6000, 8000]
        max_dd_pct, max_dd_val, peak, trough = calculate_max_drawdown(equity)
        
        # Should detect 50% drawdown from 12000 to 6000
        self.assertEqual(peak, 12000)
        self.assertEqual(trough, 6000)
        self.assertAlmostEqual(max_dd_pct, -50, places=0)
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        # Empty list
        max_dd_pct, max_dd_val, peak, trough = calculate_max_drawdown([])
        self.assertEqual(max_dd_pct, 0.0)
        
        # Single value
        max_dd_pct, max_dd_val, peak, trough = calculate_max_drawdown([10000])
        self.assertEqual(max_dd_pct, 0.0)


class TestEnhancedPerformanceMetrics(unittest.TestCase):
    """Test cases for enhanced performance metrics"""
    
    def test_basic_metrics_only(self):
        """Test with just trade data (no equity curve)"""
        trades = [
            {'pnl': '100'},
            {'pnl': '-50'},
            {'pnl': '75'}
        ]
        
        metrics = calculate_performance_metrics(trades)
        
        # Basic metrics should be calculated
        self.assertEqual(metrics['total_trades'], 3)
        self.assertEqual(metrics['total_pnl'], 125.0)
        self.assertGreater(metrics['win_rate'], 0)
        
        # Advanced metrics should be present but may be 0
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
    
    def test_with_equity_curve(self):
        """Test with trade data and equity curve"""
        trades = [
            {'pnl': '100'},
            {'pnl': '-50'},
            {'pnl': '75'}
        ]
        equity_curve = [10000, 10100, 10050, 10125]
        
        metrics = calculate_performance_metrics(
            trades,
            equity_curve=equity_curve,
            initial_capital=10000.0
        )
        
        # All metrics should be calculated
        self.assertEqual(metrics['total_trades'], 3)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertNotEqual(metrics['max_drawdown'], 0.0)
    
    def test_winning_trades_only(self):
        """Test with only winning trades"""
        trades = [
            {'pnl': '100'},
            {'pnl': '150'},
            {'pnl': '75'}
        ]
        
        metrics = calculate_performance_metrics(trades)
        
        self.assertEqual(metrics['win_rate'], 100.0)
        self.assertEqual(metrics['total_pnl'], 325.0)
        self.assertGreater(metrics['sharpe_ratio'], 0)
    
    def test_losing_trades_only(self):
        """Test with only losing trades"""
        trades = [
            {'pnl': '-100'},
            {'pnl': '-150'},
            {'pnl': '-75'}
        ]
        
        metrics = calculate_performance_metrics(trades)
        
        self.assertEqual(metrics['win_rate'], 0.0)
        self.assertEqual(metrics['total_pnl'], -325.0)
        self.assertLess(metrics['sharpe_ratio'], 0)
    
    def test_empty_trades(self):
        """Test with no trades"""
        metrics = calculate_performance_metrics([])
        
        # Should return default values
        self.assertEqual(metrics['total_trades'], 0)
        self.assertEqual(metrics['total_pnl'], 0.0)
        self.assertEqual(metrics['win_rate'], 0.0)
        self.assertEqual(metrics['sharpe_ratio'], 0.0)
        self.assertEqual(metrics['max_drawdown'], 0.0)


class TestCalmarRatio(unittest.TestCase):
    """Test cases for Calmar Ratio calculation"""
    
    def test_positive_return_with_drawdown(self):
        """Test Calmar ratio with positive return and drawdown"""
        total_return = 20.0  # 20% return
        max_drawdown = -10.0  # -10% drawdown
        
        calmar = calculate_calmar_ratio(total_return, max_drawdown)
        
        # Calmar should be positive (20 / 10 = 2.0)
        self.assertAlmostEqual(calmar, 2.0, places=1)
    
    def test_zero_drawdown(self):
        """Test Calmar ratio with zero drawdown"""
        total_return = 20.0
        max_drawdown = 0.0
        
        calmar = calculate_calmar_ratio(total_return, max_drawdown)
        
        # Should return 0 when no drawdown
        self.assertEqual(calmar, 0.0)
    
    def test_negative_return(self):
        """Test Calmar ratio with negative return"""
        total_return = -10.0
        max_drawdown = -15.0
        
        calmar = calculate_calmar_ratio(total_return, max_drawdown)
        
        # Should be negative
        self.assertLess(calmar, 0)


class TestVolatility(unittest.TestCase):
    """Test cases for Volatility calculation"""
    
    def test_stable_equity(self):
        """Test volatility with stable equity curve"""
        equity = [10000, 10010, 10020, 10030, 10040]
        
        volatility = calculate_volatility(equity)
        
        # Should have low volatility
        self.assertGreaterEqual(volatility, 0)
        self.assertLess(volatility, 0.1)
    
    def test_volatile_equity(self):
        """Test volatility with volatile equity curve"""
        equity = [10000, 11000, 9500, 12000, 9000, 11500]
        
        volatility = calculate_volatility(equity)
        
        # Should have higher volatility
        self.assertGreater(volatility, 0.1)
    
    def test_insufficient_data(self):
        """Test volatility with insufficient data"""
        # Empty list
        volatility = calculate_volatility([])
        self.assertEqual(volatility, 0.0)
        
        # Single value
        volatility = calculate_volatility([10000])
        self.assertEqual(volatility, 0.0)


class TestAvgTradeDuration(unittest.TestCase):
    """Test cases for Average Trade Duration calculation"""
    
    def test_simple_trade_duration(self):
        """Test with simple BUY-SELL pattern"""
        now = datetime.now()
        trades = [
            {'type': 'BUY', 'timestamp': now.isoformat(), 'pnl': '0'},
            {'type': 'SELL', 'timestamp': (now + timedelta(hours=1)).isoformat(), 'pnl': '100'}
        ]
        
        avg_duration = calculate_avg_trade_duration(trades)
        
        # Should be 3600 seconds (1 hour)
        self.assertAlmostEqual(avg_duration, 3600, delta=1)
    
    def test_multiple_trades(self):
        """Test with multiple trades"""
        now = datetime.now()
        trades = [
            {'type': 'BUY', 'timestamp': now.isoformat(), 'pnl': '0'},
            {'type': 'SELL', 'timestamp': (now + timedelta(hours=2)).isoformat(), 'pnl': '100'},
            {'type': 'BUY', 'timestamp': (now + timedelta(hours=3)).isoformat(), 'pnl': '0'},
            {'type': 'SELL', 'timestamp': (now + timedelta(hours=4)).isoformat(), 'pnl': '50'}
        ]
        
        avg_duration = calculate_avg_trade_duration(trades)
        
        # Average should be (7200 + 3600) / 2 = 5400 seconds
        self.assertAlmostEqual(avg_duration, 5400, delta=1)
    
    def test_no_complete_trades(self):
        """Test with no complete trades"""
        now = datetime.now()
        trades = [
            {'type': 'BUY', 'timestamp': now.isoformat(), 'pnl': '0'}
        ]
        
        avg_duration = calculate_avg_trade_duration(trades)
        
        # Should return 0
        self.assertEqual(avg_duration, 0.0)


class TestProfitFactor(unittest.TestCase):
    """Test cases for Profit Factor calculation"""
    
    def test_positive_profit_factor(self):
        """Test profit factor with wins and losses"""
        trades = [
            {'pnl': '100'},
            {'pnl': '150'},
            {'pnl': '-50'},
            {'pnl': '-25'}
        ]
        
        profit_factor = calculate_profit_factor(trades)
        
        # (100 + 150) / (50 + 25) = 250 / 75 = 3.33
        self.assertAlmostEqual(profit_factor, 3.33, places=1)
    
    def test_only_wins(self):
        """Test profit factor with only winning trades"""
        trades = [
            {'pnl': '100'},
            {'pnl': '150'}
        ]
        
        profit_factor = calculate_profit_factor(trades)
        
        # Should be infinity
        self.assertEqual(profit_factor, float('inf'))
    
    def test_only_losses(self):
        """Test profit factor with only losing trades"""
        trades = [
            {'pnl': '-100'},
            {'pnl': '-150'}
        ]
        
        profit_factor = calculate_profit_factor(trades)
        
        # Should be 0
        self.assertEqual(profit_factor, 0.0)
    
    def test_empty_trades(self):
        """Test profit factor with no trades"""
        profit_factor = calculate_profit_factor([])
        
        self.assertEqual(profit_factor, 0.0)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for real-world scenarios"""
    
    def test_realistic_trading_scenario(self):
        """Test with realistic trading data"""
        # Simulate a series of trades
        now = datetime.now()
        trades = [
            {'pnl': '0', 'type': 'BUY', 'timestamp': now.isoformat()},
            {'pnl': '150.00', 'type': 'SELL', 'timestamp': (now + timedelta(hours=1)).isoformat()},
            {'pnl': '0', 'type': 'BUY', 'timestamp': (now + timedelta(hours=2)).isoformat()},
            {'pnl': '-75.00', 'type': 'SELL', 'timestamp': (now + timedelta(hours=3)).isoformat()},
            {'pnl': '0', 'type': 'BUY', 'timestamp': (now + timedelta(hours=4)).isoformat()},
            {'pnl': '200.00', 'type': 'SELL', 'timestamp': (now + timedelta(hours=6)).isoformat()},
        ]
        
        # Simulate equity curve
        equity = [10000]
        for trade in trades:
            if trade['type'] == 'SELL':
                equity.append(equity[-1] + float(trade['pnl']))
        
        metrics = calculate_performance_metrics(
            trades,
            equity_curve=equity,
            initial_capital=10000.0
        )
        
        # Validate all metrics are calculated
        self.assertGreater(metrics['total_trades'], 0)
        self.assertNotEqual(metrics['total_pnl'], 0)
        self.assertGreater(metrics['win_rate'], 0)
        self.assertLess(metrics['win_rate'], 100)
        self.assertIsInstance(metrics['sharpe_ratio'], (int, float))
        self.assertIsInstance(metrics['max_drawdown'], (int, float))
        
        # Check new metrics
        self.assertIn('calmar_ratio', metrics)
        self.assertIn('volatility', metrics)
        self.assertIn('avg_trade_duration', metrics)
        self.assertIn('profit_factor', metrics)
        
        # ROI should match expected
        expected_pnl = sum(float(t['pnl']) for t in trades if t['type'] == 'SELL')
        self.assertAlmostEqual(metrics['total_pnl'], expected_pnl, places=2)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSharpeRatio))
    suite.addTests(loader.loadTestsFromTestCase(TestMaximumDrawdown))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedPerformanceMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestCalmarRatio))
    suite.addTests(loader.loadTestsFromTestCase(TestVolatility))
    suite.addTests(loader.loadTestsFromTestCase(TestAvgTradeDuration))
    suite.addTests(loader.loadTestsFromTestCase(TestProfitFactor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
