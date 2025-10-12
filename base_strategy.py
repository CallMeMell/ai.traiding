"""
base_strategy.py - Enhanced Base Strategy Framework
===================================================
Enhanced base strategy framework with data feed support, exchange connection,
and comprehensive logging for implementing video-based trading strategies.

This module provides a foundation for building complex trading strategies
with built-in support for:
- Multi-timeframe data feeds
- Exchange connection utilities
- Advanced logging and monitoring
- State management
- Performance tracking
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


# ========== DATA STRUCTURES ==========

@dataclass
class StrategyState:
    """Tracks the internal state of a strategy"""
    last_signal: int = 0
    last_signal_time: Optional[datetime] = None
    position_open: bool = False
    position_entry_price: float = 0.0
    position_entry_time: Optional[datetime] = None
    trades_count: int = 0
    wins_count: int = 0
    losses_count: int = 0
    total_profit: float = 0.0
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataFeed:
    """Represents a data feed with OHLCV data"""
    symbol: str
    timeframe: str
    data: pd.DataFrame
    last_update: Optional[datetime] = None
    
    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """Check if data feed is stale"""
        if self.last_update is None:
            return True
        age = (datetime.now() - self.last_update).total_seconds()
        return age > max_age_seconds
    
    def validate(self) -> bool:
        """Validate data feed integrity"""
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_cols):
            return False
        if len(self.data) < 2:
            return False
        return True


# ========== ENHANCED BASE STRATEGY ==========

class EnhancedBaseStrategy(ABC):
    """
    Enhanced base strategy class with advanced features
    
    This class extends the basic strategy pattern with:
    - State management
    - Multi-timeframe support
    - Exchange connection utilities
    - Performance tracking
    - Advanced logging
    """
    
    def __init__(
        self,
        name: str,
        params: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize enhanced base strategy
        
        Args:
            name: Strategy name
            params: Strategy parameters
            config: Optional configuration dict
        """
        self.name = name
        self.params = params
        self.config = config or {}
        self.enabled = True
        
        # State management
        self.state = StrategyState()
        
        # Data feeds for multi-timeframe analysis
        self.data_feeds: Dict[str, DataFeed] = {}
        
        # Performance tracking
        self.performance_metrics = {
            'signals_generated': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'last_execution_time': None,
            'avg_execution_time_ms': 0.0,
            'errors_count': 0
        }
        
        # Exchange connection info (for future use)
        self.exchange_info = {
            'connected': False,
            'exchange_name': None,
            'last_connection_check': None
        }
        
        logger.info(f"✓ Enhanced Strategy initialized: {name}")
        self._on_init()
    
    def _on_init(self):
        """Hook for custom initialization in derived classes"""
        pass
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate trading signal based on data
        
        Args:
            df: DataFrame with OHLCV data (primary timeframe)
        
        Returns:
            Signal: 1 = BUY, 0 = HOLD, -1 = SELL
        """
        pass
    
    def generate_signal_with_context(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Generate signal with additional context information
        
        Args:
            df: DataFrame with OHLCV data
            context: Optional context dictionary
        
        Returns:
            Tuple of (signal, context_info)
        """
        start_time = datetime.now()
        
        try:
            # Generate base signal
            signal = self.generate_signal(df)
            
            # Update state
            self.state.last_signal = signal
            self.state.last_signal_time = datetime.now()
            
            # Track performance
            self._update_performance_metrics(signal, start_time)
            
            # Build context info
            context_info = {
                'signal': signal,
                'signal_text': self._signal_to_text(signal),
                'timestamp': datetime.now().isoformat(),
                'current_price': df['close'].iloc[-1] if len(df) > 0 else 0,
                'strategy_state': self._get_state_dict(),
                'confidence': self._calculate_confidence(df, signal)
            }
            
            return signal, context_info
            
        except Exception as e:
            self.performance_metrics['errors_count'] += 1
            logger.error(f"Error generating signal in {self.name}: {e}")
            return 0, {'signal': 0, 'error': str(e)}
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate input data"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Missing column in {self.name}: {col}")
                return False
        
        if len(df) < 2:
            logger.warning(f"Insufficient data for {self.name}: {len(df)} rows")
            return False
        
        # Validate OHLC logic
        if not all(df['high'] >= df['low']):
            logger.error(f"Invalid OHLC data: high < low in {self.name}")
            return False
        
        return True
    
    def add_data_feed(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame
    ) -> bool:
        """
        Add a data feed for multi-timeframe analysis
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (e.g., '1h', '4h', '1d')
            data: OHLCV DataFrame
        
        Returns:
            True if added successfully
        """
        feed = DataFeed(
            symbol=symbol,
            timeframe=timeframe,
            data=data,
            last_update=datetime.now()
        )
        
        if not feed.validate():
            logger.error(f"Invalid data feed for {symbol} {timeframe}")
            return False
        
        key = f"{symbol}_{timeframe}"
        self.data_feeds[key] = feed
        logger.debug(f"Data feed added: {key} ({len(data)} rows)")
        return True
    
    def get_data_feed(
        self,
        symbol: str,
        timeframe: str
    ) -> Optional[pd.DataFrame]:
        """
        Get data feed by symbol and timeframe
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
        
        Returns:
            DataFrame or None if not found
        """
        key = f"{symbol}_{timeframe}"
        feed = self.data_feeds.get(key)
        
        if feed is None:
            return None
        
        if feed.is_stale():
            logger.warning(f"Data feed is stale: {key}")
        
        return feed.data
    
    def update_state(self, **kwargs):
        """
        Update strategy state
        
        Args:
            **kwargs: State fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
                logger.debug(f"State updated: {key} = {value}")
            else:
                self.state.custom_data[key] = value
    
    def on_position_opened(
        self,
        entry_price: float,
        quantity: float,
        side: str
    ):
        """
        Callback when position is opened
        
        Args:
            entry_price: Entry price
            quantity: Position size
            side: 'long' or 'short'
        """
        self.state.position_open = True
        self.state.position_entry_price = entry_price
        self.state.position_entry_time = datetime.now()
        self.state.trades_count += 1
        
        logger.info(
            f"{self.name} - Position opened: {side} @ {entry_price} "
            f"(quantity: {quantity})"
        )
    
    def on_position_closed(
        self,
        exit_price: float,
        profit: float,
        side: str
    ):
        """
        Callback when position is closed
        
        Args:
            exit_price: Exit price
            profit: Realized profit/loss
            side: 'long' or 'short'
        """
        self.state.position_open = False
        self.state.total_profit += profit
        
        if profit > 0:
            self.state.wins_count += 1
        else:
            self.state.losses_count += 1
        
        logger.info(
            f"{self.name} - Position closed: {side} @ {exit_price} "
            f"(P&L: {profit:.2f})"
        )
    
    def _update_performance_metrics(self, signal: int, start_time: datetime):
        """Update internal performance metrics"""
        self.performance_metrics['signals_generated'] += 1
        
        if signal == 1:
            self.performance_metrics['buy_signals'] += 1
        elif signal == -1:
            self.performance_metrics['sell_signals'] += 1
        else:
            self.performance_metrics['hold_signals'] += 1
        
        # Calculate execution time
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Update moving average of execution time
        n = self.performance_metrics['signals_generated']
        current_avg = self.performance_metrics['avg_execution_time_ms']
        self.performance_metrics['avg_execution_time_ms'] = (
            (current_avg * (n - 1) + execution_time_ms) / n
        )
        
        self.performance_metrics['last_execution_time'] = datetime.now().isoformat()
    
    def _calculate_confidence(self, df: pd.DataFrame, signal: int) -> float:
        """
        Calculate confidence score for the signal (0-1)
        Override in derived classes for custom confidence calculation
        """
        return 0.5  # Default neutral confidence
    
    def _signal_to_text(self, signal: int) -> str:
        """Convert signal to text"""
        if signal == 1:
            return "BUY"
        elif signal == -1:
            return "SELL"
        else:
            return "HOLD"
    
    def _get_state_dict(self) -> Dict[str, Any]:
        """Get state as dictionary"""
        return {
            'last_signal': self.state.last_signal,
            'last_signal_time': (
                self.state.last_signal_time.isoformat()
                if self.state.last_signal_time else None
            ),
            'position_open': self.state.position_open,
            'trades_count': self.state.trades_count,
            'wins_count': self.state.wins_count,
            'losses_count': self.state.losses_count,
            'win_rate': (
                self.state.wins_count / self.state.trades_count
                if self.state.trades_count > 0 else 0
            ),
            'total_profit': self.state.total_profit
        }
    
    def update_params(self, new_params: Dict[str, Any]):
        """Update strategy parameters"""
        self.params.update(new_params)
        logger.info(f"Parameters updated for {self.name}")
        self._on_params_updated()
    
    def _on_params_updated(self):
        """Hook for custom parameter update handling"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'params': self.params,
            'state': self._get_state_dict(),
            'performance': self.performance_metrics.copy(),
            'data_feeds': list(self.data_feeds.keys())
        }
    
    def reset_state(self):
        """Reset strategy state"""
        self.state = StrategyState()
        logger.info(f"State reset for {self.name}")
    
    def export_state(self, filepath: str):
        """Export state to JSON file"""
        state_data = {
            'name': self.name,
            'timestamp': datetime.now().isoformat(),
            'state': self._get_state_dict(),
            'performance': self.performance_metrics,
            'params': self.params
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        logger.info(f"State exported to {filepath}")
    
    def import_state(self, filepath: str):
        """Import state from JSON file"""
        with open(filepath, 'r') as f:
            state_data = json.load(f)
        
        # Restore state (basic restoration - extend as needed)
        state_dict = state_data.get('state', {})
        self.state.trades_count = state_dict.get('trades_count', 0)
        self.state.wins_count = state_dict.get('wins_count', 0)
        self.state.losses_count = state_dict.get('losses_count', 0)
        self.state.total_profit = state_dict.get('total_profit', 0.0)
        
        logger.info(f"State imported from {filepath}")


# ========== EXAMPLE IMPLEMENTATION ==========

class VideoBasedStrategy(EnhancedBaseStrategy):
    """
    Example implementation of a video-based strategy
    
    This serves as a template for implementing strategies from YouTube videos
    or other educational sources.
    """
    
    def __init__(self, params: Dict[str, Any]):
        super().__init__("VideoBasedStrategy", params)
        
        # Example: Strategy parameters from video
        self.ma_short = params.get('ma_short', 10)
        self.ma_long = params.get('ma_long', 50)
        self.rsi_period = params.get('rsi_period', 14)
        self.rsi_oversold = params.get('rsi_oversold', 30)
        self.rsi_overbought = params.get('rsi_overbought', 70)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate signal based on video strategy logic
        
        This is a placeholder implementation. Replace with actual
        strategy logic from the video.
        """
        if not self.enabled or not self.validate_data(df):
            return 0
        
        if len(df) < max(self.ma_long, self.rsi_period) + 1:
            return 0
        
        df_copy = df.copy()
        
        # Calculate indicators
        df_copy['ma_short'] = df_copy['close'].rolling(self.ma_short).mean()
        df_copy['ma_long'] = df_copy['close'].rolling(self.ma_long).mean()
        
        # RSI calculation
        delta = df_copy['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(self.rsi_period).mean()
        avg_loss = loss.rolling(self.rsi_period).mean()
        rs = avg_gain / avg_loss
        df_copy['rsi'] = 100 - (100 / (1 + rs))
        
        # Get current values
        ma_short_curr = df_copy['ma_short'].iloc[-1]
        ma_long_curr = df_copy['ma_long'].iloc[-1]
        rsi_curr = df_copy['rsi'].iloc[-1]
        
        if pd.isna(ma_short_curr) or pd.isna(ma_long_curr) or pd.isna(rsi_curr):
            return 0
        
        # Example strategy logic: MA crossover + RSI confirmation
        if ma_short_curr > ma_long_curr and rsi_curr < self.rsi_overbought:
            return 1  # BUY signal
        elif ma_short_curr < ma_long_curr and rsi_curr > self.rsi_oversold:
            return -1  # SELL signal
        
        return 0  # HOLD
    
    def _calculate_confidence(self, df: pd.DataFrame, signal: int) -> float:
        """Calculate confidence based on signal strength"""
        if signal == 0:
            return 0.0
        
        # Simple confidence calculation based on RSI distance from threshold
        df_copy = df.copy()
        delta = df_copy['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(self.rsi_period).mean()
        avg_loss = loss.rolling(self.rsi_period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_curr = rsi.iloc[-1]
        
        if pd.isna(rsi_curr):
            return 0.5
        
        if signal == 1:  # BUY
            # Higher confidence when RSI is more oversold
            confidence = max(0, (self.rsi_oversold - rsi_curr) / self.rsi_oversold)
            return min(1.0, confidence + 0.5)
        else:  # SELL
            # Higher confidence when RSI is more overbought
            confidence = max(0, (rsi_curr - self.rsi_overbought) / (100 - self.rsi_overbought))
            return min(1.0, confidence + 0.5)


# ========== UTILITY FUNCTIONS ==========

def create_strategy_from_video(
    video_id: str,
    strategy_name: str,
    params: Dict[str, Any]
) -> EnhancedBaseStrategy:
    """
    Factory function to create strategy based on video reference
    
    Args:
        video_id: YouTube video ID or reference
        strategy_name: Name for the strategy
        params: Strategy parameters
    
    Returns:
        Strategy instance
    """
    logger.info(f"Creating strategy from video: {video_id}")
    
    # This is a template - implement specific video strategies here
    # For now, returns the example VideoBasedStrategy
    return VideoBasedStrategy(params)


def log_strategy_performance(strategy: EnhancedBaseStrategy, detailed: bool = False):
    """
    Log strategy performance metrics
    
    Args:
        strategy: Strategy instance
        detailed: If True, log detailed metrics
    """
    info = strategy.get_info()
    logger.info(f"=== Performance: {strategy.name} ===")
    logger.info(f"Total Signals: {info['performance']['signals_generated']}")
    logger.info(f"Buy/Sell/Hold: {info['performance']['buy_signals']}/"
                f"{info['performance']['sell_signals']}/"
                f"{info['performance']['hold_signals']}")
    
    if detailed:
        logger.info(f"Trades: {info['state']['trades_count']}")
        logger.info(f"Win Rate: {info['state']['win_rate']:.2%}")
        logger.info(f"Total P&L: {info['state']['total_profit']:.2f}")
        logger.info(f"Avg Execution Time: {info['performance']['avg_execution_time_ms']:.2f}ms")
