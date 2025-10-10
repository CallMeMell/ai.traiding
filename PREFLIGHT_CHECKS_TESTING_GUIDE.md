# 🧪 Preflight Checks Testing Guide

## Overview

This guide explains how to test the enhanced live trading preflight checks system.

## What's New

The preflight checks have been enhanced with:

1. **Risk Configuration Validation** - Validates `config/live_risk.yaml` parameters
2. **Order Types Support** - Ensures configured order types are supported by the exchange
3. **Kill Switch Detection** - Reports KILL_SWITCH status
4. **Enhanced MIN_NOTIONAL Display** - Shows detailed minimum notional and lot size info
5. **Automatic Logging** - Logs results to `logs/preflight_checks.log`
6. **Comprehensive Test Suite** - 20 automated tests covering all scenarios

## Running Tests

### Automated Tests

Run the comprehensive test suite:

```bash
# Windows
.\venv\Scripts\python.exe test_live_preflight.py

# Linux/macOS
./venv/bin/python test_live_preflight.py
```

**Test Coverage:**
- ✅ Environment variable validation (4 tests)
- ✅ Credentials validation (3 tests)
- ✅ Time synchronization (2 tests)
- ✅ Risk configuration (3 tests)
- ✅ Kill switch detection (3 tests)
- ✅ Order types support (2 tests)
- ✅ Exchange info validation (2 tests)
- ✅ Integration tests (1 test)

### Manual Testing

#### Test 1: Missing Configuration

Test behavior when `config/live_risk.yaml` is missing:

```powershell
# Remove config temporarily
Move-Item config\live_risk.yaml config\live_risk.yaml.backup

# Run preflight (should fail)
.\venv\Scripts\python.exe scripts\live_preflight.py

# Restore config
Move-Item config\live_risk.yaml.backup config\live_risk.yaml
```

**Expected:** Error message about missing risk configuration file.

#### Test 2: Invalid Risk Parameters

Test validation of risk parameters:

```yaml
# Create test config with invalid values
# config/live_risk.yaml
pairs: BTCUSDT
max_risk_per_trade: 0.15  # Too high (>10%)
daily_loss_limit: 0.01
max_open_exposure: 0.05
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
```

**Expected:** Error about `max_risk_per_trade` being out of range.

#### Test 3: Kill Switch Enabled

Test with kill switch enabled:

```powershell
$env:LIVE_ACK = "I_UNDERSTAND"
$env:DRY_RUN = "false"
$env:LIVE_TRADING = "true"
$env:KILL_SWITCH = "true"
$env:BINANCE_BASE_URL = "https://api.binance.com"
$env:BINANCE_API_KEY = "test_key_1234567890"
$env:BINANCE_API_SECRET = "test_secret_1234567890"

.\venv\Scripts\python.exe scripts\live_preflight.py
```

**Expected:** All checks pass, but KILL_SWITCH status is reported as enabled.

#### Test 4: Valid Configuration (Dry Run)

Test with all valid settings (without real API keys):

```powershell
$env:LIVE_ACK = "I_UNDERSTAND"
$env:DRY_RUN = "false"
$env:LIVE_TRADING = "true"
$env:BINANCE_BASE_URL = "https://api.binance.com"
$env:BINANCE_API_KEY = "test_key_1234567890"
$env:BINANCE_API_SECRET = "test_secret_1234567890"

.\venv\Scripts\python.exe scripts\live_preflight.py
```

**Expected:** 
- Environment checks pass ✅
- Credentials checks pass ✅
- Risk config checks pass ✅
- Kill switch check passes ✅
- Network checks fail (expected without real credentials) ❌

## Test Scenarios Covered

### Scenario 1: Missing LIVE_ACK

```powershell
# Don't set LIVE_ACK
.\venv\Scripts\python.exe scripts\live_preflight.py
```

**Result:** ❌ Preflight fails with "LIVE_ACK must be set to 'I_UNDERSTAND'"

### Scenario 2: DRY_RUN Still Enabled

```powershell
$env:LIVE_ACK = "I_UNDERSTAND"
$env:DRY_RUN = "true"  # Should be false
.\venv\Scripts\python.exe scripts\live_preflight.py
```

**Result:** ❌ Preflight fails with "DRY_RUN must be set to 'false' for live trading"

### Scenario 3: Invalid Order Types

Edit `config/live_risk.yaml`:
```yaml
allowed_order_types: INVALID_TYPE
```

**Result:** ❌ Preflight fails with validation error

### Scenario 4: Slippage Out of Range

Edit `config/live_risk.yaml`:
```yaml
max_slippage: 0.10  # 10% - too high
```

**Result:** ❌ Preflight fails with "max_slippage must be between 0 and 0.05 (5%)"

### Scenario 5: All Checks Pass

With valid configuration and environment:

**Result:** ✅ All checks pass, ready for live trading

## Logs

Check the log file for audit trail:

```powershell
Get-Content logs\preflight_checks.log -Tail 50
```

## Integration with VS Code

The preflight checks are automatically run when using the "Live: Runner" task:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Select "Tasks: Run Task"
3. Choose "Live: Runner"
4. Preflight checks run automatically before starting the runner

## Troubleshooting

### Common Issues

**Issue:** "Risk configuration file not found"
- **Solution:** Run `.\scripts\setup_live.ps1` to create the configuration

**Issue:** "Symbol not found on exchange"
- **Solution:** Check that trading pairs in config are valid Binance symbols

**Issue:** "Time drift too large"
- **Solution:** Synchronize your system clock

**Issue:** "Authentication failed - check API keys"
- **Solution:** Verify API keys in Windows Credential Manager

## Best Practices

1. **Always run preflight checks** before live trading
2. **Review logs** regularly to ensure all checks pass
3. **Test with KILL_SWITCH=true** first to verify setup
4. **Monitor the first few trades** closely after setup
5. **Keep risk parameters conservative** (especially when starting)

## Next Steps

After all tests pass:

1. Review LIVE_TRADING_SETUP_GUIDE.md
2. Configure risk parameters carefully
3. Test with KILL_SWITCH enabled first
4. Monitor closely when running live

---

**Last Updated:** 2025-10-10  
**Version:** 2.0 (Enhanced Preflight Checks)
