"""
test_portfolio_optimizer.py - Tests for Portfolio Optimizer
===========================================================
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio_optimizer import PortfolioOptimizer, optimize_portfolio, rebalance_portfolio


class TestPortfolioOptimizer(unittest.TestCase):
    """Tests for PortfolioOptimizer"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        
        # Create sample price data for 3 assets
        dates = pd.date_range('2023-01-01', periods=252, freq='D')
        
        self.prices = pd.DataFrame({
            'ASSET_A': 100 + np.cumsum(np.random.randn(252) * 2),
            'ASSET_B': 50 + np.cumsum(np.random.randn(252) * 1.5),
            'ASSET_C': 200 + np.cumsum(np.random.randn(252) * 3)
        }, index=dates)
        
        self.optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = PortfolioOptimizer(risk_free_rate=0.03)
        self.assertEqual(optimizer.risk_free_rate, 0.03)
    
    def test_calculate_returns(self):
        """Test returns calculation"""
        returns = self.optimizer.calculate_returns(self.prices)
        
        self.assertIsInstance(returns, pd.DataFrame)
        self.assertEqual(returns.shape[1], 3)  # 3 assets
        self.assertEqual(len(returns), len(self.prices) - 1)  # One less due to pct_change
    
    def test_calculate_expected_returns(self):
        """Test expected returns calculation"""
        returns = self.optimizer.calculate_returns(self.prices)
        expected_returns = self.optimizer.calculate_expected_returns(returns)
        
        self.assertIsInstance(expected_returns, pd.Series)
        self.assertEqual(len(expected_returns), 3)  # 3 assets
        self.assertTrue(all(isinstance(x, (int, float)) for x in expected_returns))
    
    def test_calculate_covariance_matrix(self):
        """Test covariance matrix calculation"""
        returns = self.optimizer.calculate_returns(self.prices)
        cov_matrix = self.optimizer.calculate_covariance_matrix(returns)
        
        self.assertIsInstance(cov_matrix, pd.DataFrame)
        self.assertEqual(cov_matrix.shape, (3, 3))
        
        # Check symmetry
        self.assertTrue(np.allclose(cov_matrix, cov_matrix.T))
        
        # Check positive semi-definite
        eigenvalues = np.linalg.eigvals(cov_matrix)
        self.assertTrue(all(eigenvalues >= -1e-10))
    
    def test_portfolio_performance(self):
        """Test portfolio performance calculation"""
        returns = self.optimizer.calculate_returns(self.prices)
        expected_returns = self.optimizer.calculate_expected_returns(returns)
        cov_matrix = self.optimizer.calculate_covariance_matrix(returns)
        
        # Equal weights
        weights = np.array([1/3, 1/3, 1/3])
        
        ret, vol, sharpe = self.optimizer.portfolio_performance(
            weights, expected_returns, cov_matrix
        )
        
        self.assertIsInstance(ret, float)
        self.assertIsInstance(vol, float)
        self.assertIsInstance(sharpe, float)
        self.assertGreater(vol, 0)
    
    def test_maximize_sharpe_ratio(self):
        """Test maximum Sharpe ratio optimization"""
        returns = self.optimizer.calculate_returns(self.prices)
        expected_returns = self.optimizer.calculate_expected_returns(returns)
        cov_matrix = self.optimizer.calculate_covariance_matrix(returns)
        
        result = self.optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix)
        
        self.assertIn('weights', result)
        self.assertIn('sharpe_ratio', result)
        self.assertIn('expected_return', result)
        self.assertIn('volatility', result)
        
        # Check weights sum to 1
        weights_sum = sum(result['weights'].values())
        self.assertAlmostEqual(weights_sum, 1.0, places=6)
        
        # Check all weights are non-negative
        self.assertTrue(all(w >= -1e-6 for w in result['weights'].values()))
    
    def test_minimize_volatility(self):
        """Test minimum volatility optimization"""
        returns = self.optimizer.calculate_returns(self.prices)
        expected_returns = self.optimizer.calculate_expected_returns(returns)
        cov_matrix = self.optimizer.calculate_covariance_matrix(returns)
        
        result = self.optimizer.minimize_volatility(expected_returns, cov_matrix)
        
        self.assertIn('weights', result)
        self.assertIn('volatility', result)
        
        # Check weights sum to 1
        weights_sum = sum(result['weights'].values())
        self.assertAlmostEqual(weights_sum, 1.0, places=6)
    
    def test_risk_parity(self):
        """Test risk parity optimization"""
        returns = self.optimizer.calculate_returns(self.prices)
        cov_matrix = self.optimizer.calculate_covariance_matrix(returns)
        
        result = self.optimizer.risk_parity(cov_matrix)
        
        self.assertIn('weights', result)
        
        # Check weights sum to 1
        weights_sum = sum(result['weights'].values())
        self.assertAlmostEqual(weights_sum, 1.0, places=6)
    
    def test_kelly_criterion(self):
        """Test Kelly Criterion calculation"""
        # Test case with 60% win rate and 2:1 win/loss ratio
        kelly = self.optimizer.kelly_criterion(win_rate=0.6, win_loss_ratio=2.0)
        
        self.assertGreater(kelly, 0)
        self.assertLess(kelly, 1)
        
        # Test case with losing strategy
        kelly_losing = self.optimizer.kelly_criterion(win_rate=0.3, win_loss_ratio=1.0)
        self.assertEqual(kelly_losing, 0)  # Should recommend no position
    
    def test_optimize_portfolio_convenience_function(self):
        """Test convenience function for optimization"""
        result = optimize_portfolio(self.prices, method='max_sharpe')
        
        self.assertIn('weights', result)
        self.assertIn('sharpe_ratio', result)
    
    def test_rebalance_portfolio(self):
        """Test portfolio rebalancing calculation"""
        current_weights = {
            'ASSET_A': 0.4,
            'ASSET_B': 0.3,
            'ASSET_C': 0.3
        }
        
        target_weights = {
            'ASSET_A': 0.5,
            'ASSET_B': 0.25,
            'ASSET_C': 0.25
        }
        
        trades = rebalance_portfolio(current_weights, target_weights, threshold=0.01)
        
        self.assertIn('ASSET_A', trades)  # Should rebalance
        self.assertAlmostEqual(trades['ASSET_A'], 0.1)
        self.assertAlmostEqual(trades['ASSET_B'], -0.05)


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPortfolioOptimizer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.exit(0 if run_tests() else 1)
