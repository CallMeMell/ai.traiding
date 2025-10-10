# 📊 SLO Monitor Guide

**Service Level Objectives (SLO) Monitoring für Automation Workflows**

Der SLO Monitor überwacht Fehlerquoten und Render-Zeiten und erzeugt automatisch `needs-review` Events bei SLO-Verstößen.

---

## 🎯 Features

- ✅ **Error Rate Monitoring**: Überwacht Fehlerquoten gegen definierte Schwellenwerte
- ✅ **Render Time Monitoring**: Prüft API-Response-Zeiten (P95 < 500ms)
- ✅ **Needs-Review Events**: Automatische Event-Generierung bei SLO-Verstößen
- ✅ **Configurable Thresholds**: Anpassbare Schwellenwerte für Error-Rate und Render-Time
- ✅ **Integration mit SessionStore**: Events werden automatisch persistiert

---

## 🚀 Quick Start

### Installation

Keine zusätzliche Installation erforderlich - der SLO Monitor ist Teil des Automation-Moduls.

### Basis-Verwendung

```python
from automation.slo_monitor import SLOMonitor

# Monitor initialisieren
monitor = SLOMonitor()

# Error-Rate prüfen
monitor.check_error_rate()

# Render-Zeit prüfen
monitor.check_render_time()

# Schwellenwerte anpassen
monitor.error_rate_threshold = 0.05  # 5% Fehlerquote erlaubt
```

---

## 📖 Detaillierte Verwendung

### 1. Monitor Initialisierung

```python
from automation.slo_monitor import SLOMonitor
from core.session_store import SessionStore

# Mit Standard-Schwellenwerten
monitor = SLOMonitor()

# Mit benutzerdefinierten Schwellenwerten
monitor = SLOMonitor(
    error_rate_threshold=0.05,        # 5% Fehlerquote
    render_time_threshold_ms=1000.0,  # 1000ms Render-Zeit
    session_store=SessionStore()
)
```

### 2. Messungen hinzufügen

#### Error-Rate Messungen

```python
# Erfolgreiche Operation
monitor.add_error_measurement(success=True)

# Fehlerhafte Operation
monitor.add_error_measurement(success=False)

# Mit Zeitstempel
from datetime import datetime
monitor.add_error_measurement(success=True, timestamp=datetime.now())
```

#### Render-Time Messungen

```python
# Render-Zeit unter Schwellenwert
monitor.add_render_time_measurement(render_time_ms=300.0)

# Render-Zeit über Schwellenwert
monitor.add_render_time_measurement(render_time_ms=800.0)

# Mit Zeitstempel
monitor.add_render_time_measurement(
    render_time_ms=450.0,
    timestamp=datetime.now()
)
```

### 3. SLO Status prüfen

```python
# Error-Rate prüfen
error_status = monitor.check_error_rate()
print(f"Error Rate Status: {error_status['status']}")
print(f"Current: {error_status['current_percentage']:.2f}%")
print(f"Target: {error_status['target_percentage']}%")

# Render-Time prüfen
render_status = monitor.check_render_time()
print(f"Render Time Status: {render_status['status']}")

# Alle SLOs prüfen
all_status = monitor.get_all_status()
```

### 4. Schwellenwerte anpassen

```python
# Error-Rate Schwellenwert setzen (0.0 - 1.0)
monitor.error_rate_threshold = 0.05  # 5%

# Render-Time Schwellenwert setzen (in Millisekunden)
monitor.render_time_threshold_ms = 750.0  # 750ms
```

---

## 📊 SLO Definitionen

### Error Rate SLO

- **Name**: `error_rate`
- **Beschreibung**: Fehlerquote < 1%
- **Target**: 99.0% Erfolgsquote
- **Zeitfenster**: 7 Tage
- **Error Budget**: 1.0%

### Render Time SLO

- **Name**: `api_response_time` (auch als `render_time` referenziert)
- **Beschreibung**: API Response Time P95 < 500ms
- **Target**: 95.0% unter Schwellenwert
- **Zeitfenster**: 7 Tage
- **Error Budget**: 5.0%

---

## 🔔 Needs-Review Events

Bei SLO-Verstößen (Status `at_risk` oder `breached`) erzeugt der Monitor automatisch `needs-review` Events:

### Event-Struktur

```json
{
  "timestamp": "2024-01-15T10:30:00.000000",
  "type": "needs-review",
  "level": "warning",  // oder "error" bei BREACHED
  "message": "SLO error_rate is at_risk: 97.50% (target: 99.00%)",
  "details": {
    "slo_name": "error_rate",
    "status": "at_risk",
    "current_percentage": 97.5,
    "target_percentage": 99.0,
    "error_budget_remaining": 15.2,
    "threshold": 0.01,
    "total_measurements": 100,
    "failed_measurements": 3
  }
}
```

### Event-Levels

- **`warning`**: SLO Status = `at_risk` (Error Budget > 20%)
- **`error`**: SLO Status = `breached` (Error Budget ≤ 20%)

---

## 🔧 Integration in Automation Workflows

### Beispiel: Integration in Automation Runner

```python
from automation.runner import AutomationRunner
from automation.slo_monitor import SLOMonitor

# Monitor initialisieren
slo_monitor = SLOMonitor()

# Runner ausführen
runner = AutomationRunner()
try:
    result = runner.run()
    
    # Erfolg als Messung hinzufügen
    slo_monitor.add_error_measurement(success=True)
    
    # Render-Zeit messen (falls verfügbar)
    if 'duration_seconds' in result:
        render_time_ms = result['duration_seconds'] * 1000
        slo_monitor.add_render_time_measurement(render_time_ms)
    
except Exception as e:
    # Fehler als Messung hinzufügen
    slo_monitor.add_error_measurement(success=False)
    raise

# SLOs prüfen
slo_monitor.check_error_rate()
slo_monitor.check_render_time()
```

### Beispiel: Periodisches Monitoring

```python
import time
from automation.slo_monitor import SLOMonitor

monitor = SLOMonitor()

# Periodische SLO-Prüfung (z.B. alle 5 Minuten)
while True:
    # Operations durchführen und Messungen hinzufügen
    # ...
    
    # SLOs prüfen
    status = monitor.get_all_status()
    
    print(f"Error Rate: {status['error_rate']['status']}")
    print(f"Render Time: {status['render_time']['status']}")
    
    time.sleep(300)  # 5 Minuten warten
```

---

## 📈 Best Practices

### 1. Regelmäßige Messungen

Füge Messungen kontinuierlich hinzu, um aussagekräftige SLO-Statistiken zu erhalten:

```python
# Bei jedem API-Call
try:
    start_time = time.time()
    result = api_call()
    elapsed_ms = (time.time() - start_time) * 1000
    
    monitor.add_error_measurement(success=True)
    monitor.add_render_time_measurement(elapsed_ms)
except Exception as e:
    monitor.add_error_measurement(success=False)
    raise
```

### 2. Angemessene Schwellenwerte

Wähle Schwellenwerte basierend auf deinen Service-Anforderungen:

- **Trading Bots**: Niedrige Error-Rate (1-2%), moderate Render-Zeit (500-1000ms)
- **Monitoring Services**: Sehr niedrige Error-Rate (<1%), schnelle Render-Zeit (<500ms)
- **Batch Processing**: Höhere Error-Rate (5%), längere Render-Zeit (2000ms+)

### 3. Event-Monitoring

Überwache `needs-review` Events im SessionStore:

```python
from core.session_store import SessionStore

store = SessionStore()
events = store.read_events()

# Nur needs-review Events
review_events = [e for e in events if e.get('type') == 'needs-review']

for event in review_events:
    print(f"⚠️ {event['message']}")
    print(f"   Status: {event['details']['status']}")
    print(f"   Error Budget: {event['details']['error_budget_remaining']:.1f}%")
```

---

## 🧪 Testing

Tests für den SLO Monitor befinden sich in `tests/test_slo_monitor.py`:

```bash
# Alle SLO Monitor Tests ausführen
pytest tests/test_slo_monitor.py -v

# Nur Error-Rate Tests
pytest tests/test_slo_monitor.py -k error_rate -v

# Nur Render-Time Tests
pytest tests/test_slo_monitor.py -k render_time -v
```

---

## 🔍 Troubleshooting

### Problem: Keine Events werden generiert

**Lösung**: Stelle sicher, dass der SessionStore korrekt initialisiert ist:

```python
from core.session_store import SessionStore
import os

# Verzeichnis für Session-Daten erstellen
os.makedirs("data/session", exist_ok=True)

# SessionStore initialisieren
store = SessionStore()
monitor = SLOMonitor(session_store=store)
```

### Problem: SLO immer "compliant"

**Lösung**: Füge mehr Messungen hinzu (mindestens 20-30):

```python
# Mehr Messungen für statistische Relevanz
for i in range(100):
    monitor.add_error_measurement(success=(i % 10 != 0))  # 10% Fehlerquote
```

### Problem: Schwellenwert-Fehler

**Lösung**: Überprüfe Schwellenwert-Bereiche:

```python
# Error-Rate: 0.0 - 1.0
monitor.error_rate_threshold = 0.05  # ✅ 5%
# monitor.error_rate_threshold = 5.0  # ❌ Fehler!

# Render-Time: > 0
monitor.render_time_threshold_ms = 500.0  # ✅ 500ms
# monitor.render_time_threshold_ms = -100  # ❌ Fehler!
```

---

## 📚 Weitere Ressourcen

- **System Monitoring**: `system/monitoring/slo.py` - Basis-SLO-Monitor-Implementierung
- **Session Store**: `core/session_store.py` - Event-Persistierung
- **Automation Runner**: `automation/runner.py` - Integration mit Workflows
- **Tests**: `tests/test_slo_monitor.py` - Beispiele und Test-Cases

---

## 🤝 Contributing

Verbesserungen am SLO Monitor sind willkommen! Bitte beachte:

1. **Tests hinzufügen**: Neue Features brauchen Tests
2. **Dokumentation aktualisieren**: Dieses Guide aktualisieren
3. **Bestehende Tests nicht brechen**: Alle Tests müssen weiterhin laufen

---

**Made for Windows ⭐ | PowerShell-First | python-dotenv CLI | DRY_RUN Default**
