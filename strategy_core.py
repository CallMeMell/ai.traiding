"""
strategy_core.py - Reversal-Trailing-Stop Strategy Implementation
==================================================================

Core trading strategy that combines:
1. Immediate position entry on signal detection
2. Dynamic trailing stop-loss mechanism
3. Reversal logic for trend changes

This strategy is designed for volatile markets with clear trend reversals.
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import logging
from abc import ABC

# Import base strategy if available, otherwise define minimal interface
try:
    from strategy import BaseStrategy
except ImportError:
    from abc import ABC, abstractmethod
    
    class BaseStrategy(ABC):
        """Minimal base strategy for standalone use"""
        def __init__(self, name: str, params: Dict[str, Any]):
            self.name = name
            self.params = params
            self.enabled = True
        
        @abstractmethod
        def generate_signal(self, df: pd.DataFrame) -> int:
            pass

logger = logging.getLogger(__name__)


class ReversalTrailingStopStrategy(BaseStrategy):
    """
    Reversal-Trailing-Stop Trading Strategy
    
    STRATEGY LOGIC:
    ===============
    
    1. REVERSAL DETECTION:
       - Uses RSI to detect oversold/overbought conditions
       - Confirms with price momentum (rate of change)
       - Validates with volume increase
    
    2. IMMEDIATE ENTRY:
       - Enters position immediately when reversal is detected
       - No waiting for confirmation bars
       - Fast execution to catch early trend
    
    3. TRAILING STOP-LOSS:
       - Dynamic stop that moves with profitable trades
       - Never moves against the position
       - Based on ATR (Average True Range) for volatility adjustment
    
    4. REVERSAL EXIT:
       - Exits when opposite reversal signal is detected
       - Protects profits by recognizing trend exhaustion
       - Can exit before stop-loss is hit
    
    PARAMETERS:
    ===========
    - rsi_period: Period for RSI calculation (default: 14)
    - rsi_oversold: RSI level for oversold condition (default: 30)
    - rsi_overbought: RSI level for overbought condition (default: 70)
    - roc_period: Rate of Change period (default: 10)
    - roc_threshold: Minimum ROC for momentum confirmation (default: 2.0%)
    - volume_mult: Volume multiplier for confirmation (default: 1.2x)
    - atr_period: ATR period for volatility (default: 14)
    - trailing_stop_mult: ATR multiplier for trailing stop (default: 2.0)
    - initial_stop_mult: Initial stop-loss multiplier (default: 3.0)
    """
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize Reversal-Trailing-Stop Strategy
        
        Args:
            params: Strategy parameters dictionary
        """
        # Default parameters
        default_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'roc_period': 10,
            'roc_threshold': 2.0,
            'volume_mult': 1.2,
            'atr_period': 14,
            'trailing_stop_mult': 2.0,
            'initial_stop_mult': 3.0,
            'min_bars': 50  # Minimum bars needed for calculation
        }
        
        # Merge with provided params
        if params:
            default_params.update(params)
        
        super().__init__("Reversal-Trailing-Stop", default_params)
        
        # Extract parameters
        self.rsi_period = self.params['rsi_period']
        self.rsi_oversold = self.params['rsi_oversold']
        self.rsi_overbought = self.params['rsi_overbought']
        self.roc_period = self.params['roc_period']
        self.roc_threshold = self.params['roc_threshold']
        self.volume_mult = self.params['volume_mult']
        self.atr_period = self.params['atr_period']
        self.trailing_stop_mult = self.params['trailing_stop_mult']
        self.initial_stop_mult = self.params['initial_stop_mult']
        self.min_bars = self.params['min_bars']
        
        # Position tracking
        self.position = 0  # 0 = no position, 1 = long, -1 = short
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.highest_price = 0.0  # For long positions
        self.lowest_price = 0.0   # For short positions
        
        logger.info(f"✓ {self.name} initialized with parameters: {self.params}")
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with 'close' column
            period: RSI period
        
        Returns:
            Series with RSI values
        """
        close = df['close']
        delta = close.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ATR period
        
        Returns:
            Series with ATR values
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def calculate_roc(self, df: pd.DataFrame, period: int = 10) -> pd.Series:
        """
        Calculate Rate of Change (ROC)
        
        Args:
            df: DataFrame with 'close' column
            period: ROC period
        
        Returns:
            Series with ROC values (percentage)
        """
        close = df['close']
        roc = ((close - close.shift(period)) / close.shift(period)) * 100
        
        return roc
    
    def detect_reversal(self, df: pd.DataFrame) -> int:
        """
        Detect reversal signals
        
        Returns:
            1 = Bullish reversal (BUY)
            -1 = Bearish reversal (SELL)
            0 = No reversal
        """
        if len(df) < self.min_bars:
            return 0
        
        # Calculate indicators
        rsi = self.calculate_rsi(df, self.rsi_period)
        roc = self.calculate_roc(df, self.roc_period)
        
        # Current values
        rsi_curr = rsi.iloc[-1]
        roc_curr = roc.iloc[-1]
        
        # Volume confirmation
        volume_curr = df['volume'].iloc[-1]
        volume_avg = df['volume'].rolling(window=20).mean().iloc[-1]
        volume_confirmed = volume_curr > (volume_avg * self.volume_mult)
        
        if pd.isna(rsi_curr) or pd.isna(roc_curr):
            return 0
        
        # Bullish reversal conditions
        if (rsi_curr < self.rsi_oversold and 
            roc_curr < -self.roc_threshold and 
            volume_confirmed):
            logger.info(f"🔄 Bullish reversal detected: RSI={rsi_curr:.2f}, ROC={roc_curr:.2f}%")
            return 1
        
        # Bearish reversal conditions
        if (rsi_curr > self.rsi_overbought and 
            roc_curr > self.roc_threshold and 
            volume_confirmed):
            logger.info(f"🔄 Bearish reversal detected: RSI={rsi_curr:.2f}, ROC={roc_curr:.2f}%")
            return -1
        
        return 0
    
    def calculate_trailing_stop(self, current_price: float, atr: float) -> float:
        """
        Calculate trailing stop-loss price
        
        Args:
            current_price: Current market price
            atr: Current ATR value
        
        Returns:
            New stop-loss price
        """
        if self.position == 1:  # Long position
            # Update highest price
            if current_price > self.highest_price:
                self.highest_price = current_price
            
            # Calculate trailing stop (never moves down)
            new_stop = self.highest_price - (atr * self.trailing_stop_mult)
            self.stop_loss = max(self.stop_loss, new_stop)
            
        elif self.position == -1:  # Short position
            # Update lowest price
            if current_price < self.lowest_price or self.lowest_price == 0:
                self.lowest_price = current_price
            
            # Calculate trailing stop (never moves up)
            new_stop = self.lowest_price + (atr * self.trailing_stop_mult)
            if self.stop_loss == 0:
                self.stop_loss = new_stop
            else:
                self.stop_loss = min(self.stop_loss, new_stop)
        
        return self.stop_loss
    
    def check_stop_loss(self, current_price: float) -> bool:
        """
        Check if stop-loss is triggered
        
        Args:
            current_price: Current market price
        
        Returns:
            True if stop-loss triggered, False otherwise
        """
        if self.position == 1:  # Long position
            return current_price <= self.stop_loss
        elif self.position == -1:  # Short position
            return current_price >= self.stop_loss
        
        return False
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate trading signal
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            1 = BUY, -1 = SELL, 0 = HOLD
        """
        if not self.enabled or len(df) < self.min_bars:
            return 0
        
        current_price = df['close'].iloc[-1]
        atr = self.calculate_atr(df, self.atr_period).iloc[-1]
        
        if pd.isna(atr):
            return 0
        
        # Update trailing stop if in position
        if self.position != 0:
            self.calculate_trailing_stop(current_price, atr)
        
        # Check stop-loss
        if self.position != 0 and self.check_stop_loss(current_price):
            logger.info(f"🛑 Stop-loss triggered at ${current_price:.2f} (Stop: ${self.stop_loss:.2f})")
            signal = -self.position  # Exit signal
            self.reset_position()
            return signal
        
        # Detect reversal
        reversal = self.detect_reversal(df)
        
        # No position - Look for entry
        if self.position == 0:
            if reversal == 1:  # Bullish reversal
                self.position = 1
                self.entry_price = current_price
                self.highest_price = current_price
                self.stop_loss = current_price - (atr * self.initial_stop_mult)
                logger.info(f"📈 LONG entry at ${current_price:.2f}, Stop: ${self.stop_loss:.2f}")
                return 1
            
            elif reversal == -1:  # Bearish reversal
                self.position = -1
                self.entry_price = current_price
                self.lowest_price = current_price
                self.stop_loss = current_price + (atr * self.initial_stop_mult)
                logger.info(f"📉 SHORT entry at ${current_price:.2f}, Stop: ${self.stop_loss:.2f}")
                return -1
        
        # In position - Check for opposite reversal (exit signal)
        else:
            if self.position == 1 and reversal == -1:
                logger.info(f"🔄 Opposite reversal detected, exiting LONG at ${current_price:.2f}")
                self.reset_position()
                return -1
            
            elif self.position == -1 and reversal == 1:
                logger.info(f"🔄 Opposite reversal detected, exiting SHORT at ${current_price:.2f}")
                self.reset_position()
                return 1
        
        return 0  # HOLD
    
    def reset_position(self):
        """Reset position tracking variables"""
        self.position = 0
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.highest_price = 0.0
        self.lowest_price = 0.0
    
    def get_position_info(self) -> Dict[str, Any]:
        """
        Get current position information
        
        Returns:
            Dictionary with position details
        """
        return {
            'position': self.position,
            'position_type': 'LONG' if self.position == 1 else 'SHORT' if self.position == -1 else 'NONE',
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'highest_price': self.highest_price if self.position == 1 else None,
            'lowest_price': self.lowest_price if self.position == -1 else None
        }
    
    def get_strategy_description(self) -> str:
        """
        Get detailed strategy description
        
        Returns:
            String with strategy explanation
        """
        return f"""
        ╔═══════════════════════════════════════════════════════════════╗
        ║        REVERSAL-TRAILING-STOP STRATEGY DESCRIPTION           ║
        ╚═══════════════════════════════════════════════════════════════╝
        
        STRATEGY TYPE: Reversal + Trend Following with Dynamic Risk Management
        
        ENTRY LOGIC:
        ───────────
        1. Detect oversold/overbought conditions using RSI
           - Bullish: RSI < {self.rsi_oversold}
           - Bearish: RSI > {self.rsi_overbought}
        
        2. Confirm with momentum (Rate of Change)
           - Strong momentum: |ROC| > {self.roc_threshold}%
        
        3. Validate with volume increase
           - Volume > {self.volume_mult}x average
        
        4. IMMEDIATE ENTRY when all conditions met
        
        EXIT LOGIC:
        ──────────
        1. Trailing Stop-Loss (Primary Exit)
           - Initial stop: Entry ± {self.initial_stop_mult} × ATR
           - Trails by: {self.trailing_stop_mult} × ATR
           - Never moves against position
        
        2. Reversal Exit (Secondary Exit)
           - Opposite reversal signal detected
           - Protects profits by exiting early
        
        RISK MANAGEMENT:
        ───────────────
        - ATR-based position sizing
        - Dynamic stop-loss adjustment
        - Volatility-adjusted entries and exits
        
        PARAMETERS:
        ──────────
        RSI Period: {self.rsi_period}
        RSI Oversold: {self.rsi_oversold}
        RSI Overbought: {self.rsi_overbought}
        ROC Period: {self.roc_period}
        ROC Threshold: {self.roc_threshold}%
        Volume Multiplier: {self.volume_mult}x
        ATR Period: {self.atr_period}
        Trailing Stop: {self.trailing_stop_mult} × ATR
        Initial Stop: {self.initial_stop_mult} × ATR
        
        BEST FOR:
        ────────
        - Volatile markets with clear reversals
        - Trending markets after consolidation
        - Cryptocurrency and forex trading
        - 15-minute to 4-hour timeframes
        """


# ==================== BACKTESTING WRAPPER ====================

class ReversalTrailingStopBacktest:
    """
    Wrapper class for backtesting the Reversal-Trailing-Stop strategy
    """
    
    def __init__(self, initial_capital: float = 10000.0, 
                 trade_size: float = 100.0,
                 params: Optional[Dict[str, Any]] = None):
        """
        Initialize backtest wrapper
        
        Args:
            initial_capital: Starting capital
            trade_size: Size of each trade
            params: Strategy parameters
        """
        self.strategy = ReversalTrailingStopStrategy(params)
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trade_size = trade_size
        self.position = 0
        self.entry_price = 0.0
        self.trades = []
    
    def run_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run backtest on historical data
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            Dictionary with backtest results
        """
        logger.info("=" * 70)
        logger.info("🚀 STARTING REVERSAL-TRAILING-STOP BACKTEST")
        logger.info("=" * 70)
        
        for i in range(self.strategy.min_bars, len(df)):
            df_slice = df.iloc[:i+1].copy()
            signal = self.strategy.generate_signal(df_slice)
            current_price = df_slice['close'].iloc[-1]
            timestamp = df_slice['timestamp'].iloc[-1] if 'timestamp' in df_slice.columns else i
            
            # Process signal
            if signal == 1 and self.position == 0:  # BUY
                self.position = 1
                self.entry_price = current_price
                self.trades.append({
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'price': current_price,
                    'quantity': self.trade_size,
                    'capital_before': self.capital,
                    'pnl': 0.0
                })
                logger.info(f"📊 [{timestamp}] BUY @ ${current_price:.2f}")
            
            elif signal == -1 and self.position == 1:  # SELL
                pnl = (current_price - self.entry_price) * self.trade_size
                self.capital += pnl
                self.position = 0
                
                self.trades.append({
                    'timestamp': timestamp,
                    'type': 'SELL',
                    'price': current_price,
                    'quantity': self.trade_size,
                    'capital_before': self.capital - pnl,
                    'pnl': pnl
                })
                logger.info(f"💰 [{timestamp}] SELL @ ${current_price:.2f} | P&L: ${pnl:.2f}")
        
        # Calculate metrics
        results = self.calculate_metrics()
        self.print_report(results)
        
        return results
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.trades:
            return {}
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_pnl': total_pnl,
            'roi': (total_pnl / self.initial_capital) * 100,
            'total_trades': len([t for t in self.trades if t['type'] == 'SELL']),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len([t for t in self.trades if t['type'] == 'SELL']) * 100) if losing_trades or winning_trades else 0,
            'avg_win': np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0,
            'avg_loss': np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0,
            'best_trade': max([t['pnl'] for t in self.trades]),
            'worst_trade': min([t['pnl'] for t in self.trades]),
        }
    
    def print_report(self, results: Dict[str, Any]):
        """Print backtest report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 BACKTEST REPORT - REVERSAL-TRAILING-STOP STRATEGY")
        logger.info("=" * 70)
        logger.info(f"Initial Capital:  ${results['initial_capital']:,.2f}")
        logger.info(f"Final Capital:    ${results['final_capital']:,.2f}")
        logger.info(f"Total P&L:        ${results['total_pnl']:,.2f}")
        logger.info(f"ROI:              {results['roi']:.2f}%")
        logger.info("-" * 70)
        logger.info(f"Total Trades:     {results['total_trades']}")
        logger.info(f"Winning Trades:   {results['winning_trades']}")
        logger.info(f"Losing Trades:    {results['losing_trades']}")
        logger.info(f"Win Rate:         {results['win_rate']:.2f}%")
        logger.info(f"Average Win:      ${results['avg_win']:.2f}")
        logger.info(f"Average Loss:     ${results['avg_loss']:.2f}")
        logger.info(f"Best Trade:       ${results['best_trade']:.2f}")
        logger.info(f"Worst Trade:      ${results['worst_trade']:.2f}")
        logger.info("=" * 70 + "\n")


# ==================== DEMO USAGE ====================

if __name__ == "__main__":
    """
    Demo usage of Reversal-Trailing-Stop Strategy
    """
    import logging
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Print strategy description
    strategy = ReversalTrailingStopStrategy()
    print(strategy.get_strategy_description())
    
    # Generate sample data for demonstration
    print("\n📊 Generating sample data for backtest demonstration...")
    
    try:
        from utils import generate_sample_data
        df = generate_sample_data(n_bars=500, start_price=30000, volatility=0.02)
        
        # Run backtest
        backtest = ReversalTrailingStopBacktest(
            initial_capital=10000.0,
            trade_size=100.0
        )
        results = backtest.run_backtest(df)
        
    except ImportError:
        print("⚠️  utils module not found. To run backtest, use:")
        print("    python backtester.py")
        print("\nStrategy is ready to be integrated with the existing backtesting system.")
