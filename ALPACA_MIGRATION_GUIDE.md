# 🔄 Alpaca API Migration Guide

## Overview

This trading bot has been **migrated from Binance API to Alpaca API** as the primary trading platform. This guide explains the changes, how to configure the bot, and how to use it with Alpaca.

---

## ✨ What's New

### 🆕 Alpaca API Integration
- **Primary Trading Platform**: Alpaca API is now the main data source and order execution platform
- **Stock & Crypto Support**: Trade stocks, ETFs, and crypto (via Alpaca)
- **Paper Trading**: Full paper trading support with Alpaca
- **Real-time Data**: Access to real-time market data and quotes
- **Order Management**: Market orders, limit orders, stop-loss, and take-profit

### 🆕 LSOB Strategy
- **Long-Short On Breakout**: New strategy that identifies and trades price breakouts
- **Risk Management**: Built-in ATR-based stop-loss and take-profit calculations
- **Volume Confirmation**: Uses volume to confirm breakouts
- **Volatility Filter**: Avoids trades during excessive volatility

### 🔐 Secure Key Management
- **keys.env File**: All API keys are stored in a secure `keys.env` file
- **Git Ignored**: `keys.env` is automatically excluded from version control
- **Environment Variables**: Support for loading keys from environment variables

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `alpaca-py` - Alpaca API SDK
- `pandas`, `numpy` - Data processing
- `python-dotenv` - Environment variable management
- `Flask` - Web dashboard
- `matplotlib`, `plotly` - Visualization

### 2. Configure API Keys

Create a `keys.env` file in the project root:

```bash
cp keys.env keys.env.local
```

Edit `keys.env.local` with your actual API keys:

```env
# Alpaca API Keys
ALPACA_API_KEY=your_actual_api_key_here
ALPACA_SECRET_KEY=your_actual_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Optional: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: 
- Get your Alpaca API keys from: https://alpaca.markets/
- For paper trading: Use `https://paper-api.alpaca.markets`
- For live trading: Use `https://api.alpaca.markets`
- **Never commit keys.env to version control!**

### 3. Verify Installation

Test the Alpaca integration:

```bash
python3 alpaca_integration.py
```

This will:
- Test connection to Alpaca
- Load historical data for AAPL
- Display current price
- Show account information (if keys are configured)

---

## 🎯 Available Strategies

The bot now includes **5 trading strategies**:

### 1. MA Crossover
- **Type**: Trend-Following
- **Timeframe**: Medium to Long-term
- **Parameters**: Short window (50), Long window (200)

### 2. RSI Mean Reversion
- **Type**: Mean Reversion
- **Timeframe**: Short-term
- **Parameters**: RSI period (14), Oversold (35), Overbought (65)

### 3. Bollinger Bands
- **Type**: Volatility Breakout
- **Timeframe**: Medium-term
- **Parameters**: Window (20), Std Dev (2.0)

### 4. EMA Crossover
- **Type**: Fast Trend-Following
- **Timeframe**: Daytrading
- **Parameters**: Short window (9), Long window (21)

### 5. LSOB (New!)
- **Type**: Breakout Strategy with Risk Management
- **Timeframe**: Intraday to Medium-term
- **Features**:
  - Bollinger Bands for breakout detection
  - ATR-based stop-loss and take-profit
  - Volume confirmation
  - Volatility filter
- **Parameters**:
  - BB window: 20
  - BB std: 2.0
  - ATR window: 14
  - Volume threshold: 1.2x average
  - Stop loss: 2x ATR
  - Take profit: 3x ATR

---

## 🚀 Usage

### Running the Bot

#### Paper Trading (Simulated)
```bash
python3 main.py
```

This will:
- Use simulated data if no API keys are configured
- Use Alpaca paper trading if API keys are available
- Run with default configuration from `config.py`

#### Customize Strategies

Edit `config.py` to change active strategies:

```python
# config.py
active_strategies: list = field(default_factory=lambda: ["lsob", "ema_crossover"])
cooperation_logic: str = "OR"  # "AND" or "OR"
```

#### Test LSOB Strategy

```bash
python3 lsob_strategy.py
```

This runs the LSOB strategy example with simulated data.

### Golden Cross Bot (Updated)

The Golden Cross Bot now supports both Alpaca and Binance:

```bash
# Paper trading with Alpaca (stocks)
python3 golden_cross_bot.py --mode paper --symbol AAPL

# Paper trading with crypto
python3 golden_cross_bot.py --mode paper --symbol BTCUSD

# Live trading (CAUTION!)
python3 golden_cross_bot.py --mode live --symbol AAPL
```

---

## 🔧 Configuration

### Strategy Configuration

All strategies are configured in `config.py`:

```python
strategies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
    "lsob": {
        "bb_window": 20,
        "bb_std": 2.0,
        "atr_window": 14,
        "volume_threshold": 1.2,
        "breakout_threshold": 0.005,
        "stop_loss_atr_mult": 2.0,
        "take_profit_atr_mult": 3.0,
        "max_volatility": 0.05
    },
    # ... other strategies
})
```

### Risk Management

Configure risk parameters in `config.py`:

```python
# Risk Management
max_position_size: float = 1000.0
max_positions: int = 10
risk_per_trade: float = 0.02  # 2% per trade
max_daily_loss: float = 0.05  # 5% max daily loss

# Stop-Loss & Take-Profit
enable_stop_loss: bool = True
stop_loss_percent: float = 10.0
enable_take_profit: bool = True
take_profit_percent: float = 20.0
```

---

## 📊 API Comparison

### Alpaca (Primary)
✅ **Advantages**:
- Commission-free trading
- Stock and crypto support
- Easy to use API
- Great paper trading support
- US-based and regulated

❌ **Limitations**:
- US market hours only (stocks)
- Requires US-based account or international support
- Limited to supported assets

### Binance (Legacy Support)
✅ **Advantages**:
- 24/7 crypto trading
- Wide range of cryptocurrencies
- High liquidity

❌ **Limitations**:
- Complex API
- Requires separate API keys
- Regulatory uncertainty in some regions

---

## 🔒 Security Best Practices

1. **Never commit API keys**: Always use `keys.env` and keep it in `.gitignore`
2. **Use paper trading first**: Test thoroughly before live trading
3. **Set appropriate limits**: Configure `max_position_size` and `max_daily_loss`
4. **Monitor regularly**: Check logs and trades frequently
5. **Backup your trades**: Regularly backup `data/trades.csv`

---

## 🧪 Testing

### Test Alpaca Integration

```bash
# Test data provider
python3 -c "from alpaca_integration import AlpacaDataProvider; dp = AlpacaDataProvider(); print(dp.test_connection())"

# Run example
python3 alpaca_integration.py
```

### Test LSOB Strategy

```bash
python3 lsob_strategy.py
```

### Run Existing Tests

```bash
python3 test_system.py
```

---

## 📚 Additional Resources

- **Alpaca Documentation**: https://alpaca.markets/docs/
- **Alpaca API Keys**: https://app.alpaca.markets/paper/dashboard/overview
- **Trading Bot FAQ**: See `FAQ.md` for common questions
- **Strategy Guide**: See individual strategy files for detailed documentation

---

## 🆘 Troubleshooting

### "Alpaca connection failed"
- Check that your API keys are correct in `keys.env`
- Verify you're using the correct base URL (paper vs live)
- Check your internet connection

### "No data returned"
- Verify the symbol is valid (e.g., 'AAPL', 'TSLA', 'BTCUSD')
- Check that the market is open (for stocks)
- Try with a different symbol

### "Module not found: alpaca"
- Run `pip install alpaca-py`
- Ensure you're in the correct virtual environment

### "LSOB strategy not available"
- This is a warning, not an error - the strategy will still work
- Ensure `lsob_strategy.py` is in the same directory

---

## 🎉 Next Steps

1. **Configure your API keys** in `keys.env`
2. **Test the connection** with `python3 alpaca_integration.py`
3. **Run paper trading** with `python3 main.py`
4. **Monitor results** in `logs/` and `data/trades.csv`
5. **Backtest strategies** with different parameters
6. **Go live** when you're confident (use paper trading first!)

---

## 📝 Changelog

### Version 2.0 - Alpaca Migration
- ✅ Migrated from Binance to Alpaca API
- ✅ Added LSOB (Long-Short On Breakout) strategy
- ✅ Implemented secure key management with `keys.env`
- ✅ Updated all documentation
- ✅ Added comprehensive error handling
- ✅ Maintained backward compatibility with Binance (legacy)

---

**Happy Trading! 🚀📈**
