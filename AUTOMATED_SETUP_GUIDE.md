# 🚀 Vollautomatisierter Live Trading Setup Guide

**Vollständiger, sicherer und automatisierter Setup-Flow für Live Trading**

---

## 📋 Überblick

Der automatisierte Setup-Task führt den kompletten Setup-Prozess für Live Trading durch:

1. ✅ **Python-Umgebungsprüfung** - Validiert Python-Version und Dependencies
2. ✅ **API-Key-Abfrage** - Sichere, lokale Eingabe und Speicherung in Windows Credential Manager
3. ✅ **Risk-Konfiguration** - Automatische oder manuelle Risk-Parameter-Konfiguration
4. ✅ **Preflight-Checks** - Umfassende Systemprüfungen vor dem Trading
5. ✅ **Dry-Run-Test** - Automatischer Test-Lauf im Dry-Run-Modus
6. ✅ **Status-Reporting** - Detaillierte Logs und Zusammenfassung

**🔐 Sicherheit:** Keine API-Keys werden außerhalb des lokalen Systems gespeichert!

---

## 🎯 Quick Start

### Windows (Empfohlen)

**Interaktiver Modus (Erste Einrichtung):**
```powershell
.\scripts\automated_setup.ps1
```

**Automatischer Modus (mit Defaults):**
```powershell
.\scripts\automated_setup.ps1 -Auto
```

**Ohne Dry-Run-Test:**
```powershell
.\scripts\automated_setup.ps1 -SkipDryRun
```

### Linux/macOS

```bash
python3 scripts/automated_setup.py
```

**Mit Auto-Modus:**
```bash
python3 scripts/automated_setup.py --auto
```

---

## 🛠️ VS Code Integration

Der Setup ist als VS Code Task verfügbar:

1. **Ctrl+Shift+P** → "Tasks: Run Task"
2. Wähle **"Live: Automated Setup"**
3. Folge den Anweisungen

**Automatischer Modus (für Testing):**
- Task: **"Live: Automated Setup (Auto)"**

---

## 📝 Setup-Ablauf im Detail

### 1. Python-Umgebungsprüfung ✅

Der Setup prüft:
- Python-Version (min. 3.8)
- Virtual Environment (venv)
- Erforderliche Packages (keyring, pyyaml, python-dotenv, requests)

**Ausgabe:**
```
ℹ️ Checking Python environment...
✅ Python version: 3.10.0
✅ Virtual environment exists
✅ Package 'keyring' available
✅ Package 'yaml' available
✅ Package 'requests' available
```

### 2. API-Key-Abfrage 🔑

**Interaktiver Modus:**
- Eingabe von Binance API Key und Secret
- Sichere Speicherung in Windows Credential Manager
- Keine Keys werden in Logs oder Files gespeichert

**Auto-Modus:**
- Verwendet existierende Credentials aus Credential Manager
- Überspringt Eingabe-Prompt

**Ausgabe:**
```
ℹ️ Running API key setup...
📝 Enter your Binance API credentials
   (Keys will be stored securely and never displayed)

BINANCE_API_KEY: [EINGABE]
BINANCE_API_SECRET (hidden): [***]
✅ Credentials stored securely in Windows Credential Manager
✅ Credentials verified in Windows Credential Manager
✅ API keys stored and verified
```

### 3. Risk-Konfiguration ⚙️

**Interaktiver Modus:**
- Optionale automatische Strategie-Auswahl via Backtesting
- Eingabe von Risk-Management-Parametern
- Speicherung in `config/live_risk.yaml`

**Auto-Modus:**
- Verwendet sichere Default-Werte
- Führt Strategie-Auswahl automatisch durch

**Default Risk-Parameter:**
```yaml
pairs: BTCUSDT
strategy: Golden Cross (50/200)
max_risk_per_trade: 0.005  # 0.5%
daily_loss_limit: 0.01     # 1.0%
max_open_exposure: 0.05    # 5.0%
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003        # 0.3%
```

**Ausgabe:**
```
ℹ️ Configuring risk management...
🎯 Running strategy selection...
✅ Strategy selected: Golden Cross (50/200)
✅ Risk configuration complete
ℹ️   Pairs: BTCUSDT
ℹ️   Strategy: Golden Cross (50/200)
ℹ️   Max risk/trade: 0.50%
```

### 4. Preflight-Checks 🚀

Führt umfassende System-Checks durch:

1. **Environment Variables** - LIVE_ACK, DRY_RUN, LIVE_TRADING, BINANCE_BASE_URL
2. **API Credentials** - Keys vorhanden und valide
3. **Time Sync** - Zeitabweichung < 1000ms
4. **Exchange Info** - Trading-Pairs verfügbar und aktiv
5. **Account Balance** - Mindestguthaben vorhanden
6. **Risk Configuration** - Config-File valide
7. **Order Types** - Order-Types vom Exchange unterstützt
8. **Kill Switch** - Status-Check (informational)

**Ausgabe:**
```
ℹ️ Running preflight checks...
🚀 Live Trading Preflight Checks
🔍 Checking environment variables...
[OK] ✅ LIVE_ACK is set correctly
[OK] ✅ DRY_RUN is set to false
...
✅ Preflight checks passed
```

### 5. Dry-Run-Test 🧪

Führt einen kurzen Test-Lauf im Dry-Run-Modus durch:
- Startet Automation Runner im Testnet
- Läuft 10 Sekunden
- Validiert grundlegende Funktionalität

**Ausgabe:**
```
ℹ️ Running dry-run test...
ℹ️ Starting automation runner in dry-run mode (10 seconds)...
✅ Dry-run test completed
```

**Optional überspringen:**
```powershell
.\scripts\automated_setup.ps1 -SkipDryRun
```

### 6. Status-Reporting 📊

Generiert zwei Dateien:

**Detailliertes Log:**
- `logs/automated_setup_YYYYMMDD_HHMMSS.log`
- Vollständiger Log aller Schritte
- Timestamps für jeden Schritt

**Summary Report:**
- `logs/setup_summary.md`
- Zusammenfassung des Setup-Status
- Risk-Konfiguration
- Security-Checklist
- Next Steps

**Beispiel-Summary:**
```markdown
# 🚀 Live Trading Setup Summary
**Generated:** 2025-10-10 14:30:00
---

## ✅ Setup Status
**Success Rate:** 100% (6/6 steps)

**Completed Steps:**
- ✅ python_env
- ✅ api_keys
- ✅ risk_config
- ✅ preflight
- ✅ dry_run
- ✅ report

## ⚙️ Risk Configuration
- **Trading Pairs:** BTCUSDT
- **Strategy:** Golden Cross (50/200)
- **Max Risk per Trade:** 0.50%
- **Daily Loss Limit:** 1.00%
- **Max Open Exposure:** 5.00%
- **Order Types:** LIMIT_ONLY
- **Max Slippage:** 0.30%

## 🔐 Security Checklist
- [x] API keys stored in Windows Credential Manager
- [x] No secrets in config files
- [x] Risk parameters validated
- [x] Preflight checks configured
- [ ] IP restrictions enabled on API keys (manual)
- [ ] 2FA enabled on Binance account (manual)
- [ ] Withdrawal permissions disabled (manual)

## 📋 Next Steps
1. Review the risk configuration in `config/live_risk.yaml`
2. Set up IP restrictions on your Binance API keys
3. Verify 2FA is enabled on your Binance account
4. Set `LIVE_ACK=I_UNDERSTAND` in your environment
5. Run `scripts/start_live_prod.ps1` to start live trading
```

---

## 🔧 Kommandozeilen-Optionen

### PowerShell (Windows)

```powershell
# Vollständige Syntax
.\scripts\automated_setup.ps1 [-Auto] [-SkipDryRun] [-Help]

# Optionen:
#   -Auto          Automatischer Modus (Defaults, keine Prompts)
#   -SkipDryRun    Dry-Run-Test überspringen
#   -Help          Hilfe anzeigen
```

### Python (Cross-Platform)

```bash
# Vollständige Syntax
python scripts/automated_setup.py [--auto] [--skip-dry-run] [--help]

# Optionen:
#   --auto          Automatischer Modus
#   --skip-dry-run  Dry-Run-Test überspringen
#   --help          Hilfe anzeigen
```

---

## 📁 Dateien und Verzeichnisse

### Erstellt durch Setup:

```
ai.traiding/
├── venv/                           # Virtual Environment (falls nicht vorhanden)
├── config/
│   └── live_risk.yaml             # Risk-Konfiguration (KEINE SECRETS!)
├── logs/
│   ├── automated_setup_*.log      # Detaillierte Setup-Logs
│   ├── setup_summary.md           # Setup-Zusammenfassung
│   └── preflight_checks.log       # Preflight-Check-Logs
└── data/
    └── strategy_ranking.csv        # Strategie-Ranking (falls Auswahl durchgeführt)
```

### Windows Credential Manager:

```
Service: ai.traiding
Credentials:
├── binance_api_key      → [Ihr API Key]
└── binance_api_secret   → [Ihr API Secret]
```

**Zugriff:** Windows → Systemsteuerung → Credential Manager → Windows-Anmeldeinformationen

---

## ⚠️ Troubleshooting

### Problem: "Python is not installed"

**Lösung:**
1. Python 3.8+ installieren von https://www.python.org/
2. Während Installation: "Add Python to PATH" aktivieren
3. Terminal neu starten

### Problem: "Failed to install required packages"

**Lösung:**
```powershell
# Pip manuell upgraden
.\venv\Scripts\python.exe -m pip install --upgrade pip

# Packages einzeln installieren
.\venv\Scripts\python.exe -m pip install keyring pyyaml python-dotenv requests
```

### Problem: "Credentials not found in Credential Manager"

**Lösung:**
1. Setup erneut ausführen
2. API Keys erneut eingeben
3. Windows Credential Manager prüfen (siehe oben)

### Problem: "Preflight checks failed"

**Mögliche Ursachen:**
- LIVE_ACK nicht gesetzt → `$env:LIVE_ACK = "I_UNDERSTAND"`
- API Keys ungültig → Keys in Binance prüfen
- Zeitabweichung zu groß → Windows-Zeit synchronisieren
- Keine Internet-Verbindung → Netzwerk prüfen

**Lösung:**
```powershell
# Detaillierte Preflight-Logs ansehen
type logs\preflight_checks.log

# Preflight manuell ausführen
$env:LIVE_ACK = "I_UNDERSTAND"
$env:DRY_RUN = "true"
$env:LIVE_TRADING = "false"
.\venv\Scripts\python.exe scripts\live_preflight.py
```

### Problem: "Dry-run test failed"

**Lösung:**
- Dry-Run-Test ist optional
- Setup trotzdem erfolgreich abgeschlossen
- Bei Bedarf überspringen: `-SkipDryRun`

---

## 🔒 Sicherheitshinweise

### ✅ Sichere Praktiken:

1. **API-Keys nur lokal gespeichert**
   - Windows Credential Manager
   - Niemals in Git oder Cloud

2. **Minimale Permissions**
   - Nur TRADING-Permission aktivieren
   - KEINE Withdrawal-Permission

3. **IP-Restrictions**
   - IP-Whitelist in Binance aktivieren
   - Nur Ihre Trading-IP erlauben

4. **2FA aktiviert**
   - Zwei-Faktor-Authentifizierung pflicht
   - Google Authenticator oder ähnlich

5. **Minimales Kapital**
   - Mit kleinem Betrag starten
   - Erst nach erfolgreichen Tests erhöhen

### ❌ Zu vermeiden:

- ❌ API-Keys per E-Mail senden
- ❌ Keys in Screenshots teilen
- ❌ Keys in Code hardcoden
- ❌ Withdrawal-Permissions aktivieren
- ❌ Ohne IP-Restrictions handeln

---

## 📊 Nach dem Setup

### Live Trading starten:

```powershell
# 1. LIVE_ACK setzen (manuell!)
$env:LIVE_ACK = "I_UNDERSTAND"

# 2. Live Trading starten
.\scripts\start_live_prod.ps1
```

### View Session Dashboard:

```powershell
# Monitoring-Dashboard starten (paralleles Terminal)
.\venv\Scripts\python.exe -m streamlit run tools/view_session_app.py --server.port 8501
```

### Logs überwachen:

```powershell
# Setup-Logs
Get-Content logs\setup_summary.md

# Preflight-Logs
Get-Content logs\preflight_checks.log

# Trading-Logs
Get-Content logs\*.log -Tail 50 -Wait
```

---

## 🧪 Testing und CI/CD

### Automatischer Setup für Tests:

```powershell
# Vollautomatischer Setup mit Defaults
.\scripts\automated_setup.ps1 -Auto -SkipDryRun
```

### In CI/CD Pipeline:

```yaml
# GitHub Actions / Azure Pipelines
- name: Setup Live Trading Environment
  run: |
    python scripts/automated_setup.py --auto --skip-dry-run
  env:
    BINANCE_API_KEY: ${{ secrets.BINANCE_API_KEY }}
    BINANCE_API_SECRET: ${{ secrets.BINANCE_API_SECRET }}
```

---

## 📚 Weiterführende Dokumentation

- **[LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md)** - Manueller Setup-Prozess
- **[PREFLIGHT_AUTOMATION_SUMMARY.md](PREFLIGHT_AUTOMATION_SUMMARY.md)** - Preflight-Check-Details
- **[LIVE_TRADING_MANUAL_TEST_GUIDE.md](LIVE_TRADING_MANUAL_TEST_GUIDE.md)** - Manuelles Testing
- **[SECURE_LIVE_TRADING_IMPLEMENTATION_SUMMARY.md](SECURE_LIVE_TRADING_IMPLEMENTATION_SUMMARY.md)** - Sicherheits-Implementierung

---

## 🆘 Support

Bei Problemen:

1. **Logs prüfen:** `logs/automated_setup_*.log` und `logs/setup_summary.md`
2. **Tests ausführen:** `python test_automated_setup.py`
3. **GitHub Issue erstellen:** Mit Logs und Fehlerbeschreibung

---

**Made for Windows ⭐ | PowerShell-First | Secure by Design | Vollautomatisiert**
