"""
lsob_strategy.py - Long-Short On Breakout Strategy
==================================================

LSOB (Long-Short On Breakout) Strategy Implementation

Strategy Logic:
1. Identifies price breakouts using multiple indicators
2. Takes long positions on upward breakouts
3. Takes short positions on downward breakouts
4. Includes comprehensive risk management
5. Uses volume confirmation and volatility filters

Key Features:
- Bollinger Bands for breakout detection
- ATR (Average True Range) for volatility measurement
- Volume confirmation
- Dynamic position sizing based on risk
- Stop-loss and take-profit levels
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
import logging

from strategy import BaseStrategy

logger = logging.getLogger(__name__)


class LSOBStrategy(BaseStrategy):
    """
    Long-Short On Breakout Strategy
    
    Takes long positions when price breaks above resistance
    and short positions when price breaks below support.
    Uses multiple confirmation signals and risk management.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize LSOB Strategy
        
        Args:
            params: Dictionary with strategy parameters
                - bb_window: Bollinger Bands window (default: 20)
                - bb_std: Bollinger Bands standard deviations (default: 2.0)
                - atr_window: ATR window for volatility (default: 14)
                - volume_threshold: Volume confirmation threshold (default: 1.2x average)
                - breakout_threshold: Minimum breakout percentage (default: 0.5%)
                - stop_loss_atr_mult: Stop loss as multiple of ATR (default: 2.0)
                - take_profit_atr_mult: Take profit as multiple of ATR (default: 3.0)
                - max_volatility: Maximum allowed volatility (default: 5%)
        """
        super().__init__("LSOB", params)
        
        # Bollinger Bands parameters
        self.bb_window = params.get('bb_window', 20)
        self.bb_std = params.get('bb_std', 2.0)
        
        # ATR parameters
        self.atr_window = params.get('atr_window', 14)
        
        # Volume confirmation
        self.volume_threshold = params.get('volume_threshold', 1.2)
        
        # Breakout parameters
        self.breakout_threshold = params.get('breakout_threshold', 0.005)  # 0.5%
        
        # Risk management
        self.stop_loss_atr_mult = params.get('stop_loss_atr_mult', 2.0)
        self.take_profit_atr_mult = params.get('take_profit_atr_mult', 3.0)
        self.max_volatility = params.get('max_volatility', 0.05)  # 5%
        
        logger.info(f"✓ LSOB Strategy initialized with BB({self.bb_window}, {self.bb_std}), ATR({self.atr_window})")
    
    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            df: DataFrame with OHLC data
        
        Returns:
            Series with ATR values
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR as moving average of TR
        atr = tr.rolling(window=self.atr_window).mean()
        
        return atr
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> tuple:
        """
        Calculate Bollinger Bands
        
        Args:
            df: DataFrame with close prices
        
        Returns:
            Tuple of (middle_band, upper_band, lower_band)
        """
        close = df['close']
        
        # Middle band (SMA)
        middle_band = close.rolling(window=self.bb_window).mean()
        
        # Standard deviation
        std = close.rolling(window=self.bb_window).std()
        
        # Upper and lower bands
        upper_band = middle_band + (self.bb_std * std)
        lower_band = middle_band - (self.bb_std * std)
        
        return middle_band, upper_band, lower_band
    
    def check_volume_confirmation(self, df: pd.DataFrame) -> bool:
        """
        Check if volume confirms the breakout
        
        Args:
            df: DataFrame with volume data
        
        Returns:
            True if volume is above threshold
        """
        if len(df) < self.bb_window:
            return False
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-self.bb_window:].mean()
        
        if avg_volume == 0:
            return False
        
        volume_ratio = current_volume / avg_volume
        
        return volume_ratio >= self.volume_threshold
    
    def check_volatility_filter(self, atr: pd.Series, df: pd.DataFrame) -> bool:
        """
        Check if volatility is within acceptable range
        
        Args:
            atr: ATR Series
            df: DataFrame with close prices
        
        Returns:
            True if volatility is acceptable
        """
        if pd.isna(atr.iloc[-1]):
            return False
        
        current_price = df['close'].iloc[-1]
        current_atr = atr.iloc[-1]
        
        # Calculate volatility as ATR / price
        volatility = current_atr / current_price
        
        return volatility <= self.max_volatility
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate trading signal based on LSOB strategy
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            Signal: 1 = BUY (Long), 0 = HOLD, -1 = SELL (Short)
        """
        if not self.enabled or not self.validate_data(df):
            return 0
        
        # Need enough data for calculations
        min_length = max(self.bb_window, self.atr_window) + 2
        if len(df) < min_length:
            logger.debug(f"LSOB: Not enough data ({len(df)} < {min_length})")
            return 0
        
        try:
            df_copy = df.copy()
            
            # Calculate indicators
            middle_band, upper_band, lower_band = self.calculate_bollinger_bands(df_copy)
            atr = self.calculate_atr(df_copy)
            
            # Get current and previous values
            close_curr = df_copy['close'].iloc[-1]
            close_prev = df_copy['close'].iloc[-2]
            
            upper_curr = upper_band.iloc[-1]
            upper_prev = upper_band.iloc[-2]
            lower_curr = lower_band.iloc[-1]
            lower_prev = lower_band.iloc[-2]
            
            # Check for NaN values
            if pd.isna(upper_curr) or pd.isna(lower_curr) or pd.isna(atr.iloc[-1]):
                logger.debug("LSOB: Indicator values are NaN")
                return 0
            
            # Apply volatility filter
            if not self.check_volatility_filter(atr, df_copy):
                logger.debug("LSOB: Volatility too high")
                return 0
            
            # Calculate breakout percentage
            upper_breakout_pct = (close_curr - upper_curr) / upper_curr if upper_curr > 0 else 0
            lower_breakout_pct = (lower_curr - close_curr) / lower_curr if lower_curr > 0 else 0
            
            # Check for upward breakout (LONG signal)
            if close_curr > upper_curr and close_prev <= upper_prev:
                # Breakout above upper band
                if upper_breakout_pct >= self.breakout_threshold:
                    # Volume confirmation
                    if self.check_volume_confirmation(df_copy):
                        logger.info(f"LSOB: LONG signal - Upward breakout detected")
                        logger.debug(f"  Price: {close_curr:.2f}, Upper Band: {upper_curr:.2f}")
                        logger.debug(f"  Breakout: {upper_breakout_pct*100:.2f}%")
                        return 1  # BUY (Long)
            
            # Check for downward breakout (SHORT signal)
            if close_curr < lower_curr and close_prev >= lower_prev:
                # Breakout below lower band
                if lower_breakout_pct >= self.breakout_threshold:
                    # Volume confirmation
                    if self.check_volume_confirmation(df_copy):
                        logger.info(f"LSOB: SHORT signal - Downward breakout detected")
                        logger.debug(f"  Price: {close_curr:.2f}, Lower Band: {lower_curr:.2f}")
                        logger.debug(f"  Breakout: {lower_breakout_pct*100:.2f}%")
                        return -1  # SELL (Short)
            
            return 0  # HOLD
            
        except Exception as e:
            logger.error(f"LSOB: Error generating signal: {e}")
            return 0
    
    def calculate_position_size(self, capital: float, current_price: float,
                               atr: float, use_kelly: bool = False,
                               trade_history: list = None) -> float:
        """
        Calculate position size based on risk management
        
        Args:
            capital: Available capital
            current_price: Current asset price
            atr: Current ATR value
            use_kelly: Use Kelly Criterion for position sizing (default: False)
            trade_history: List of past trades for Kelly calculation (optional)
        
        Returns:
            Position size (number of shares/contracts)
        """
        # Default: Risk 1% of capital per trade (ATR-based method)
        if not use_kelly or trade_history is None or len(trade_history) < 10:
            # Standard ATR-based position sizing
            risk_amount = capital * 0.01
            
            # Stop loss distance
            stop_loss_distance = atr * self.stop_loss_atr_mult
            
            if stop_loss_distance == 0:
                return 0
            
            # Position size = Risk Amount / Stop Loss Distance
            position_size = risk_amount / stop_loss_distance
            
            # Ensure we can afford the position
            max_shares = capital / current_price
            position_size = min(position_size, max_shares * 0.5)  # Max 50% of capital
            
            return max(1, int(position_size))
        
        # Kelly Criterion position sizing
        try:
            from utils import calculate_kelly_position_size
            from config import config
            
            # Calculate statistics from trade history
            pnls = [float(t.get('pnl', 0)) for t in trade_history[-config.kelly_lookback_trades:] 
                   if t.get('pnl', '0') != '0.00']
            
            if not pnls or len(pnls) < 5:
                # Fall back to standard method if not enough data
                logger.debug("Insufficient trade history for Kelly, using standard sizing")
                return self.calculate_position_size(capital, current_price, atr, 
                                                   use_kelly=False, trade_history=None)
            
            # Calculate win rate and average win/loss
            wins = [p for p in pnls if p > 0]
            losses = [abs(p) for p in pnls if p < 0]
            
            win_rate = len(wins) / len(pnls) if pnls else 0
            avg_win = sum(wins) / len(wins) if wins else 1
            avg_loss = sum(losses) / len(losses) if losses else 1
            
            # Calculate Kelly position size
            kelly_position_value = calculate_kelly_position_size(
                capital=capital,
                win_rate=win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                kelly_fraction=config.kelly_fraction,
                max_position_pct=config.kelly_max_position_pct
            )
            
            # Convert to number of shares
            kelly_shares = kelly_position_value / current_price if current_price > 0 else 0
            
            logger.info(
                f"Kelly sizing: win_rate={win_rate:.2%}, "
                f"avg_win=${avg_win:.2f}, avg_loss=${avg_loss:.2f}, "
                f"position=${kelly_position_value:.2f} ({kelly_shares:.2f} shares)"
            )
            
            return max(1, int(kelly_shares))
            
        except Exception as e:
            logger.warning(f"Kelly calculation failed: {e}, using standard sizing")
            return self.calculate_position_size(capital, current_price, atr, 
                                               use_kelly=False, trade_history=None)
    
    def calculate_stop_loss(self, entry_price: float, atr: float, side: str) -> float:
        """
        Calculate stop loss level
        
        Args:
            entry_price: Entry price
            atr: Current ATR value
            side: 'long' or 'short'
        
        Returns:
            Stop loss price
        """
        stop_distance = atr * self.stop_loss_atr_mult
        
        if side.lower() == 'long':
            return entry_price - stop_distance
        else:  # short
            return entry_price + stop_distance
    
    def calculate_take_profit(self, entry_price: float, atr: float, side: str) -> float:
        """
        Calculate take profit level
        
        Args:
            entry_price: Entry price
            atr: Current ATR value
            side: 'long' or 'short'
        
        Returns:
            Take profit price
        """
        profit_distance = atr * self.take_profit_atr_mult
        
        if side.lower() == 'long':
            return entry_price + profit_distance
        else:  # short
            return entry_price - profit_distance
    
    def get_risk_levels(self, df: pd.DataFrame, entry_price: float,
                       side: str) -> Dict[str, float]:
        """
        Get stop loss and take profit levels for a trade
        
        Args:
            df: DataFrame with OHLCV data
            entry_price: Entry price
            side: 'long' or 'short'
        
        Returns:
            Dictionary with stop_loss and take_profit levels
        """
        if len(df) < self.atr_window:
            return {'stop_loss': 0, 'take_profit': 0}
        
        atr = self.calculate_atr(df)
        current_atr = atr.iloc[-1]
        
        if pd.isna(current_atr) or current_atr == 0:
            return {'stop_loss': 0, 'take_profit': 0}
        
        stop_loss = self.calculate_stop_loss(entry_price, current_atr, side)
        take_profit = self.calculate_take_profit(entry_price, current_atr, side)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'atr': current_atr
        }


# ========== EXAMPLE USAGE ==========

def example_lsob_strategy():
    """Example of LSOB strategy usage"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  LSOB Strategy - Example")
    print("=" * 70)
    
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # Generate price data with trend and volatility
    base_price = 100
    trend = np.linspace(0, 20, 100)
    noise = np.random.randn(100) * 2
    close_prices = base_price + trend + noise
    
    # Create OHLCV data
    df = pd.DataFrame({
        'open': close_prices - np.random.rand(100) * 0.5,
        'high': close_prices + np.random.rand(100) * 2,
        'low': close_prices - np.random.rand(100) * 2,
        'close': close_prices,
        'volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)
    
    # Initialize strategy
    params = {
        'bb_window': 20,
        'bb_std': 2.0,
        'atr_window': 14,
        'volume_threshold': 1.2,
        'breakout_threshold': 0.005,
        'stop_loss_atr_mult': 2.0,
        'take_profit_atr_mult': 3.0
    }
    
    strategy = LSOBStrategy(params)
    
    # Test strategy on data
    print("\nTesting LSOB Strategy...")
    signals = []
    
    for i in range(30, len(df)):
        df_subset = df.iloc[:i+1]
        signal = strategy.generate_signal(df_subset)
        
        if signal != 0:
            price = df_subset['close'].iloc[-1]
            signal_type = "LONG" if signal == 1 else "SHORT"
            print(f"{df_subset.index[-1].date()}: {signal_type} signal at ${price:.2f}")
            
            # Get risk levels
            risk_levels = strategy.get_risk_levels(df_subset, price, 
                                                   'long' if signal == 1 else 'short')
            if risk_levels['stop_loss'] > 0:
                print(f"  Stop Loss: ${risk_levels['stop_loss']:.2f}")
                print(f"  Take Profit: ${risk_levels['take_profit']:.2f}")
                print(f"  ATR: ${risk_levels['atr']:.2f}")
            
            signals.append(signal)
    
    if signals:
        print(f"\n✓ Generated {len(signals)} signals")
        print(f"  Long signals: {signals.count(1)}")
        print(f"  Short signals: {signals.count(-1)}")
    else:
        print("\n⚠️ No signals generated")
    
    print("\n✓ Example completed!")


if __name__ == "__main__":
    example_lsob_strategy()
