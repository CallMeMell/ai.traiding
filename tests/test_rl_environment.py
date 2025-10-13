"""
test_rl_environment.py - Tests for RL Trading Environment
=========================================================
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl_environment import TradingEnvironment


class TestRLEnvironment(unittest.TestCase):
    """Tests for TradingEnvironment"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample data
        np.random.seed(42)
        n_samples = 200
        
        self.test_data = pd.DataFrame({
            'close': 100 + np.cumsum(np.random.randn(n_samples) * 2),
            'volume': np.random.randint(1000, 10000, n_samples),
            'rsi': np.random.uniform(30, 70, n_samples),
            'ma_short': 100 + np.cumsum(np.random.randn(n_samples)),
            'ma_long': 100 + np.cumsum(np.random.randn(n_samples) * 0.5)
        })
    
    def test_initialization(self):
        """Test environment initializes correctly"""
        env = TradingEnvironment(
            data=self.test_data,
            initial_capital=10000.0,
            window_size=30
        )
        
        self.assertEqual(env.initial_capital, 10000.0)
        self.assertEqual(env.window_size, 30)
        self.assertEqual(env.action_space.n, 21)
        self.assertIsNotNone(env.observation_space)
    
    def test_reset(self):
        """Test environment reset"""
        env = TradingEnvironment(self.test_data, initial_capital=10000.0)
        
        obs = env.reset()
        
        self.assertIsInstance(obs, np.ndarray)
        self.assertEqual(obs.dtype, np.float32)
        self.assertEqual(env.current_step, 0)
        self.assertEqual(env.capital, 10000.0)
        self.assertEqual(env.holdings, 0.0)
        self.assertEqual(env.position, 0)
    
    def test_step_hold_action(self):
        """Test HOLD action"""
        env = TradingEnvironment(self.test_data, initial_capital=10000.0)
        env.reset()
        
        initial_capital = env.capital
        
        # Take HOLD action (action 10)
        obs, reward, done, info = env.step(10)
        
        self.assertIsInstance(obs, np.ndarray)
        self.assertIsInstance(reward, float)
        self.assertIsInstance(done, bool)
        self.assertIsInstance(info, dict)
        self.assertEqual(env.capital, initial_capital)
        self.assertEqual(env.holdings, 0.0)
    
    def test_step_buy_action(self):
        """Test BUY action"""
        env = TradingEnvironment(self.test_data, initial_capital=10000.0)
        env.reset()
        
        # Take BUY action (action 4 = BUY 50%)
        obs, reward, done, info = env.step(4)
        
        self.assertLess(env.capital, 10000.0)  # Capital decreased
        self.assertGreater(env.holdings, 0.0)  # Holdings increased
        self.assertEqual(env.position, 1)  # Position is long
        self.assertTrue(info['trade_info']['executed'])
    
    def test_step_sell_action(self):
        """Test SELL action"""
        env = TradingEnvironment(self.test_data, initial_capital=10000.0)
        env.reset()
        
        # First buy
        env.step(4)  # BUY 50%
        holdings_after_buy = env.holdings
        
        # Then sell
        obs, reward, done, info = env.step(15)  # SELL 50%
        
        self.assertLess(env.holdings, holdings_after_buy)
        self.assertTrue(info['trade_info']['executed'])
    
    def test_action_decoding(self):
        """Test action decoding"""
        env = TradingEnvironment(self.test_data)
        
        # Test BUY actions
        action_type, amount = env._decode_action(0)
        self.assertEqual(action_type, 'BUY')
        self.assertAlmostEqual(amount, 0.1)
        
        action_type, amount = env._decode_action(9)
        self.assertEqual(action_type, 'BUY')
        self.assertAlmostEqual(amount, 1.0)
        
        # Test HOLD action
        action_type, amount = env._decode_action(10)
        self.assertEqual(action_type, 'HOLD')
        self.assertEqual(amount, 0.0)
        
        # Test SELL actions
        action_type, amount = env._decode_action(11)
        self.assertEqual(action_type, 'SELL')
        self.assertAlmostEqual(amount, 0.1)
        
        action_type, amount = env._decode_action(20)
        self.assertEqual(action_type, 'SELL')
        self.assertAlmostEqual(amount, 1.0)
    
    def test_episode_completion(self):
        """Test full episode"""
        env = TradingEnvironment(self.test_data, initial_capital=10000.0, window_size=30)
        obs = env.reset()
        
        done = False
        steps = 0
        
        while not done and steps < 100:
            action = np.random.randint(0, 21)
            obs, reward, done, info = env.step(action)
            steps += 1
        
        self.assertGreater(steps, 0)
        self.assertIsInstance(obs, np.ndarray)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        env = TradingEnvironment(self.test_data, initial_capital=10000.0)
        env.reset()
        
        # Run some steps
        for _ in range(50):
            action = np.random.randint(0, 21)
            env.step(action)
        
        metrics = env.get_performance_metrics()
        
        self.assertIn('final_value', metrics)
        self.assertIn('roi', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('total_trades', metrics)
        
        self.assertIsInstance(metrics['roi'], float)
        self.assertIsInstance(metrics['sharpe_ratio'], float)
    
    def test_observation_shape(self):
        """Test observation shape is consistent"""
        env = TradingEnvironment(self.test_data, initial_capital=10000.0, window_size=30)
        obs = env.reset()
        
        expected_shape = env.observation_space.shape
        self.assertEqual(obs.shape, expected_shape)
        
        # Step and check again
        obs, _, _, _ = env.step(10)
        self.assertEqual(obs.shape, expected_shape)


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRLEnvironment)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.exit(0 if run_tests() else 1)
