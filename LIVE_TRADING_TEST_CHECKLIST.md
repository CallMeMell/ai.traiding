# ✅ Live Trading Test Checklist

**Quick Reference - Schnell-Checkliste für manuelle Tests**

Verwende diese Checkliste zusammen mit dem detaillierten [LIVE_TRADING_MANUAL_TEST_GUIDE.md](LIVE_TRADING_MANUAL_TEST_GUIDE.md).

---

## 🔑 1. API Keys Setup

- [ ] Alte/kompromittierte Keys auf Binance gelöscht
- [ ] Neue API Keys auf Binance erstellt
- [ ] Berechtigungen gesetzt:
  - [ ] ✅ Enable Reading
  - [ ] ✅ Enable Spot & Margin Trading
  - [ ] ❌ Enable Withdrawals (MUSS deaktiviert sein!)
- [ ] IP-Whitelist aktiviert (optional aber empfohlen)
- [ ] API Key & Secret kopiert (Secret nur einmal sichtbar!)
- [ ] Screenshot erstellt (Keys zensiert)

---

## 🔧 2. Setup-Assistent

- [ ] PowerShell geöffnet im Projektverzeichnis
- [ ] Setup-Assistent gestartet:
  ```powershell
  .\scripts\setup_live.ps1
  ```
  Oder via VS Code: `Ctrl+Shift+P` → "Tasks: Run Task" → "Live: Setup"
- [ ] API Key eingegeben
- [ ] API Secret eingegeben (wird als `***` angezeigt)
- [ ] Risk-Parameter konfiguriert:
  - [ ] Trading pairs: `BTCUSDT`
  - [ ] Max risk per trade: `0.001` (0.1%)
  - [ ] Order types: `1` (LIMIT_ONLY)
  - [ ] Andere: Defaults akzeptiert
- [ ] Erfolgsmeldungen gesehen:
  - [ ] ✅ Credentials stored securely
  - [ ] ✅ Credentials verified
  - [ ] ✅ Setup Complete
- [ ] Screenshot erstellt (keine Keys sichtbar!)

---

## 📄 3. Konfiguration prüfen

- [ ] `config/live_risk.yaml` existiert:
  ```powershell
  Get-Content config\live_risk.yaml
  ```
- [ ] Inhalt geprüft:
  - [ ] Nur Risk-Parameter vorhanden
  - [ ] KEINE API Keys
  - [ ] KEINE Secrets
- [ ] Screenshot erstellt

---

## 🔐 4. Credential Manager prüfen

- [ ] Windows Credential Manager geöffnet:
  ```powershell
  control /name Microsoft.CredentialManager
  ```
- [ ] "Windows Credentials" ausgewählt
- [ ] Einträge gefunden:
  - [ ] `ai.traiding:binance_api_key`
  - [ ] `ai.traiding:binance_api_secret`
- [ ] Screenshot erstellt (NICHT auf "Show" klicken!)

---

## ✈️ 5. Preflight-Check

- [ ] `LIVE_ACK` gesetzt:
  ```powershell
  $env:LIVE_ACK = "I_UNDERSTAND"
  echo $env:LIVE_ACK  # Sollte "I_UNDERSTAND" ausgeben
  ```
- [ ] Preflight ausgeführt:
  ```powershell
  .\venv\Scripts\python.exe scripts\live_preflight.py
  ```
- [ ] Alle Checks erfolgreich:
  - [ ] [OK] ✅ LIVE_ACK is set correctly
  - [ ] [OK] ✅ DRY_RUN is set to false
  - [ ] [OK] ✅ LIVE_TRADING is set to true
  - [ ] [OK] ✅ Production endpoint configured
  - [ ] [OK] ✅ API credentials present
  - [ ] [OK] ✅ System time synchronized
  - [ ] [OK] ✅ Connected to exchange
  - [ ] [OK] ✅ Account balance sufficient
- [ ] Final Message: "✅ All preflight checks passed"
- [ ] Screenshot/Log erstellt (keine Keys!)

---

## 🛑 6. KILL_SWITCH Test

- [ ] KILL_SWITCH aktiviert:
  ```powershell
  $env:KILL_SWITCH = "true"
  echo $env:KILL_SWITCH  # Sollte "true" ausgeben
  ```
- [ ] Live-Runner gestartet:
  ```powershell
  .\scripts\start_live_prod.ps1
  ```
- [ ] Erwartetes Verhalten beobachtet:
  - [ ] 🛑 "KILL_SWITCH ENABLED" Warnung angezeigt
  - [ ] ✅ Preflight-Checks durchlaufen
  - [ ] ✅ Checks erfolgreich
  - [ ] 🛑 "KILL_SWITCH is enabled - not starting runner"
  - [ ] 🛑 Script endet OHNE `automation\runner.py` zu starten
- [ ] Screenshot/Log erstellt

---

## 📝 7. Probe-LIMIT-Order

⚠️ **ACHTUNG:** Dieser Schritt platziert eine **echte Order** auf Binance!

### Vorbereitung

- [ ] KILL_SWITCH deaktiviert:
  ```powershell
  Remove-Item Env:\KILL_SWITCH
  ```
- [ ] Test-Parameter festgelegt:
  - [ ] Symbol: `BTCUSDT`
  - [ ] Type: `LIMIT`
  - [ ] Preis: Weit vom Markt (z.B. $20,000 bei BTC ~$43,500)
  - [ ] Menge: Minimal (~0.00055 BTC = ~11 USDT notional)
- [ ] Binance Account hat ausreichend Balance (min. 20 USDT)

### Order platzieren

- [ ] Test-Order via Python-Script erstellt (siehe Guide)
- [ ] Order ausgeführt
- [ ] Response erhalten:
  - [ ] HTTP Status: 200
  - [ ] `"status": "NEW"`
  - [ ] `"orderId"` vorhanden
  - [ ] `"executedQty": "0.00000000"` (nicht gefüllt)
- [ ] Log/Response gespeichert

### Verifikation

- [ ] Binance Web-UI geöffnet:
  [Spot Open Orders](https://www.binance.com/en/my/orders/spot/open-orders)
- [ ] Order sichtbar in "Open Orders":
  - [ ] Symbol: BTCUSDT
  - [ ] Type: Limit
  - [ ] Price: ~20000
  - [ ] Amount: ~0.00055
  - [ ] Status: NEW
- [ ] Screenshot erstellt

### Clean-up

- [ ] Order storniert (via Web-UI oder API)
- [ ] Order in "Order History" verschoben
- [ ] Screenshot erstellt (stornierte Order)

---

## 📊 8. Dokumentation

### Screenshots gesammelt

- [ ] Binance API Key Settings (Keys zensiert)
- [ ] Setup-Assistent "Setup Complete"
- [ ] Windows Credential Manager (ai.traiding Einträge)
- [ ] Preflight-Check "All checks passed"
- [ ] KILL_SWITCH Test Output
- [ ] Order-Placement Response
- [ ] Binance Open Orders (Order sichtbar)
- [ ] Binance Order History (Order storniert)

### Log-Auszüge gesammelt

- [ ] Setup-Assistent Complete-Meldung
- [ ] Preflight "All preflight checks passed"
- [ ] KILL_SWITCH "not starting runner"
- [ ] Order Response JSON

### Sicherheitsprüfung

- [ ] KEINE API Keys in Screenshots
- [ ] KEINE Secrets in Logs
- [ ] KEINE Credentials sichtbar
- [ ] Alle sensiblen Daten zensiert

---

## ✅ Acceptance Criteria erfüllt

- [ ] Live-Trading Setup ist abgeschlossen
- [ ] Schlüssel und Risk-Config sind nur lokal (nicht in Git)
- [ ] Preflight-Check meldet OK
- [ ] KILL_SWITCH blockiert Orders (Runner startet nicht)
- [ ] Probe-LIMIT-Order wurde platziert und im Log angezeigt
- [ ] Order ist auf Binance sichtbar
- [ ] Alle Dokumentation (Screenshots, Logs) gesichert
- [ ] Keine Secrets wurden geleakt

---

## 🎯 Nächste Schritte

Nach erfolgreichem Abschluss aller Tests:

1. **Dokumentation einreichen:**
   - Screenshots in Issue posten (oder als Attachment)
   - Log-Auszüge als Code-Blocks einfügen
   - Bestätigung, dass alle Checks erfolgreich waren

2. **Issue als erledigt markieren:**
   - Alle Checkboxen im Original-Issue abhaken
   - "Proof/Nachweis" Sektion mit Screenshots füllen
   - Issue schließen oder zur Review stellen

3. **Optional: Weiterführende Tests:**
   - Test mit mehreren Trading-Pairs
   - Test mit verschiedenen Risk-Parametern
   - Test mit View Session Dashboard parallel
   - Test mit echtem (kleinem!) Trading-Zyklus

---

## 📖 Weiterführende Dokumentation

- **Detaillierte Anleitung:** [LIVE_TRADING_MANUAL_TEST_GUIDE.md](LIVE_TRADING_MANUAL_TEST_GUIDE.md)
- **Setup Guide:** [LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md)
- **Implementation Summary:** [SECURE_LIVE_TRADING_IMPLEMENTATION_SUMMARY.md](SECURE_LIVE_TRADING_IMPLEMENTATION_SUMMARY.md)
- **Original PR:** [#69](https://github.com/CallMeMell/ai.traiding/pull/69)

---

## ⚠️ Bei Problemen

Falls Fehler auftreten, siehe **Troubleshooting** Sektion in [LIVE_TRADING_MANUAL_TEST_GUIDE.md](LIVE_TRADING_MANUAL_TEST_GUIDE.md).

Häufige Probleme:
- Credentials not found → Setup nochmal ausführen
- Time sync error → `w32tm /resync`
- USDT balance too low → Min. 10 USDT auf Binance
- Authentication failed → API Keys / IP-Whitelist prüfen

---

**Status:** ⬜ Nicht gestartet | 🔄 In Arbeit | ✅ Abgeschlossen

**Viel Erfolg! 🚀**
