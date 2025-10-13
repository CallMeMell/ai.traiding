"""
demo_portfolio_optimization.py - Portfolio Optimization Demo
============================================================
Demonstrates Modern Portfolio Theory and portfolio optimization.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from portfolio_optimizer import (
    PortfolioOptimizer,
    optimize_portfolio,
    rebalance_portfolio
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title: str = ""):
    """Print a separator line"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def create_sample_portfolio_data() -> pd.DataFrame:
    """Create sample price data for multiple assets"""
    np.random.seed(42)
    
    # Generate 2 years of daily data
    dates = pd.date_range('2022-01-01', periods=504, freq='D')
    
    # Simulate asset prices with different characteristics
    assets = {
        'BTC': {
            'start': 40000,
            'drift': 0.0002,
            'volatility': 0.03,
            'label': 'Bitcoin (High Risk/Return)'
        },
        'ETH': {
            'start': 3000,
            'drift': 0.00015,
            'volatility': 0.035,
            'label': 'Ethereum (High Risk/Return)'
        },
        'STOCK': {
            'start': 100,
            'drift': 0.0003,
            'volatility': 0.015,
            'label': 'Tech Stock (Medium Risk/Return)'
        },
        'BOND': {
            'start': 100,
            'drift': 0.00008,
            'volatility': 0.005,
            'label': 'Bond ETF (Low Risk/Return)'
        },
        'GOLD': {
            'start': 1800,
            'drift': 0.00005,
            'volatility': 0.01,
            'label': 'Gold (Low Risk/Return)'
        }
    }
    
    prices_data = {}
    for asset, params in assets.items():
        # Generate prices using geometric Brownian motion
        returns = np.random.normal(params['drift'], params['volatility'], len(dates))
        price_series = params['start'] * np.exp(np.cumsum(returns))
        prices_data[asset] = price_series
    
    prices = pd.DataFrame(prices_data, index=dates)
    
    return prices


def demo_basic_optimization():
    """Demo 1: Basic portfolio optimization"""
    print_separator("Demo 1: Basic Portfolio Optimization")
    
    # Create sample data
    prices = create_sample_portfolio_data()
    
    print(f"\n📊 Portfolio Data:")
    print(f"   Assets: {list(prices.columns)}")
    print(f"   Date range: {prices.index[0]} to {prices.index[-1]}")
    print(f"   Samples: {len(prices)}")
    
    print(f"\n💰 Price Summary:")
    print(prices.describe().round(2))
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    # Calculate returns
    returns = optimizer.calculate_returns(prices)
    expected_returns = optimizer.calculate_expected_returns(returns)
    cov_matrix = optimizer.calculate_covariance_matrix(returns)
    
    print(f"\n📈 Expected Annual Returns:")
    for asset, ret in expected_returns.items():
        print(f"   {asset}: {ret*100:.2f}%")
    
    # Optimize for maximum Sharpe ratio
    print(f"\n🎯 Optimizing for Maximum Sharpe Ratio...")
    result = optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix)
    
    print(f"\n✅ Optimal Portfolio (Max Sharpe):")
    print(f"   Expected Return: {result['expected_return']*100:.2f}%")
    print(f"   Volatility: {result['volatility']*100:.2f}%")
    print(f"   Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    
    print(f"\n📊 Optimal Weights:")
    for asset, weight in result['weights'].items():
        print(f"   {asset}: {weight*100:.1f}%")
    
    return prices, optimizer, result


def demo_minimum_volatility():
    """Demo 2: Minimum volatility portfolio"""
    print_separator("Demo 2: Minimum Volatility Portfolio")
    
    prices = create_sample_portfolio_data()
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    returns = optimizer.calculate_returns(prices)
    expected_returns = optimizer.calculate_expected_returns(returns)
    cov_matrix = optimizer.calculate_covariance_matrix(returns)
    
    print(f"\n🎯 Optimizing for Minimum Volatility...")
    result = optimizer.minimize_volatility(expected_returns, cov_matrix)
    
    print(f"\n✅ Minimum Volatility Portfolio:")
    print(f"   Expected Return: {result['expected_return']*100:.2f}%")
    print(f"   Volatility: {result['volatility']*100:.2f}%")
    print(f"   Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    
    print(f"\n📊 Optimal Weights:")
    for asset, weight in result['weights'].items():
        print(f"   {asset}: {weight*100:.1f}%")


def demo_risk_parity():
    """Demo 3: Risk parity portfolio"""
    print_separator("Demo 3: Risk Parity Portfolio")
    
    prices = create_sample_portfolio_data()
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    returns = optimizer.calculate_returns(prices)
    cov_matrix = optimizer.calculate_covariance_matrix(returns)
    
    print(f"\n🎯 Calculating Risk Parity Weights...")
    result = optimizer.risk_parity(cov_matrix)
    
    print(f"\n✅ Risk Parity Portfolio:")
    print(f"   Each asset contributes equally to portfolio risk")
    
    print(f"\n📊 Risk Parity Weights:")
    for asset, weight in result['weights'].items():
        print(f"   {asset}: {weight*100:.1f}%")


def demo_kelly_criterion():
    """Demo 4: Kelly Criterion position sizing"""
    print_separator("Demo 4: Kelly Criterion Position Sizing")
    
    optimizer = PortfolioOptimizer()
    
    print(f"\n🎲 Kelly Criterion Examples:")
    
    # Example 1: Good strategy
    win_rate = 0.55
    win_loss_ratio = 1.5
    kelly = optimizer.kelly_criterion(win_rate, win_loss_ratio)
    
    print(f"\n   Strategy 1 (Good):")
    print(f"   - Win Rate: {win_rate*100:.0f}%")
    print(f"   - Win/Loss Ratio: {win_loss_ratio:.1f}:1")
    print(f"   - Kelly Position Size: {kelly*100:.1f}%")
    
    # Example 2: Great strategy
    win_rate = 0.65
    win_loss_ratio = 2.0
    kelly = optimizer.kelly_criterion(win_rate, win_loss_ratio)
    
    print(f"\n   Strategy 2 (Great):")
    print(f"   - Win Rate: {win_rate*100:.0f}%")
    print(f"   - Win/Loss Ratio: {win_loss_ratio:.1f}:1")
    print(f"   - Kelly Position Size: {kelly*100:.1f}%")
    
    # Example 3: Poor strategy
    win_rate = 0.45
    win_loss_ratio = 1.0
    kelly = optimizer.kelly_criterion(win_rate, win_loss_ratio)
    
    print(f"\n   Strategy 3 (Poor):")
    print(f"   - Win Rate: {win_rate*100:.0f}%")
    print(f"   - Win/Loss Ratio: {win_loss_ratio:.1f}:1")
    print(f"   - Kelly Position Size: {kelly*100:.1f}% (No position recommended)")


def demo_rebalancing():
    """Demo 5: Portfolio rebalancing"""
    print_separator("Demo 5: Portfolio Rebalancing")
    
    prices = create_sample_portfolio_data()
    
    # Optimize portfolio
    result = optimize_portfolio(prices, method='max_sharpe')
    target_weights = result['weights']
    
    # Simulate current portfolio that has drifted
    current_weights = {}
    for asset in target_weights:
        drift = np.random.uniform(-0.15, 0.15)
        current_weights[asset] = max(0, target_weights[asset] + drift)
    
    # Normalize current weights
    total = sum(current_weights.values())
    current_weights = {k: v/total for k, v in current_weights.items()}
    
    print(f"\n📊 Current Portfolio Weights:")
    for asset, weight in current_weights.items():
        print(f"   {asset}: {weight*100:.1f}%")
    
    print(f"\n🎯 Target Portfolio Weights:")
    for asset, weight in target_weights.items():
        print(f"   {asset}: {weight*100:.1f}%")
    
    # Calculate rebalancing trades
    trades = rebalance_portfolio(current_weights, target_weights, threshold=0.05)
    
    if trades:
        print(f"\n🔄 Rebalancing Trades Needed:")
        for asset, trade in trades.items():
            action = "BUY" if trade > 0 else "SELL"
            print(f"   {action} {asset}: {abs(trade)*100:.1f}%")
    else:
        print(f"\n✅ No rebalancing needed (all differences < 5%)")


def demo_efficient_frontier():
    """Demo 6: Efficient frontier visualization"""
    print_separator("Demo 6: Efficient Frontier")
    
    prices = create_sample_portfolio_data()
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    returns = optimizer.calculate_returns(prices)
    expected_returns = optimizer.calculate_expected_returns(returns)
    cov_matrix = optimizer.calculate_covariance_matrix(returns)
    
    print(f"\n📈 Calculating Efficient Frontier...")
    frontier = optimizer.efficient_frontier(expected_returns, cov_matrix, n_points=30)
    
    print(f"\n✅ Efficient Frontier calculated: {len(frontier)} points")
    print(f"\n   Sample points:")
    print(frontier.head(5).to_string())
    
    # Try to plot if matplotlib is available
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(frontier['volatility'] * 100, frontier['return'] * 100, 'b-', linewidth=2)
        plt.scatter(frontier['volatility'] * 100, frontier['return'] * 100, c=frontier['sharpe'], cmap='viridis', s=50)
        plt.colorbar(label='Sharpe Ratio')
        plt.xlabel('Volatility (%)')
        plt.ylabel('Expected Return (%)')
        plt.title('Efficient Frontier')
        plt.grid(True, alpha=0.3)
        
        # Save plot
        import os
        os.makedirs('models/portfolio', exist_ok=True)
        plt.savefig('models/portfolio/efficient_frontier.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 Plot saved to: models/portfolio/efficient_frontier.png")
        plt.close()
    except Exception as e:
        logger.warning(f"Could not create plot: {e}")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Portfolio Optimization Demo" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run demos
    demo_basic_optimization()
    demo_minimum_volatility()
    demo_risk_parity()
    demo_kelly_criterion()
    demo_rebalancing()
    demo_efficient_frontier()
    
    print_separator("All Demos Complete!")
    print("\n📝 Next Steps:")
    print("   1. Use your own asset data")
    print("   2. Experiment with different optimization methods")
    print("   3. Implement dynamic rebalancing strategies")
    print("   4. Combine with ML predictions for better asset selection")
    print("")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
