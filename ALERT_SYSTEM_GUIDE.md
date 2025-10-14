# 📱 Alert System Integration Guide

**Status**: ✅ **IMPLEMENTIERT**  
**Version**: 1.0.0  
**Datum**: 2025-10-14

---

## 📋 Überblick

Das Alert System ermöglicht Multi-Channel Benachrichtigungen für kritische Trading-Events über:
- ✅ **Telegram Bot** - Echtzeit Push-Benachrichtigungen
- ✅ **Email (SMTP)** - Detaillierte Reports mit HTML-Templates
- 🔄 **Discord** - Geplant für zukünftige Version

---

## 🚀 Quick Start

### 1. Telegram Bot einrichten

#### Schritt 1: Bot erstellen bei BotFather

```
1. Öffne Telegram und suche nach @BotFather
2. Sende /newbot
3. Gib einen Namen für deinen Bot ein (z.B. "My Trading Bot")
4. Gib einen Username ein (muss auf "bot" enden, z.B. "mytradingbot")
5. BotFather sendet dir deinen Bot Token
```

#### Schritt 2: Chat ID ermitteln

```
1. Starte einen Chat mit deinem Bot
2. Sende eine beliebige Nachricht
3. Öffne: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
4. Finde die "chat": {"id": 123456789} in der Antwort
5. Notiere die Chat ID
```

#### Schritt 3: Credentials in .env eintragen

```bash
# .env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
ENABLE_TELEGRAM_ALERTS=true
```

### 2. Email Alerts einrichten

#### Gmail SMTP

```bash
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Nicht dein Gmail Passwort!
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
ENABLE_EMAIL_ALERTS=true
```

**⚠️ Wichtig für Gmail:**
1. Aktiviere "2-Faktor-Authentifizierung" in deinem Google Account
2. Erstelle ein "App-Passwort" unter: https://myaccount.google.com/apppasswords
3. Verwende das App-Passwort, NICHT dein Gmail Passwort!

#### Andere SMTP-Provider

```bash
# Outlook/Office365
SMTP_HOST=smtp.office365.com
SMTP_PORT=587

# Yahoo
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587

# GMX
SMTP_HOST=mail.gmx.net
SMTP_PORT=587
```

---

## 📚 Verwendung

### In Python Code

```python
from alerts import AlertManager

# Initialisiere Alert Manager
alert_manager = AlertManager(
    enable_telegram=True,
    enable_email=True
)

# Trade Alert senden
alert_manager.send_trade_alert(
    order_type='BUY',
    symbol='BTC/USDT',
    price=50000.0,
    quantity=0.1,
    strategies=['RSI', 'EMA Crossover'],
    capital=10500.0
)

# Circuit Breaker Alert
alert_manager.send_circuit_breaker_alert(
    drawdown=-25.0,
    limit=20.0,
    capital=7500.0,
    initial_capital=10000.0
)

# Performance Update
alert_manager.send_performance_update(
    capital=10500.0,
    initial_capital=10000.0,
    total_trades=25,
    win_rate=65.0,
    profit_factor=1.8,
    sharpe_ratio=1.5
)

# Custom Nachricht
alert_manager.send_custom_message(
    message="Trading Bot gestartet!",
    subject="Bot Status",
    priority="high"
)
```

### Nur Telegram

```python
from alerts import TelegramAlert

telegram = TelegramAlert()

# Einfache Nachricht
telegram.send_message("Test Nachricht")

# Trade Alert
telegram.send_trade_alert(
    order_type='BUY',
    symbol='BTC/USDT',
    price=50000.0,
    quantity=0.1,
    strategies=['RSI'],
    capital=10000.0
)
```

### Nur Email

```python
from alerts import EmailAlert

email = EmailAlert()

# Einfache Email
email.send_email(
    subject="Test",
    body_text="Test Nachricht"
)

# Trade Alert Email
email.send_trade_alert(
    order_type='SELL',
    symbol='BTC/USDT',
    price=51000.0,
    quantity=0.1,
    strategies=['Bollinger Bands'],
    capital=11000.0,
    pnl=1000.0
)
```

---

## 🔧 Integration mit LiveTradingBot

Das Alert System ist bereits im `main.py` (LiveTradingBot) integriert!

### Automatische Alerts für:

1. **Trade Execution (BUY/SELL)**
   - Wird automatisch bei jedem Trade gesendet
   - Enthält: Preis, Menge, Strategien, Kapital

2. **Circuit Breaker**
   - Wird bei Drawdown-Limit Überschreitung gesendet
   - Enthält: Drawdown %, Verlust $, verbleibendes Kapital

3. **Performance Updates**
   - Kann manuell oder periodisch gesendet werden
   - Enthält: ROI, Win Rate, Profit Factor, Sharpe Ratio

### Aktivierung

```bash
# In .env setzen
ENABLE_TELEGRAM_ALERTS=true
ENABLE_EMAIL_ALERTS=true
```

Dann einfach den Bot starten:

```powershell
.\scripts\start_live.ps1
```

---

## 📊 Alert-Typen

### 1. Trade Alerts

**Telegram Format:**
```
📈 BUY Signal

Symbol: BTC/USDT
Preis: $50,000.00
Menge: 0.100000
Strategien: RSI, EMA Crossover
Kapital: $10,500.00

2025-10-14 19:45:00
```

**Email Format:**
- HTML Email mit Farb-Coding (Grün für BUY, Rot für SELL)
- Detaillierte Metrik-Tabelle
- Professional Design

### 2. Circuit Breaker Alerts

**Priorität:** 🔴 **HIGH** (keine Silent Notification)

```
🚨 CIRCUIT BREAKER AUSGELÖST!

⚠️ Trading wurde automatisch gestoppt!

Drawdown: -25.00% (Limit: 20.00%)
Verlust: $2,500.00 (25.00%)
Verbleibendes Kapital: $7,500.00
Start-Kapital: $10,000.00

Bitte System überprüfen!
```

### 3. Performance Updates

**Priorität:** 🟢 **NORMAL** (Silent Notification möglich)

```
📊 Performance Update

ROI: +5.00%
Kapital: $10,500.00 (Start: $10,000.00)
Trades: 25
Win Rate: 65.0%
Profit Factor: 1.80
Sharpe Ratio: 1.50
```

### 4. Error Alerts

```
❌ Fehler: API Connection Failed

Meldung: Unable to connect to Binance API

Kontext:
• Timestamp: 2025-10-14 19:45:00
• Symbol: BTC/USDT
• Retry Count: 3
```

---

## 🧪 Testing

### Test Telegram Alert

```python
python -c "from alerts import TelegramAlert; bot = TelegramAlert(); bot.send_message('Test!')"
```

### Test Email Alert

```python
python -c "from alerts import EmailAlert; email = EmailAlert(); email.send_email('Test', 'Test Body')"
```

### Test Alert Manager

```python
python -m alerts.alert_manager
```

### Run Tests

```powershell
python -m pytest test_alert_system.py -v
```

**Expected Output:**
```
test_alert_system.py::TestTelegramAlert::test_init_without_credentials PASSED
test_alert_system.py::TestTelegramAlert::test_send_message_success PASSED
test_alert_system.py::TestEmailAlert::test_send_email_success PASSED
test_alert_system.py::TestAlertManager::test_send_trade_alert PASSED

=================== 18 passed in 0.17s ===================
```

---

## 🔒 Sicherheit

### Best Practices

1. **Niemals Credentials committen**
   - `.env` ist in `.gitignore`
   - Nur `.env.example` als Template

2. **App-Passwörter verwenden**
   - Für Gmail: App-Passwort statt Hauptpasswort
   - Für andere Provider: API Keys wenn verfügbar

3. **Rate Limiting beachten**
   - Telegram: ~30 messages/second pro Bot
   - Email: Provider-abhängig (z.B. Gmail: 500/day)

4. **Sensitive Data in Nachrichten**
   - Keine API Keys in Alerts
   - Keine Passwörter
   - Nur öffentliche Trade-Daten

### Windows Credential Manager (Optional)

Für Production kannst du Credentials sicher in Windows Credential Manager speichern:

```powershell
# Credential speichern
cmdkey /generic:"TradingBot_Telegram" /user:"bot_token" /pass:"your_token"

# In Code laden (mit pywin32)
import win32cred
cred = win32cred.CredRead("TradingBot_Telegram", win32cred.CRED_TYPE_GENERIC)
bot_token = cred['CredentialBlob'].decode('utf-8')
```

---

## 📈 Monitoring & Statistiken

```python
# Hole Alert-Statistiken
stats = alert_manager.get_statistics()

print(stats)
# {
#     'total_alerts': 42,
#     'telegram_sent': 20,
#     'telegram_failed': 0,
#     'email_sent': 20,
#     'email_failed': 2
# }

# Prüfe ob Kanäle aktiv
if alert_manager.is_any_channel_active():
    print("✓ Mindestens ein Alert-Kanal aktiv")
```

---

## 🐛 Troubleshooting

### Telegram

**Problem:** Bot sendet keine Nachrichten

**Lösungen:**
1. Prüfe Bot Token und Chat ID
2. Starte Chat mit Bot (sende /start)
3. Prüfe Bot-Permissions in BotFather
4. Teste Verbindung: `curl "https://api.telegram.org/bot<TOKEN>/getMe"`

### Email

**Problem:** Email wird nicht gesendet

**Lösungen:**
1. Prüfe SMTP Credentials
2. Für Gmail: Verwende App-Passwort
3. Prüfe Firewall/Port-Blocking (587, 465)
4. Teste mit `telnet smtp.gmail.com 587`
5. Prüfe Spam-Ordner

**Problem:** "Authentication failed"

```
Lösung für Gmail:
1. Google Account → Sicherheit
2. 2-Faktor-Authentifizierung aktivieren
3. App-Passwörter → Neue App erstellen
4. Passwort in .env eintragen
```

---

## 🔄 Geplante Features

- [ ] Discord Webhook Integration
- [ ] SMS Alerts (via Twilio)
- [ ] Slack Integration
- [ ] WhatsApp Business API
- [ ] Alert Rules Engine (Custom Triggers)
- [ ] Alert Templates (User-definiert)
- [ ] Multi-Language Support

---

## 📚 Referenzen

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **SMTP RFC**: https://tools.ietf.org/html/rfc5321
- **Gmail SMTP**: https://support.google.com/mail/answer/7126229
- **Issue Reference**: ROADMAP.md M3.4, M5.4

---

## 💡 Beispiele

### Periodische Performance Updates

```python
import schedule
import time

def send_daily_report():
    alert_manager.send_performance_update(
        capital=bot.capital,
        initial_capital=bot.initial_capital,
        total_trades=len(bot.trade_logger.get_all_trades()),
        win_rate=calculate_win_rate(bot.trade_logger.get_all_trades()),
        profit_factor=calculate_profit_factor(bot.trade_logger.get_all_trades()),
        sharpe_ratio=calculate_sharpe_ratio(bot.equity_curve)
    )

# Täglich um 18:00
schedule.every().day.at("18:00").do(send_daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Conditional Alerts

```python
# Nur bei großen Gewinnen/Verlusten
if abs(pnl) > 500:
    alert_manager.send_trade_alert(
        order_type='SELL',
        symbol=symbol,
        price=price,
        quantity=quantity,
        strategies=strategies,
        capital=capital,
        pnl=pnl,
        channels=['telegram', 'email']  # Beide Kanäle
    )
else:
    # Kleine Trades nur per Telegram
    alert_manager.send_trade_alert(
        ...,
        channels=['telegram']  # Nur Telegram
    )
```

---

**Implementiert von**: GitHub Copilot  
**Datum**: 2025-10-14  
**Status**: ✅ PRODUCTION READY
