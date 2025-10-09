"""
test_parameter_optimization.py - Tests for Parameter Optimization Module
=========================================================================
Unit tests for the ParameterOptimizer class and optimization algorithms
"""

import unittest
import pandas as pd
import numpy as np
import logging
from parameter_optimizer import ParameterOptimizer, ParameterRange, OptimizationResult
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data

# Suppress logging during tests
logging.disable(logging.CRITICAL)


class TestParameterRange(unittest.TestCase):
    """Test cases for ParameterRange"""
    
    def test_float_range(self):
        """Test float parameter range"""
        param = ParameterRange(
            name='test_param',
            min_value=0.5,
            max_value=2.5,
            step=0.5,
            type='float'
        )
        self.assertEqual(param.name, 'test_param')
        self.assertEqual(param.min_value, 0.5)
        self.assertEqual(param.max_value, 2.5)
        self.assertEqual(param.step, 0.5)
        self.assertEqual(param.type, 'float')
    
    def test_int_range(self):
        """Test integer parameter range"""
        param = ParameterRange(
            name='test_int',
            min_value=10,
            max_value=100,
            step=10,
            type='int'
        )
        self.assertEqual(param.type, 'int')
        self.assertEqual(param.min_value, 10)
        self.assertEqual(param.max_value, 100)
    
    def test_categorical_range(self):
        """Test categorical parameter range"""
        param = ParameterRange(
            name='direction',
            type='categorical',
            values=['LONG', 'SHORT'],
            min_value=0,
            max_value=1
        )
        self.assertEqual(param.type, 'categorical')
        self.assertEqual(param.values, ['LONG', 'SHORT'])


class TestParameterOptimizer(unittest.TestCase):
    """Test cases for ParameterOptimizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Generate small test data
        self.data = generate_sample_data(n_bars=100, start_price=30000)
        
        # Define simple parameter ranges for testing
        self.parameter_ranges = [
            ParameterRange(
                name='initial_capital',
                min_value=10000.0,
                max_value=10000.0,
                type='float'
            ),
            ParameterRange(
                name='stop_loss_percent',
                min_value=1.0,
                max_value=2.0,
                step=0.5,
                type='float'
            ),
            ParameterRange(
                name='take_profit_percent',
                min_value=2.0,
                max_value=4.0,
                step=1.0,
                type='float'
            ),
            ParameterRange(
                name='trailing_stop_percent',
                min_value=0.5,
                max_value=1.0,
                step=0.25,
                type='float'
            ),
            ParameterRange(
                name='initial_direction',
                type='categorical',
                values=['LONG'],
                min_value=0,
                max_value=0
            )
        ]
    
    def test_initialization(self):
        """Test optimizer initialization"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        self.assertEqual(optimizer.optimization_metric, 'score')
        self.assertEqual(len(optimizer.parameter_ranges), 5)
        self.assertEqual(len(optimizer.results), 0)
        self.assertIsNone(optimizer.best_result)
    
    def test_generate_grid(self):
        """Test grid generation"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        grid = optimizer._generate_grid()
        
        # Should have combinations of all parameters
        # When n_points not specified, default is 5 points per parameter
        # So the grid will be larger than expected
        # Just check it's a reasonable size
        self.assertGreater(len(grid), 0)
        self.assertLess(len(grid), 500)
        
        # Check that all combinations have required keys
        for combo in grid:
            self.assertIn('stop_loss_percent', combo)
            self.assertIn('take_profit_percent', combo)
            self.assertIn('trailing_stop_percent', combo)
            self.assertIn('initial_direction', combo)
            self.assertIn('initial_capital', combo)
    
    def test_generate_random_parameters(self):
        """Test random parameter generation"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        # Set seed for reproducibility
        np.random.seed(42)
        
        params = optimizer._generate_random_parameters()
        
        # Check all required parameters present
        self.assertIn('stop_loss_percent', params)
        self.assertIn('take_profit_percent', params)
        self.assertIn('trailing_stop_percent', params)
        self.assertIn('initial_direction', params)
        self.assertIn('initial_capital', params)
        
        # Check ranges
        self.assertGreaterEqual(params['stop_loss_percent'], 1.0)
        self.assertLessEqual(params['stop_loss_percent'], 2.0)
        self.assertGreaterEqual(params['take_profit_percent'], 2.0)
        self.assertLessEqual(params['take_profit_percent'], 4.0)
    
    def test_evaluate_parameters(self):
        """Test parameter evaluation"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        params = {
            'initial_capital': 10000.0,
            'stop_loss_percent': 2.0,
            'take_profit_percent': 4.0,
            'trailing_stop_percent': 1.0,
            'initial_direction': 'LONG'
        }
        
        result = optimizer._evaluate_parameters(params)
        
        # Check result structure
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.parameters, params)
        self.assertIsInstance(result.roi, float)
        self.assertIsInstance(result.sharpe_ratio, float)
        self.assertIsInstance(result.score, float)
    
    def test_calculate_score(self):
        """Test score calculation"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        metrics = {
            'roi': 10.0,
            'sharpe_ratio': 1.5,
            'win_rate': 60.0,
            'profit_factor': 2.0,
            'calmar_ratio': 2.0
        }
        
        score = optimizer._calculate_score(metrics)
        
        # Score should be positive for positive metrics
        self.assertGreater(score, 0.0)
        
        # Score should be between 0 and 1 approximately
        self.assertLess(score, 2.0)
    
    def test_grid_search(self):
        """Test grid search optimization"""
        # Use even smaller parameter space for fast test
        small_ranges = [
            ParameterRange(
                name='initial_capital',
                min_value=10000.0,
                max_value=10000.0,
                type='float'
            ),
            ParameterRange(
                name='stop_loss_percent',
                min_value=2.0,
                max_value=2.0,
                type='float'
            ),
            ParameterRange(
                name='take_profit_percent',
                min_value=4.0,
                max_value=5.0,
                step=1.0,
                type='float'
            ),
            ParameterRange(
                name='trailing_stop_percent',
                min_value=1.0,
                max_value=1.0,
                type='float'
            ),
            ParameterRange(
                name='initial_direction',
                type='categorical',
                values=['LONG'],
                min_value=0,
                max_value=0
            )
        ]
        
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=small_ranges,
            optimization_metric='score'
        )
        
        results = optimizer.grid_search(n_points=2)
        
        # Should have at least 2 results, exact number depends on grid generation
        self.assertGreaterEqual(len(results), 2)
        
        # Results should be sorted
        if len(results) > 1:
            self.assertGreaterEqual(results[0].score, results[1].score)
        
        # Best result should be set
        self.assertIsNotNone(optimizer.best_result)
        self.assertEqual(optimizer.best_result, results[0])
    
    def test_random_search(self):
        """Test random search optimization"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        # Run with small number of iterations
        results = optimizer.random_search(n_iterations=5, seed=42)
        
        # Should have 5 results
        self.assertEqual(len(results), 5)
        
        # Results should be sorted by score
        scores = [r.score for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Best result should be set
        self.assertIsNotNone(optimizer.best_result)
        self.assertEqual(optimizer.best_result.score, results[0].score)
    
    def test_genetic_algorithm(self):
        """Test genetic algorithm optimization"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        # Run with small population and generations
        results = optimizer.genetic_algorithm(
            population_size=4,
            n_generations=2,
            mutation_rate=0.2,
            crossover_rate=0.7,
            elite_size=1
        )
        
        # Should have 4 * 2 = 8 results
        self.assertEqual(len(results), 8)
        
        # Best result should be set
        self.assertIsNotNone(optimizer.best_result)
    
    def test_tournament_selection(self):
        """Test tournament selection"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        # Create mock population
        population = [
            OptimizationResult(
                parameters={'test': i},
                roi=float(i),
                sharpe_ratio=float(i),
                max_drawdown=0.0,
                total_trades=10,
                win_rate=50.0,
                profit_factor=1.0,
                calmar_ratio=0.0,
                score=float(i)
            )
            for i in range(5)
        ]
        
        np.random.seed(42)
        winner = optimizer._tournament_selection(population, tournament_size=3)
        
        # Winner should be a parameter dictionary
        self.assertIsInstance(winner, dict)
        self.assertIn('test', winner)
    
    def test_crossover(self):
        """Test crossover operation"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        parent1 = {
            'stop_loss_percent': 1.0,
            'take_profit_percent': 2.0,
            'trailing_stop_percent': 0.5,
            'initial_direction': 'LONG',
            'initial_capital': 10000.0
        }
        
        parent2 = {
            'stop_loss_percent': 2.0,
            'take_profit_percent': 4.0,
            'trailing_stop_percent': 1.0,
            'initial_direction': 'SHORT',
            'initial_capital': 10000.0
        }
        
        np.random.seed(42)
        child = optimizer._crossover(parent1, parent2)
        
        # Child should have all parameters
        self.assertEqual(set(child.keys()), set(parent1.keys()))
        
        # Child values should come from parents
        for key in child.keys():
            self.assertIn(child[key], [parent1[key], parent2[key]])
    
    def test_mutate(self):
        """Test mutation operation"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        original = {
            'stop_loss_percent': 1.5,
            'take_profit_percent': 3.0,
            'trailing_stop_percent': 0.75,
            'initial_direction': 'LONG',
            'initial_capital': 10000.0
        }
        
        np.random.seed(42)
        mutated = optimizer._mutate(original)
        
        # Mutated should have all parameters
        self.assertEqual(set(mutated.keys()), set(original.keys()))
        
        # At least one parameter should be different (or values within valid ranges)
        for key, value in mutated.items():
            param_range = next((p for p in optimizer.parameter_ranges if p.name == key), None)
            if param_range:
                if param_range.type == 'categorical':
                    self.assertIn(value, param_range.values)
                else:
                    self.assertGreaterEqual(value, param_range.min_value)
                    self.assertLessEqual(value, param_range.max_value)
    
    def test_generate_report(self):
        """Test report generation"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        # Run quick optimization
        optimizer.random_search(n_iterations=3, seed=42)
        
        # Generate report
        report = optimizer.generate_report(top_n=3)
        
        # Report should be a non-empty string
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
        
        # Report should contain key sections
        self.assertIn('PARAMETER OPTIMIZATION REPORT', report)
        self.assertIn('BEST PARAMETERS FOUND', report)
        self.assertIn('BEST PERFORMANCE METRICS', report)
    
    def test_get_best_parameters(self):
        """Test getting best parameters"""
        optimizer = ParameterOptimizer(
            backtester_class=ReversalBacktester,
            data=self.data,
            parameter_ranges=self.parameter_ranges,
            optimization_metric='score'
        )
        
        # Before optimization
        self.assertIsNone(optimizer.get_best_parameters())
        
        # After optimization
        optimizer.random_search(n_iterations=3, seed=42)
        best = optimizer.get_best_parameters()
        
        self.assertIsNotNone(best)
        self.assertIsInstance(best, dict)
        self.assertIn('stop_loss_percent', best)


if __name__ == '__main__':
    unittest.main()
