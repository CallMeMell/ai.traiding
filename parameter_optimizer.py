"""
parameter_optimizer.py - Parameter Optimization Module
======================================================
Automated parameter optimization for trading strategies using various
search algorithms including Grid Search, Random Search, and Genetic Algorithms.

This module integrates with the existing backtesting infrastructure to
systematically find optimal parameters for trading strategies.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple, Optional, Callable
from dataclasses import dataclass, field
import itertools
from copy import deepcopy
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ParameterRange:
    """Defines a parameter's search range"""
    name: str
    min_value: float
    max_value: float
    step: Optional[float] = None  # For grid search
    type: str = 'float'  # 'float', 'int', or 'categorical'
    values: Optional[List[Any]] = None  # For categorical parameters


@dataclass
class OptimizationResult:
    """Result of a single parameter combination evaluation"""
    parameters: Dict[str, Any]
    roi: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    win_rate: float
    profit_factor: float
    calmar_ratio: float
    score: float  # Combined optimization score


class ParameterOptimizer:
    """
    Parameter Optimization Engine for Trading Strategies
    
    Supports multiple optimization algorithms:
    - Grid Search: Exhaustive search over parameter grid
    - Random Search: Random sampling from parameter space
    - Genetic Algorithm: Evolutionary optimization (advanced)
    
    The optimizer runs backtests with different parameter combinations
    and ranks them based on multiple performance metrics.
    """
    
    def __init__(
        self,
        backtester_class,
        data: pd.DataFrame,
        parameter_ranges: List[ParameterRange],
        optimization_metric: str = 'score',
        scoring_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the parameter optimizer
        
        Args:
            backtester_class: Backtester class to use (e.g., ReversalBacktester)
            data: Historical data for backtesting
            parameter_ranges: List of parameter ranges to optimize
            optimization_metric: Metric to optimize ('score', 'roi', 'sharpe_ratio', etc.)
            scoring_weights: Custom weights for combined score calculation
        """
        self.backtester_class = backtester_class
        self.data = data
        self.parameter_ranges = parameter_ranges
        self.optimization_metric = optimization_metric
        
        # Default scoring weights (can be customized)
        self.scoring_weights = scoring_weights or {
            'roi': 0.3,
            'sharpe_ratio': 0.25,
            'win_rate': 0.15,
            'profit_factor': 0.15,
            'calmar_ratio': 0.15
        }
        
        # Results storage
        self.results: List[OptimizationResult] = []
        self.best_result: Optional[OptimizationResult] = None
        
        logger.info("=" * 70)
        logger.info("🔬 PARAMETER OPTIMIZER INITIALIZED")
        logger.info("=" * 70)
        logger.info(f"Optimization Metric: {optimization_metric}")
        logger.info(f"Parameters to optimize: {len(parameter_ranges)}")
        for param in parameter_ranges:
            logger.info(f"  - {param.name}: [{param.min_value}, {param.max_value}]")
        logger.info("=" * 70)
    
    def grid_search(
        self,
        n_points: Optional[int] = None,
        parallel: bool = False
    ) -> List[OptimizationResult]:
        """
        Perform grid search optimization
        
        Args:
            n_points: Number of points per parameter (if step not specified)
            parallel: Whether to run backtests in parallel (not implemented yet)
        
        Returns:
            List of optimization results sorted by performance
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔍 STARTING GRID SEARCH OPTIMIZATION")
        logger.info("=" * 70)
        
        # Generate parameter grid
        param_grid = self._generate_grid(n_points)
        total_combinations = len(param_grid)
        
        logger.info(f"Total combinations to test: {total_combinations}")
        logger.info("=" * 70 + "\n")
        
        # Test each combination
        for i, params in enumerate(param_grid, 1):
            logger.info(f"[{i}/{total_combinations}] Testing: {params}")
            
            result = self._evaluate_parameters(params)
            self.results.append(result)
            
            logger.info(f"  ROI: {result.roi:.2f}%, Sharpe: {result.sharpe_ratio:.2f}, Score: {result.score:.4f}")
        
        # Sort results by optimization metric
        self._rank_results()
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ GRID SEARCH COMPLETED")
        logger.info("=" * 70)
        
        return self.results
    
    def random_search(
        self,
        n_iterations: int = 50,
        seed: Optional[int] = None
    ) -> List[OptimizationResult]:
        """
        Perform random search optimization
        
        Args:
            n_iterations: Number of random parameter combinations to test
            seed: Random seed for reproducibility
        
        Returns:
            List of optimization results sorted by performance
        """
        logger.info("\n" + "=" * 70)
        logger.info("🎲 STARTING RANDOM SEARCH OPTIMIZATION")
        logger.info("=" * 70)
        logger.info(f"Number of iterations: {n_iterations}")
        logger.info("=" * 70 + "\n")
        
        if seed is not None:
            np.random.seed(seed)
        
        # Generate and test random parameter combinations
        for i in range(n_iterations):
            params = self._generate_random_parameters()
            
            logger.info(f"[{i+1}/{n_iterations}] Testing: {params}")
            
            result = self._evaluate_parameters(params)
            self.results.append(result)
            
            logger.info(f"  ROI: {result.roi:.2f}%, Sharpe: {result.sharpe_ratio:.2f}, Score: {result.score:.4f}")
        
        # Sort results by optimization metric
        self._rank_results()
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ RANDOM SEARCH COMPLETED")
        logger.info("=" * 70)
        
        return self.results
    
    def genetic_algorithm(
        self,
        population_size: int = 20,
        n_generations: int = 10,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elite_size: int = 2
    ) -> List[OptimizationResult]:
        """
        Perform genetic algorithm optimization
        
        Args:
            population_size: Size of each generation
            n_generations: Number of generations to evolve
            mutation_rate: Probability of parameter mutation
            crossover_rate: Probability of crossover between parents
            elite_size: Number of best individuals to preserve
        
        Returns:
            List of optimization results sorted by performance
        """
        logger.info("\n" + "=" * 70)
        logger.info("🧬 STARTING GENETIC ALGORITHM OPTIMIZATION")
        logger.info("=" * 70)
        logger.info(f"Population size: {population_size}")
        logger.info(f"Generations: {n_generations}")
        logger.info(f"Mutation rate: {mutation_rate}")
        logger.info(f"Crossover rate: {crossover_rate}")
        logger.info("=" * 70 + "\n")
        
        # Initialize population
        population = [self._generate_random_parameters() for _ in range(population_size)]
        
        for generation in range(n_generations):
            logger.info(f"\n{'='*70}")
            logger.info(f"GENERATION {generation + 1}/{n_generations}")
            logger.info("=" * 70)
            
            # Evaluate population
            generation_results = []
            for i, params in enumerate(population):
                logger.info(f"[{i+1}/{population_size}] Testing: {params}")
                result = self._evaluate_parameters(params)
                generation_results.append(result)
                self.results.append(result)
                logger.info(f"  Score: {result.score:.4f}")
            
            # Sort by fitness
            generation_results.sort(key=lambda x: x.score, reverse=True)
            
            # Log best of generation
            best_gen = generation_results[0]
            logger.info(f"\n🏆 Best of Generation {generation + 1}:")
            logger.info(f"  Parameters: {best_gen.parameters}")
            logger.info(f"  Score: {best_gen.score:.4f}")
            logger.info(f"  ROI: {best_gen.roi:.2f}%")
            logger.info(f"  Sharpe: {best_gen.sharpe_ratio:.2f}")
            
            # Create next generation
            if generation < n_generations - 1:
                # Elitism: keep best individuals
                next_population = [r.parameters for r in generation_results[:elite_size]]
                
                # Generate rest through selection, crossover, and mutation
                while len(next_population) < population_size:
                    # Tournament selection
                    parent1 = self._tournament_selection(generation_results)
                    parent2 = self._tournament_selection(generation_results)
                    
                    # Crossover
                    if np.random.random() < crossover_rate:
                        child = self._crossover(parent1, parent2)
                    else:
                        child = deepcopy(parent1)
                    
                    # Mutation
                    if np.random.random() < mutation_rate:
                        child = self._mutate(child)
                    
                    next_population.append(child)
                
                population = next_population
        
        # Sort all results
        self._rank_results()
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ GENETIC ALGORITHM COMPLETED")
        logger.info("=" * 70)
        
        return self.results
    
    def _generate_grid(self, n_points: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate parameter grid for grid search"""
        param_values = {}
        
        for param in self.parameter_ranges:
            if param.type == 'categorical' and param.values:
                param_values[param.name] = param.values
            elif param.type == 'int':
                step = param.step or max(1, int((param.max_value - param.min_value) / (n_points or 5)))
                param_values[param.name] = list(range(
                    int(param.min_value),
                    int(param.max_value) + 1,
                    step
                ))
            else:  # float
                if param.step:
                    param_values[param.name] = list(np.arange(
                        param.min_value,
                        param.max_value + param.step,
                        param.step
                    ))
                else:
                    n = n_points or 5
                    param_values[param.name] = list(np.linspace(
                        param.min_value,
                        param.max_value,
                        n
                    ))
        
        # Generate all combinations
        keys = list(param_values.keys())
        values = list(param_values.values())
        combinations = list(itertools.product(*values))
        
        return [dict(zip(keys, combo)) for combo in combinations]
    
    def _generate_random_parameters(self) -> Dict[str, Any]:
        """Generate random parameter combination"""
        params = {}
        
        for param in self.parameter_ranges:
            if param.type == 'categorical' and param.values:
                params[param.name] = np.random.choice(param.values)
            elif param.type == 'int':
                params[param.name] = np.random.randint(
                    int(param.min_value),
                    int(param.max_value) + 1
                )
            else:  # float
                params[param.name] = np.random.uniform(
                    param.min_value,
                    param.max_value
                )
        
        return params
    
    def _evaluate_parameters(self, params: Dict[str, Any]) -> OptimizationResult:
        """
        Evaluate a parameter combination by running backtest
        
        Args:
            params: Parameter dictionary to test
        
        Returns:
            OptimizationResult with performance metrics
        """
        # Suppress detailed logging during optimization
        logging.getLogger().setLevel(logging.ERROR)
        
        try:
            # Create backtester with these parameters
            backtester = self.backtester_class(**params)
            
            # Run backtest
            backtester.run(self.data)
            
            # Extract metrics
            stats = backtester.strategy.get_statistics() if hasattr(backtester, 'strategy') else {}
            
            # Calculate comprehensive metrics
            from utils import calculate_performance_metrics
            
            if hasattr(backtester, 'strategy') and backtester.strategy.trades:
                metrics = calculate_performance_metrics(
                    backtester.strategy.trades,
                    equity_curve=backtester.equity_curve if hasattr(backtester, 'equity_curve') else None,
                    initial_capital=params.get('initial_capital', 10000.0)
                )
            else:
                # Fallback metrics
                metrics = {
                    'roi': stats.get('roi', 0.0),
                    'sharpe_ratio': 0.0,
                    'max_drawdown': 0.0,
                    'profit_factor': 0.0,
                    'calmar_ratio': 0.0,
                    'win_rate': stats.get('win_rate', 0.0),
                    'total_trades': stats.get('total_trades', 0)
                }
            
            # Calculate combined score
            score = self._calculate_score(metrics)
            
            result = OptimizationResult(
                parameters=params,
                roi=metrics.get('roi', stats.get('roi', 0.0)),
                sharpe_ratio=metrics.get('sharpe_ratio', 0.0),
                max_drawdown=metrics.get('max_drawdown', 0.0),
                total_trades=metrics.get('total_trades', stats.get('total_trades', 0)),
                win_rate=metrics.get('win_rate', stats.get('win_rate', 0.0)),
                profit_factor=metrics.get('profit_factor', 0.0),
                calmar_ratio=metrics.get('calmar_ratio', 0.0),
                score=score
            )
            
        except Exception as e:
            logger.error(f"Error evaluating parameters {params}: {e}")
            # Return worst possible result
            result = OptimizationResult(
                parameters=params,
                roi=-100.0,
                sharpe_ratio=-10.0,
                max_drawdown=100.0,
                total_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                calmar_ratio=-10.0,
                score=-1000.0
            )
        finally:
            # Restore logging level
            logging.getLogger().setLevel(logging.INFO)
        
        return result
    
    def _calculate_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculate combined optimization score from multiple metrics
        
        Args:
            metrics: Dictionary of performance metrics
        
        Returns:
            Combined score (higher is better)
        """
        score = 0.0
        
        # ROI contribution (normalized to 0-1)
        roi = metrics.get('roi', 0.0)
        score += self.scoring_weights['roi'] * (roi / 100.0)
        
        # Sharpe ratio contribution (normalized, assuming >3 is excellent)
        sharpe = metrics.get('sharpe_ratio', 0.0)
        score += self.scoring_weights['sharpe_ratio'] * min(sharpe / 3.0, 1.0)
        
        # Win rate contribution (0-100% -> 0-1)
        win_rate = metrics.get('win_rate', 0.0)
        score += self.scoring_weights['win_rate'] * (win_rate / 100.0)
        
        # Profit factor contribution (normalized, assuming >3 is excellent)
        profit_factor = metrics.get('profit_factor', 0.0)
        score += self.scoring_weights['profit_factor'] * min(profit_factor / 3.0, 1.0)
        
        # Calmar ratio contribution (normalized, assuming >3 is excellent)
        calmar = metrics.get('calmar_ratio', 0.0)
        score += self.scoring_weights['calmar_ratio'] * min(calmar / 3.0, 1.0)
        
        return score
    
    def _rank_results(self):
        """Sort results by optimization metric"""
        metric_key = self.optimization_metric
        
        if metric_key == 'score':
            self.results.sort(key=lambda x: x.score, reverse=True)
        elif metric_key == 'roi':
            self.results.sort(key=lambda x: x.roi, reverse=True)
        elif metric_key == 'sharpe_ratio':
            self.results.sort(key=lambda x: x.sharpe_ratio, reverse=True)
        elif metric_key == 'max_drawdown':
            self.results.sort(key=lambda x: x.max_drawdown)  # Lower is better
        elif metric_key == 'win_rate':
            self.results.sort(key=lambda x: x.win_rate, reverse=True)
        elif metric_key == 'profit_factor':
            self.results.sort(key=lambda x: x.profit_factor, reverse=True)
        elif metric_key == 'calmar_ratio':
            self.results.sort(key=lambda x: x.calmar_ratio, reverse=True)
        
        self.best_result = self.results[0] if self.results else None
    
    def _tournament_selection(
        self,
        population: List[OptimizationResult],
        tournament_size: int = 3
    ) -> Dict[str, Any]:
        """Select individual using tournament selection"""
        tournament = np.random.choice(population, size=tournament_size, replace=False)
        winner = max(tournament, key=lambda x: x.score)
        return winner.parameters
    
    def _crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform crossover between two parents"""
        child = {}
        
        for param in self.parameter_ranges:
            # Random choice from parents
            if np.random.random() < 0.5:
                child[param.name] = parent1[param.name]
            else:
                child[param.name] = parent2[param.name]
        
        return child
    
    def _mutate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate parameters"""
        mutated = deepcopy(params)
        
        # Select random parameter to mutate
        param_to_mutate = np.random.choice(self.parameter_ranges)
        
        if param_to_mutate.type == 'categorical' and param_to_mutate.values:
            mutated[param_to_mutate.name] = np.random.choice(param_to_mutate.values)
        elif param_to_mutate.type == 'int':
            # Add small random change
            delta = np.random.randint(-2, 3)
            new_val = int(mutated[param_to_mutate.name]) + delta
            new_val = max(int(param_to_mutate.min_value), min(int(param_to_mutate.max_value), new_val))
            mutated[param_to_mutate.name] = new_val
        else:  # float
            # Add small random change (±10% of range)
            range_size = param_to_mutate.max_value - param_to_mutate.min_value
            delta = np.random.uniform(-0.1 * range_size, 0.1 * range_size)
            new_val = mutated[param_to_mutate.name] + delta
            new_val = max(param_to_mutate.min_value, min(param_to_mutate.max_value, new_val))
            mutated[param_to_mutate.name] = new_val
        
        return mutated
    
    def generate_report(
        self,
        top_n: int = 10,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate optimization report
        
        Args:
            top_n: Number of top results to include
            output_file: Optional file path to save report
        
        Returns:
            Report as formatted string
        """
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append("📊 PARAMETER OPTIMIZATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total combinations tested: {len(self.results)}")
        report_lines.append(f"Optimization metric: {self.optimization_metric}")
        report_lines.append("=" * 80)
        
        if self.best_result:
            report_lines.append("\n🏆 BEST PARAMETERS FOUND:")
            report_lines.append("-" * 80)
            for param_name, param_value in self.best_result.parameters.items():
                if isinstance(param_value, float):
                    report_lines.append(f"  {param_name:.<30} {param_value:.4f}")
                else:
                    report_lines.append(f"  {param_name:.<30} {param_value}")
            
            report_lines.append("\n📈 BEST PERFORMANCE METRICS:")
            report_lines.append("-" * 80)
            report_lines.append(f"  Combined Score:........... {self.best_result.score:.4f}")
            report_lines.append(f"  ROI:...................... {self.best_result.roi:.2f}%")
            report_lines.append(f"  Sharpe Ratio:............. {self.best_result.sharpe_ratio:.3f}")
            report_lines.append(f"  Maximum Drawdown:......... {self.best_result.max_drawdown:.2f}%")
            report_lines.append(f"  Total Trades:............. {self.best_result.total_trades}")
            report_lines.append(f"  Win Rate:................. {self.best_result.win_rate:.2f}%")
            report_lines.append(f"  Profit Factor:............ {self.best_result.profit_factor:.2f}")
            report_lines.append(f"  Calmar Ratio:............. {self.best_result.calmar_ratio:.3f}")
        
        report_lines.append(f"\n📋 TOP {min(top_n, len(self.results))} PARAMETER COMBINATIONS:")
        report_lines.append("=" * 80)
        
        # Table header
        header = f"{'Rank':<6} {'Score':<10} {'ROI %':<10} {'Sharpe':<10} {'Win %':<10} {'Trades':<8}"
        report_lines.append(header)
        report_lines.append("-" * 80)
        
        # Top results
        for i, result in enumerate(self.results[:top_n], 1):
            row = (
                f"{i:<6} "
                f"{result.score:<10.4f} "
                f"{result.roi:<10.2f} "
                f"{result.sharpe_ratio:<10.3f} "
                f"{result.win_rate:<10.2f} "
                f"{result.total_trades:<8}"
            )
            report_lines.append(row)
        
        report_lines.append("\n" + "=" * 80)
        report_lines.append("✓ Optimization Report Complete")
        report_lines.append("=" * 80)
        
        report = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report)
            logger.info(f"✓ Report saved to: {output_file}")
        
        return report
    
    def save_results_csv(self, filepath: str = "data/optimization_results.csv"):
        """
        Save all optimization results to CSV
        
        Args:
            filepath: Path to output CSV file
        """
        if not self.results:
            logger.warning("No results to save")
            return
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Convert results to DataFrame
        data = []
        for result in self.results:
            row = {**result.parameters}
            row.update({
                'score': result.score,
                'roi': result.roi,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'total_trades': result.total_trades,
                'win_rate': result.win_rate,
                'profit_factor': result.profit_factor,
                'calmar_ratio': result.calmar_ratio
            })
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Results saved to: {filepath}")
    
    def get_best_parameters(self) -> Optional[Dict[str, Any]]:
        """Get the best parameter combination found"""
        return self.best_result.parameters if self.best_result else None
