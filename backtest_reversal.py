"""
backtest_reversal.py - Backtester for Reversal-Trailing-Stop Strategy
=======================================================================
Backtesting engine specifically designed for the Reversal-Trailing-Stop strategy
with comprehensive performance metrics including Sharpe Ratio and Maximum Drawdown.
"""
import sys
import pandas as pd
from datetime import datetime
from typing import Optional

from strategy_core import ReversalTrailingStopStrategy
from utils import (
    setup_logging, generate_sample_data, validate_ohlcv_data,
    calculate_sharpe_ratio, calculate_max_drawdown, calculate_performance_metrics,
    format_currency, format_percentage
)

logger = None


class ReversalBacktester:
    """
    Backtesting Engine for Reversal-Trailing-Stop Strategy
    
    Tests the Reversal-Trailing-Stop strategy with historical OHLCV data
    and provides detailed performance metrics including:
    - Total ROI
    - Sharpe Ratio
    - Maximum Drawdown
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        stop_loss_percent: float = 2.0,
        take_profit_percent: float = 4.0,
        trailing_stop_percent: float = 1.0,
        initial_direction: str = 'LONG'
    ):
        """
        Initialize the backtester
        
        Args:
            initial_capital: Starting capital
            stop_loss_percent: Stop-loss percentage (e.g., 2.0 = 2%)
            take_profit_percent: Take-profit percentage (e.g., 4.0 = 4%)
            trailing_stop_percent: Trailing stop percentage (e.g., 1.0 = 1%)
            initial_direction: Initial position direction ('LONG' or 'SHORT')
        """
        global logger
        logger = setup_logging(
            log_level="INFO",
            log_file="logs/backtest_reversal.log"
        )
        
        logger.info("=" * 70)
        logger.info("📈 REVERSAL-TRAILING-STOP BACKTESTER INITIALIZED")
        logger.info("=" * 70)
        
        # Initialize strategy
        self.strategy = ReversalTrailingStopStrategy(
            initial_capital=initial_capital,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent,
            trailing_stop_percent=trailing_stop_percent,
            initial_direction=initial_direction
        )
        
        # Tracking
        self.equity_curve = []
        self.returns = []
        
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"Stop Loss: {stop_loss_percent}%")
        logger.info(f"Take Profit: {take_profit_percent}%")
        logger.info(f"Trailing Stop: {trailing_stop_percent}%")
        logger.info(f"Initial Direction: {initial_direction}")
        logger.info("=" * 70 + "\n")
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load historical data from CSV
        
        Args:
            filepath: Path to CSV file with OHLCV data
        
        Returns:
            DataFrame with validated data
        """
        logger.info(f"Loading data from: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Convert timestamp if present
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Validate data
            is_valid, error = validate_ohlcv_data(df)
            if not is_valid:
                raise ValueError(f"Invalid data: {error}")
            
            logger.info(f"✓ {len(df)} candles loaded and validated\n")
            return df
            
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def run(self, data: pd.DataFrame):
        """
        Run backtest with given data
        
        Args:
            data: DataFrame with OHLCV data
        """
        logger.info("=" * 70)
        logger.info("🚀 STARTING BACKTEST")
        logger.info("=" * 70)
        logger.info(f"Period: {data['timestamp'].iloc[0] if 'timestamp' in data.columns else 'N/A'} to {data['timestamp'].iloc[-1] if 'timestamp' in data.columns else 'N/A'}")
        logger.info(f"Data points: {len(data)}")
        logger.info(f"Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
        logger.info("=" * 70 + "\n")
        
        # Reset tracking
        self.equity_curve = []
        self.returns = []
        
        # Initial equity
        self.equity_curve.append(self.strategy.capital)
        
        # Process each candle
        for idx, row in data.iterrows():
            candle = pd.Series({
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            })
            
            # Get previous capital
            prev_capital = self.strategy.capital
            
            # Process candle
            result = self.strategy.process_candle(candle)
            
            # Track equity
            self.equity_curve.append(self.strategy.capital)
            
            # Calculate return
            if prev_capital > 0:
                ret = (self.strategy.capital - prev_capital) / prev_capital
                self.returns.append(ret)
            
            # Log significant actions
            if result['action'] in ['BUY', 'SELL', 'REVERSE', 'REENTER']:
                logger.info(f"[Candle {idx}] {result['action']} @ ${result['price']:.2f}")
                if result['trade_info']:
                    trade = result['trade_info']
                    pnl_emoji = "💰" if trade['pnl'] > 0 else "📉"
                    logger.info(f"  {pnl_emoji} P&L: ${trade['pnl']:.2f} ({trade['exit_reason']})")
                    logger.info(f"  Capital: ${trade['capital_after']:.2f}")
        
        # Generate report
        self._generate_report()
    
    def _generate_report(self):
        """Generate detailed backtest report with all performance metrics"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 BACKTEST REPORT")
        logger.info("=" * 70)
        
        # Get strategy statistics
        stats = self.strategy.get_statistics()
        
        # Capital metrics
        logger.info(f"\n💰 CAPITAL:")
        logger.info(f"  Initial Capital:  {format_currency(stats['initial_capital'])}")
        logger.info(f"  Final Capital:    {format_currency(stats['capital'])}")
        logger.info(f"  Total P&L:        {format_currency(stats['total_pnl'])}")
        logger.info(f"  ROI:              {format_percentage(stats['roi'])}")
        
        # Trade statistics
        if stats['total_trades'] > 0:
            logger.info(f"\n📈 TRADES:")
            logger.info(f"  Total Trades:     {stats['total_trades']}")
            logger.info(f"  Winning Trades:   {stats['winning_trades']}")
            logger.info(f"  Losing Trades:    {stats['losing_trades']}")
            logger.info(f"  Win Rate:         {format_percentage(stats['win_rate'])}")
            logger.info(f"  Average Win:      {format_currency(stats['avg_win'])}")
            logger.info(f"  Average Loss:     {format_currency(stats['avg_loss'])}")
            
            # Profit Factor
            if stats['losing_trades'] > 0 and stats['avg_loss'] != 0:
                total_wins = stats['winning_trades'] * stats['avg_win']
                total_losses = abs(stats['losing_trades'] * stats['avg_loss'])
                profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
                logger.info(f"  Profit Factor:    {profit_factor:.2f}")
        
        # Advanced metrics using calculate_performance_metrics
        logger.info(f"\n📊 ADVANCED METRICS:")
        
        # Calculate comprehensive metrics
        if self.strategy.trades:
            metrics = calculate_performance_metrics(
                self.strategy.trades,
                equity_curve=self.equity_curve,
                initial_capital=stats['initial_capital']
            )
            
            logger.info(f"  Sharpe Ratio:     {metrics['sharpe_ratio']:.3f}")
            logger.info(f"  Max Drawdown:     {format_percentage(metrics['max_drawdown'])}")
            logger.info(f"  Calmar Ratio:     {metrics['calmar_ratio']:.3f}")
            logger.info(f"  Volatility:       {format_percentage(metrics['volatility'] * 100)}")
            logger.info(f"  Profit Factor:    {metrics['profit_factor']:.2f}")
            
            if metrics['avg_trade_duration'] > 0:
                avg_hours = metrics['avg_trade_duration'] / 3600
                logger.info(f"  Avg Trade Duration: {avg_hours:.2f} hours")
        else:
            logger.info(f"  No trades available for advanced metrics")
        
        # Summary interpretation
        logger.info(f"\n💡 PERFORMANCE SUMMARY:")
        
        # ROI interpretation
        if stats['roi'] > 0:
            logger.info(f"  ✅ Strategy was profitable with {format_percentage(stats['roi'])} return")
        else:
            logger.info(f"  ❌ Strategy lost {format_percentage(abs(stats['roi']))}")
        
        # Sharpe ratio interpretation
        if self.returns and len(self.returns) >= 2:
            sharpe = calculate_sharpe_ratio(self.returns)
            if sharpe > 2.0:
                logger.info(f"  ✅ Excellent risk-adjusted returns (Sharpe > 2)")
            elif sharpe > 1.0:
                logger.info(f"  ✅ Good risk-adjusted returns (Sharpe > 1)")
            elif sharpe > 0:
                logger.info(f"  ⚠️  Positive but suboptimal risk-adjusted returns")
            else:
                logger.info(f"  ❌ Poor risk-adjusted returns (negative Sharpe)")
        
        # Win rate interpretation
        if stats['total_trades'] > 0:
            if stats['win_rate'] > 60:
                logger.info(f"  ✅ High win rate: {format_percentage(stats['win_rate'])}")
            elif stats['win_rate'] > 50:
                logger.info(f"  ✓  Positive win rate: {format_percentage(stats['win_rate'])}")
            else:
                logger.info(f"  ⚠️  Below 50% win rate: {format_percentage(stats['win_rate'])}")
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ Backtest completed")
        logger.info("=" * 70 + "\n")
    
    def save_results(self, filepath: str = "data/reversal_backtest_results.csv"):
        """
        Save backtest results to CSV
        
        Args:
            filepath: Path to output file
        """
        import os
        
        if not self.strategy.trades:
            logger.warning("No trades to save")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Convert trades to DataFrame
        df = pd.DataFrame(self.strategy.trades)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"✓ Results saved to: {filepath}")
        
        # Also save equity curve
        equity_filepath = filepath.replace('.csv', '_equity.csv')
        equity_df = pd.DataFrame({
            'step': range(len(self.equity_curve)),
            'capital': self.equity_curve
        })
        equity_df.to_csv(equity_filepath, index=False, encoding='utf-8')
        logger.info(f"✓ Equity curve saved to: {equity_filepath}")


def main():
    """Main function for running backtest"""
    print("=" * 70)
    print("📈 REVERSAL-TRAILING-STOP BACKTESTER")
    print("=" * 70)
    print()
    
    # Choose data source
    print("Data source:")
    print("  [1] Load CSV file")
    print("  [2] Generate simulated data")
    print()
    
    choice = input("Choice (1/2): ").strip()
    
    try:
        # Get strategy parameters
        print("\nStrategy parameters (press Enter for defaults):")
        capital = input("Initial capital [$10,000]: ").strip() or "10000"
        stop_loss = input("Stop loss % [2.0]: ").strip() or "2.0"
        take_profit = input("Take profit % [4.0]: ").strip() or "4.0"
        trailing = input("Trailing stop % [1.0]: ").strip() or "1.0"
        direction = input("Initial direction (LONG/SHORT) [LONG]: ").strip().upper() or "LONG"
        
        # Initialize backtester
        backtester = ReversalBacktester(
            initial_capital=float(capital),
            stop_loss_percent=float(stop_loss),
            take_profit_percent=float(take_profit),
            trailing_stop_percent=float(trailing),
            initial_direction=direction
        )
        
        # Load data
        if choice == "1":
            # Load CSV
            filepath = input("Path to CSV [data/historical_data.csv]: ").strip() or "data/historical_data.csv"
            data = backtester.load_data(filepath)
        
        elif choice == "2":
            # Generate simulated data
            n_bars = input("Number of candles [1000]: ").strip() or "1000"
            n_bars = int(n_bars)
            start_price = input("Start price [30000]: ").strip() or "30000"
            start_price = float(start_price)
            
            logger.info(f"Generating {n_bars} simulated candles...")
            data = generate_sample_data(n_bars=n_bars, start_price=start_price)
            logger.info("✓ Data generated\n")
        
        else:
            print("❌ Invalid choice")
            sys.exit(1)
        
        # Run backtest
        backtester.run(data)
        
        # Save results?
        save = input("\nSave results? (y/n): ").strip().lower()
        if save == 'y':
            backtester.save_results()
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Backtest cancelled")
        sys.exit(0)
    except Exception as e:
        if logger:
            logger.error(f"❌ Error: {e}", exc_info=True)
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
