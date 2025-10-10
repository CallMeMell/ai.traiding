# Schema Validation Implementation Summary

## Ziel / Goal ✅

Events und Summary-Daten werden **strikt nach Schema validiert** und in den Systemworkflow integriert.

## Implementierung / Implementation

### 1. JSON-Schemas ✅

**Datei**: `automation/schemas.py`

Pydantic-basierte Schemas für:
- `Event`: Schema für events.jsonl Einträge
- `Summary`: Schema für summary.json
- `MetricsData`: Metriken innerhalb von Events
- `OrderData`: Order-Informationen innerhalb von Events
- `SummaryTotals`: Totals-Sektion in Summary

**Validierungsfunktionen**:
- `validate_event(event_dict)`: Strenge Validierung (wirft Exception)
- `validate_summary(summary_dict)`: Strenge Validierung (wirft Exception)

### 2. Python-Validatoren ✅

**Datei**: `automation/validate.py`

Zwei Validierungsmodi:
- **Lenient (nachsichtig)**: `validate_event_lenient()`, `validate_summary_lenient()`
  - Gibt `None` zurück bei Validierungsfehler
  - Loggt Warnungen
  - Blockiert nicht den Workflow
  
- **Strict (streng)**: `validate_event_strict()`, `validate_summary_strict()`
  - Wirft `ValidationError` bei Fehler
  - Für kritische Validierung

### 3. Integration in Runner ✅

**Datei**: `automation/runner.py`

**Änderung**: `enable_validation` ist jetzt **standardmäßig aktiviert** (True)

```python
def __init__(self, enable_validation: bool = True):  # Vorher: False
```

- Alle Events werden automatisch validiert
- Fehlerhafte Events werden geloggt, aber nicht blockiert (lenient validation)
- Rückwärtskompatibilität: Kann mit `enable_validation=False` deaktiviert werden

### 4. Integration in SessionStore ✅

**Datei**: `core/session_store.py`

**Änderungen**:
- `append_event(validate=True)`: Standardmäßig aktiviert (vorher: False)
- `write_summary(validate=True)`: Standardmäßig aktiviert (vorher: False)

Beide Methoden verwenden lenient validation:
- Validieren Daten beim Schreiben
- Loggen Warnungen bei Fehlern
- Schreiben Daten trotzdem (fail-safe)

### 5. Integration in View Session ✅

**Datei**: `tools/view_session_app.py`

**Neue Funktionalität**:
- Importiert Validatoren: `validate_event_lenient`, `validate_summary_lenient`
- Validiert alle geladenen Events
- Filtert ungültige Events aus
- Zeigt Warnung in Sidebar mit Anzahl gefilterter Events
- Validiert Summary und zeigt Warnung bei Fehlern

```python
# Validate and filter events
valid_events = []
invalid_count = 0
for event in all_events:
    validated = validate_event_lenient(event)
    if validated:
        valid_events.append(event)
    else:
        invalid_count += 1

if invalid_count > 0:
    st.sidebar.warning(f"⚠️ Filtered out {invalid_count} invalid event(s)")
```

## Tests ✅

### Schema-Tests: `test_schemas.py` (13 Tests)

- ✅ Minimal Event Validierung
- ✅ Full Event Validierung mit allen Feldern
- ✅ Invalide Timestamps werden erkannt
- ✅ Fehlende Pflichtfelder werden erkannt
- ✅ Invalide Level-Werte werden erkannt
- ✅ Lenient Validation wirft keine Exceptions
- ✅ Summary-Validierung (minimal + full)
- ✅ MetricsData und OrderData Modelle

### Integration Tests: `test_validation_integration.py` (8 Tests)

- ✅ Validation ist standardmäßig in Runner aktiviert
- ✅ SessionStore validiert standardmäßig
- ✅ Ungültige Events werden geloggt aber geschrieben
- ✅ Gültige Events passieren Validierung
- ✅ Summary-Validierung funktioniert
- ✅ Runner mit Validation läuft erfolgreich durch
- ✅ Fehlerhafte Einträge werden von lenient validator ausgeschlossen
- ✅ Gemischte valide/invalide Events werden korrekt behandelt

### Smoke Tests: `test_smoke_automation.py` (6 Tests)

- ✅ Runner im Dry-Run Modus
- ✅ Events werden generiert
- ✅ Summary wird generiert
- ✅ Events validieren erfolgreich
- ✅ Summary validiert erfolgreich
- ✅ Keine Secrets erforderlich

**Gesamt**: 27 Tests, alle bestanden ✅

## Messbarer Outcome ✅

- ✅ **JSON-Schemas vorhanden**: Pydantic-Modelle in `automation/schemas.py`
- ✅ **Python-Validatoren umgesetzt**: Lenient + Strict Modi in `automation/validate.py`
- ✅ **Integration in Runner**: Validation standardmäßig aktiviert
- ✅ **Integration in View**: Lädt und filtert valide Events
- ✅ **Tests laufen**: 27 Tests erfolgreich

## Acceptance Criteria ✅

- ✅ **Events werden nach Schema validiert**: Automatisch bei append_event()
- ✅ **Summary wird validiert**: Automatisch bei write_summary()
- ✅ **Fehlerhafte Einträge werden ausgeschlossen**: View Session filtert invalide Events
- ✅ **Tests für Validatoren laufen**: 27/27 Tests bestanden

## Technische Details

### Validierungsstrategie

Die Implementierung verwendet **lenient validation** als Standard:

1. **Schreib-Phase** (Runner → SessionStore):
   - Lenient validation beim Schreiben
   - Invalide Daten werden gewarnt aber geschrieben
   - Verhindert Datenverlust

2. **Lese-Phase** (View Session):
   - Lenient validation beim Laden
   - Invalide Daten werden gefiltert
   - Benutzer sieht nur valide Daten

### Vorteile

- ✅ **Robust**: Keine Daten gehen verloren
- ✅ **Sicher**: Nur valide Daten werden angezeigt
- ✅ **Debugging-freundlich**: Invalide Daten in Logs sichtbar
- ✅ **Rückwärtskompatibel**: Validation kann deaktiviert werden
- ✅ **Fail-safe**: System läuft auch bei Validierungsfehlern weiter

### Timestamp-Validierung

Timestamps müssen ISO 8601 Format haben:
```python
datetime.fromisoformat(timestamp)  # "2024-01-01T12:00:00"
```

### Level-Enum

Event-Level ist auf 4 Werte beschränkt:
```python
level: Literal["info", "warning", "error", "debug"]
```

## Verwendung / Usage

### Automatische Validierung (Standard)

```python
# Runner mit Validation (Standard)
runner = AutomationRunner()  # enable_validation=True (default)
runner.run()

# SessionStore validiert automatisch
store = SessionStore()
store.append_event(event)  # validate=True (default)
store.write_summary(summary)  # validate=True (default)
```

### Manuelle Validierung

```python
from automation.validate import validate_event_lenient, validate_event_strict

# Lenient: Gibt None bei Fehler zurück
validated = validate_event_lenient(event_dict)
if validated:
    print("Valid event!")
else:
    print("Invalid event - logged as warning")

# Strict: Wirft ValidationError
try:
    validated = validate_event_strict(event_dict)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Validation deaktivieren (falls nötig)

```python
# Runner ohne Validation
runner = AutomationRunner(enable_validation=False)

# SessionStore ohne Validation
store.append_event(event, validate=False)
store.write_summary(summary, validate=False)
```

## Referenzen

- **Schemas**: `automation/schemas.py`
- **Validators**: `automation/validate.py`
- **Runner Integration**: `automation/runner.py`
- **SessionStore Integration**: `core/session_store.py`
- **View Integration**: `tools/view_session_app.py`
- **Tests**: `test_schemas.py`, `test_validation_integration.py`, `test_smoke_automation.py`

## Status: ✅ ABGESCHLOSSEN

Alle Acceptance Criteria erfüllt. Validation ist vollständig in den Systemworkflow integriert.
