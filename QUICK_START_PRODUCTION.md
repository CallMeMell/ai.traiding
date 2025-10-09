# 🚀 Quick Start: Production Features

## Overview

This guide shows you how to quickly get started with the new production-ready features: security enhancements, monitoring, and alerting.

---

## ⚡ 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `cryptography` - For API key encryption
- `requests` - For webhook alerts
- Plus all existing dependencies

### 2. Run Demo

```bash
python demo_production_features.py
```

This demonstrates:
- ✅ API key encryption/decryption
- ✅ Rate limiting
- ✅ Request validation
- ✅ Multi-channel alerts
- ✅ Integration example

### 3. Run Production Readiness Tests

```bash
python test_production_readiness.py
```

Expected output:
```
✅ ALL TESTS PASSED - System appears ready for production
```

---

## 🔒 Using Security Features

### Encrypt Your API Keys

```python
from security_manager import SecurityManager

# Initialize with your master password
security = SecurityManager(master_password="your-secure-password")

# Encrypt and store your real API keys
security.store_encrypted_keys({
    "BINANCE_API_KEY": "your_real_api_key",
    "BINANCE_SECRET_KEY": "your_real_secret_key"
}, filepath="config/encrypted_keys.json")

# Later, load when needed
keys = security.load_encrypted_keys("config/encrypted_keys.json")
```

**Important**: 
- Store `MASTER_PASSWORD` in environment variable
- Never commit encrypted_keys.json to git
- Keep master password secure

### Setup Rate Limiting

```python
# Create rate limiter for Binance API (1200 requests/minute)
api_limiter = security.create_rate_limiter(
    name="binance_api",
    max_calls=1200,
    time_window=60
)

# Before making API call
if api_limiter.is_allowed():
    # Make API call
    pass
else:
    # Wait or skip
    print("Rate limit exceeded")
```

---

## 🔔 Using Alert System

### Basic Setup

```python
from alert_system import AlertSystem, AlertType, AlertSeverity

# Initialize alert system (console + file logging by default)
alerts = AlertSystem()

# Send an alert
alerts.alert(
    AlertType.TRADE_EXECUTED,
    AlertSeverity.INFO,
    "Trade Executed",
    "BUY 0.1 BTC at $50,234.50"
)
```

### Configure Email Alerts

```python
# Add email notifications
alerts.configure_email({
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password',  # Use app password, not account password
    'to_address': 'alerts@yourdomain.com'
})
```

**Gmail Setup**:
1. Enable 2-factor authentication
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use app password in config

### Configure Slack/Discord Webhooks

```python
# Slack
alerts.configure_webhook(
    webhook_url='https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    webhook_type='slack'
)

# Discord
alerts.configure_webhook(
    webhook_url='https://discord.com/api/webhooks/YOUR/WEBHOOK/URL',
    webhook_type='discord'
)
```

**Get Webhook URLs**:
- **Slack**: https://api.slack.com/messaging/webhooks
- **Discord**: Server Settings → Integrations → Webhooks → New Webhook

---

## 🎯 Integration with Trading Bot

### Example: Enhanced main.py

```python
from config import config
from strategy import TradingStrategy
from security_manager import SecurityManager
from alert_system import AlertSystem, AlertType, AlertSeverity

# Initialize components
security = SecurityManager()
alerts = AlertSystem()
strategy = TradingStrategy(config.to_dict())

# Setup rate limiters
api_limiter = security.create_rate_limiter("api", 1200, 60)
order_limiter = security.create_rate_limiter("orders", 10, 60)

# Trading loop
while trading:
    # Check API rate limit
    if not api_limiter.is_allowed():
        alerts.alert(
            AlertType.SYSTEM_ERROR,
            AlertSeverity.WARNING,
            "API Rate Limit Reached",
            "Waiting before next API call"
        )
        time.sleep(1)
        continue
    
    # Get market data
    data = fetch_market_data()
    
    # Analyze with strategy
    signal = strategy.analyze(data)
    
    # Alert on trade signal
    if signal['signal'] != 0:
        alerts.alert(
            AlertType.TRADE_SIGNAL,
            AlertSeverity.INFO,
            f"{signal['signal_text']} Signal",
            f"Strategies: {signal['triggering_strategies']}"
        )
    
    # Execute trade (with rate limit check)
    if signal['signal'] != 0 and order_limiter.is_allowed():
        # Place order
        order = place_order(signal)
        
        # Alert on execution
        alerts.alert(
            AlertType.TRADE_EXECUTED,
            AlertSeverity.INFO,
            "Order Executed",
            f"{signal['signal_text']} order placed"
        )
```

---

## 📊 Monitoring Your System

### Check Alert History

```python
# Get recent alerts
recent_alerts = alerts.get_alert_history(limit=10)

for alert in recent_alerts:
    print(f"{alert.timestamp}: {alert.title}")
```

### View Alert Statistics

```python
stats = alerts.get_alert_stats()
print(f"Total alerts: {stats['total']}")
print(f"By type: {stats['by_type']}")
print(f"By severity: {stats['by_severity']}")
```

### Generate Security Report

```python
report = security.generate_security_report()
print(f"Encrypted keys: {report['encrypted_keys_count']}")
print(f"Rate limiters: {len(report['rate_limiters'])}")

for name, limiter_stats in report['rate_limiters'].items():
    print(f"{name}: {limiter_stats['current_calls']}/{limiter_stats['max_calls']}")
```

---

## 🛡️ Best Practices

### 1. Security
- ✅ Always encrypt API keys
- ✅ Use environment variables for master password
- ✅ Never commit keys or passwords to git
- ✅ Enable IP whitelist on exchange
- ✅ Disable withdrawal permissions on API keys

### 2. Rate Limiting
- ✅ Set appropriate limits for your exchange
- ✅ Monitor blocked request count
- ✅ Implement backoff on rate limit hits
- ✅ Different limiters for different resources

### 3. Alerts
- ✅ Start with console + file alerts
- ✅ Add email for critical alerts only
- ✅ Use webhooks for team notifications
- ✅ Review alert history regularly
- ✅ Adjust thresholds based on experience

### 4. Monitoring
- ✅ Check alerts daily
- ✅ Review security logs weekly
- ✅ Monitor rate limiter stats
- ✅ Keep alert history for analysis

---

## 🚨 Alert Types Reference

| Alert Type | When to Use | Suggested Severity |
|------------|-------------|-------------------|
| TRADE_SIGNAL | Strategy generates signal | INFO |
| TRADE_EXECUTED | Order executed | INFO |
| LOSS_THRESHOLD | Approaching loss limit | WARNING |
| PROFIT_TARGET | Target reached | INFO |
| SYSTEM_ERROR | System-level error | ERROR/CRITICAL |
| API_ERROR | API call failed | ERROR |
| CONNECTION_LOST | Lost connection | CRITICAL |
| DAILY_SUMMARY | End of day report | INFO |
| RISK_LIMIT | Risk threshold hit | WARNING/ERROR |
| PERFORMANCE_ALERT | Unusual performance | WARNING |

---

## 🔧 Configuration Templates

### Minimal (Development)

```python
# security_manager
security = SecurityManager()  # Uses default password

# alert_system  
alerts = AlertSystem()  # Console + file only
```

### Recommended (Production)

```python
# security_manager
security = SecurityManager(
    master_password=os.getenv("MASTER_PASSWORD")
)

# Rate limiters
api_limiter = security.create_rate_limiter("api", 1200, 60)
order_limiter = security.create_rate_limiter("orders", 10, 60)

# alert_system
alerts = AlertSystem()
alerts.configure_email({...})  # Email for critical alerts
alerts.configure_webhook(...)  # Webhook for all alerts
```

### Advanced (Enterprise)

```python
# Multiple rate limiters
security.create_rate_limiter("api_market_data", 1200, 60)
security.create_rate_limiter("api_orders", 50, 60)
security.create_rate_limiter("api_account", 20, 60)

# Custom alert callback
def send_to_monitoring_service(alert):
    # Send to your monitoring service
    monitoring_service.log_event(alert.to_dict())
    return True

alerts.add_callback(send_to_monitoring_service, "monitoring")
```

---

## 📝 Environment Variables

Create a `.env` file:

```bash
# Master password for encryption
MASTER_PASSWORD=your-secure-master-password-change-me

# Email alerts (optional)
ALERT_EMAIL_SMTP_SERVER=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_EMAIL_TO=alerts@yourdomain.com

# Webhook alerts (optional)
ALERT_SLACK_WEBHOOK=https://hooks.slack.com/services/...
ALERT_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

---

## 🧪 Testing Your Setup

### 1. Test Security Manager

```bash
python -c "from security_manager import SecurityManager; s = SecurityManager(); print('✓ Security OK')"
```

### 2. Test Alert System

```bash
python -c "from alert_system import AlertSystem; a = AlertSystem(); print('✓ Alerts OK')"
```

### 3. Run Full Test Suite

```bash
python test_production_readiness.py
```

### 4. Run Demo

```bash
python demo_production_features.py
```

---

## 🆘 Troubleshooting

### "No module named 'cryptography'"
```bash
pip install cryptography
```

### "No module named 'requests'"
```bash
pip install requests
```

### Email alerts not working
- Check SMTP server and port
- Use app password, not account password
- Enable "Less secure app access" (if required)
- Check firewall/network settings

### Webhook alerts not working
- Verify webhook URL is correct
- Check webhook service is enabled
- Test webhook manually with curl
- Check rate limits on webhook service

---

## 📚 Additional Resources

- **Full Guide**: [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
- **Summary**: [SYSTEM_OPTIMIZATION_SUMMARY.md](SYSTEM_OPTIMIZATION_SUMMARY.md)
- **Demo**: `python demo_production_features.py`
- **Tests**: `python test_production_readiness.py`

---

## ✅ Checklist Before Going Live

- [ ] All tests passing
- [ ] API keys encrypted
- [ ] Rate limiters configured
- [ ] Alert system setup
- [ ] Email/webhook configured (optional)
- [ ] Tested with demo script
- [ ] Read production deployment guide
- [ ] Completed 7-day testnet run
- [ ] Starting with minimal capital ($50-$100)
- [ ] Emergency procedures understood

---

**Remember**: Start small, monitor constantly, be prepared to stop!

**For detailed production deployment, see**: [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
