# 🚨 Live Trading Setup Guide

**Complete guide for setting up secure live trading with Windows Credential Manager**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Security Model](#security-model)
- [Step-by-Step Setup](#step-by-step-setup)
- [Circuit Breaker (Drawdown-Limit)](#-circuit-breaker-drawdown-limit)
- [File Structure](#file-structure)
- [Scripts Reference](#scripts-reference)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Overview

This guide shows how to set up **secure live trading** with real money on Binance. The setup uses **Windows Credential Manager** (or system keychain on Linux/macOS) to store API keys, ensuring secrets never touch the filesystem.

### Key Features

- ✅ **Secure Storage**: API keys stored in Windows Credential Manager (not in files)
- ✅ **Preflight Checks**: Automatic validation before trading starts
- ✅ **Explicit Acknowledgement**: `LIVE_ACK=I_UNDERSTAND` required
- ✅ **Risk Management**: Configurable limits and order types
- ✅ **Kill Switch**: Emergency stop mechanism
- ✅ **Windows-First**: PowerShell scripts optimized for Windows

---

## Prerequisites

### Before Starting

- [ ] ⚠️ **Revoke Compromised Keys**: If you accidentally shared API keys, revoke them IMMEDIATELY on Binance
- [ ] ✅ **Create New Keys**: Generate new API keys on Binance with correct permissions
- [ ] ✅ **Enable 2FA**: Two-factor authentication must be enabled on your Binance account
- [ ] ✅ **Test Capital**: Only use money you can afford to lose
- [ ] ✅ **Testing Complete**: Have thoroughly tested with DRY_RUN and testnet

### Binance API Key Setup

1. Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Create new API key with these settings:
   - **✅ Enable Reading** (required)
   - **✅ Enable Spot & Margin Trading** (required for live trading)
   - **❌ NEVER enable Withdrawals** (security risk!)
3. **Set IP Restrictions**: Add your IP address (highly recommended)
4. **Save API Key and Secret**: You'll need these for the setup wizard

### System Requirements

- **Windows 10/11** (or Linux/macOS with keyring support)
- **Python 3.8+**
- **PowerShell 5.1+** (Windows) or **Bash** (Linux/macOS)
- **Internet Connection** (for Binance API access)

---

## Security Model

### How Secrets Are Stored

```
Windows Credential Manager (Windows)
or Keychain (macOS) or Secret Service (Linux)
└── Service: "ai.traiding"
    ├── binance_api_key: [YOUR_API_KEY]
    └── binance_api_secret: [YOUR_SECRET]
```

**NOT stored in:**
- ❌ `.env` files
- ❌ `config/` files
- ❌ Git repository
- ❌ Log files
- ❌ Command history

### Security Principles

1. **Secrets in Memory Only**: API keys loaded from Credential Manager at runtime
2. **No Disk Persistence**: Keys never written to disk
3. **Explicit Acknowledgement**: `LIVE_ACK=I_UNDERSTAND` prevents accidental live trading
4. **Preflight Validation**: Automatic checks before trading starts
5. **Kill Switch**: Emergency stop with `KILL_SWITCH=true`

---

## Step-by-Step Setup

### Step 1: Run Setup Wizard

**Windows PowerShell:**
```powershell
.\scripts\setup_live.ps1
```

**Linux/macOS:**
```bash
./scripts/setup_live.sh
```

**VS Code:**
```
Ctrl+Shift+P → "Tasks: Run Task" → "Live: Setup"
```

### Step 2: Enter API Credentials

The wizard will prompt for:

1. **BINANCE_API_KEY**: Your Binance API key (visible)
2. **BINANCE_API_SECRET**: Your API secret (hidden input)

**Example:**
```
📝 Enter your Binance API credentials
   (Keys will be stored securely and never displayed)

BINANCE_API_KEY: pk_test_51ABC...xyz789
BINANCE_API_SECRET (hidden): ********
```

### Step 3: Automatic Strategy Selection (Optional)

The wizard will offer to analyze all available strategies and recommend the best one:

```
🎯 Automatische Strategie-Auswahl
================================================================

Analysiere alle Strategien mittels Backtest...
Dies kann einige Minuten dauern.

Strategie-Auswahl durchführen? (j/n) [j]:
```

**What happens:**
- Runs backtest for all strategies with same historical data
- Analyzes ROI, Sharpe Ratio, Calmar Ratio, Max Drawdown, Win Rate
- Calculates weighted score for each strategy
- Recommends the best performing strategy

**You can:**
- ✅ Accept recommendation: Just press Enter
- ✅ Skip analysis: Enter `n` and select strategy manually
- ✅ Override recommendation: Enter different strategy name

**Available Strategies:**
- Golden Cross (50/200) - Long-term trend following
- MA Crossover (20/50) - Medium-term trend following
- RSI Mean Reversion - Oversold/overbought strategy
- EMA Crossover (9/21) - Fast EMA crossover
- Bollinger Bands - Volatility-based strategy

📖 **See [STRATEGY_SELECTION_GUIDE.md](STRATEGY_SELECTION_GUIDE.md) for detailed documentation**

### Step 4: Configure Risk Parameters

The wizard will prompt for risk management settings:

1. **Strategy**: Trading strategy to use (auto-selected or manual)
2. **Trading Pairs**: Which symbols to trade (default: `BTCUSDT`)
3. **Max Risk Per Trade**: Risk limit per trade (default: `0.005` = 0.5%)
4. **Daily Loss Limit**: Stop trading if this loss is reached (default: `0.01` = 1%)
5. **Max Open Exposure**: Total open positions limit (default: `0.05` = 5%)
6. **Order Types**: `LIMIT_ONLY` (safer) or `LIMIT_AND_MARKET` (faster)
7. **Max Slippage**: Reject orders with higher slippage (default: `0.003` = 0.3%)

**Example:**
```
📊 Configure Risk Management Parameters
   (Press Enter to accept defaults)

💡 Empfohlene Strategie: RSI Mean Reversion
Strategie [RSI Mean Reversion]:
Trading pairs [BTCUSDT]: 
Max risk per trade (0.005 = 0.5%) [0.005]: 
Daily loss limit (0.01 = 1%) [0.01]: 
Max open exposure (0.05 = 5%) [0.05]: 
Allowed order types:
  1. LIMIT_ONLY (safer, may miss fills)
  2. LIMIT_AND_MARKET (faster execution, more slippage)
Choose [1]: 1
Max slippage (0.003 = 0.3%) [0.003]: 
```

### Step 5: Review Configuration

After setup, review the generated `config/live_risk.yaml`:

```yaml
pairs: BTCUSDT
strategy: RSI Mean Reversion
max_risk_per_trade: 0.005
daily_loss_limit: 0.01
max_open_exposure: 0.05
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
max_drawdown_limit: 0.20
```

**Recommended Starter Settings:**
- **Pairs**: `BTCUSDT` (high liquidity, low spreads)
- **Order Types**: `LIMIT_ONLY` (safer, less slippage risk)
- **Risk Per Trade**: `0.005` or lower (0.5%)
- **Daily Loss**: `0.01` as circuit breaker (1%)
- **Drawdown Limit**: `0.20` (20%) - automatic stop on large losses

### Step 5: Start Live Trading

**Windows PowerShell:**
```powershell
# Set explicit acknowledgement
$env:LIVE_ACK = "I_UNDERSTAND"

# Start live trading
.\scripts\start_live_prod.ps1
```

**Linux/macOS:**
```bash
# Set explicit acknowledgement
export LIVE_ACK=I_UNDERSTAND

# Start live trading
./scripts/start_live_prod.sh
```

**VS Code:**
```powershell
# In PowerShell terminal:
$env:LIVE_ACK = "I_UNDERSTAND"

# Then run task:
Ctrl+Shift+P → "Tasks: Run Task" → "Live: Runner"
```

### Step 6: Monitor Trading

Open View Session dashboard in a separate terminal/tab:

**Windows:**
```powershell
.\venv\Scripts\python.exe -m streamlit run tools/view_session_app.py --server.port 8501
```

**Linux/macOS:**
```bash
./venv/bin/python -m streamlit run tools/view_session_app.py --server.port 8501
```

Visit: `http://localhost:8501`

---

## 🚨 Circuit Breaker (Drawdown-Limit)

### What is the Circuit Breaker?

The Circuit Breaker is an automatic safety mechanism that **stops trading immediately** when losses exceed a configured threshold. This prevents catastrophic losses during adverse market conditions or strategy failures.

### How it Works

1. **Tracks Equity Curve**: Monitors your account balance in real-time
2. **Calculates Drawdown**: Measures the percentage drop from the highest account value
3. **Triggers on Limit**: Stops all trading when drawdown exceeds `max_drawdown_limit`
4. **Logs Critical Event**: Records the event with detailed metrics
5. **Prevents New Orders**: No new trades will be executed after trigger

### Configuration

In `config/live_risk.yaml`:

```yaml
# Maximum drawdown limit (as decimal, e.g., 0.20 = 20%)
# Circuit breaker: Trading stops automatically if drawdown exceeds this limit
# Only active in production mode (not DRY_RUN)
max_drawdown_limit: 0.20
```

**Recommended Settings:**
- **Conservative**: `0.10` (10% max drawdown)
- **Moderate**: `0.20` (20% max drawdown) - **DEFAULT**
- **Aggressive**: `0.30` (30% max drawdown)

### Important Notes

⚠️ **Production Mode Only**: Circuit Breaker is **ONLY active** when `DRY_RUN=false`. This is by design to protect real money.

✅ **Automatic Shutdown**: When triggered, the trading bot will:
- Stop accepting new signals
- Log critical messages to console and log file
- Display final report with drawdown statistics
- Exit gracefully

### Example Log Output

When Circuit Breaker triggers:

```
======================================================================
🚨 CIRCUIT BREAKER AUSGELÖST! 🚨
======================================================================
Aktueller Drawdown: -22.50%
Drawdown-Limit: 20.00%
Initial Capital: $10,000.00
Current Capital: $7,750.00
Verlust: $-2,250.00
Trading wird SOFORT gestoppt!
======================================================================
```

### Testing Circuit Breaker

To test without risking money:

1. Set `DRY_RUN=false` temporarily in test environment
2. Use testnet API keys
3. Set low `max_drawdown_limit` (e.g., 0.05 = 5%)
4. Monitor logs for circuit breaker messages

---

## File Structure

### Files Created by Setup

```
ai.traiding/
├── config/
│   └── live_risk.yaml          # Risk management config (NO secrets)
├── scripts/
│   ├── setup_live.ps1          # PowerShell setup wrapper
│   ├── setup_live.py           # Python setup wizard
│   ├── setup_live.sh           # Bash setup wrapper
│   ├── live_preflight.py       # Preflight checks script
│   ├── start_live_prod.ps1     # PowerShell live runner
│   └── start_live_prod.sh      # Bash live runner
└── .gitignore                  # Excludes config/live_risk.yaml
```

### What's in .gitignore

```gitignore
# Live trading config (may contain personal risk settings)
config/live_risk.yaml
```

---

## Scripts Reference

### setup_live.ps1 / setup_live.sh

**Purpose**: Setup wizard wrapper

**What it does:**
1. Ensures venv exists
2. Installs required packages (keyring, pyyaml, python-dotenv, requests)
3. Runs `setup_live.py` (the actual wizard)

**Usage:**
```powershell
.\scripts\setup_live.ps1  # Windows
./scripts/setup_live.sh   # Linux/macOS
```

---

### setup_live.py

**Purpose**: Interactive setup wizard

**What it does:**
1. Prompts for Binance API credentials
2. Stores keys in Windows Credential Manager (via keyring)
3. Prompts for risk management parameters
4. Writes `config/live_risk.yaml` (no secrets)
5. Verifies credentials are retrievable

**Usage:**
```bash
# Usually called by setup_live.ps1/sh, but can be run directly:
./venv/bin/python scripts/setup_live.py
```

---

### live_preflight.py

**Purpose**: Preflight checks before live trading

**What it validates:**
1. **Environment Variables**: `LIVE_ACK`, `DRY_RUN`, `LIVE_TRADING`, `BINANCE_BASE_URL`
2. **Credentials**: API key and secret are present
3. **Time Sync**: Local time vs Binance server (max 1000ms drift)
4. **Exchange Info**: Trading pairs are valid and active with MIN_NOTIONAL details
5. **Account Balance**: Minimum balance requirements (10 USDT)
6. **Risk Configuration**: Validates `config/live_risk.yaml` settings
7. **Order Types**: Ensures configured order types are supported by exchange
8. **Kill Switch**: Reports KILL_SWITCH status (informational)

**Output Format:**
```
[OK] ✅ Message
[ERR] ❌ Error message
```

**Exit Codes:**
- `0`: All checks passed
- `1`: One or more checks failed

**Risk Configuration Validation:**

The script validates the following parameters from `config/live_risk.yaml`:
- `max_risk_per_trade`: Must be between 0 and 0.1 (10%)
- `daily_loss_limit`: Must be between 0 and 0.2 (20%)
- `max_open_exposure`: Must be between 0 and 1.0 (100%)
- `max_slippage`: Must be between 0 and 0.05 (5%)
- `allowed_order_types`: Must be `LIMIT_ONLY` or `LIMIT_AND_MARKET`

**Logging:**

Results are logged to `logs/preflight_checks.log` for audit trail.

**Usage:**
```bash
./venv/bin/python scripts/live_preflight.py
```

**Example Output:**
```
============================================================
🚀 Live Trading Preflight Checks
============================================================

📋 Trading pairs from config: BTCUSDT

🔍 Checking environment variables...
[OK] ✅ LIVE_ACK is set correctly
[OK] ✅ DRY_RUN is set to false
[OK] ✅ LIVE_TRADING is set to true
[OK] ✅ Production endpoint configured

🔑 Checking API credentials...
[OK] ✅ API credentials present (keys not displayed)

⏰ Checking time synchronization...
[OK] ✅ Time sync OK (drift: 234ms)

📊 Checking exchange information...
[OK] ✅ Symbol BTCUSDT validated (status: TRADING, min notional: 10.00 USDT)
[OK] ✅   Min quantity: 0.00001, Step size: 0.00001

💰 Checking account balance...
[OK] ✅ Account balance sufficient (USDT: 125.45)

⚙️  Checking risk configuration...
[OK] ✅ Risk config validated (pairs: BTCUSDT)
[OK] ✅   Max risk/trade: 0.50%, Daily loss limit: 1.00%
[OK] ✅   Max exposure: 5.00%, Order types: LIMIT_ONLY
[OK] ✅   Max slippage: 0.30%

📝 Checking order types support...
[OK] ✅ Symbol BTCUSDT supports LIMIT_ONLY

🛑 Checking kill switch status...
[OK] ✅ KILL_SWITCH is disabled - normal trading mode

============================================================
[OK] ✅ All preflight checks passed
============================================================

✅ Ready for live trading

⚠️  FINAL WARNINGS:
   - You are about to trade with REAL MONEY
   - Monitor your positions closely
   - Set up alerts for large losses
   - Have an emergency stop plan

🚀 Starting live trading runner...
```

---

### start_live_prod.ps1 / start_live_prod.sh

**Purpose**: Live trading production runner

**What it does:**
1. Checks `LIVE_ACK=I_UNDERSTAND`
2. Loads API keys from Windows Credential Manager
3. Sets production flags (`DRY_RUN=false`, `LIVE_TRADING=true`)
4. Runs preflight checks (aborts if failed)
5. Starts `automation/runner.py` with production flags

**Environment Variables:**
- **LIVE_ACK**: Must be `I_UNDERSTAND`
- **KILL_SWITCH**: Set to `true` to block orders (optional)

**Usage:**
```powershell
# Windows
$env:LIVE_ACK = "I_UNDERSTAND"
.\scripts\start_live_prod.ps1

# Linux/macOS
export LIVE_ACK=I_UNDERSTAND
./scripts/start_live_prod.sh
```

---

## Troubleshooting

### Error: "Credentials not found in Windows Credential Manager"

**Cause:** Setup wizard was not run or failed

**Solution:**
```powershell
# Re-run setup wizard
.\scripts\setup_live.ps1
```

---

### Error: "LIVE_ACK not set correctly"

**Cause:** Missing or incorrect acknowledgement

**Solution:**
```powershell
# Windows
$env:LIVE_ACK = "I_UNDERSTAND"

# Linux/macOS
export LIVE_ACK=I_UNDERSTAND
```

---

### Error: "Time drift too large: 1500ms (max 1000ms)"

**Cause:** System clock is out of sync

**Solution:**
```powershell
# Windows: Sync time
w32tm /resync

# Linux
sudo ntpdate pool.ntp.org

# macOS
sudo sntp -sS time.apple.com
```

---

### Error: "Authentication failed - check API keys"

**Cause:** Invalid API keys or IP restriction

**Solutions:**
1. **Check Keys**: Verify keys on Binance are correct
2. **IP Restriction**: Ensure your IP is whitelisted
3. **Key Permissions**: Ensure "Enable Reading" and "Enable Spot Trading" are checked
4. **Recreate Keys**: Generate new keys if needed

---

### Error: "USDT balance too low: 5.00 (minimum: 10)"

**Cause:** Insufficient balance

**Solution:**
```
Transfer at least 10 USDT to your Binance Spot account
```

---

### How to View/Delete Stored Keys

**View if keys exist (Windows PowerShell):**
```powershell
.\venv\Scripts\python.exe -c "import keyring; print('Key exists:', keyring.get_password('ai.traiding', 'binance_api_key') is not None)"
```

**Delete keys (Windows PowerShell):**
```powershell
.\venv\Scripts\python.exe -c "import keyring; keyring.delete_password('ai.traiding', 'binance_api_key'); keyring.delete_password('ai.traiding', 'binance_api_secret'); print('Keys deleted')"
```

**View in Credential Manager (Windows):**
```powershell
# Open Credential Manager
control keymgr.dll

# Look for "ai.traiding" entries
```

---

## FAQ

### Q: Are my API keys safe?

**A:** Yes, if you follow best practices:
- ✅ Keys stored in Windows Credential Manager (encrypted)
- ✅ Never written to disk
- ✅ Never printed in logs
- ❌ Don't share your API keys
- ❌ Don't enable withdrawal permissions
- ✅ Use IP restrictions

### Q: Can I use this on Linux/macOS?

**A:** Yes, the bash scripts use `keyring` which works with:
- **macOS**: Keychain
- **Linux**: Secret Service (GNOME Keyring, KWallet)

However, **Windows is the primary focus** and receives more testing.

### Q: What happens if I lose my keys?

**A:** Keys are stored in Windows Credential Manager. If you:
- Reinstall Windows → Keys are lost
- Delete user profile → Keys are lost

**Solution**: Re-run `setup_live.ps1` to re-enter your keys.

### Q: How do I change my API keys?

**A:** Re-run the setup wizard:
```powershell
.\scripts\setup_live.ps1
```
This will overwrite the existing keys.

### Q: What is the Kill Switch?

**A:** Emergency stop mechanism:
```powershell
$env:KILL_SWITCH = "true"
```
When enabled:
- Preflight checks pass
- No new orders are placed
- Open orders are cancelled (if implemented)

### Q: How do I know if live trading is active?

**A:** Check the console output:
```
Configuration:
  LIVE_ACK: I_UNDERSTAND
  DRY_RUN: false
  LIVE_TRADING: true
  BINANCE_BASE_URL: https://api.binance.com
```

Also monitor View Session dashboard at `http://localhost:8501`.

### Q: Can I test without real money?

**A:** Yes! Use the existing dry-run mode:
```powershell
# Use standard start script (not start_live_prod.ps1)
.\scripts\start_live.ps1
```
This uses `DRY_RUN=true` and testnet by default.

### Q: What if preflight checks fail?

**A:** Trading will NOT start. Fix the errors shown and try again. Common issues:
- Environment variables not set
- API keys invalid or missing
- Time out of sync
- Insufficient balance
- Invalid trading pairs
- Missing or invalid risk configuration (`config/live_risk.yaml`)
- Order types not supported by exchange
- Invalid risk parameter ranges (max_risk, daily_loss_limit, etc.)

---

## Emergency Procedures

### If You Suspect API Key Compromise

1. **Immediately**: Log into Binance and disable API keys
2. **Check Account**: Review recent trades and account activity
3. **Revoke Keys**: Delete compromised API keys
4. **Generate New**: Create new API keys with proper restrictions
5. **Re-run Setup**: `.\scripts\setup_live.ps1` with new keys
6. **Enable 2FA**: If not already enabled

### If Trading Goes Wrong

1. **Stop Runner**: Press `Ctrl+C` in the terminal
2. **Enable Kill Switch**: `$env:KILL_SWITCH = "true"`
3. **Cancel Orders**: Log into Binance and manually cancel open orders
4. **Review Logs**: Check `logs/trading_bot.log` for errors
5. **Adjust Risk**: Edit `config/live_risk.yaml` with lower limits

---

## Next Steps

After successful setup:

1. ✅ **Test with Minimum**: Start with minimal capital (50-100 USDT)
2. ✅ **Monitor Closely**: Watch first few trades in View Session
3. ✅ **Check Logs**: Review `logs/trading_bot.log` regularly
4. ✅ **Set Alerts**: Configure notifications for large losses
5. ✅ **Scale Gradually**: Increase capital only after consistent success

---

**Made with ❤️ for Windows | Secure by Default | DRY_RUN First**
