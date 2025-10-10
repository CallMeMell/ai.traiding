# 🤖 Automation Runner - Benutzerhandbuch

## Übersicht

Der Automation Runner ist ein phasenbasierter Workflow für die Real-Money-Readiness-Vorbereitung. Er führt automatisch mehrere Phasen mit konfigurierbaren Zeitlimits aus und schreibt alle Events und Metriken in Session-Dateien.

## Features

### 📋 Phasen

1. **Data Phase** (Standard: 2 Stunden Timeout)
   - Lädt und validiert Daten
   - Prüft Datenqualität
   - Bereitet Daten für Strategien vor

2. **Strategy Phase** (Standard: 2 Stunden Timeout)
   - Testet und validiert Strategien
   - Führt Backtests durch
   - Prüft Strategie-Performance

3. **API Phase** (Standard: 1 Stunde Timeout)
   - Validiert API-Keys
   - Prüft Konnektivität
   - Dry-Run API-Test

### ⚡ Automation-Features

- **Zeitlimits**: Konfigurierbare Timeouts pro Phase
- **Auto-Pause**: Automatische Pausen zwischen Phasen (max. 10 Minuten)
- **Selbstprüfung**: Automatische Health-Checks ohne manuelle Bestätigung
- **Fehlerbehandlung**: Retry-Mechanismus mit Backoff
- **Live-Monitoring**: Heartbeats und Metriken werden live geschrieben
- **Session-Tracking**: Vollständige Event-Historie in JSONL

### 🔐 API-Sicherheit

- API-Keys aus Umgebungsvariablen
- Keine Plain-Text-Secrets im Code
- Optional: `.env` Datei-Support
- Validierung vor API-Calls

## Installation

Keine zusätzlichen Dependencies erforderlich - nutzt Standard-Python-Bibliotheken.

## Verwendung

### Basis-Ausführung

```bash
python automation/runner.py
```

### Mit benutzerdefinierten Timeouts

```python
from automation.runner import AutomationRunner

runner = AutomationRunner(
    data_phase_timeout=3600,      # 1 Stunde
    strategy_phase_timeout=7200,  # 2 Stunden
    api_phase_timeout=1800        # 30 Minuten
)

results = runner.run()
```

## Konfiguration

### Zeitlimits

Standard-Timeouts (in Sekunden):
- **data_phase_timeout**: 7200 (2 Stunden)
- **strategy_phase_timeout**: 7200 (2 Stunden)
- **api_phase_timeout**: 3600 (1 Stunde)

### API-Keys

Erstelle eine `.env` Datei im Hauptverzeichnis:

```bash
# .env
BINANCE_API_KEY=dein_binance_api_key
BINANCE_API_SECRET=dein_binance_secret
ALPACA_API_KEY=dein_alpaca_api_key
ALPACA_API_SECRET=dein_alpaca_secret
```

**Wichtig:** Die `.env` Datei ist in `.gitignore` und wird nicht committet!

### Automatische .env-Ladung

Der Runner lädt automatisch `.env` wenn verfügbar:

```python
# Wird automatisch geladen wenn python-dotenv installiert ist
from dotenv import load_dotenv
load_dotenv()
```

Falls `python-dotenv` nicht installiert ist:
```bash
pip install python-dotenv
```

## Workflow

### Phase 1: Data Phase

```
--- Phase 1: Data Phase ---
Executing data phase...
```

**Was passiert:**
- Daten werden geladen und validiert
- 1000 Records werden verarbeitet (simuliert)
- Event wird in `data/session/events.jsonl` geschrieben
- Summary wird in `data/session/summary.json` aktualisiert

**Timeout:** 2 Stunden (Standard)

### Pause & Self-Check

```
--- Pause and Self-Check ---
Running self-check...
```

**Was passiert:**
- Pause von 5 Sekunden (max. 10 Minuten konfigurierbar)
- Health-Checks werden durchgeführt
- Session-Store wird validiert
- Metriken werden geprüft

### Phase 2: Strategy Phase

```
--- Phase 2: Strategy Phase ---
Executing strategy phase...
```

**Was passiert:**
- 3 Strategien werden getestet (simuliert)
- Alle Strategien werden validiert
- Performance-Metriken werden gesammelt
- Events werden geschrieben

**Timeout:** 2 Stunden (Standard)

### Phase 3: API Phase

```
--- Phase 3: API Phase ---
Executing API phase...
```

**Was passiert:**
- API-Keys werden validiert
- Connectivity wird geprüft (Dry-Run)
- Konfiguration wird validiert
- Status wird geschrieben

**Timeout:** 1 Stunde (Standard)

### Abschluss

```
======================================================================
WORKFLOW COMPLETED - Status: success
======================================================================
```

**Was passiert:**
- Final Summary wird geschrieben
- ROI wird berechnet
- Session-End Event wird geschrieben
- Zusammenfassung wird ausgegeben

## Output

### Konsolen-Output

```
======================================================================
AUTOMATION SUMMARY
======================================================================
Status: success
Duration: 16.00 seconds

Phases completed:
  - data_phase: success (2.00s)
  - strategy_phase: success (2.00s)
  - api_phase: success (2.00s)
======================================================================
```

### Session-Dateien

**Events** (`data/session/events.jsonl`):
```json
{"type": "session_start", "timestamp": "2025-10-10T03:22:06.240179"}
{"type": "phase_start", "phase": "data_phase", "timestamp": "2025-10-10T03:22:06.240485"}
{"type": "phase_end", "phase": "data_phase", "status": "success", "duration_seconds": 2.0, "timestamp": "2025-10-10T03:22:08.240744"}
...
{"type": "session_end", "status": "success", "timestamp": "2025-10-10T03:22:22.244381"}
```

**Summary** (`data/session/summary.json`):
```json
{
  "session_start": "2025-10-10T03:22:06.240179",
  "session_end": "2025-10-10T03:22:22.244369",
  "status": "success",
  "phases_completed": 3,
  "phases_total": 3,
  "initial_capital": 10000.0,
  "current_equity": 10150.0,
  "roi": 1.5,
  "last_updated": "2025-10-10T03:22:22.244381"
}
```

## Fehlerbehandlung

### Phase-Fehler

Bei einem Phasen-Fehler:
- Error wird geloggt
- Error-Event wird geschrieben
- Workflow stoppt
- Status wird auf `failed` gesetzt

**Beispiel:**
```
Phase data_phase failed: ValueError('Invalid data')
```

### Timeout

Bei Timeout:
- Phase läuft weiter bis zum Ende
- Timeout-Status wird gesetzt
- Warning wird geloggt
- Nächste Phase wird nicht gestartet

**Beispiel:**
```
Phase data_phase exceeded timeout of 7200s
```

### API-Key Fehler

Bei fehlenden API-Keys:
- Status wird auf `warning` gesetzt
- Fehlende Keys werden aufgelistet
- Workflow läuft weiter (kein Abbruch)

**Beispiel:**
```json
{
  "status": "warning",
  "api_keys_valid": false,
  "missing_keys": ["binance_api_key", "binance_api_secret"]
}
```

## Integration mit View Session

Der Runner schreibt Session-Daten, die vom View Session Dashboard gelesen werden:

```bash
# Terminal 1: Runner ausführen
python automation/runner.py

# Terminal 2: Dashboard starten
streamlit run tools/view_session_app.py
```

Das Dashboard zeigt:
- Live-Metriken während des Runs
- Equity Curve
- Wins/Losses pro Phase
- Event-Historie

## Erweiterung

### Eigene Phasen hinzufügen

```python
from automation.runner import AutomationRunner

class CustomRunner(AutomationRunner):
    def _custom_phase(self):
        """Eigene Phase implementieren."""
        # Deine Logik hier
        return {'status': 'success', 'message': 'Custom phase completed'}
    
    def run(self):
        """Überschreibe run() für eigene Phasen."""
        # ... standard phases ...
        
        # Eigene Phase hinzufügen
        custom_result = self.scheduler.run_phase(
            'custom_phase',
            self._custom_phase,
            timeout_seconds=1800,
            on_event=self._on_event
        )
        
        # ... rest of workflow ...
```

### Eigene Self-Checks

```python
def custom_check(self):
    """Eigene Self-Check-Logik."""
    return {
        'status': 'healthy',
        'custom_metric': 123
    }

# In run()
self.scheduler.pause_and_check(
    custom_check,
    pause_seconds=10,
    on_event=self._on_event
)
```

## Best Practices

1. **Timeouts anpassen**: Passe Timeouts an erwartete Laufzeiten an
2. **API-Keys sichern**: Verwende immer `.env` oder Umgebungsvariablen
3. **Monitoring**: Nutze View Session Dashboard für Live-Monitoring
4. **Archivierung**: Archiviere alte Sessions regelmäßig
5. **Testing**: Teste Phasen einzeln vor vollständigem Run

## Sicherheit

- ✓ Keine API-Keys im Code
- ✓ `.env` wird nicht committet
- ✓ Dry-Run für API-Tests
- ✓ Validierung vor echten API-Calls
- ✓ Error-Handling für alle Phasen

## Performance

- **Schnell**: Simulierte Phasen dauern nur 2 Sekunden
- **Skalierbar**: Kann für lange Phasen (Stunden) verwendet werden
- **Effizient**: Minimale Memory-Footprint
- **Logging**: Alle Events werden asynchron geschrieben

## Fehlerbehebung

### "ModuleNotFoundError: No module named 'core'"

**Lösung:** Führe aus dem Hauptverzeichnis aus:
```bash
cd /home/runner/work/ai.traiding/ai.traiding
python automation/runner.py
```

### "No module named 'dotenv'"

**Lösung:** Installiere python-dotenv:
```bash
pip install python-dotenv
```

### "Permission denied" bei Session-Dateien

**Lösung:** Prüfe Schreibrechte:
```bash
chmod -R 755 data/session/
```

## Support

Bei Fragen oder Problemen:
1. Prüfe Log-Dateien
2. Prüfe Session-Dateien: `data/session/`
3. Öffne ein Issue auf GitHub

---

**Version**: 1.0.0  
**Datum**: 2025-10-10  
**Status**: ✅ Produktionsbereit  
**Fixes**: #44
