# 📊 View Session Streamlit Dashboard - Benutzerhandbuch

## Übersicht

Das View Session Dashboard ist eine lightweight Streamlit-Anwendung zur Visualisierung von Trading-Sessions und deren Performance in Echtzeit.

**Wichtig:** Diese Komponente ist komplett optional und entkoppelt von der Trading-Runtime-Logik. Sie ist Zero-Risk und kann sicher verwendet werden.

## Features

### 📈 Visualisierungen

- **Equity Curve**: Liniendiagramm zeigt die Entwicklung des Kapitals über Zeit
- **Wins vs Losses**: Balkendiagramm zeigt Gewinne und Verluste pro Phase
- **Event-Historie**: Tabelle mit den letzten 20 Events

### 🔍 Filter

- **Zeitbereich**:
  - Alle Events
  - Letzte 1 Stunde
  - Letzte 24 Stunden
  - Letzte 7 Tage
  - Benutzerdefinierter Bereich (Start- und Enddatum)

- **Strategy Tag**:
  - Alle Phasen
  - data_phase
  - strategy_phase
  - api_phase

### ⚡ Live-Updates

- **Auto-Refresh**: Optional alle 5 Sekunden
- **URL-Persistenz**: Filterzustand wird in der URL gespeichert (Seite kann neu geladen werden)

## Installation

### 1. Streamlit installieren

```bash
pip install streamlit plotly
```

### 2. Dashboard starten

```bash
streamlit run tools/view_session_app.py
```

Das Dashboard öffnet sich automatisch im Browser unter `http://localhost:8501`

## Datenquelle

Das Dashboard liest Session-Daten aus:

- **Events**: `data/session/events.jsonl` (JSONL-Format, ein Event pro Zeile)
- **Summary**: `data/session/summary.json` (JSON-Format mit Zusammenfassung)

Diese Dateien werden automatisch vom Automation Runner erstellt.

## Workflow

### 1. Automation Runner ausführen

```bash
python automation/runner.py
```

Der Runner erstellt:
- Session-Events in `data/session/events.jsonl`
- Rolling Summary in `data/session/summary.json`

### 2. Dashboard öffnen

```bash
streamlit run tools/view_session_app.py
```

### 3. Daten visualisieren

Das Dashboard zeigt:
- **Metriken**: Initial Capital, Current Equity, ROI, Fortschritt
- **Charts**: Equity Curve, Wins/Losses
- **Events**: Tabelle mit Event-Historie

### 4. Filter anwenden

Verwende die Sidebar, um:
- Zeitbereich einzugrenzen
- Nach Strategy-Tag zu filtern
- Auto-Refresh zu aktivieren

## Datenformat

### Events (JSONL)

Jede Zeile ist ein JSON-Objekt:

```json
{"type": "session_start", "timestamp": "2025-10-10T03:22:06.240179"}
{"type": "phase_start", "phase": "data_phase", "timestamp": "2025-10-10T03:22:06.240485"}
{"type": "phase_end", "phase": "data_phase", "status": "success", "duration_seconds": 2.0, "timestamp": "2025-10-10T03:22:08.240744"}
```

**Event-Typen:**
- `session_start`: Session wurde gestartet
- `session_end`: Session wurde beendet
- `phase_start`: Phase wurde gestartet
- `phase_end`: Phase wurde beendet
- `pause_start`: Pause wurde gestartet
- `pause_end`: Pause wurde beendet
- `heartbeat`: Heartbeat-Signal
- `error`: Fehler aufgetreten

### Summary (JSON)

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

**Felder:**
- `session_start`: Startzeitpunkt der Session (ISO 8601)
- `session_end`: Endzeitpunkt der Session (ISO 8601)
- `status`: Status der Session (`running`, `success`, `failed`, `error`)
- `phases_completed`: Anzahl abgeschlossener Phasen
- `phases_total`: Gesamtanzahl der Phasen
- `initial_capital`: Startkapital in $
- `current_equity`: Aktuelles Kapital in $
- `roi`: Return on Investment in %
- `last_updated`: Letztes Update (ISO 8601)

## Verwendung ohne Streamlit

Falls Streamlit nicht installiert ist, können die Session-Dateien auch direkt gelesen werden:

```bash
# Events anzeigen
cat data/session/events.jsonl

# Summary anzeigen
cat data/session/summary.json

# Events mit jq formatieren
cat data/session/events.jsonl | jq .
```

## Entwicklung

### Architektur

```
tools/view_session_app.py
├── ViewSessionApp (Hauptklasse)
│   ├── render_header() - Seitenkopf
│   ├── render_filters() - Filter-Sidebar
│   ├── render_summary_metrics() - Metriken
│   ├── render_pnl_chart() - Equity Chart
│   ├── render_wins_losses_chart() - Wins/Losses Chart
│   └── render_events_table() - Event-Tabelle
└── SessionStore (aus core/)
    ├── read_events() - Liest Events
    └── read_summary() - Liest Summary
```

### Erweiterungen

Das Dashboard kann erweitert werden mit:

- **Mehr Charts**: z.B. Trade-Volumen, Drawdown
- **Erweiterte Filter**: z.B. nach Status, nach Fehlertyp
- **Export**: z.B. CSV, PDF
- **Vergleiche**: z.B. mehrere Sessions nebeneinander

## Fehlerbehebung

### Dashboard zeigt "No session data available"

**Ursache:** Keine Session-Dateien vorhanden

**Lösung:**
```bash
python automation/runner.py
```

### "ModuleNotFoundError: No module named 'streamlit'"

**Ursache:** Streamlit nicht installiert

**Lösung:**
```bash
pip install streamlit plotly
```

### Dashboard lädt nicht im Browser

**Ursache:** Port 8501 bereits belegt

**Lösung:**
```bash
streamlit run tools/view_session_app.py --server.port 8502
```

## Best Practices

1. **Regelmäßig Sessions durchführen**: Mehr Daten = bessere Visualisierungen
2. **Auto-Refresh verwenden**: Für Live-Monitoring während der Automation
3. **Filter nutzen**: Fokus auf relevante Zeitbereiche und Phasen
4. **Archivieren**: Alte Session-Dateien regelmäßig archivieren

## Sicherheit

- **Keine Secrets**: Dashboard enthält keine API-Keys oder Secrets
- **Read-Only**: Dashboard ändert keine Trading-Daten
- **Optional**: Kann jederzeit deaktiviert werden ohne Trading zu beeinflussen

## Support

Bei Fragen oder Problemen:
1. Prüfe die Log-Dateien: `logs/`
2. Prüfe die Session-Dateien: `data/session/`
3. Öffne ein Issue auf GitHub

---

**Version**: 1.0.0  
**Datum**: 2025-10-10  
**Status**: ✅ Produktionsbereit
