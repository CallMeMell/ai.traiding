# 🤖 Automated Workflow Guide - Trading Bot Preparation

## Überblick

Der **Automated Workflow** ist ein vollautomatisches System zur Vorbereitung des KI-Trading-Bots für den Echtgeld-Einsatz. Es implementiert einen strukturierten Workflow mit Zeitlimits, automatischer Fehlerkorrektur und Live-View-Session für maximale Transparenz und Sicherheit.

---

## ✨ Features

### 🎯 Automatisierte Tasks mit Zeitlimit
- **Task 1: Datenanalyse** (2 Stunden)
  - Marktdaten laden und validieren
  - Statistiken berechnen
  - Qualitätsprüfung durchführen
  
- **Task 2: Strategie-Optimierung** (2 Stunden)
  - Backtesting durchführen
  - Performance-Metriken berechnen
  - ROI und Sharpe Ratio validieren
  
- **Task 3: API-Vorbereitung** (1 Stunde)
  - API-Credentials prüfen
  - Verbindung testen
  - 24/7-Betrieb vorbereiten

### 🔄 Automatische Fehlerkorrektur
- Automatische Wiederholung bei Fehlern (bis zu 3 Versuche)
- Detaillierte Fehlerprotokollierung
- Intelligente Fehlerbehandlung

### 📊 Live-View-Session
- Echtzeit-Fortschrittsanzeige
- Alle Zwischenschritte visualisiert
- JSON-basierte Session-Speicherung
- Integration mit Web-Dashboard

### ⏱️ Fortschrittskontrolle
- Automatische Pausen nach jedem Task (max. 10 Minuten)
- Zeitlimit-Überwachung für jeden Task
- Automatische oder manuelle Fortsetzung

---

## 🚀 Schnellstart

### Installation

Stellen Sie sicher, dass alle Dependencies installiert sind:

```bash
pip install -r requirements.txt
```

### Einfacher Start

```bash
python automated_workflow.py
```

Der Workflow führt Sie durch alle Schritte mit klaren Anweisungen.

### Mit benutzerdefinierten Optionen

```bash
# Mit manueller Bestätigung zwischen Tasks
python automated_workflow.py --manual

# Mit benutzerdefinierter Session-ID
python automated_workflow.py --session-id my_workflow_2024
```

---

## 📖 Verwendung

### Workflow starten

```python
from automated_workflow import create_default_workflow

# Workflow erstellen
manager = create_default_workflow()

# Workflow ausführen (vollautomatisch)
success = manager.execute_workflow(auto_continue=True)

# Oder mit manueller Bestätigung
success = manager.execute_workflow(auto_continue=False)
```

### Custom Workflow erstellen

```python
from automated_workflow import WorkflowManager, WorkflowTask

# Manager erstellen
manager = WorkflowManager(session_id="custom_workflow")

# Custom Task definieren
def my_custom_task(logger, live_view):
    logger.info("Executing custom task...")
    live_view.add_update('progress', "Processing data...")
    
    # Your logic here
    result = {"status": "success", "data": {...}}
    
    return result

# Task hinzufügen
manager.add_task(WorkflowTask(
    name="Custom Task",
    description="My custom trading bot task",
    time_limit_hours=1.0,
    execute_func=my_custom_task,
    auto_retry=True,
    max_retries=2,
    pause_after_completion_minutes=5.0
))

# Workflow ausführen
manager.execute_workflow()
```

### Live-View-Session

```python
from automated_workflow import LiveViewSession

# Session erstellen
session = LiveViewSession("my_session")

# Updates hinzufügen
session.add_update('info', "Starting process...")
session.add_update('progress', "50% complete", {'step': 1, 'total': 2})
session.add_update('success', "Process completed!")

# Status abrufen
status = session.get_status()
print(status)
```

---

## 📊 Session Management

### Session Details anzeigen

```bash
# Session-Details anzeigen
python automated_workflow.py --view-session workflow_20241010_120000
```

### Session-Dateien

Alle Sessions werden gespeichert in:
```
data/workflow_sessions/
├── {session_id}.json              # Live-View-Session-Daten
└── {session_id}_summary.json      # Workflow-Zusammenfassung
```

### Session-Struktur

```json
{
  "session_id": "workflow_20241010_120000",
  "start_time": "2024-10-10T12:00:00",
  "end_time": "2024-10-10T15:30:00",
  "total_duration_minutes": 210,
  "total_tasks": 3,
  "successful_tasks": 3,
  "failed_tasks": 0,
  "results": [
    {
      "task_name": "Data Analysis",
      "status": "completed",
      "duration_seconds": 3600,
      "success": true,
      "data": {...}
    }
  ]
}
```

---

## 🔧 Konfiguration

### Task-Parameter anpassen

```python
from automated_workflow import WorkflowTask

task = WorkflowTask(
    name="My Task",
    description="Task description",
    time_limit_hours=2.0,           # Zeitlimit in Stunden
    execute_func=my_function,        # Ausführungsfunktion
    auto_retry=True,                 # Automatische Wiederholung bei Fehler
    max_retries=3,                   # Maximale Anzahl Wiederholungen
    pause_after_completion_minutes=10.0  # Pause nach Task (Minuten)
)
```

### Workflow-Manager-Optionen

```python
from automated_workflow import WorkflowManager

manager = WorkflowManager(
    session_id="my_workflow"  # Optional: Custom Session-ID
)

# Auto-Continue konfigurieren
manager.execute_workflow(
    auto_continue=True  # True = automatisch, False = manuelle Bestätigung
)
```

---

## 📈 Integration mit Dashboard

Der Automated Workflow integriert sich nahtlos mit dem Web-Dashboard:

### Dashboard starten

```bash
python dashboard.py --web
```

### Workflow-Status im Dashboard anzeigen

Die Live-View-Sessions sind automatisch im Dashboard sichtbar unter:
- **View Sessions** → Workflow-Sessions

### Programmatische Integration

```python
from dashboard import create_dashboard
from automated_workflow import create_default_workflow

# Dashboard erstellen
dashboard = create_dashboard()

# Workflow ausführen
manager = create_default_workflow()
success = manager.execute_workflow()

# Status im Dashboard aktualisieren
status = manager.get_workflow_status()
dashboard.add_metric('workflow_status', status)
```

---

## 🛡️ Sicherheit und Best Practices

### API-Credentials

⚠️ **WICHTIG**: Speichern Sie API-Keys niemals im Code!

Verwenden Sie Umgebungsvariablen:

```bash
# .env oder keys.env
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET_API_KEY=your_testnet_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret
```

### Testnet zuerst!

Testen Sie immer zuerst im Testnet:

```python
from config import config

# Stellen Sie sicher, dass Testnet-Keys konfiguriert sind
assert config.BINANCE_TESTNET_API_KEY, "Testnet API key required"
assert config.BINANCE_TESTNET_SECRET_KEY, "Testnet secret key required"
```

### Monitoring

Überwachen Sie den Workflow:

```bash
# Log-Datei überwachen
tail -f logs/workflow_{session_id}.log

# Session-Status prüfen
python automated_workflow.py --view-session {session_id}
```

---

## 🧪 Testing

### Unit Tests

```bash
# Alle Tests ausführen
python -m pytest test_automated_workflow.py -v

# Spezifische Tests
python -m pytest test_automated_workflow.py::test_workflow_execution -v
```

### Integration Tests

```python
from automated_workflow import create_default_workflow

# Test-Workflow erstellen
manager = create_default_workflow()

# Workflow ausführen (mit kurzen Zeitlimits für Tests)
success = manager.execute_workflow(auto_continue=True)

assert success, "Workflow should complete successfully"
assert len(manager.results) == 3, "All tasks should execute"
```

---

## 📋 Workflow-Schritte im Detail

### Task 1: Datenanalyse (2 Stunden)

**Ziel**: Marktdaten analysieren und validieren

**Schritte**:
1. Marktdaten laden (CSV oder generieren)
2. Datenqualität validieren
3. Marktstatistiken berechnen
4. Selbstprüfung durchführen

**Output**:
```json
{
  "total_candles": 5000,
  "date_range": "2023-01-01 to 2024-10-10",
  "avg_price": 45000.50,
  "volatility": 0.65,
  "data_quality": "good"
}
```

### Task 2: Strategie-Optimierung (2 Stunden)

**Ziel**: Trading-Strategie optimieren und testen

**Schritte**:
1. Daten für Backtesting laden
2. Strategie initialisieren
3. Backtest durchführen
4. Performance validieren

**Output**:
```json
{
  "roi": 15.5,
  "sharpe_ratio": 1.8,
  "max_drawdown": -8.2,
  "total_trades": 150,
  "win_rate": 62.5
}
```

**Validierung**:
- Minimum ROI: 5%
- Minimum Sharpe Ratio: 1.0
- Maximum Drawdown: < 20%

### Task 3: API-Vorbereitung (1 Stunde)

**Ziel**: Broker-API für Echtgeld vorbereiten

**Schritte**:
1. API-Credentials prüfen
2. Sicherheit validieren
3. Verbindung testen
4. 24/7-Betrieb vorbereiten

**Output**:
```json
{
  "api_status": {
    "binance_configured": true,
    "binance_testnet_configured": true
  },
  "connection_test": {
    "status": "success",
    "message": "Testnet connection successful"
  },
  "operational_status": {
    "logging_configured": true,
    "error_handling_active": true,
    "monitoring_enabled": true,
    "auto_restart_ready": true
  }
}
```

---

## 🔍 Troubleshooting

### Problem: Workflow schlägt fehl

**Lösung**:
1. Log-Datei prüfen: `logs/workflow_{session_id}.log`
2. Session-Details anzeigen: `python automated_workflow.py --view-session {session_id}`
3. Fehler beheben und erneut starten

### Problem: Task überschreitet Zeitlimit

**Lösung**:
1. Zeitlimit erhöhen in `WorkflowTask`
2. Task-Funktion optimieren
3. Datenvolumen reduzieren

### Problem: API-Verbindung schlägt fehl

**Lösung**:
1. API-Credentials prüfen (`.env`, `keys.env`)
2. Testnet-Keys verwenden für Tests
3. Netzwerkverbindung prüfen

### Problem: Unvollständige Daten

**Lösung**:
1. Daten neu generieren: `python utils.py --generate-data`
2. Externe Datenquelle verwenden
3. Datenvalidierung anpassen

---

## 📚 Erweiterte Features

### Custom Task-Functions

```python
def advanced_analysis_task(logger, live_view):
    """Custom task with advanced features"""
    
    # Progress tracking
    total_steps = 5
    for i in range(total_steps):
        logger.info(f"Step {i+1}/{total_steps}")
        live_view.update_task_status(
            "Advanced Analysis",
            f"Processing step {i+1}",
            (i+1) / total_steps * 100
        )
        
        # Your logic here
        time.sleep(1)
    
    return {"status": "success", "steps_completed": total_steps}
```

### Parallel Task Execution

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_workflow():
    """Execute multiple tasks in parallel"""
    
    manager = WorkflowManager()
    
    # Add tasks as usual
    # Note: Tasks will still execute sequentially by default
    # For true parallel execution, implement custom logic
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit tasks to executor
        futures = [executor.submit(task.execute_func, logger, live_view) 
                   for task in manager.tasks]
        
        # Wait for completion
        results = [f.result() for f in futures]
    
    return results
```

### Email Notifications

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(subject, message):
    """Send email notification on workflow completion"""
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'workflow@tradingbot.com'
    msg['To'] = 'admin@example.com'
    
    # Send email
    # (Configure SMTP settings)
    pass

# Use in workflow
manager = create_default_workflow()
success = manager.execute_workflow()

if success:
    send_notification(
        "Workflow Completed",
        f"Workflow {manager.session_id} completed successfully"
    )
```

---

## 🎯 Next Steps

Nach erfolgreichem Workflow-Abschluss:

1. **Review Results**: Session-Zusammenfassung prüfen
2. **Test in Testnet**: Bot im Testnet testen
3. **Monitor Performance**: Live-Monitoring aktivieren
4. **Start Live Trading**: Echtgeld-Trading starten (mit Vorsicht!)

### Weiterführende Dokumentation

- [Dashboard Guide](DASHBOARD_GUIDE.md) - Dashboard-Integration
- [Live Market Monitor Guide](LIVE_MARKET_MONITOR_GUIDE.md) - Live-Monitoring
- [Backtesting Guide](BACKTESTING_GUIDE.md) - Strategie-Testing
- [Broker API Guide](BROKER_API_GUIDE.md) - API-Integration

---

## 📞 Support

Bei Fragen oder Problemen:
- GitHub Issues: [ai.traiding/issues](https://github.com/CallMeMell/ai.traiding/issues)
- Dokumentation: Siehe README.md und weitere Guides

---

## 📝 Changelog

### Version 1.0.0 (2024-10-10)
- ✨ Initial release
- 🎯 Drei automatisierte Tasks (Datenanalyse, Strategie-Optimierung, API-Vorbereitung)
- 📊 Live-View-Session-Integration
- ⏱️ Zeitlimit-Management
- 🔄 Automatische Fehlerkorrektur
- 📈 Dashboard-Integration

---

## 🔒 Lizenz

Siehe LICENSE-Datei im Hauptverzeichnis.
