# 🔄 Binance API Migration Guide

## Overview

This guide will help you migrate to the Binance API as the primary trading platform for the AI Trading Bot. Binance has been set as the default API provider, with Alpaca maintained as legacy support.

---

## 📋 Table of Contents

1. [Why Binance?](#why-binance)
2. [Prerequisites](#prerequisites)
3. [Getting API Keys](#getting-api-keys)
4. [Configuration](#configuration)
5. [Installation](#installation)
6. [Usage Examples](#usage-examples)
7. [Trading Strategies](#trading-strategies)
8. [Risk Management](#risk-management)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## 🎯 Why Binance?

### Advantages
- **24/7 Trading**: Cryptocurrency markets never sleep
- **Global Access**: Available in most countries
- **Lower Fees**: Competitive trading fees
- **High Liquidity**: Deep order books for major pairs
- **Testnet Support**: Free paper trading environment
- **Advanced Features**: Futures, options, margin trading
- **WebSocket Support**: Real-time data streaming

### Supported Assets
- ✅ Cryptocurrencies (BTC, ETH, BNB, etc.)
- ✅ Stablecoins (USDT, USDC, BUSD)
- ✅ 1000+ Trading Pairs

---

## 🔑 Prerequisites

### System Requirements
- Python 3.8 or higher
- Internet connection
- 1GB free disk space

### Required Knowledge
- Basic Python programming
- Understanding of trading concepts
- Binance account (for live trading)

---

## 🔐 Getting API Keys

### For Testnet (Paper Trading - Recommended for Beginners)

1. **Visit Binance Testnet**:
   - Go to: https://testnet.binance.vision/
   
2. **Create Account**:
   - Sign up with GitHub or email
   - No KYC required
   - Free test tokens provided

3. **Generate API Keys**:
   - Navigate to API settings
   - Click "Generate HMAC_SHA256 Key"
   - Save both API Key and Secret Key securely
   - **Important**: Never share these keys!

### For Production (Live Trading - Use with Caution!)

1. **Create Binance Account**:
   - Go to: https://www.binance.com/
   - Complete KYC verification
   - Enable 2FA (Required)

2. **Generate API Keys**:
   - Go to Account → API Management
   - Create new API key
   - **Enable these permissions only**:
     - ✅ Enable Reading
     - ✅ Enable Spot & Margin Trading
     - ❌ Enable Withdrawals (NEVER enable this!)
   
3. **Secure Your API Keys**:
   - Add IP restrictions (Recommended)
   - Set trading limits
   - Enable anti-phishing code
   - Store keys in secure location

---

## ⚙️ Configuration

### Step 1: Create Configuration File

Copy the template file:
```bash
cp keys.env.template keys.env
```

### Step 2: Add Your API Keys

Edit `keys.env` with your favorite text editor:

```env
# For Paper Trading (Testnet)
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_SECRET_KEY=your_testnet_secret_key_here

# For Live Trading (Production)
# BINANCE_API_KEY=your_production_api_key_here
# BINANCE_SECRET_KEY=your_production_secret_key_here

# Optional: OpenAI for AI features
OPENAI_API_KEY=your_openai_key_here

# Logging
LOG_LEVEL=INFO
```

**Important**: 
- Never commit `keys.env` to git (it's already in `.gitignore`)
- Use testnet keys first to test your strategies
- Only use production keys when you're confident

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `python-binance>=1.0.19` - Binance API client
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `python-dotenv>=1.0.0` - Environment variables
- `Flask>=3.0.0` - Web dashboard
- `matplotlib>=3.7.0` - Visualization
- `plotly>=5.18.0` - Interactive charts

### Step 2: Verify Installation

```bash
python3 -c "from binance_integration import BinanceDataProvider; print('✓ Binance integration ready')"
```

Expected output:
```
✓ Binance integration ready
```

---

## 🚀 Usage Examples

### Example 1: Basic Trading Bot (Simulation Mode)

Test without API keys first:

```bash
python3 main.py
```

This runs in simulation mode with:
- Simulated market data
- No real money
- No API connection needed

### Example 2: Paper Trading with Testnet

With Binance testnet keys in `keys.env`:

```bash
# The bot will automatically detect and use Binance testnet
python3 main.py
```

### Example 3: Golden Cross Strategy

```bash
# Paper trading mode (testnet)
python3 golden_cross_bot.py --mode paper --symbol BTCUSDT

# Testnet mode with custom capital
python3 golden_cross_bot.py --mode testnet --symbol BTCUSDT --capital 5000

# Custom check interval (every 30 minutes)
python3 golden_cross_bot.py --mode paper --interval 1800
```

### Example 4: Custom Strategy Configuration

Edit `config.py` to customize strategies:

```python
# In config.py
active_strategies = ["rsi", "ema_crossover", "lsob"]
cooperation_logic = "OR"  # OR means any strategy can trigger

# Strategy parameters
strategies = {
    "rsi": {
        "window": 14,
        "oversold_threshold": 30,
        "overbought_threshold": 70
    },
    "ema_crossover": {
        "short_window": 9,
        "long_window": 21
    },
    "lsob": {
        "bb_window": 20,
        "atr_window": 14,
        "breakout_threshold": 0.005
    }
}
```

---

## 📈 Trading Strategies

### Available Strategies

1. **RSI (Relative Strength Index)**
   - Type: Mean Reversion
   - Best for: Range-bound markets
   - Buy: RSI < 30 (oversold)
   - Sell: RSI > 70 (overbought)

2. **EMA Crossover**
   - Type: Trend Following
   - Best for: Trending markets
   - Buy: Fast EMA crosses above Slow EMA
   - Sell: Fast EMA crosses below Slow EMA

3. **LSOB (Long-Short On Breakout)**
   - Type: Volatility Breakout
   - Best for: High volatility periods
   - Uses: Bollinger Bands + ATR + Volume
   - Buy: Breakout above upper band with volume
   - Sell: Breakout below lower band

4. **Bollinger Bands**
   - Type: Volatility Based
   - Buy: Price touches lower band
   - Sell: Price touches upper band

5. **Golden Cross**
   - Type: Long-term Trend
   - Buy: 50 MA crosses above 200 MA
   - Sell: 50 MA crosses below 200 MA
   - Best for: Long-term positions

### Strategy Cooperation Modes

**OR Mode** (Default):
- Any strategy can trigger a trade
- More trades, faster reactions
- Higher risk of false signals

**AND Mode**:
- All strategies must agree
- Fewer trades, stronger confirmation
- Lower risk, potentially missing opportunities

---

## 🛡️ Risk Management

### Built-in Risk Controls

1. **Position Sizing**:
   ```python
   max_position_size = 1000.0  # Maximum per position
   risk_per_trade = 0.02       # 2% risk per trade
   ```

2. **Stop Loss**:
   ```python
   enable_stop_loss = True
   stop_loss_percent = 10.0    # 10% stop loss
   ```

3. **Take Profit**:
   ```python
   enable_take_profit = True
   take_profit_percent = 20.0  # 20% take profit
   ```

4. **Daily Loss Limit**:
   ```python
   max_daily_loss = 0.05       # 5% maximum daily loss
   ```

### Recommended Settings

**Conservative**:
```python
risk_per_trade = 0.01           # 1%
stop_loss_percent = 5.0         # 5%
take_profit_percent = 10.0      # 10%
cooperation_logic = "AND"       # All strategies must agree
```

**Moderate** (Default):
```python
risk_per_trade = 0.02           # 2%
stop_loss_percent = 10.0        # 10%
take_profit_percent = 20.0      # 20%
cooperation_logic = "OR"        # Any strategy can trigger
```

**Aggressive**:
```python
risk_per_trade = 0.05           # 5%
stop_loss_percent = 15.0        # 15%
take_profit_percent = 30.0      # 30%
cooperation_logic = "OR"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "BINANCE_AVAILABLE = False"
**Problem**: python-binance not installed
**Solution**: 
```bash
pip install python-binance
```

#### 2. "Connection Error: Failed to resolve 'api.binance.com'"
**Problem**: Network blocked or firewall
**Solution**:
- Check internet connection
- Try disabling VPN
- Check firewall settings
- Use simulation mode: `python3 main.py` (no API needed)

#### 3. "API Key Invalid"
**Problem**: Wrong API keys or expired
**Solution**:
- Verify keys in `keys.env`
- Check if keys are for correct environment (testnet vs production)
- Regenerate keys on Binance
- Ensure no extra spaces in keys

#### 4. "Bot runs but no trades"
**Problem**: Strategy conditions not met
**Solution**:
- Check logs: `tail -f logs/trading_bot.log`
- Try different symbols
- Adjust strategy parameters
- Use simulation mode to test

#### 5. "Permission Denied" error
**Problem**: API key permissions insufficient
**Solution**:
- Check API key permissions on Binance
- Enable "Spot & Margin Trading"
- DO NOT enable "Withdrawals"

### Debug Mode

Enable detailed logging:
```python
# In config.py or keys.env
LOG_LEVEL=DEBUG
```

Then check logs:
```bash
tail -f logs/trading_bot.log
```

---

## 🔒 Security Best Practices

### Critical Security Rules

1. **Never Share API Keys**:
   - ❌ Don't commit to git
   - ❌ Don't share in screenshots
   - ❌ Don't post in forums
   - ❌ Don't send via email/chat

2. **Use IP Restrictions**:
   - Go to Binance → API Management
   - Add your server IP
   - Blocks access from other locations

3. **Limit Permissions**:
   - ✅ Enable Reading
   - ✅ Enable Spot Trading
   - ❌ NEVER enable Withdrawals
   - ❌ Disable unnecessary permissions

4. **Use Testnet First**:
   - Always test with testnet
   - Verify strategies work
   - Check for bugs
   - Only then move to production

5. **Monitor Regularly**:
   - Check trades daily
   - Review logs
   - Monitor account balance
   - Set up alerts

6. **Secure Your System**:
   - Keep Python updated
   - Use virtual environments
   - Enable 2FA on Binance
   - Use strong passwords

### Emergency Procedures

**If API Keys Compromised**:
1. Immediately disable keys on Binance
2. Check account for unauthorized trades
3. Generate new keys
4. Review security settings
5. Enable 2FA if not already active

**If Bot Malfunctions**:
1. Stop the bot: `Ctrl+C`
2. Close all open positions manually on Binance
3. Review logs: `logs/trading_bot.log`
4. Test in simulation mode first
5. Only restart when issue is resolved

---

## 📊 Monitoring and Logs

### Log Files

All logs are stored in `logs/` directory:
- `trading_bot.log` - Main bot logs
- `golden_cross_bot_*.log` - Golden Cross strategy logs

### Trade History

All trades are recorded in CSV format:
- `data/trades.csv` - Main bot trades
- `data/golden_cross_trades_*.csv` - Golden Cross trades

### View Logs in Real-time

```bash
# Main bot logs
tail -f logs/trading_bot.log

# Golden Cross bot logs
tail -f logs/golden_cross_bot_BTCUSDT_paper.log
```

### Performance Metrics

Check trade performance:
```bash
python3 -c "
import pandas as pd
trades = pd.read_csv('data/trades.csv')
print(trades.describe())
"
```

---

## 🎓 Next Steps

### For Beginners
1. ✅ Read this guide completely
2. ✅ Get testnet API keys
3. ✅ Run in simulation mode first
4. ✅ Test with testnet for 1 week
5. ✅ Review all trades
6. ✅ Adjust strategies as needed
7. ✅ Only then consider live trading

### For Experienced Traders
1. ✅ Review strategy parameters
2. ✅ Customize risk management
3. ✅ Backtest with historical data
4. ✅ Test on testnet
5. ✅ Start with small capital
6. ✅ Scale up gradually

---

## 📞 Support

### Documentation
- **Main README**: `README.md`
- **FAQ**: `FAQ.md`
- **Strategy Guide**: Check strategy files

### Community
- **Issues**: Report on GitHub
- **Binance API Docs**: https://binance-docs.github.io/apidocs/

### Useful Links
- Binance Testnet: https://testnet.binance.vision/
- Binance API Status: https://binance.statuspage.io/
- Python-Binance Docs: https://python-binance.readthedocs.io/

---

## ⚠️ Disclaimer

**IMPORTANT**: 
- This bot is for educational purposes
- Trading cryptocurrencies carries high risk
- Never invest more than you can afford to lose
- Always test thoroughly before live trading
- Past performance does not guarantee future results
- Use at your own risk

**NOT FINANCIAL ADVICE**: This software does not provide financial, investment, or trading advice. Always do your own research and consult with qualified professionals.

---

## ✨ Credits

- **Original Bot**: CallMeMell
- **API Provider**: Binance
- **Python Library**: python-binance

---

**🎉 Happy Trading! Remember: Start with Testnet, Test Thoroughly, Trade Responsibly.**
