# 🔍 Pre-Live Checks - Automatisierte Validierung vor Live-Trading

## Übersicht

Die **Pre-Live Checks** sind automatisierte Validierungen, die **vor jedem Trading-Workflow** ausgeführt werden, um sicherzustellen, dass:

- ✅ Ausreichend Daten vorhanden und aktuell sind
- ✅ Strategien getestet und performant sind  
- ✅ API-Konnektivität funktioniert
- ✅ Keine kritischen Fehler vorliegen

**Bei kritischen Fehlern wird der Workflow automatisch abgebrochen** - so wird verhindert, dass Trading mit ungeprüften Konfigurationen startet.

---

## 🎯 Warum Pre-Live Checks?

**Problem ohne Checks:**
- Trading startet mit unvollständigen Daten
- Strategien wurden nicht ausreichend getestet
- API Keys fehlen oder sind ungültig
- Fehler werden erst während des Tradings erkannt

**Lösung mit Pre-Live Checks:**
- ✅ Frühzeitige Erkennung von Problemen
- ✅ Automatischer Abbruch bei kritischen Fehlern
- ✅ Strukturierte Fehlerberichte
- ✅ Klare Unterscheidung: Critical vs. Warning
- ✅ Sicherer Start nur bei bestandenen Checks

---

## 📋 Implementierte Checks

### 1. **Data Validation** 🗂️

**Geprüft wird:**
- ✅ Mindestanzahl Datensätze vorhanden (min. 100)
- ✅ Daten sind aktuell (max. 24h alt)
- ✅ Datenqualität ist ausreichend

**Beispiel-Output:**
```
🔍 Check 1: Data Validation
  ✅ Data records: 1000 (min: 100)
  ✅ Data freshness: 1h old (max: 24h)
```

**Bei Fehler:**
```
🔍 Check 1: Data Validation
  ❌ Insufficient data: 50 records (min: 100)
```

### 2. **Strategy Validation** 📊

**Geprüft wird:**
- ✅ Win-Rate über Minimum (min. 40%)
- ✅ Drawdown unter Maximum (max. 25%)
- ✅ Ausreichend Backtest-Trades (min. 20)

**Beispiel-Output:**
```
🔍 Check 2: Strategy Validation
  ✅ Strategy win rate: 55.0% (min: 40.0%)
  ✅ Strategy drawdown: 15.0% (max: 25.0%)
  ✅ Backtest trades: 50 (min: 20)
```

**Bei Fehler:**
```
🔍 Check 2: Strategy Validation
  ❌ Strategy win rate too low: 35.0% (min: 40.0%)
```

### 3. **API Connectivity** 🔌

**Geprüft wird:**
- ✅ API Keys vorhanden (nur in Production kritisch)
- ✅ Production Endpoint konfiguriert (nur in Live-Mode)
- ✅ Connectivity Check ausgeführt

**Beispiel-Output (DRY_RUN):**
```
🔍 Check 3: API Connectivity
  ⚠️  API keys missing (OK in DRY_RUN): binance_api_key, binance_api_secret
```

**Beispiel-Output (Production):**
```
🔍 Check 3: API Connectivity
  ✅ API keys present: 2
  ✅ Production endpoint configured
```

**Bei Fehler (Production):**
```
🔍 Check 3: API Connectivity
  ❌ API keys missing: binance_api_key, binance_api_secret
```

---

## 🚦 Status-Kategorien

### ✅ **Success**
- Alle Checks bestanden
- Workflow läuft normal weiter
- Keine Warnungen

### ⚠️ **Warning**
- Checks bestanden mit Warnungen
- Workflow läuft mit Vorsicht weiter
- Nicht-kritische Probleme erkannt

**Beispiele für Warnings:**
- Daten sind etwas alt (aber noch innerhalb Toleranz)
- Drawdown ist hoch (aber noch akzeptabel)
- API Keys fehlen in DRY_RUN Mode

### 🚨 **Critical**
- Kritische Fehler erkannt
- **Workflow wird ABGEBROCHEN**
- Fehler müssen behoben werden

**Beispiele für Critical:**
- Zu wenige Datensätze
- Win-Rate zu niedrig
- API Keys fehlen in Production Mode

---

## 📊 Workflow-Integration

### **Ablauf im AutomationRunner**

```
1. Session Start
2. ⚡ PRE-LIVE CHECKS ⚡
   ├─ Data Validation
   ├─ Strategy Validation
   └─ API Connectivity
   
   ✅ Success → Weiter zu Phase 1
   ⚠️  Warning → Warnung loggen, weiter zu Phase 1
   🚨 Critical → WORKFLOW ABGEBROCHEN
   
3. Phase 1: Data Phase
4. Phase 2: Strategy Phase  
5. Phase 3: API Phase
6. Session End
```

### **Bei kritischem Fehler:**

```
======================================================================
🚨 WORKFLOW ABORTED - CRITICAL PRE-LIVE CHECK FAILURES
======================================================================
Critical failures (2):
  1. Insufficient data: 50 records (min: 100)
  2. API keys missing: binance_api_key, binance_api_secret
======================================================================
❌ Fix these issues before starting live trading!
======================================================================
```

---

## 🔧 Konfiguration

### **Thresholds anpassen**

Die Check-Schwellwerte sind in den Check-Methoden definiert:

**Data Validation:**
```python
min_records_required = 100      # Min. Datensätze
max_age_hours = 24              # Max. Datenalter in Stunden
```

**Strategy Validation:**
```python
min_win_rate = 0.40             # Min. 40% Win-Rate
max_acceptable_drawdown = 0.25  # Max. 25% Drawdown
min_backtest_trades = 20        # Min. 20 Backtest-Trades
```

### **DRY_RUN vs. Production**

Pre-Live Checks berücksichtigen den Trading-Mode:

| Check | DRY_RUN | Production |
|-------|---------|------------|
| Data Validation | Critical | Critical |
| Strategy Validation | Critical | Critical |
| Missing API Keys | ⚠️ Warning | 🚨 Critical |
| Production Endpoint | - | 🚨 Critical |

---

## 📝 Event-Logging

Pre-Live Checks generieren strukturierte Events:

### **Events:**

1. **pre_live_check_start**
   - Markiert Start der Pre-Live Checks

2. **pre_live_check_complete**
   - Enthält Ergebnis aller Checks
   - Details: critical_failures, warnings, check results

3. **workflow_aborted** (bei Critical)
   - Markiert Workflow-Abbruch
   - Details: critical_failures

### **Beispiel Event (pre_live_check_complete):**

```json
{
  "timestamp": "2025-10-12T11:00:00.000000",
  "type": "pre_live_check_complete",
  "level": "info",
  "status": "success",
  "message": "Pre-live checks completed with status: success",
  "details": {
    "critical_failures": [],
    "warnings": ["API keys missing (OK in DRY_RUN)"],
    "checks": {
      "data_validation": {
        "status": "success",
        "message": "Data validation passed"
      },
      "strategy_validation": {
        "status": "success", 
        "message": "Strategy validation passed"
      },
      "api_connectivity": {
        "status": "warning",
        "message": "API keys missing (OK in DRY_RUN)"
      }
    }
  }
}
```

---

## 🧪 Testing

### **Unit-Tests ausführen:**

```powershell
# Windows (PowerShell)
.\venv\Scripts\python.exe test_pre_live_checks.py

# Linux/macOS
python3 test_pre_live_checks.py
```

### **Test-Coverage:**

```
✅ 15/15 Tests bestanden

Getestet:
- Einzelne Check-Funktionen
- Pre-Live Check Integration
- Workflow-Abbruch bei Critical Failures
- Workflow-Fortsetzung bei Warnings
- DRY_RUN vs. Production Mode
- Multiple Fehler gleichzeitig
- Exception Handling
- Event-Generierung
```

---

## 🔍 Debugging

### **Logs prüfen:**

Pre-Live Checks loggen ausführlich:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### **Check einzeln ausführen:**

```python
from automation.runner import AutomationRunner

runner = AutomationRunner()

# Einzelne Checks testen
data_result = runner._check_data_validation()
strategy_result = runner._check_strategy_validation()
api_result = runner._check_api_connectivity()

print(f"Data: {data_result}")
print(f"Strategy: {strategy_result}")
print(f"API: {api_result}")
```

### **Alle Checks ausführen:**

```python
from automation.runner import AutomationRunner

runner = AutomationRunner()
result = runner._run_pre_live_checks()

print(f"Status: {result['status']}")
print(f"Critical Failures: {result['critical_failures']}")
print(f"Warnings: {result['warnings']}")
```

---

## 🎯 Best Practices

### ✅ **Do's**

- **Immer Pre-Live Checks aktiviert lassen** (Standard-Verhalten)
- **Critical Failures sofort beheben** vor erneutem Start
- **Warnings ernst nehmen** und zeitnah beheben
- **Logs regelmäßig prüfen** auf Muster
- **Thresholds an deine Strategie anpassen**

### ❌ **Don'ts**

- **Nie Pre-Live Checks überspringen** für Live-Trading
- **Critical Failures nicht ignorieren**
- **Thresholds nicht zu niedrig setzen** (Sicherheit!)
- **Production Mode nicht ohne API Keys starten**

---

## 📚 Weitere Dokumentation

- **automation/runner.py** - Implementierung
- **test_pre_live_checks.py** - Unit-Tests
- **AUTOMATION_RUNNER_GUIDE.md** - Automation Runner Guide
- **scripts/live_preflight.py** - Existierende Preflight Checks

---

## 🚀 Beispiel: Vollständiger Workflow

```powershell
# 1. Environment vorbereiten
$env:DRY_RUN = "true"

# 2. Automation Runner starten
.\venv\Scripts\python.exe -m automation.runner

# Output:
# ======================================================================
# AUTOMATION RUNNER - REAL-MONEY READINESS WORKFLOW
# ======================================================================
# 
# ======================================================================
# PRE-LIVE CHECKS
# ======================================================================
# RUNNING PRE-LIVE CHECKS
# 
# 🔍 Check 1: Data Validation
#   ✅ Data records: 1000 (min: 100)
#   ✅ Data freshness: 1h old (max: 24h)
# 
# 🔍 Check 2: Strategy Validation
#   ✅ Strategy win rate: 55.0% (min: 40.0%)
#   ✅ Strategy drawdown: 15.0% (max: 25.0%)
#   ✅ Backtest trades: 50 (min: 20)
# 
# 🔍 Check 3: API Connectivity
#   ⚠️  API keys missing (OK in DRY_RUN): binance_api_key, binance_api_secret
# 
# ⚠️  PRE-LIVE CHECKS PASSED WITH WARNINGS: 1 warning(s)
# ======================================================================
# 
# --- Phase 1: Data Phase ---
# ...
```

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default | Safety First**
