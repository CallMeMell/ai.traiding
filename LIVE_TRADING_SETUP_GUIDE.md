# 🚨 Live Trading Setup Guide

**Complete guide for setting up secure live trading with Windows Credential Manager**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Security Model](#security-model)
- [Step-by-Step Setup](#step-by-step-setup)
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

### Step 3: Configure Risk Parameters

The wizard will prompt for risk management settings:

1. **Trading Pairs**: Which symbols to trade (default: `BTCUSDT`)
2. **Max Risk Per Trade**: Risk limit per trade (default: `0.005` = 0.5%)
3. **Daily Loss Limit**: Stop trading if this loss is reached (default: `0.01` = 1%)
4. **Max Open Exposure**: Total open positions limit (default: `0.05` = 5%)
5. **Order Types**: `LIMIT_ONLY` (safer) or `LIMIT_AND_MARKET` (faster)
6. **Max Slippage**: Reject orders with higher slippage (default: `0.003` = 0.3%)

**Example:**
```
📊 Configure Risk Management Parameters
   (Press Enter to accept defaults)

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

### Step 4: Review Configuration

After setup, review the generated `config/live_risk.yaml`:

```yaml
pairs: BTCUSDT
max_risk_per_trade: 0.005
daily_loss_limit: 0.01
max_open_exposure: 0.05
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
```

**Recommended Starter Settings:**
- **Pairs**: `BTCUSDT` (high liquidity, low spreads)
- **Order Types**: `LIMIT_ONLY` (safer, less slippage risk)
- **Risk Per Trade**: `0.005` or lower (0.5%)
- **Daily Loss**: `0.01` as circuit breaker (1%)

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
4. **Exchange Info**: Trading pairs are valid and active
5. **Account Balance**: Minimum balance requirements (10 USDT)

**Output Format:**
```
[OK] ✅ Message
[ERR] ❌ Error message
```

**Exit Codes:**
- `0`: All checks passed
- `1`: One or more checks failed

**Usage:**
```bash
./venv/bin/python scripts/live_preflight.py
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
