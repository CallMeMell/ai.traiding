# 🚀 Ein-Klick Dev Live Session - Setup Guide

## Overview

Die Ein-Klick Dev Live Session ist ein vollständig automatisierter Workflow, der Entwicklern ermöglicht, mit einem einzigen Befehl die komplette Entwicklungs- und Monitoring-Umgebung zu starten.

## Features

### ✅ Vollständig Automatisiert
- **Keine manuelle Konfiguration** erforderlich
- **Idempotent** - kann beliebig oft ausgeführt werden
- **Self-Healing** - erkennt und behebt fehlende Dependencies

### ✅ Cross-Platform
- **Windows** (PowerShell)
- **macOS** (Bash)
- **Linux** (Bash)
- **GitHub Codespaces** (Remote Development)

### ✅ Sicher und Risikofrei
- **DRY_RUN-Modus** als Standard
- **Keine API-Keys** erforderlich
- **Simulierte Daten** für Tests
- **Kein echtes Geld** involviert

## Quick Start

### Option 1: VS Code (Empfohlen)

1. **Öffne das Projekt in VS Code**
2. **Drücke** `Ctrl+Shift+P` (Windows/Linux) oder `Cmd+Shift+P` (macOS)
3. **Tippe** "Tasks: Run Task"
4. **Wähle** "Dev: Live Session"
5. **Fertig!** Dashboard öffnet sich automatisch

### Option 2: Shell/PowerShell

**Linux/macOS:**
```bash
./scripts/start_live.sh
```

**Windows PowerShell:**
```powershell
.\scripts\start_live.ps1
```

## Setup Validation

Vor dem ersten Start kannst du dein Setup validieren:

**Linux/macOS:**
```bash
./scripts/validate_setup.sh
```

**Windows PowerShell:**
```powershell
.\scripts\validate_setup.ps1
```

Das Validierungsskript prüft:
- ✅ Python-Installation
- ✅ Projektstruktur
- ✅ Virtual Environment
- ✅ Port-Verfügbarkeit
- ✅ PowerShell Execution Policy (nur Windows)

## Was passiert beim Start?

### Phase 1: Pre-flight Checks (5 Sekunden)
- Python-Version wird geprüft
- Projektstruktur wird validiert
- Konflikte werden erkannt

### Phase 2: Setup (1-2 Minuten beim ersten Mal)
- Virtual Environment wird erstellt (`venv/`)
- pip wird aktualisiert
- Dependencies werden installiert:
  - streamlit
  - plotly
  - pandas
  - requests
  - python-dotenv
  - pydantic
  - jsonschema
- Verzeichnisse werden angelegt (`data/session/`)

### Phase 3: Start (5-10 Sekunden)
- **Automation Runner** startet im DRY_RUN-Modus
  - Generiert Events
  - Schreibt nach `data/session/events.jsonl`
  - Keine echten Trading-Operationen
- **Streamlit Dashboard** startet auf Port 8501
  - Liest Events aus `events.jsonl`
  - Zeigt Live-Updates
  - Auto-Refresh alle 10 Sekunden

### Phase 4: Ready!
- Browser öffnet sich automatisch
- Dashboard zeigt Events in Echtzeit
- Beide Prozesse laufen parallel
- Ctrl+C stoppt alles

## Verfügbare VS Code Tasks

### Install Dev Deps
**Zweck:** Einmalige Einrichtung der Entwicklungsumgebung  
**Wann nutzen:** Nur beim ersten Setup oder nach venv-Löschung  
**Was passiert:**
- Erstellt venv
- Aktualisiert pip
- Installiert alle Dependencies

### Run: Automation Runner (Dry-Run)
**Zweck:** Backend-Tests ohne echte Trading-Operationen  
**Wann nutzen:** Zum Testen von Automation-Logik  
**Was passiert:**
- Setzt `DRY_RUN=true`
- Setzt `BROKER_NAME=binance`
- Setzt `BINANCE_BASE_URL=https://testnet.binance.vision`
- Startet `automation/runner.py`

### Run: View Session (Streamlit)
**Zweck:** Frontend-Tests und Event-Monitoring  
**Wann nutzen:** Zum Anzeigen von Events aus vergangenen Sessions  
**Was passiert:**
- Startet Streamlit auf Port 8501
- Liest Events aus `data/session/events.jsonl`
- Zeigt Dashboard mit Live-Updates

### Dev: Live Session ⭐
**Zweck:** Complete Dev-Umgebung mit einem Klick  
**Wann nutzen:** Empfohlen für normale Entwicklung  
**Was passiert:**
- Startet Automation Runner und View Session **parallel**
- Beide Prozesse laufen gleichzeitig
- Dashboard zeigt Live-Events

### Stop: All Sessions
**Zweck:** Alle laufenden Streamlit-Prozesse beenden  
**Wann nutzen:** Aufräumen nach Entwicklung  
**Was passiert:**
- Stoppt alle Streamlit-Prozesse
- Gibt Port 8501 frei

## Troubleshooting

### Validation Script nutzen
Der einfachste Weg, Probleme zu erkennen:
```bash
./scripts/validate_setup.sh  # Linux/macOS
.\scripts\validate_setup.ps1  # Windows
```

### Häufige Probleme

#### "streamlit: command not found"
**Ursache:** venv nicht aktiviert oder Streamlit nicht installiert  
**Lösung:**
```bash
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
pip install streamlit
```

#### "Port 8501 already in use"
**Ursache:** Alter Streamlit-Prozess läuft noch  
**Lösung:**
```bash
pkill -f streamlit         # Linux/Mac
taskkill /F /IM streamlit.exe  # Windows
# Oder nutze VS Code Task "Stop: All Sessions"
```

#### "No module named 'core'"
**Ursache:** PYTHONPATH nicht gesetzt  
**Lösung:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH = "$(pwd)"                # Windows
```

#### View Session zeigt "No data available"
**Ursache:** Runner läuft nicht oder generiert keine Events  
**Lösung:**
1. Warte 5-10 Sekunden nach Runner-Start
2. Prüfe ob `data/session/events.jsonl` existiert
3. Drücke "Refresh Now" im Dashboard
4. Starte beide Prozesse neu mit "Dev: Live Session"

#### venv-Aktivierung schlägt fehl (Windows)
**Ursache:** PowerShell Execution Policy zu restriktiv  
**Lösung:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Dependencies-Installation schlägt fehl
**Ursache:** Veraltetes pip oder Netzwerkprobleme  
**Lösung:**
```bash
pip install --upgrade pip
pip install streamlit plotly pandas requests python-dotenv pydantic jsonschema
```

## Technische Details

### Architektur
```
┌─────────────────────────────────────┐
│  VS Code Task "Dev: Live Session"  │
└─────────────┬───────────────────────┘
              │ (parallel start)
       ┌──────┴──────┐
       ▼             ▼
┌─────────────┐  ┌──────────────┐
│  Automation │  │   Streamlit  │
│   Runner    │  │  Dashboard   │
│  (DRY_RUN)  │  │  (Port 8501) │
└──────┬──────┘  └──────┬───────┘
       │                │
       ▼                ▼
   events.jsonl ────────┘
   (data/session/)
```

### Dateien und Verzeichnisse
```
ai.traiding/
├── .vscode/
│   ├── tasks.json         # VS Code Tasks
│   ├── settings.json      # VS Code Settings (Port-Forwarding)
│   └── extensions.json    # Empfohlene Extensions
├── scripts/
│   ├── start_live.sh      # Shell-Script für Linux/macOS
│   ├── start_live.ps1     # PowerShell-Script für Windows
│   ├── validate_setup.sh  # Setup-Validator für Linux/macOS
│   └── validate_setup.ps1 # Setup-Validator für Windows
├── automation/
│   └── runner.py          # Automation Runner
├── tools/
│   └── view_session_app.py # Streamlit Dashboard
├── data/
│   └── session/
│       ├── events.jsonl   # Event Log
│       └── summary.json   # Session Summary
└── venv/                  # Virtual Environment (automatisch erstellt)
```

### Environment Variables
Die folgenden Umgebungsvariablen werden automatisch gesetzt:

```bash
DRY_RUN=true                              # Keine echten Trading-Operationen
BROKER_NAME=binance                       # Broker-Auswahl
BINANCE_BASE_URL=https://testnet.binance.vision  # Testnet URL
```

## Best Practices

### Für tägliche Entwicklung
1. Starte mit "Dev: Live Session" Task
2. Lass die Session laufen während du entwickelst
3. Code-Änderungen sofort sichtbar
4. Stoppe mit Ctrl+C wenn fertig

### Für Debugging
1. Nutze einzelne Tasks ("Run: Automation Runner" oder "Run: View Session")
2. Schaue in Logs: `data/session/events.jsonl`
3. Prüfe Session Summary: `data/session/summary.json`

### Für Team-Arbeit
1. Validierungsskript in CI/CD integrieren
2. Dokumentierte Troubleshooting-Schritte im Team teilen
3. Shell-Skripte für automatisierte Tests nutzen

## Support

Bei Problemen:
1. **Validation Script** ausführen
2. **Troubleshooting-Sektion** in README prüfen
3. **Issue** auf GitHub erstellen mit:
   - Output des Validation Scripts
   - Fehlermeldungen
   - Betriebssystem und Python-Version

## Weiterführende Dokumentation

- [VIEW_SESSION_GUIDE.md](VIEW_SESSION_GUIDE.md) - Detaillierte View Session Dokumentation
- [AUTOMATION_RUNNER_GUIDE.md](AUTOMATION_RUNNER_GUIDE.md) - Automation Runner Details
- [README.md](README.md) - Haupt-Dokumentation

---

**Version:** 1.0  
**Letzte Aktualisierung:** 2025-10-10
