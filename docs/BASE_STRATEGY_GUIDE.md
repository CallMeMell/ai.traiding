# 📚 Enhanced Base Strategy Framework Guide

**Comprehensive guide for implementing video-based and custom trading strategies**

This guide explains how to use the enhanced base strategy framework to implement trading strategies from YouTube videos, tutorials, or custom designs.

---

## 🎯 Overview

The Enhanced Base Strategy Framework (`base_strategy.py`) provides a powerful foundation for building sophisticated trading strategies with:

- ✅ **Multi-timeframe data feed support**
- ✅ **State management and persistence**
- ✅ **Performance tracking**
- ✅ **Exchange connection utilities**
- ✅ **Advanced logging and monitoring**
- ✅ **Position lifecycle callbacks**

---

## 🚀 Quick Start

### Using the Video-Based Strategy Template

The framework includes a ready-to-use template for implementing strategies from videos:

```python
from base_strategy import VideoBasedStrategy

# Define strategy parameters
params = {
    'ma_short': 10,
    'ma_long': 50,
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70
}

# Create strategy instance
strategy = VideoBasedStrategy(params)

# Generate signal
signal = strategy.generate_signal(df)
print(f"Signal: {signal}")  # 1=BUY, 0=HOLD, -1=SELL
```

### Creating Your Own Strategy

Extend `EnhancedBaseStrategy` to create custom strategies:

```python
from base_strategy import EnhancedBaseStrategy
import pandas as pd

class MyVideoStrategy(EnhancedBaseStrategy):
    def __init__(self, params):
        super().__init__("MyVideoStrategy", params)
        # Initialize your parameters
        self.param1 = params.get('param1', 10)
        self.param2 = params.get('param2', 20)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """Implement your strategy logic here"""
        if not self.validate_data(df):
            return 0
        
        # Your trading logic
        # ... calculate indicators
        # ... generate signal
        
        if buy_condition:
            return 1  # BUY
        elif sell_condition:
            return -1  # SELL
        else:
            return 0  # HOLD
```

---

## 📊 Key Features

### 1. Multi-Timeframe Analysis

Add multiple data feeds for comprehensive analysis:

```python
strategy = VideoBasedStrategy(params)

# Add 1-hour data
strategy.add_data_feed('BTC/USDT', '1h', df_1h)

# Add 4-hour data
strategy.add_data_feed('BTC/USDT', '4h', df_4h)

# Add daily data
strategy.add_data_feed('BTC/USDT', '1d', df_1d)

# Access in your strategy
df_4h = strategy.get_data_feed('BTC/USDT', '4h')
if df_4h is not None:
    # Analyze higher timeframe
    daily_trend = calculate_trend(df_4h)
```

### 2. State Management

Track strategy state across executions:

```python
# Update custom state
strategy.update_state(
    custom_indicator_value=42.5,
    last_alert_time=datetime.now()
)

# Access state
if strategy.state.position_open:
    print(f"Entry price: {strategy.state.position_entry_price}")
    print(f"Trades count: {strategy.state.trades_count}")
    print(f"Win rate: {strategy.state.wins_count / strategy.state.trades_count}")
```

### 3. Position Lifecycle Callbacks

Track position events:

```python
# Called when position opens
strategy.on_position_opened(
    entry_price=50000.0,
    quantity=0.01,
    side='long'
)

# Called when position closes
strategy.on_position_closed(
    exit_price=51000.0,
    profit=10.0,
    side='long'
)
```

### 4. Enhanced Signal Generation

Get signals with context information:

```python
signal, context = strategy.generate_signal_with_context(df)

print(f"Signal: {context['signal_text']}")
print(f"Confidence: {context['confidence']:.2f}")
print(f"Current Price: {context['current_price']}")
print(f"Win Rate: {context['strategy_state']['win_rate']:.2%}")
```

### 5. Performance Tracking

Monitor strategy performance:

```python
from base_strategy import log_strategy_performance

# Log basic performance
log_strategy_performance(strategy)

# Log detailed performance
log_strategy_performance(strategy, detailed=True)

# Get performance metrics
info = strategy.get_info()
print(f"Total signals: {info['performance']['signals_generated']}")
print(f"Buy signals: {info['performance']['buy_signals']}")
print(f"Avg execution time: {info['performance']['avg_execution_time_ms']:.2f}ms")
```

### 6. State Persistence

Save and restore strategy state:

```python
# Export state to file
strategy.export_state('data/strategy_state.json')

# Import state from file
strategy.import_state('data/strategy_state.json')

# Reset state
strategy.reset_state()
```

---

## 🎬 Implementing Strategies from YouTube Videos

### Step-by-Step Process

#### 1. Analyze the Video

Watch the video (e.g., https://youtu.be/FDmV1bIub_s) and document:

- Trading indicators used (MA, RSI, MACD, etc.)
- Entry conditions
- Exit conditions
- Risk management rules
- Timeframes

#### 2. Define Parameters

Create a parameter dictionary:

```python
video_params = {
    # Indicators
    'ema_fast': 12,
    'ema_slow': 26,
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    
    # Entry rules
    'min_volume_ratio': 1.5,
    'trend_confirmation': True,
    
    # Risk management
    'stop_loss_percent': 2.0,
    'take_profit_percent': 4.0
}
```

#### 3. Implement the Strategy

```python
from base_strategy import EnhancedBaseStrategy
import pandas as pd
import numpy as np

class YouTubeStrategy_FDmV1bIub_s(EnhancedBaseStrategy):
    """Strategy from YouTube video FDmV1bIub_s"""
    
    def __init__(self, params):
        super().__init__("YT_FDmV1bIub_s", params)
        
        # Extract parameters
        self.ema_fast = params.get('ema_fast', 12)
        self.ema_slow = params.get('ema_slow', 26)
        self.rsi_period = params.get('rsi_period', 14)
        self.rsi_oversold = params.get('rsi_oversold', 30)
        self.rsi_overbought = params.get('rsi_overbought', 70)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """Generate signal based on video strategy"""
        if not self.validate_data(df):
            return 0
        
        # Need enough data for indicators
        min_periods = max(self.ema_slow, self.rsi_period) + 1
        if len(df) < min_periods:
            return 0
        
        df_copy = df.copy()
        
        # Calculate EMA
        df_copy['ema_fast'] = df_copy['close'].ewm(
            span=self.ema_fast, adjust=False
        ).mean()
        df_copy['ema_slow'] = df_copy['close'].ewm(
            span=self.ema_slow, adjust=False
        ).mean()
        
        # Calculate RSI
        delta = df_copy['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(self.rsi_period).mean()
        avg_loss = loss.rolling(self.rsi_period).mean()
        rs = avg_gain / avg_loss
        df_copy['rsi'] = 100 - (100 / (1 + rs))
        
        # Get current values
        ema_fast_curr = df_copy['ema_fast'].iloc[-1]
        ema_slow_curr = df_copy['ema_slow'].iloc[-1]
        rsi_curr = df_copy['rsi'].iloc[-1]
        
        # Check for NaN
        if pd.isna(ema_fast_curr) or pd.isna(rsi_curr):
            return 0
        
        # BUY Signal: EMA crossover + RSI oversold
        if (ema_fast_curr > ema_slow_curr and 
            rsi_curr < self.rsi_overbought):
            return 1  # BUY
        
        # SELL Signal: EMA bearish + RSI overbought
        elif (ema_fast_curr < ema_slow_curr and 
              rsi_curr > self.rsi_oversold):
            return -1  # SELL
        
        return 0  # HOLD
```

#### 4. Register in Strategy Manager

Add to `config.py`:

```python
strategies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
    # ... existing strategies ...
    "youtube_strategy": {
        "ema_fast": 12,
        "ema_slow": 26,
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70
    }
})
```

Add to `strategy.py` STRATEGY_MAP:

```python
from your_module import YouTubeStrategy_FDmV1bIub_s

self.STRATEGY_MAP['youtube_strategy'] = YouTubeStrategy_FDmV1bIub_s
```

#### 5. Test the Strategy

```python
# Backtest
from backtester import Backtester

config = {
    'active_strategies': ['youtube_strategy'],
    'cooperation_logic': 'OR',
    'strategies': {
        'youtube_strategy': video_params
    }
}

backtester = Backtester(config)
results = backtester.run(df)
print(results)
```

---

## 🔧 Advanced Features

### Custom Confidence Calculation

Override `_calculate_confidence()` for signal quality assessment:

```python
def _calculate_confidence(self, df: pd.DataFrame, signal: int) -> float:
    """Calculate confidence score (0-1)"""
    if signal == 0:
        return 0.0
    
    # Calculate based on multiple factors
    rsi_confidence = self._calculate_rsi_confidence(df)
    volume_confidence = self._calculate_volume_confidence(df)
    trend_confidence = self._calculate_trend_confidence(df)
    
    # Weighted average
    confidence = (
        0.4 * rsi_confidence +
        0.3 * volume_confidence +
        0.3 * trend_confidence
    )
    
    return min(1.0, max(0.0, confidence))
```

### Multi-Timeframe Confirmation

Use multiple timeframes for better signals:

```python
def generate_signal(self, df: pd.DataFrame) -> int:
    # Primary timeframe signal
    primary_signal = self._analyze_primary_timeframe(df)
    
    if primary_signal == 0:
        return 0
    
    # Higher timeframe confirmation
    df_4h = self.get_data_feed('BTC/USDT', '4h')
    if df_4h is not None:
        higher_trend = self._get_trend(df_4h)
        
        # Only trade with higher timeframe
        if primary_signal == 1 and higher_trend != 'bullish':
            return 0
        if primary_signal == -1 and higher_trend != 'bearish':
            return 0
    
    return primary_signal
```

### Event Hooks

Override lifecycle hooks:

```python
def _on_init(self):
    """Called after initialization"""
    logger.info(f"Custom initialization for {self.name}")
    self.custom_cache = {}

def _on_params_updated(self):
    """Called after parameters are updated"""
    logger.info("Parameters changed, recalculating indicators")
    self.custom_cache.clear()
```

---

## 📝 Integration with Main Bot

### Option 1: Activate in Config

Edit `config.py`:

```python
active_strategies: list = field(default_factory=lambda: [
    "video_based",  # Use the template
    "rsi",
    "ema_crossover"
])
```

### Option 2: Programmatic Activation

```python
from config import config

# Add video-based strategy
config.active_strategies.append('video_based')
config.strategies['video_based'] = {
    'ma_short': 10,
    'ma_long': 50,
    'rsi_period': 14
}

# Save configuration
config.save_to_file()
```

### Option 3: Dynamic Registration

```python
from strategy import StrategyManager

# Create strategy manager
manager = StrategyManager(config_dict)

# Manually add strategy
from base_strategy import VideoBasedStrategy
manager.STRATEGY_MAP['my_strategy'] = VideoBasedStrategy
manager._initialize_strategies()
```

---

## 🧪 Testing

### Unit Tests

```python
import pytest
from base_strategy import VideoBasedStrategy
from utils import generate_sample_data

def test_video_strategy_initialization():
    params = {'ma_short': 10, 'ma_long': 50}
    strategy = VideoBasedStrategy(params)
    
    assert strategy.name == "VideoBasedStrategy"
    assert strategy.enabled == True
    assert strategy.ma_short == 10

def test_video_strategy_signal_generation():
    params = {'ma_short': 10, 'ma_long': 50}
    strategy = VideoBasedStrategy(params)
    
    df = generate_sample_data(n_bars=100)
    signal = strategy.generate_signal(df)
    
    assert signal in [-1, 0, 1]

def test_multi_timeframe_data_feeds():
    strategy = VideoBasedStrategy({})
    
    df_1h = generate_sample_data(n_bars=100)
    df_4h = generate_sample_data(n_bars=100)
    
    assert strategy.add_data_feed('BTC/USDT', '1h', df_1h) == True
    assert strategy.add_data_feed('BTC/USDT', '4h', df_4h) == True
    
    retrieved = strategy.get_data_feed('BTC/USDT', '1h')
    assert retrieved is not None
    assert len(retrieved) == 100
```

### Backtesting

```python
from backtester import Backtester

# Configure
config = {
    'initial_capital': 10000,
    'trade_size': 100,
    'active_strategies': ['video_based'],
    'cooperation_logic': 'OR',
    'strategies': {
        'video_based': {
            'ma_short': 10,
            'ma_long': 50,
            'rsi_period': 14
        }
    }
}

# Run backtest
backtester = Backtester(config)
results = backtester.run(historical_data)

# Analyze
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

---

## 🔍 Troubleshooting

### Problem: Strategy not generating signals

**Possible causes:**
- Insufficient data (need enough bars for indicators)
- Parameters too restrictive
- Data validation failing

**Solution:**
```python
# Enable debug logging
import logging
logging.getLogger('base_strategy').setLevel(logging.DEBUG)

# Check data validation
if not strategy.validate_data(df):
    print("Data validation failed")

# Check parameter values
print(strategy.get_info())
```

### Problem: State not persisting

**Solution:**
```python
# Explicitly export state after important events
strategy.on_position_closed(exit_price, profit, 'long')
strategy.export_state('data/strategy_state.json')

# Restore on startup
strategy.import_state('data/strategy_state.json')
```

### Problem: Performance degradation

**Solution:**
```python
# Monitor execution time
info = strategy.get_info()
if info['performance']['avg_execution_time_ms'] > 100:
    print("Warning: Strategy execution time is high")

# Optimize indicator calculation
# Cache results where possible
```

---

## 📚 Reference

### EnhancedBaseStrategy API

#### Methods

- `generate_signal(df)` - Generate trading signal (abstract)
- `generate_signal_with_context(df, context)` - Generate signal with metadata
- `validate_data(df)` - Validate input data
- `add_data_feed(symbol, timeframe, data)` - Add multi-timeframe data
- `get_data_feed(symbol, timeframe)` - Get data feed
- `update_state(**kwargs)` - Update strategy state
- `on_position_opened(price, quantity, side)` - Position opened callback
- `on_position_closed(price, profit, side)` - Position closed callback
- `update_params(params)` - Update parameters
- `get_info()` - Get strategy information
- `reset_state()` - Reset state
- `export_state(filepath)` - Export state to JSON
- `import_state(filepath)` - Import state from JSON

#### Properties

- `name` - Strategy name
- `params` - Strategy parameters
- `enabled` - Enable/disable flag
- `state` - StrategyState object
- `data_feeds` - Dict of DataFeed objects
- `performance_metrics` - Performance tracking dict

---

## 💡 Best Practices

1. **Always validate data** before processing
2. **Use logging extensively** for debugging
3. **Test with backtesting** before live trading
4. **Start with paper trading** (DRY_RUN=true)
5. **Monitor performance metrics** regularly
6. **Export state periodically** for recovery
7. **Document your strategy logic** clearly
8. **Use multi-timeframe confirmation** for better signals
9. **Implement proper risk management**
10. **Version control your strategies**

---

## 🎓 Examples

See the following files for complete examples:

- `base_strategy.py` - Framework implementation
- `test_base_strategy.py` - Unit tests (to be created)
- `demo_video_strategy.py` - Demo application (to be created)

---

## 📞 Support

For questions or issues:

1. Check this guide first
2. Review the code examples
3. Check existing strategies in `strategy.py`
4. Enable debug logging
5. Open a GitHub issue

---

**Made for Windows ⭐ | Enhanced Strategy Framework | Video-Based Strategy Support**
