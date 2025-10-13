"""
portfolio_optimizer.py - Portfolio Optimization Module
======================================================
Modern Portfolio Theory (Markowitz) and portfolio optimization strategies.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """
    Portfolio optimizer using Modern Portfolio Theory
    
    Implements:
    - Markowitz Mean-Variance Optimization
    - Maximum Sharpe Ratio
    - Minimum Volatility
    - Risk Parity
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.risk_free_rate = risk_free_rate
        logger.info(f"PortfolioOptimizer initialized (risk-free rate: {risk_free_rate})")
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns from price data
        
        Args:
            prices: DataFrame with asset prices (columns = assets)
        
        Returns:
            DataFrame of returns
        """
        returns = prices.pct_change().dropna()
        return returns
    
    def calculate_expected_returns(
        self,
        returns: pd.DataFrame,
        method: str = 'mean'
    ) -> pd.Series:
        """
        Calculate expected returns
        
        Args:
            returns: DataFrame of returns
            method: 'mean' or 'ewm' (exponentially weighted)
        
        Returns:
            Series of expected annual returns
        """
        if method == 'mean':
            expected_returns = returns.mean() * 252  # Annualize
        elif method == 'ewm':
            expected_returns = returns.ewm(span=60).mean().iloc[-1] * 252
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return expected_returns
    
    def calculate_covariance_matrix(
        self,
        returns: pd.DataFrame,
        method: str = 'sample'
    ) -> pd.DataFrame:
        """
        Calculate covariance matrix
        
        Args:
            returns: DataFrame of returns
            method: 'sample' or 'ledoit_wolf'
        
        Returns:
            Covariance matrix (annualized)
        """
        if method == 'sample':
            cov_matrix = returns.cov() * 252  # Annualize
        elif method == 'ledoit_wolf':
            from sklearn.covariance import LedoitWolf
            lw = LedoitWolf()
            cov_matrix = pd.DataFrame(
                lw.fit(returns).covariance_ * 252,
                index=returns.columns,
                columns=returns.columns
            )
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return cov_matrix
    
    def portfolio_performance(
        self,
        weights: np.ndarray,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame
    ) -> Tuple[float, float, float]:
        """
        Calculate portfolio performance metrics
        
        Args:
            weights: Asset weights
            expected_returns: Expected returns
            cov_matrix: Covariance matrix
        
        Returns:
            (return, volatility, sharpe_ratio)
        """
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return portfolio_return, portfolio_volatility, sharpe_ratio
    
    def maximize_sharpe_ratio(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        constraints: Optional[List] = None
    ) -> Dict[str, any]:
        """
        Find portfolio weights that maximize Sharpe ratio
        
        Args:
            expected_returns: Expected returns for each asset
            cov_matrix: Covariance matrix
            constraints: Additional constraints
        
        Returns:
            Dict with weights and metrics
        """
        n_assets = len(expected_returns)
        
        # Objective: minimize negative Sharpe ratio
        def neg_sharpe(weights):
            ret, vol, sharpe = self.portfolio_performance(weights, expected_returns, cov_matrix)
            return -sharpe
        
        # Constraints
        constraints_list = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        ]
        if constraints:
            constraints_list.extend(constraints)
        
        # Bounds: 0 <= weight <= 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            neg_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list
        )
        
        if not result.success:
            logger.warning(f"Optimization failed: {result.message}")
        
        optimal_weights = result.x
        ret, vol, sharpe = self.portfolio_performance(optimal_weights, expected_returns, cov_matrix)
        
        return {
            'weights': dict(zip(expected_returns.index, optimal_weights)),
            'expected_return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'success': result.success
        }
    
    def minimize_volatility(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        target_return: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Find minimum volatility portfolio
        
        Args:
            expected_returns: Expected returns
            cov_matrix: Covariance matrix
            target_return: Optional target return constraint
        
        Returns:
            Dict with weights and metrics
        """
        n_assets = len(expected_returns)
        
        # Objective: minimize volatility
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        ]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.dot(x, expected_returns) - target_return
            })
        
        # Bounds
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        ret, vol, sharpe = self.portfolio_performance(optimal_weights, expected_returns, cov_matrix)
        
        return {
            'weights': dict(zip(expected_returns.index, optimal_weights)),
            'expected_return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'success': result.success
        }
    
    def risk_parity(
        self,
        cov_matrix: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Calculate risk parity portfolio weights
        
        Equal risk contribution from each asset
        
        Args:
            cov_matrix: Covariance matrix
        
        Returns:
            Dict with weights
        """
        n_assets = len(cov_matrix)
        
        # Objective: minimize difference in risk contributions
        def risk_parity_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights)
            risk_contrib = weights * marginal_contrib / portfolio_vol
            
            # Minimize variance of risk contributions
            return np.sum((risk_contrib - risk_contrib.mean()) ** 2)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        
        # Bounds
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            risk_parity_objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        
        return {
            'weights': dict(zip(cov_matrix.index, optimal_weights)),
            'success': result.success
        }
    
    def efficient_frontier(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        n_points: int = 50
    ) -> pd.DataFrame:
        """
        Calculate efficient frontier
        
        Args:
            expected_returns: Expected returns
            cov_matrix: Covariance matrix
            n_points: Number of points on frontier
        
        Returns:
            DataFrame with frontier points
        """
        min_return = expected_returns.min()
        max_return = expected_returns.max()
        
        target_returns = np.linspace(min_return, max_return, n_points)
        
        frontier = []
        for target in target_returns:
            result = self.minimize_volatility(expected_returns, cov_matrix, target_return=target)
            if result['success']:
                frontier.append({
                    'return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe': result['sharpe_ratio']
                })
        
        return pd.DataFrame(frontier)
    
    def kelly_criterion(
        self,
        win_rate: float,
        win_loss_ratio: float
    ) -> float:
        """
        Calculate Kelly Criterion position size
        
        Args:
            win_rate: Probability of winning (0-1)
            win_loss_ratio: Average win / average loss
        
        Returns:
            Optimal position size (fraction of capital)
        """
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Apply half-Kelly for safety
        kelly_half = kelly / 2
        
        # Bound between 0 and 1
        kelly_bounded = max(0, min(kelly_half, 1))
        
        return kelly_bounded


def optimize_portfolio(
    prices: pd.DataFrame,
    method: str = 'max_sharpe',
    risk_free_rate: float = 0.02,
    **kwargs
) -> Dict[str, any]:
    """
    Convenience function for portfolio optimization
    
    Args:
        prices: DataFrame of asset prices
        method: 'max_sharpe', 'min_vol', or 'risk_parity'
        risk_free_rate: Annual risk-free rate
        **kwargs: Additional arguments for specific methods
    
    Returns:
        Optimization results
    """
    optimizer = PortfolioOptimizer(risk_free_rate=risk_free_rate)
    
    returns = optimizer.calculate_returns(prices)
    expected_returns = optimizer.calculate_expected_returns(returns)
    cov_matrix = optimizer.calculate_covariance_matrix(returns)
    
    if method == 'max_sharpe':
        result = optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix)
    elif method == 'min_vol':
        result = optimizer.minimize_volatility(expected_returns, cov_matrix, **kwargs)
    elif method == 'risk_parity':
        result = optimizer.risk_parity(cov_matrix)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return result


def rebalance_portfolio(
    current_weights: Dict[str, float],
    target_weights: Dict[str, float],
    threshold: float = 0.05
) -> Dict[str, float]:
    """
    Calculate rebalancing trades
    
    Args:
        current_weights: Current portfolio weights
        target_weights: Target weights from optimization
        threshold: Minimum weight difference to trigger rebalance
    
    Returns:
        Dict of trades (positive = buy, negative = sell)
    """
    trades = {}
    
    for asset in target_weights:
        current = current_weights.get(asset, 0)
        target = target_weights[asset]
        difference = target - current
        
        if abs(difference) > threshold:
            trades[asset] = difference
    
    return trades
