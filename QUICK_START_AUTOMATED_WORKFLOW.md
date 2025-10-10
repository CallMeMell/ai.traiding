# 🤖 Quick Start: Automated Workflow

## Schnellstart in 3 Schritten

### 1️⃣ Installation

```bash
# Dependencies installieren
pip install -r requirements.txt
```

### 2️⃣ Workflow starten

**Windows:**
```bash
start_automated_workflow.bat
```

**Linux/Mac:**
```bash
./start_automated_workflow.sh
```

**Oder direkt mit Python:**
```bash
python automated_workflow.py
```

### 3️⃣ Bestätigen und Ausführen

```
Type 'START' to begin: START
```

Der Workflow führt automatisch 3 Tasks aus:
1. ✅ **Datenanalyse** (2 Stunden)
2. ✅ **Strategie-Optimierung** (2 Stunden)
3. ✅ **API-Vorbereitung** (1 Stunde)

---

## 📊 Was passiert während des Workflows?

### Task 1: Datenanalyse
- Lädt oder generiert Marktdaten
- Validiert Datenqualität (OHLCV)
- Berechnet Statistiken (Volatilität, Durchschnittspreise)
- Führt Selbstprüfung durch

**Output:**
```
📋 TASK 1/3: Data Analysis
  Step 1/4: Loading market data...
  Step 2/4: Validating data quality...
  ✓ Data validation passed: 5000 candles
  Step 3/4: Calculating market statistics...
  Step 4/4: Running self-check...
  ✅ Task completed successfully in 1847.3s
```

### Task 2: Strategie-Optimierung
- Initialisiert Trading-Strategie
- Führt Backtest durch
- Berechnet Performance-Metriken
- Validiert Mindestanforderungen (ROI > 5%, Sharpe > 1.0)

**Output:**
```
📋 TASK 2/3: Strategy Optimization
  Step 1/4: Loading data for backtesting...
  Step 2/4: Initializing strategy...
  Step 3/4: Running backtest...
  Step 4/4: Validating performance...
  Performance: ROI: 12.5%, Sharpe: 1.8, Win Rate: 65%
  ✅ Task completed successfully in 2154.8s
```

### Task 3: API-Vorbereitung
- Prüft API-Credentials (Binance)
- Validiert Sicherheit
- Testet Verbindung (Testnet)
- Bereitet 24/7-Betrieb vor

**Output:**
```
📋 TASK 3/3: API Preparation
  Step 1/4: Checking API credentials...
  Step 2/4: Validating security...
  ✓ API keys loaded from environment files
  Step 3/4: Testing API connection...
  ✓ Binance testnet connection successful
  Step 4/4: Preparing for 24/7 operation...
  ✅ Task completed successfully in 543.2s
```

---

## 🔄 Automatische Features

### Fehlerkorrektur
- Automatische Wiederholung bei Fehlern (bis zu 3x)
- Detaillierte Fehlerprotokollierung
- Graceful Degradation

### Pausen zwischen Tasks
- 10 Minuten Pause nach jedem Task
- Automatische Fortsetzung (oder manuell mit `--manual`)
- Zeit für Qualitätskontrolle

### Live-View-Session
- Echtzeit-Fortschrittsanzeige
- JSON-basierte Persistierung
- Integration mit Web-Dashboard

---

## 📁 Workflow-Ergebnisse

Nach Abschluss finden Sie:

### Log-Datei
```
logs/workflow_{session_id}.log
```

### Session-Daten
```
data/workflow_sessions/{session_id}.json              # Live-View
data/workflow_sessions/{session_id}_summary.json      # Summary
```

### Session Details anzeigen
```bash
python automated_workflow.py --view-session workflow_20241010_120000
```

---

## 🎛️ Erweiterte Optionen

### Custom Session-ID
```bash
python automated_workflow.py --session-id my_workflow_2024
```

### Manuelle Bestätigung zwischen Tasks
```bash
python automated_workflow.py --manual
```

### Programmatische Verwendung
```python
from automated_workflow import create_default_workflow

manager = create_default_workflow()
success = manager.execute_workflow(auto_continue=True)

if success:
    print("✅ Bot bereit für Echtgeld-Trading!")
else:
    print("⚠️  Fehler im Workflow, bitte Logs prüfen")
```

---

## 🌐 Dashboard-Integration

### Workflow-Sessions im Dashboard anzeigen

1. Dashboard starten:
```bash
python dashboard.py --web
```

2. Browser öffnen: `http://localhost:5000`

3. API-Endpoints:
   - `GET /api/workflow-sessions` - Liste aller Sessions
   - `GET /api/workflow-sessions/<id>` - Session-Details

---

## 🧪 Demo ausführen

Interaktive Demo mit 4 Modi:

```bash
python demo_automated_workflow.py
```

**Demo-Optionen:**
1. Full Workflow Configuration
2. Live View Session Demo
3. Workflow Status Tracking
4. Simple Workflow Execution (läuft tatsächlich durch)

---

## 📚 Weitere Dokumentation

- **Vollständiger Guide**: [AUTOMATED_WORKFLOW_GUIDE.md](AUTOMATED_WORKFLOW_GUIDE.md)
- **Implementation Summary**: [AUTOMATED_WORKFLOW_IMPLEMENTATION_SUMMARY.md](AUTOMATED_WORKFLOW_IMPLEMENTATION_SUMMARY.md)
- **Tests**: `test_automated_workflow.py`

---

## ❓ Häufige Fragen

### Q: Wie lange dauert der Workflow?
**A:** Standard: ~5 Stunden (2h + 2h + 1h) plus Pausen. Kann aber schneller sein je nach Datenmenge.

### Q: Kann ich Tasks überspringen?
**A:** Derzeit nicht. Alle 3 Tasks sind für eine sichere Vorbereitung notwendig.

### Q: Was passiert bei einem Fehler?
**A:** Der Task wird automatisch bis zu 3x wiederholt. Bei weiterem Fehler wird der Workflow gestoppt.

### Q: Kann ich den Workflow anpassen?
**A:** Ja! Siehe [AUTOMATED_WORKFLOW_GUIDE.md](AUTOMATED_WORKFLOW_GUIDE.md) für Custom Tasks.

### Q: Ist mein Bot danach wirklich bereit für Echtgeld?
**A:** Der Workflow validiert die Grundlagen. Testen Sie IMMER zuerst im Testnet!

---

## ⚠️ Wichtiger Hinweis

**Testnet zuerst!** Verwenden Sie immer Testnet-Keys für Tests:

```env
# In .env oder keys.env
BINANCE_TESTNET_API_KEY=your_testnet_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret
```

Erst nach ausreichendem Testing im Testnet sollten Sie zu Echtgeld-Trading wechseln!

---

## 🎯 Nächste Schritte nach Workflow

1. ✅ Workflow-Ergebnisse prüfen
2. 🧪 Bot im Testnet testen
3. 📊 Performance überwachen
4. 💰 Mit kleinem Kapital starten
5. 📈 Schrittweise erhöhen

**Viel Erfolg beim Trading! 🚀**
