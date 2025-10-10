# 🧪 Live Trading Manual Test Guide

**Manuelle Testanleitung für Live-Trading-Setup (Windows, Binance)**

Dieses Dokument beschreibt die vollständige manuelle Testprozedur für das Live-Trading-Setup mit Windows und Binance. Folgen Sie den Schritten der Reihe nach und dokumentieren Sie die Ergebnisse.

---

## ⚠️ Wichtige Sicherheitshinweise

- **NIEMALS** echte API-Keys in Screenshots oder Logs teilen
- **NUR** mit Kapital testen, das Sie verlieren können
- **IMMER** mit minimalen Beträgen starten
- **ZUERST** alte/kompromittierte API-Keys löschen
- **IP-Whitelist** für API-Keys aktivieren (empfohlen)

---

## 📋 Voraussetzungen

Vor dem Start sicherstellen:

- [ ] Windows 10/11 mit PowerShell
- [ ] Python 3.8+ installiert
- [ ] Git Repository geclont und PR #69 gemerged
- [ ] Binance-Account mit aktiviertem 2FA
- [ ] **KEINE** alten/kompromittierten API-Keys mehr aktiv

---

## 🔑 Schritt 1: Neue Binance API Keys erstellen

### 1.1 Alte Keys löschen (falls vorhanden)

1. Öffne [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Lösche alle alten/kompromittierten API Keys
3. Bestätige die Löschung per 2FA

### 1.2 Neue Keys erstellen

1. Klicke auf "Create API" → "System generated"
2. Gib einen Namen ein (z.B. "ai.traiding-live-test")
3. Bestätige per 2FA
4. **Kopiere API Key und Secret sofort** (Secret wird nur einmal angezeigt!)

### 1.3 Key-Berechtigungen konfigurieren

**Aktiviere:**
- ✅ **Enable Reading** (erforderlich)
- ✅ **Enable Spot & Margin Trading** (erforderlich für Live-Trading)

**Deaktiviere:**
- ❌ **Enable Withdrawals** (NIEMALS aktivieren!)
- ❌ **Enable Futures**
- ❌ **Enable Internal Transfer**

### 1.4 IP-Whitelist aktivieren (empfohlen)

1. Klicke auf "Edit restrictions"
2. Wähle "Restrict access to trusted IPs only"
3. Füge deine öffentliche IP hinzu ([What is my IP?](https://www.whatismyip.com/))
4. Speichere die Änderungen

### 1.5 Dokumentation

**Erstelle Screenshot:**
- ✅ API Key Management Seite (mit zensiertem Key)
- ✅ Berechtigungen sichtbar (Reading + Spot Trading)
- ✅ IP-Whitelist aktiviert (falls verwendet)
- ⚠️ **WICHTIG:** Secret NICHT im Screenshot zeigen!

---

## 🔧 Schritt 2: Setup-Assistent ausführen

### 2.1 PowerShell öffnen

1. Drücke `Win + X`
2. Wähle "Windows PowerShell" oder "Terminal"
3. Navigiere zum Projektverzeichnis:
   ```powershell
   cd C:\Pfad\zum\ai.traiding
   ```

### 2.2 VS Code Task "Live: Setup" ausführen

**Option A: Via VS Code Task (empfohlen)**
```
1. Öffne VS Code im Projektverzeichnis
2. Drücke Ctrl+Shift+P
3. Tippe "Tasks: Run Task"
4. Wähle "Live: Setup"
```

**Option B: Direkt via PowerShell**
```powershell
.\scripts\setup_live.ps1
```

### 2.3 API Keys eingeben

Der Setup-Assistent wird nach folgenden Informationen fragen:

```
🔐 Live Trading Setup Wizard
==========================================

⚠️  WARNING: Live trading involves REAL MONEY
   - Only use API keys with TRADING permissions
   - NEVER enable withdrawal permissions
   - Use IP restrictions on your API keys
   - Start with minimal capital you can afford to lose

This wizard will:
  1. Securely store API keys in Windows Credential Manager
  2. Configure risk management parameters
  3. Create config/live_risk.yaml (no secrets)

📝 Enter your Binance API credentials
   (Keys will be stored securely and never displayed)

BINANCE_API_KEY: [HIER_API_KEY_EINGEBEN]
BINANCE_API_SECRET (hidden): [HIER_SECRET_EINGEBEN - wird nicht angezeigt]
```

**Eingabe:**
1. Kopiere API Key aus Binance und füge ein
2. Kopiere API Secret aus Binance und füge ein (wird als `***` angezeigt)
3. Bestätige mit Enter

### 2.4 Risk-Parameter eingeben

Der Assistent fragt nach Risk-Management-Parametern:

```
📊 Configure Risk Management Parameters
   (Press Enter to accept defaults)

Trading pairs [BTCUSDT]: [Enter für Default oder z.B. BTCUSDT,ETHUSDT]
Max risk per trade (0.005 = 0.5%) [0.005]: [Enter für Default oder z.B. 0.001]
Daily loss limit (0.01 = 1%) [0.01]: [Enter für Default]
Max open exposure (0.05 = 5%) [0.05]: [Enter für Default oder z.B. 0.02]
Allowed order types:
  1. LIMIT_ONLY (safer, may miss fills)
  2. LIMIT_AND_MARKET (faster execution, more slippage)
Choose [1]: 1 [IMMER 1 wählen für Tests!]
Max slippage (0.003 = 0.3%) [0.003]: [Enter für Default]
```

**Empfohlene Eingaben für Tests:**
- Trading pairs: `BTCUSDT` (hohe Liquidität)
- Max risk per trade: `0.001` (0.1% - sehr konservativ)
- Order types: `1` (LIMIT_ONLY)
- Alles andere: Defaults verwenden

### 2.5 Setup-Bestätigung prüfen

Der Assistent sollte folgende Erfolgsmeldungen zeigen:

```
✅ Credentials stored securely in Windows Credential Manager
✅ Credentials verified in Windows Credential Manager
✅ Risk configuration written to config/live_risk.yaml

==========================================================
✅ Setup Complete!
==========================================================

Next steps:
  1. Review config/live_risk.yaml
  2. Set LIVE_ACK=I_UNDERSTAND in your environment
  3. Run: scripts/start_live_prod.ps1
```

### 2.6 Dokumentation

**Erstelle Screenshots:**
- ✅ Setup-Assistent Start (mit Warnings)
- ✅ "Credentials stored securely" Meldung
- ✅ "Setup Complete" Meldung
- ⚠️ **WICHTIG:** Keine API Keys sichtbar!

---

## 📄 Schritt 3: Config-Datei prüfen

### 3.1 Prüfe, ob `config/live_risk.yaml` erstellt wurde

```powershell
# Datei anzeigen
Get-Content config\live_risk.yaml
```

**Erwartete Ausgabe:**
```yaml
pairs: BTCUSDT
max_risk_per_trade: 0.001
daily_loss_limit: 0.01
max_open_exposure: 0.02
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
```

### 3.2 Sicherheitsprüfung

**Stelle sicher:**
- ❌ **KEINE** API Keys in der Datei
- ❌ **KEINE** Secrets in der Datei
- ✅ Nur Risk-Parameter vorhanden

### 3.3 Dokumentation

**Erstelle Screenshot:**
- ✅ Inhalt von `config/live_risk.yaml`
- ✅ Bestätige, dass keine Secrets vorhanden sind

---

## 🔐 Schritt 4: Windows Credential Manager prüfen

### 4.1 Credential Manager öffnen

```powershell
# Öffne Credential Manager
control /name Microsoft.CredentialManager
```

### 4.2 Credentials prüfen

1. Gehe zu "Windows Credentials" (Windows-Anmeldeinformationen)
2. Suche nach Einträgen mit "ai.traiding"
3. Sollte zwei Einträge zeigen:
   - `ai.traiding:binance_api_key`
   - `ai.traiding:binance_api_secret`

### 4.3 Dokumentation

**Erstelle Screenshot:**
- ✅ Windows Credential Manager mit ai.traiding Einträgen
- ⚠️ **WICHTIG:** Klicke NICHT auf "Show" für die Secrets!

---

## ✈️ Schritt 5: Preflight-Check ausführen

### 5.1 LIVE_ACK setzen

```powershell
# Setze Acknowledgement
$env:LIVE_ACK = "I_UNDERSTAND"

# Prüfe, ob gesetzt
echo $env:LIVE_ACK
# Sollte ausgeben: I_UNDERSTAND
```

### 5.2 Preflight-Check ausführen

```powershell
# Direkt via Python
.\venv\Scripts\python.exe scripts\live_preflight.py
```

### 5.3 Erwartete Ausgabe

Der Preflight-Check sollte folgende Prüfungen durchführen:

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
[OK] ✅ System time synchronized (offset: 123 ms)

🌐 Checking exchange connectivity...
[OK] ✅ Connected to exchange (BTCUSDT: $43,521.50)

💰 Checking account balance...
[OK] ✅ Account balance sufficient (USDT: 50.00)

============================================================
[OK] ✅ All preflight checks passed
============================================================

✅ Ready for live trading

⚠️  FINAL WARNINGS:
   - You are about to trade with REAL MONEY
   - Monitor your positions closely
   - Set up alerts for large losses
   - Have an emergency plan ready
```

### 5.4 Bei Fehlern

Falls Fehler auftreten, prüfe:

| Fehler | Lösung |
|--------|--------|
| `LIVE_ACK not set` | `$env:LIVE_ACK = "I_UNDERSTAND"` nochmal ausführen |
| `Credentials not found` | Setup-Assistent nochmal ausführen |
| `Time sync error` | Systemzeit prüfen und synchronisieren |
| `USDT balance too low` | Mindestens 10 USDT auf Binance Spot-Account |
| `Authentication failed` | API Keys prüfen, evtl. IP-Whitelist Problem |

### 5.5 Dokumentation

**Erstelle Screenshots/Log:**
- ✅ Komplette Preflight-Check Ausgabe
- ✅ Alle "OK" Meldungen sichtbar
- ✅ "All preflight checks passed" am Ende
- ⚠️ **WICHTIG:** Keine API Keys im Output!

---

## 🛑 Schritt 6: KILL_SWITCH Test

### 6.1 KILL_SWITCH aktivieren

```powershell
# Aktiviere Kill Switch
$env:KILL_SWITCH = "true"

# Prüfe, ob gesetzt
echo $env:KILL_SWITCH
# Sollte ausgeben: true
```

### 6.2 start_live_prod.ps1 mit KILL_SWITCH ausführen

```powershell
# Start mit aktivem KILL_SWITCH
.\scripts\start_live_prod.ps1
```

### 6.3 Erwartete Ausgabe

Das Script sollte:
1. ✅ Preflight-Checks durchführen
2. ✅ Checks erfolgreich bestehen
3. 🛑 Dann **STOPPEN** ohne Trading zu starten

```
==========================================
🚨 LIVE PRODUCTION TRADING
==========================================

⚠️  WARNING: This will trade with REAL MONEY

✅ LIVE_ACK acknowledged

🔐 Loading API keys from Windows Credential Manager...
✅ API keys loaded (keys not displayed)

Configuration:
  LIVE_ACK: I_UNDERSTAND
  DRY_RUN: false
  LIVE_TRADING: true
  BINANCE_BASE_URL: https://api.binance.com
  BROKER_NAME: binance

🛑 KILL_SWITCH ENABLED
   Preflight will pass but live orders will be blocked
   Open orders will be cancelled (if implemented)

🚀 Running preflight checks...

[... Preflight Checks laufen durch ...]

[OK] ✅ All preflight checks passed

🛑 KILL_SWITCH is enabled - not starting runner
   To disable: Remove or set KILL_SWITCH=false
```

**Wichtig:** Das Script sollte **HIER ENDEN** und NICHT `automation\runner.py` starten!

### 6.4 Dokumentation

**Erstelle Screenshots/Log:**
- ✅ KILL_SWITCH Aktivierung (`$env:KILL_SWITCH = "true"`)
- ✅ Start-Ausgabe mit "KILL_SWITCH ENABLED" Warnung
- ✅ Preflight Checks durchlaufen
- ✅ "KILL_SWITCH is enabled - not starting runner" Meldung
- ✅ Script endet OHNE Runner zu starten

---

## 📝 Schritt 7: Probe-LIMIT-Order Test

**⚠️ ACHTUNG:** Dies wird eine **echte Order** auf Binance platzieren!

### 7.1 KILL_SWITCH deaktivieren

```powershell
# Entferne KILL_SWITCH
$env:KILL_SWITCH = "false"
# ODER
Remove-Item Env:\KILL_SWITCH
```

### 7.2 Testparameter festlegen

Für sicheres Testen:
- **Symbol:** BTCUSDT (hohe Liquidität)
- **Order Type:** LIMIT
- **Preis:** Weit weg vom Marktpreis (z.B. 50% unter/über)
- **Menge:** Minimal-Notional (~11 USDT für BTCUSDT)

**Beispiel:** 
- Aktueller BTC-Preis: $43,500
- Test-Limit-Order: **$20,000** (weit unter Markt - wird nicht gefüllt)
- Menge: `0.00055 BTC` (= ~11 USDT notional)

### 7.3 Order platzieren

**Option A: Via start_live_prod.ps1 (nur wenn Runner echte Orders platziert)**

⚠️ **HINWEIS:** Dies startet den vollständigen Trading-Runner. Stelle sicher, dass deine Strategy nur Test-Orders platziert!

```powershell
# Stelle sicher, dass LIVE_ACK gesetzt ist
$env:LIVE_ACK = "I_UNDERSTAND"

# Starte Live Trading (ohne KILL_SWITCH)
.\scripts\start_live_prod.ps1
```

**Option B: Manuelle Test-Order via Python-Script**

Erstelle temporäres Test-Script `test_order.py`:

```python
import os
import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode

# Lade Keys aus Environment (werden von start_live_prod.ps1 gesetzt)
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
base_url = "https://api.binance.com"

# Test-Order Parameter
symbol = "BTCUSDT"
side = "BUY"
order_type = "LIMIT"
time_in_force = "GTC"
quantity = "0.00055"  # Minimal amount
price = "20000.00"    # Weit unter Markt - wird nicht gefüllt

# Erstelle signierte Order
timestamp = int(time.time() * 1000)
params = {
    "symbol": symbol,
    "side": side,
    "type": order_type,
    "timeInForce": time_in_force,
    "quantity": quantity,
    "price": price,
    "timestamp": timestamp,
    "recvWindow": 5000
}

query_string = urlencode(params)
signature = hmac.new(
    api_secret.encode('utf-8'),
    query_string.encode('utf-8'),
    hashlib.sha256
).hexdigest()

url = f"{base_url}/api/v3/order?{query_string}&signature={signature}"
headers = {"X-MBX-APIKEY": api_key}

print("Platziere Test-LIMIT-Order...")
print(f"Symbol: {symbol}")
print(f"Side: {side}")
print(f"Price: {price}")
print(f"Quantity: {quantity}")
print()

response = requests.post(url, headers=headers)
print("Response Status:", response.status_code)
print("Response Body:", response.json())
```

Ausführen:
```powershell
# Lade Keys in Environment
.\scripts\start_live_prod.ps1 # Strg+C nach Preflight
# ODER führe manuell aus:
.\venv\Scripts\python.exe test_order.py
```

### 7.4 Erwartete Ausgabe

Die Order sollte erfolgreich platziert werden:

```json
{
  "symbol": "BTCUSDT",
  "orderId": 123456789,
  "orderListId": -1,
  "clientOrderId": "abc123xyz",
  "transactTime": 1699999999999,
  "price": "20000.00000000",
  "origQty": "0.00055000",
  "executedQty": "0.00000000",
  "cummulativeQuoteQty": "0.00000000",
  "status": "NEW",
  "timeInForce": "GTC",
  "type": "LIMIT",
  "side": "BUY",
  "fills": []
}
```

**Wichtig:**
- ✅ `"status": "NEW"` - Order wurde akzeptiert
- ✅ `"executedQty": "0.00000000"` - Noch nicht gefüllt
- ✅ `orderId` vorhanden - Order ist auf Binance

### 7.5 Order auf Binance prüfen

1. Gehe zu [Binance Spot Orders](https://www.binance.com/en/my/orders/spot/open-orders)
2. Prüfe "Open Orders"
3. Du solltest die Test-Order sehen:
   - Symbol: BTCUSDT
   - Type: Limit
   - Price: 20000.00
   - Amount: 0.00055
   - Status: NEW

### 7.6 Order stornieren (Clean-up)

```powershell
# Storniere Order (ersetze ORDER_ID mit deiner orderId)
# Kann via Binance Web-UI oder API gemacht werden
```

Via Web-UI: Klicke auf "Cancel" bei der Order

### 7.7 Dokumentation

**Erstelle Screenshots/Log:**
- ✅ Order-Placement Log mit Response
- ✅ `orderId` und `status: NEW` sichtbar
- ✅ Screenshot von Binance Open Orders (Order sichtbar)
- ✅ Screenshot nach Stornierung (Order in "Order History")
- ⚠️ **WICHTIG:** Keine API Keys im Log!

---

## 📊 Schritt 8: Ergebnis-Zusammenfassung

### 8.1 Checkliste

Markiere alle abgeschlossenen Schritte:

- [ ] Neue Binance API Keys erstellt (keine Withdraw-Rechte, IP-Whitelist)
- [ ] Setup-Assistent erfolgreich ausgeführt
- [ ] API Keys in Windows Credential Manager gespeichert
- [ ] `config/live_risk.yaml` erstellt und geprüft
- [ ] Preflight-Check erfolgreich durchgelaufen
- [ ] KILL_SWITCH Test: Orders wurden blockiert
- [ ] Probe-LIMIT-Order platziert und im Log sichtbar
- [ ] Probe-Order auf Binance sichtbar
- [ ] Probe-Order storniert (Clean-up)
- [ ] Screenshots/Logs gesichert

### 8.2 Dokumentation sammeln

Stelle sicher, dass du folgende Dokumente hast:

1. **Screenshots:**
   - ✅ Binance API Key Settings (Keys zensiert)
   - ✅ Setup-Assistent Ausgabe
   - ✅ Windows Credential Manager (ai.traiding Einträge)
   - ✅ Preflight-Check OK-Ausgaben
   - ✅ KILL_SWITCH Test (Runner nicht gestartet)
   - ✅ Order-Placement Response
   - ✅ Binance Open Orders (Order sichtbar)

2. **Log-Auszüge:**
   - ✅ Setup-Assistent Complete-Meldung
   - ✅ Preflight-Check "All checks passed"
   - ✅ KILL_SWITCH "not starting runner"
   - ✅ Order Response JSON

3. **Sicherheitsprüfung:**
   - ⚠️ **KEINE** API Keys in Screenshots
   - ⚠️ **KEINE** Secrets in Logs
   - ⚠️ **KEINE** Credentials sichtbar

---

## 🔧 Troubleshooting

### Problem: "Python is not installed"

**Lösung:**
```powershell
# Python installieren
winget install Python.Python.3.11

# Oder manuell von python.org
```

### Problem: "Virtual environment not found"

**Lösung:**
```powershell
# Venv erstellen
python -m venv venv
```

### Problem: "Failed to load credentials from Credential Manager"

**Lösung:**
```powershell
# Setup nochmal ausführen
.\scripts\setup_live.ps1
```

### Problem: "USDT balance too low"

**Lösung:**
- Mindestens 10 USDT auf Binance Spot-Account übertragen
- Für Tests: 20-50 USDT empfohlen

### Problem: "Authentication failed (401)"

**Mögliche Ursachen:**
1. API Keys falsch eingegeben → Setup nochmal ausführen
2. IP-Whitelist aktiv, aber andere IP → IP in Binance aktualisieren
3. Keys wurden revoked → Neue Keys erstellen

### Problem: "Time sync error"

**Lösung:**
```powershell
# Windows Zeit synchronisieren
w32tm /resync

# Zeit-Service prüfen
w32tm /query /status
```

### Problem: "Order would trigger immediately"

**Erklärung:** Dein Limit-Preis ist zu nah am Marktpreis.

**Lösung:**
- Preis weiter vom Markt entfernen
- Für BUY: Viel niedriger (z.B. -50%)
- Für SELL: Viel höher (z.B. +50%)

---

## 📖 Referenzen

- **Setup Guide:** `LIVE_TRADING_SETUP_GUIDE.md`
- **Implementation Summary:** `SECURE_LIVE_TRADING_IMPLEMENTATION_SUMMARY.md`
- **Setup Script:** `scripts/setup_live.ps1`
- **Preflight Script:** `scripts/live_preflight.py`
- **Live Runner Script:** `scripts/start_live_prod.ps1`
- **PR:** [CallMeMell/ai.traiding#69](https://github.com/CallMeMell/ai.traiding/pull/69)

---

## ⚠️ Wichtige Erinnerungen

1. **Sicherheit geht vor:**
   - Keine API Keys teilen
   - Keine Screenshots mit Secrets
   - IP-Whitelist verwenden
   - 2FA immer aktiv

2. **Klein anfangen:**
   - Nur Testkapital verwenden
   - Minimale Order-Größen
   - LIMIT_ONLY Orders
   - Konservative Risk-Parameter

3. **Monitoring:**
   - View Session Dashboard laufen lassen
   - Binance Web-UI im Auge behalten
   - Logs regelmäßig prüfen
   - Alerts einrichten

4. **Emergency Plan:**
   - KILL_SWITCH Befehl kennen: `$env:KILL_SWITCH = "true"`
   - Binance Web-UI URL bookmarken
   - Mobile App für schnelle Reaktion
   - Support-Kontakte bereithalten

---

**Good Luck & Trade Safe! 🚀**
