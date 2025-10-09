"""
batch_backtester.py - Batch Backtesting for Multiple Strategies
================================================================
Test multiple strategies simultaneously and compare performance
"""
import os
import sys
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from utils import (
    setup_logging, generate_sample_data, validate_ohlcv_data,
    calculate_performance_metrics, format_currency, format_percentage,
    generate_equity_curve_chart, generate_drawdown_chart,
    generate_pnl_distribution_chart
)

logger = None


class BatchBacktester:
    """
    Batch Backtesting Engine for Multiple Strategies
    
    Tests multiple strategies with the same historical data and
    compares their performance metrics side-by-side.
    """
    
    def __init__(self, initial_capital: float = 10000.0, trade_size: float = 100.0):
        """
        Args:
            initial_capital: Starting capital for all strategies
            trade_size: Trade size for all strategies
        """
        global logger
        logger = setup_logging(log_level="INFO")
        
        logger.info("=" * 70)
        logger.info("📊 BATCH BACKTESTER INITIALIZED")
        logger.info("=" * 70)
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"Trade Size: {trade_size}")
        logger.info("=" * 70 + "\n")
        
        self.initial_capital = initial_capital
        self.trade_size = trade_size
        self.results: Dict[str, Dict[str, Any]] = {}
        self.strategies: Dict[str, Any] = {}
    
    def add_strategy(self, name: str, strategy: Any):
        """
        Add a strategy to the batch test
        
        Args:
            name: Unique name for the strategy
            strategy: Strategy instance with generate_signal() method
        """
        self.strategies[name] = strategy
        logger.info(f"✓ Added strategy: {name}")
    
    def backtest_single_strategy(self, strategy_name: str, strategy: Any, 
                                 data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run backtest for a single strategy
        
        Args:
            strategy_name: Name of the strategy
            strategy: Strategy instance
            data: OHLCV DataFrame
        
        Returns:
            Dictionary with performance metrics and results
        """
        logger.info(f"\n🔄 Backtesting: {strategy_name}")
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity_curve = []
        
        # Determine minimum bars needed
        if hasattr(strategy, 'long_window'):
            min_bars = strategy.long_window + 10
        elif hasattr(strategy, 'window'):
            min_bars = strategy.window + 10
        else:
            min_bars = 100
        
        # Iterate through data
        for i in range(min_bars, len(data)):
            df_slice = data.iloc[:i+1].copy()
            
            # Generate signal
            try:
                signal = strategy.generate_signal(df_slice)
            except Exception as e:
                logger.warning(f"Signal generation failed at bar {i}: {e}")
                signal = 0
            
            current_price = df_slice['close'].iloc[-1]
            current_time = df_slice['timestamp'].iloc[-1] if 'timestamp' in df_slice.columns else i
            
            # BUY Signal
            if signal == 1 and position == 0:
                position = 1
                entry_price = current_price
                trades.append({
                    'timestamp': current_time,
                    'type': 'BUY',
                    'price': current_price,
                    'quantity': self.trade_size,
                    'capital_before': capital,
                    'pnl': 0
                })
            
            # SELL Signal
            elif signal == -1 and position == 1:
                pnl = (current_price - entry_price) * self.trade_size
                capital += pnl
                position = 0
                trades.append({
                    'timestamp': current_time,
                    'type': 'SELL',
                    'price': current_price,
                    'quantity': self.trade_size,
                    'capital_before': capital - pnl,
                    'pnl': pnl
                })
            
            # Track equity
            equity_curve.append({
                'timestamp': current_time,
                'capital': capital,
                'position_value': position * self.trade_size * current_price
            })
        
        # Calculate performance metrics
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        
        if not sell_trades:
            metrics = {
                'strategy_name': strategy_name,
                'total_trades': 0,
                'total_pnl': 0,
                'roi': 0,
                'win_rate': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'avg_trade': 0,
                'final_capital': capital,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        else:
            pnls = [t['pnl'] for t in sell_trades]
            total_pnl = sum(pnls)
            wins = [p for p in pnls if p > 0]
            
            # Use utility function for extended metrics
            equity_values = [e['capital'] for e in equity_curve]
            extended_metrics = calculate_performance_metrics(
                sell_trades, 
                equity_values, 
                self.initial_capital
            )
            
            metrics = {
                'strategy_name': strategy_name,
                'total_trades': len(sell_trades),
                'total_pnl': total_pnl,
                'roi': (total_pnl / self.initial_capital) * 100,
                'win_rate': (len(wins) / len(pnls)) * 100 if pnls else 0,
                'best_trade': max(pnls) if pnls else 0,
                'worst_trade': min(pnls) if pnls else 0,
                'avg_trade': total_pnl / len(pnls) if pnls else 0,
                'final_capital': capital,
                'sharpe_ratio': extended_metrics.get('sharpe_ratio', 0),
                'max_drawdown': extended_metrics.get('max_drawdown', 0)
            }
        
        logger.info(f"  ✓ {metrics['total_trades']} trades | ROI: {metrics['roi']:.2f}%")
        
        return {
            'metrics': metrics,
            'trades': trades,
            'equity_curve': equity_curve
        }
    
    def run_batch(self, data: pd.DataFrame):
        """
        Run backtest for all strategies
        
        Args:
            data: OHLCV DataFrame
        """
        if not self.strategies:
            logger.error("No strategies added. Use add_strategy() first.")
            return
        
        logger.info("\n" + "=" * 70)
        logger.info("🚀 STARTING BATCH BACKTEST")
        logger.info("=" * 70)
        logger.info(f"Strategies: {len(self.strategies)}")
        logger.info(f"Data points: {len(data)}")
        if 'timestamp' in data.columns:
            logger.info(f"Period: {data['timestamp'].iloc[0]} to {data['timestamp'].iloc[-1]}")
        logger.info("=" * 70)
        
        # Test each strategy
        for name, strategy in self.strategies.items():
            try:
                result = self.backtest_single_strategy(name, strategy, data)
                self.results[name] = result
            except Exception as e:
                logger.error(f"❌ Error testing {name}: {e}")
                import traceback
                traceback.print_exc()
                self.results[name] = {
                    'metrics': {
                        'strategy_name': name,
                        'error': str(e)
                    },
                    'trades': [],
                    'equity_curve': []
                }
        
        # Print comparison
        self._print_comparison()
    
    def _print_comparison(self):
        """Print detailed comparison of all strategies"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 BATCH BACKTEST RESULTS")
        logger.info("=" * 70)
        
        # Filter successful results
        successful_results = [
            (name, res['metrics']) 
            for name, res in self.results.items() 
            if 'error' not in res['metrics']
        ]
        
        if not successful_results:
            logger.error("No successful backtests to compare")
            return
        
        # Sort by ROI
        sorted_results = sorted(
            successful_results,
            key=lambda x: x[1]['roi'],
            reverse=True
        )
        
        # Print table header
        print(f"\n{'Rank':<6}{'Strategy':<35}{'Trades':<10}{'ROI':<12}{'Win Rate':<12}{'Sharpe':<10}")
        print("-" * 85)
        
        # Print results
        for rank, (name, metrics) in enumerate(sorted_results, 1):
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            
            print(f"{emoji} #{rank:<3}{name:<35}"
                  f"{metrics['total_trades']:<10}"
                  f"{metrics['roi']:>+10.2f}%  "
                  f"{metrics['win_rate']:>9.1f}%  "
                  f"{metrics['sharpe_ratio']:>8.2f}")
        
        print("-" * 85)
        
        # Detailed results for top 3
        logger.info("\n" + "=" * 70)
        logger.info("🏆 TOP 3 DETAILED RESULTS")
        logger.info("=" * 70)
        
        for rank, (name, metrics) in enumerate(sorted_results[:3], 1):
            logger.info(f"\n{rank}. {name}")
            logger.info(f"   Initial Capital:  ${self.initial_capital:,.2f}")
            logger.info(f"   Final Capital:    ${metrics['final_capital']:,.2f}")
            logger.info(f"   Total P&L:        ${metrics['total_pnl']:,.2f}")
            logger.info(f"   ROI:              {metrics['roi']:+.2f}%")
            logger.info(f"   Total Trades:     {metrics['total_trades']}")
            logger.info(f"   Win Rate:         {metrics['win_rate']:.1f}%")
            logger.info(f"   Best Trade:       ${metrics['best_trade']:,.2f}")
            logger.info(f"   Worst Trade:      ${metrics['worst_trade']:,.2f}")
            logger.info(f"   Avg Trade:        ${metrics['avg_trade']:,.2f}")
            logger.info(f"   Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}")
            logger.info(f"   Max Drawdown:     {metrics['max_drawdown']:.2f}%")
        
        # Print errors if any
        errors = [(name, res['metrics']) for name, res in self.results.items() 
                 if 'error' in res['metrics']]
        if errors:
            logger.info("\n⚠️ ERRORS:")
            for name, metrics in errors:
                logger.info(f"  - {name}: {metrics['error']}")
        
        logger.info("\n" + "=" * 70)
    
    def export_results(self, output_dir: str = "data"):
        """
        Export results to CSV
        
        Args:
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Export summary
        summary_data = []
        for name, result in self.results.items():
            if 'error' not in result['metrics']:
                summary_data.append(result['metrics'])
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df = summary_df.sort_values('roi', ascending=False)
            summary_file = os.path.join(output_dir, 'batch_backtest_summary.csv')
            summary_df.to_csv(summary_file, index=False)
            logger.info(f"\n✓ Summary exported to: {summary_file}")
        
        # Export individual strategy results
        for name, result in self.results.items():
            if result['trades']:
                safe_name = name.replace('/', '_').replace(' ', '_')
                trades_file = os.path.join(output_dir, f'trades_{safe_name}.csv')
                trades_df = pd.DataFrame(result['trades'])
                trades_df.to_csv(trades_file, index=False)
                logger.info(f"✓ Trades exported to: {trades_file}")
    
    def visualize_results(self, output_dir: str = "data", use_plotly: bool = False):
        """
        Generate visualizations for all strategies
        
        Args:
            output_dir: Directory to save visualizations
            use_plotly: Use Plotly instead of Matplotlib
        
        Returns:
            Dictionary mapping strategy names to their chart paths
        """
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 GENERATING BATCH VISUALIZATIONS")
        logger.info("=" * 70)
        
        all_charts = {}
        ext = '.html' if use_plotly else '.png'
        
        for name, result in self.results.items():
            if 'error' in result['metrics']:
                continue
            
            safe_name = name.replace('/', '_').replace(' ', '_')
            strategy_charts = {}
            
            # Equity curve
            if result['equity_curve']:
                equity_file = os.path.join(output_dir, f'equity_{safe_name}{ext}')
                chart_result = generate_equity_curve_chart(
                    result['equity_curve'],
                    equity_file,
                    use_plotly=use_plotly,
                    title=f"Equity Curve - {name}"
                )
                if chart_result:
                    strategy_charts['equity'] = chart_result
            
            # Drawdown
            if result['equity_curve']:
                drawdown_file = os.path.join(output_dir, f'drawdown_{safe_name}{ext}')
                chart_result = generate_drawdown_chart(
                    result['equity_curve'],
                    drawdown_file,
                    use_plotly=use_plotly,
                    title=f"Drawdown - {name}"
                )
                if chart_result:
                    strategy_charts['drawdown'] = chart_result
            
            # P&L distribution
            if result['trades']:
                pnl_file = os.path.join(output_dir, f'pnl_{safe_name}{ext}')
                chart_result = generate_pnl_distribution_chart(
                    result['trades'],
                    pnl_file,
                    use_plotly=use_plotly,
                    title=f"P&L Distribution - {name}"
                )
                if chart_result:
                    strategy_charts['pnl'] = chart_result
            
            if strategy_charts:
                all_charts[name] = strategy_charts
        
        logger.info(f"✓ Generated visualizations for {len(all_charts)} strategies")
        logger.info("=" * 70 + "\n")
        
        return all_charts


def main():
    """Main function for batch backtesting"""
    print("=" * 70)
    print("📊 BATCH BACKTESTING - MULTIPLE STRATEGIES")
    print("=" * 70)
    print()
    
    # Import strategies
    try:
        from strategy import (
            MACrossoverStrategy,
            RSIStrategy,
            BollingerBandsStrategy,
            EMACrossoverStrategy
        )
        from golden_cross_strategy import GoldenCrossStrategy
    except ImportError as e:
        print(f"❌ Error importing strategies: {e}")
        print("Make sure all strategy modules are available.")
        sys.exit(1)
    
    # Choose data source
    print("Data source:")
    print("  [1] Simulated data (1000 bars)")
    print("  [2] Simulated data (2000 bars)")
    print("  [3] Load from CSV")
    print()
    
    choice = input("Choice (1-3): ").strip()
    
    try:
        if choice == "1":
            data = generate_sample_data(n_bars=1000, start_price=30000)
            logger.info("✓ Generated 1000 simulated bars")
        elif choice == "2":
            data = generate_sample_data(n_bars=2000, start_price=30000)
            logger.info("✓ Generated 2000 simulated bars")
        elif choice == "3":
            filepath = input("CSV file path: ").strip()
            data = pd.read_csv(filepath)
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
            logger.info(f"✓ Loaded {len(data)} bars from {filepath}")
        else:
            print("❌ Invalid choice")
            sys.exit(1)
        
        # Validate data
        is_valid, error = validate_ohlcv_data(data)
        if not is_valid:
            print(f"❌ Invalid data: {error}")
            sys.exit(1)
        
        # Get parameters
        capital_input = input("\nInitial Capital ($) [10000]: ").strip() or "10000"
        capital = float(capital_input)
        
        trade_size_input = input("Trade Size [100]: ").strip() or "100"
        trade_size = float(trade_size_input)
        
        # Create batch backtester
        batch_tester = BatchBacktester(initial_capital=capital, trade_size=trade_size)
        
        # Add strategies
        print("\nAdding strategies...")
        batch_tester.add_strategy(
            'Golden Cross (50/200)',
            GoldenCrossStrategy({
                'short_window': 50,
                'long_window': 200,
                'confirmation_days': 3
            })
        )
        batch_tester.add_strategy(
            'MA Crossover (20/50)',
            MACrossoverStrategy({'short_window': 20, 'long_window': 50})
        )
        batch_tester.add_strategy(
            'RSI Mean Reversion',
            RSIStrategy({'window': 14, 'oversold_threshold': 35, 'overbought_threshold': 65})
        )
        batch_tester.add_strategy(
            'EMA Crossover (9/21)',
            EMACrossoverStrategy({'short_window': 9, 'long_window': 21})
        )
        batch_tester.add_strategy(
            'Bollinger Bands',
            BollingerBandsStrategy({'window': 20, 'std_dev': 2.0})
        )
        
        # Run batch backtest
        batch_tester.run_batch(data)
        
        # Export results
        export = input("\nExport results? (y/n): ").strip().lower()
        if export == 'y':
            batch_tester.export_results()
        
        # Generate visualizations
        viz = input("Generate visualizations? (y/n): ").strip().lower()
        if viz == 'y':
            use_plotly_input = input("Use Plotly (interactive)? (y/n): ").strip().lower()
            use_plotly = use_plotly_input == 'y'
            batch_tester.visualize_results(use_plotly=use_plotly)
        
        print("\n✓ Batch backtest completed!\n")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Batch backtest cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
