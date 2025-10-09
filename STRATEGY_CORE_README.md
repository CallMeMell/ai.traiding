# Reversal-Trailing-Stop Strategy

## Overview

The **Reversal-Trailing-Stop Strategy** is an aggressive trading approach that maintains continuous market exposure through automated position management and reversal logic.

## Strategy Features

### 1. Immediate Entry
- The bot **immediately enters a position** upon initialization
- Default initial direction is LONG, but can be configured to start SHORT
- No waiting for specific market conditions - immediate market exposure

### 2. Trailing Stop-Loss
- Once a position is **in profit**, the stop-loss automatically trails the price movement
- For LONG positions: Stop-loss moves up as price increases
- For SHORT positions: Stop-loss moves down as price decreases
- The stop-loss **never moves unfavorably** (only locks in profits)

### 3. Position Reversal on Stop-Loss
- When the trailing stop-loss is breached, the position is immediately closed
- A new position is **immediately opened in the opposite direction**
- Uses the updated capital (including P&L from the closed trade)
- Example: LONG position stopped out → Immediately open SHORT position

### 4. Take-Profit Re-Entry
- When take-profit is hit, the position is closed with profit
- A new position is **immediately opened in the same direction**
- Capitalizes on continued momentum in the same direction

## Usage

### Basic Usage

```python
from strategy_core import ReversalTrailingStopStrategy
import pandas as pd

# Initialize the strategy
strategy = ReversalTrailingStopStrategy(
    initial_capital=10000.0,      # Starting capital
    stop_loss_percent=2.0,        # 2% stop-loss
    take_profit_percent=4.0,      # 4% take-profit
    trailing_stop_percent=1.0,    # 1% trailing stop distance
    initial_direction='LONG'      # Start with LONG position
)

# Process each price candle
for _, candle in price_data.iterrows():
    result = strategy.process_candle(candle)
    
    # Check the action taken
    if result['action'] == 'BUY':
        print(f"Opened LONG position at ${result['price']:.2f}")
    elif result['action'] == 'SELL':
        print(f"Opened SHORT position at ${result['price']:.2f}")
    elif result['action'] == 'REVERSE':
        print(f"Reversed position: {result['trade_info']}")
    elif result['action'] == 'REENTER':
        print(f"Re-entered position: {result['trade_info']}")

# Get performance statistics
stats = strategy.get_statistics()
print(f"Total P&L: ${stats['total_pnl']:.2f}")
print(f"ROI: {stats['roi']:.2f}%")
print(f"Win Rate: {stats['win_rate']:.2f}%")
```

### Running the Built-in Example

The `strategy_core.py` file includes a complete example:

```bash
python strategy_core.py
```

This will:
1. Generate 500 candles of sample price data
2. Run the strategy on this data
3. Print detailed statistics and performance metrics

## Input Data Format

The strategy expects price data as pandas Series with the following fields:

```python
candle = {
    'open': 30000.00,      # Opening price
    'high': 30100.00,      # Highest price in the period
    'low': 29900.00,       # Lowest price in the period
    'close': 30000.00,     # Closing price
    'volume': 1000000      # Trading volume
}
```

## Strategy Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `initial_capital` | float | 10000.0 | Starting trading capital |
| `stop_loss_percent` | float | 2.0 | Initial stop-loss percentage (2.0 = 2%) |
| `take_profit_percent` | float | 4.0 | Take-profit percentage (4.0 = 4%) |
| `trailing_stop_percent` | float | 1.0 | Distance for trailing stop (1.0 = 1%) |
| `initial_direction` | str | 'LONG' | Initial position direction ('LONG' or 'SHORT') |

## Return Values

The `process_candle()` method returns a dictionary with:

```python
{
    'action': 'BUY' | 'SELL' | 'REVERSE' | 'REENTER' | 'HOLD',
    'price': float,           # Current price
    'position': {             # Current position info
        'has_position': bool,
        'direction': str,
        'entry_price': float,
        'stop_loss': float,
        'take_profit': float,
        'capital': float
    },
    'trade_info': {           # Only present when trade is closed
        'direction': str,
        'entry_price': float,
        'exit_price': float,
        'pnl': float,
        'exit_reason': 'STOP_LOSS' | 'TAKE_PROFIT',
        'capital_after': float
    }
}
```

## Performance Metrics

Call `get_statistics()` to retrieve performance metrics:

```python
stats = strategy.get_statistics()
# Returns:
# {
#     'total_trades': int,
#     'winning_trades': int,
#     'losing_trades': int,
#     'win_rate': float,        # Percentage
#     'total_pnl': float,
#     'roi': float,             # Percentage
#     'avg_win': float,
#     'avg_loss': float,
#     'capital': float,
#     'initial_capital': float
# }
```

Or use `print_statistics()` for a formatted output:

```python
strategy.print_statistics()
```

Output:
```
======================================================================
📊 REVERSAL-TRAILING-STOP STRATEGY STATISTICS
======================================================================

💰 CAPITAL:
  Initial Capital:  $10,000.00
  Final Capital:    $10,782.74
  Total P&L:        $782.74
  ROI:              7.83%

📈 TRADES:
  Total Trades:     60
  Winning Trades:   25
  Losing Trades:    35
  Win Rate:         41.67%
  Average Win:      $125.80
  Average Loss:     $-67.49
======================================================================
```

## Testing

Run the test suite to verify the strategy:

```bash
python test_strategy_core.py
```

The test suite includes:
- Initialization tests
- Immediate entry verification
- Stop-loss reversal logic
- Take-profit re-entry logic
- Trailing stop updates
- Capital management
- SHORT position mechanics
- Integration scenarios

## Strategy Behavior

### LONG Position Flow
1. Enter LONG at current price
2. Set stop-loss at entry - 2%
3. Set take-profit at entry + 4%
4. As price rises (in profit), trailing stop follows 1% below highest price
5. If stop-loss hit → Close LONG, Open SHORT (REVERSAL)
6. If take-profit hit → Close LONG, Open LONG (RE-ENTRY)

### SHORT Position Flow
1. Enter SHORT at current price
2. Set stop-loss at entry + 2%
3. Set take-profit at entry - 4%
4. As price falls (in profit), trailing stop follows 1% above lowest price
5. If stop-loss hit → Close SHORT, Open LONG (REVERSAL)
6. If take-profit hit → Close SHORT, Open SHORT (RE-ENTRY)

## Risk Considerations

⚠️ **Important Notes:**

1. **High Activity**: This strategy maintains continuous market exposure and can generate many trades
2. **Transaction Costs**: Consider broker fees and slippage in real trading
3. **Volatility Sensitivity**: Performs best in volatile markets but can be whipsawed in choppy conditions
4. **Capital Management**: All available capital is always in the market
5. **No Drawdown Protection**: The strategy does not include max drawdown limits

## Customization

You can extend the strategy by:

1. **Adding filters**: Only reverse in certain market conditions
2. **Dynamic parameters**: Adjust stop-loss/take-profit based on volatility (ATR)
3. **Position sizing**: Vary position size based on confidence or risk metrics
4. **Multiple timeframes**: Use higher timeframe trends to bias direction
5. **Maximum reversals**: Add a limit on consecutive reversals

## Integration with Existing Bot

To integrate with the existing trading bot framework:

```python
from strategy_core import ReversalTrailingStopStrategy
from config import config

# In your trading bot
strategy = ReversalTrailingStopStrategy(
    initial_capital=config.initial_capital,
    stop_loss_percent=config.stop_loss_percent,
    take_profit_percent=config.take_profit_percent,
    trailing_stop_percent=config.trailing_stop_percent,
    initial_direction='LONG'
)

# In your trading loop
for candle in market_data:
    result = strategy.process_candle(candle)
    
    if result['action'] in ['BUY', 'SELL', 'REVERSE', 'REENTER']:
        # Execute the trade
        execute_order(result)
```

## License

This strategy implementation is part of the ai.traiding project.

## Support

For issues or questions, please refer to the main repository documentation or create an issue on GitHub.
