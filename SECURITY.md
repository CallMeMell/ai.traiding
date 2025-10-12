# 🔐 Security Policy

## Overview

The ai.traiding project is a professional trading bot that handles sensitive financial data and API credentials. This document outlines our security practices, vulnerability reporting procedures, and best practices for users.

## 🚨 Security Principles

### Core Security Guidelines

1. **API Key Protection**
   - Never commit API keys to version control
   - Use Windows Credential Manager (or system keychain) for secure storage
   - Never store keys in `.env` files for production
   - Disable withdrawal permissions on all API keys

2. **DRY_RUN Default**
   - All trading operations default to `DRY_RUN=true`
   - Real trading requires explicit acknowledgement (`LIVE_ACK=I_UNDERSTAND`)
   - Test thoroughly with testnet before live trading

3. **Minimal Permissions**
   - API keys should have minimal required permissions
   - ✅ Enable: Reading, Spot Trading
   - ❌ Disable: Withdrawals, Transfers, Futures (unless specifically needed)

4. **IP Whitelisting**
   - Configure IP restrictions on Binance API keys
   - Update IP whitelist when trading from new locations

5. **Emergency Stop**
   - `KILL_SWITCH=true` immediately blocks all live orders
   - Use the emergency stop feature if suspicious activity detected

## 🔒 Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| dev     | :white_check_mark: |
| < 1.0   | :x:                |

## 📢 Reporting a Vulnerability

### How to Report

If you discover a security vulnerability, please follow these steps:

1. **DO NOT** create a public GitHub issue
2. **DO NOT** disclose the vulnerability publicly
3. **DO** send a private report to: [Insert Contact Email/Method]

### What to Include

Your report should include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if available)
- Your contact information

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix Development**: Within 30 days (depending on severity)
- **Public Disclosure**: After fix is released

## 🛡️ Security Best Practices for Users

### Before Trading

- [ ] Review all code changes before deployment
- [ ] Test with `DRY_RUN=true` extensively
- [ ] Use Binance Testnet for paper trading
- [ ] Verify API key permissions
- [ ] Set up IP whitelisting
- [ ] Enable 2FA on exchange accounts
- [ ] Start with small capital amounts

### During Trading

- [ ] Monitor logs regularly (`logs/` directory)
- [ ] Check session data in View Session
- [ ] Set appropriate risk limits
- [ ] Keep software dependencies updated
- [ ] Use the preflight checks before live trading

### API Key Management

**Create New Keys:**
```powershell
# Windows: Run the setup wizard
.\scripts\setup_live.ps1

# This stores keys securely in Windows Credential Manager
```

**View Stored Keys:**
```powershell
.\scripts\view_secrets.ps1
```

**Delete Keys:**
```powershell
.\scripts\delete_secrets.ps1
```

### Emergency Procedures

**If Keys Are Compromised:**

1. **Immediately** revoke API keys on Binance
2. Set `KILL_SWITCH=true` in `.env`
3. Stop all running trading processes
4. Generate new API keys with updated IP restrictions
5. Run setup wizard again with new keys
6. Review recent trading activity for unauthorized trades

**If Unauthorized Trades Detected:**

1. Set `KILL_SWITCH=true` immediately
2. Close all open positions manually on exchange
3. Revoke API keys
4. Review logs for root cause
5. Contact exchange support if funds are at risk

## 🚫 Known Security Considerations

### Dependencies

- Regularly update Python dependencies: `pip install -r requirements.txt --upgrade`
- Monitor for security advisories in `python-dotenv`, `requests`, `pandas`, etc.
- Use virtual environments to isolate project dependencies

### Environment Variables

- Never commit `.env` files to Git (included in `.gitignore`)
- Use `.env.example` as template
- For live trading, prefer Windows Credential Manager over `.env`

### Logging

- Logs are stored in `logs/` directory (excluded from Git)
- Logs should never contain API keys or secrets
- Review logs for sensitive data before sharing

### Data Storage

- Session data stored in `data/session/` (excluded from Git)
- Trade history in `data/trades.csv` (excluded from Git)
- Backup sensitive data securely, never to public repositories

## 🔍 Security Audit Checklist

Before deploying to production:

- [ ] All API keys stored securely (not in files)
- [ ] `.gitignore` includes all sensitive files
- [ ] `DRY_RUN=true` by default
- [ ] IP whitelisting configured on API keys
- [ ] Withdrawal permissions disabled on API keys
- [ ] Emergency stop mechanism tested
- [ ] Preflight checks pass
- [ ] Logs reviewed for sensitive data
- [ ] Risk limits configured appropriately
- [ ] Monitoring and alerting set up

## 📚 Additional Resources

- [Live Trading Setup Guide](LIVE_TRADING_SETUP_GUIDE.md) - Complete security setup
- [Binance API Security](https://www.binance.com/en/support/faq/360002502072) - Official Binance documentation
- [README.md](README.md) - Project overview and features
- [PROGRESS.md](PROGRESS.md) - Current development status

## ⚖️ Disclaimer

**USE AT YOUR OWN RISK**

This software is provided "as is" without warranty of any kind. Trading cryptocurrencies and other financial instruments involves substantial risk of loss. 

- **No Financial Advice**: This software is not financial advice
- **Test Thoroughly**: Always test with paper trading first
- **Monitor Continuously**: Never leave automated trading unattended
- **Risk Capital Only**: Only trade with money you can afford to lose
- **No Guarantees**: Past performance does not guarantee future results

The developers and contributors of this project are not responsible for any financial losses incurred through the use of this software.

## 📝 Version History

| Date       | Version | Changes                          |
|------------|---------|----------------------------------|
| 2025-10-10 | 1.0     | Initial security policy created  |

---

**Last Updated**: 2025-10-10  
**Contact**: [GitHub Issues](https://github.com/CallMeMell/ai.traiding/issues) (for non-security issues)
