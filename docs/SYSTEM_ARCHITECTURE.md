# 🏗️ System Architecture - ai.traiding

**Version:** 1.1.0  
**Last Updated:** 2025-10-10

## 📋 Übersicht

Das ai.traiding System ist eine vollautomatisierte Trading-Plattform mit modularer Architektur, Health Checks, und umfassender Fehlerbehandlung.

---

## 🎯 Architektur-Prinzipien

### 1. **Windows-First Development**
- PowerShell-Skripte als primäre CLI-Tools
- Direkte venv-Aufrufe (`venv\Scripts\python.exe`)
- python-dotenv CLI mit `--override` Flag

### 2. **Safety by Default**
- `DRY_RUN=true` als Standard
- Testnet als Default für alle Broker-APIs
- Umfassende Validierung vor Trading-Operationen

### 3. **Modulare Struktur**
- Lose gekoppelte Komponenten
- Klare Schnittstellen zwischen Modulen
- Einfache Erweiterbarkeit

### 4. **Observability**
- Zentralisiertes strukturiertes Logging
- Health Checks zwischen Phasen
- Metriken und SLO-Tracking

---

## 🏛️ System-Komponenten

```
┌─────────────────────────────────────────────────────────────┐
│                    System Orchestrator                       │
│  - Phase Management                                          │
│  - Health Checks                                             │
│  - Recovery Logic                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼───────┐         ┌──────▼──────┐
│  Adapters │         │   Logging   │
│  - Base   │         │  - Console  │
│  - Binance│         │  - File     │
│  - Factory│         │  - JSON     │
└───┬───────┘         └──────┬──────┘
    │                        │
┌───▼───────────────────────▼──────────────────────────┐
│              Core Automation System                   │
│  - Runner                                            │
│  - Scheduler                                         │
│  - Session Store                                     │
└──────────────────────────────────────────────────────┘
```

---

## 📦 Module Details

### 1. **System Orchestrator** (`system/orchestrator.py`)

**Verantwortlichkeiten:**
- Koordination aller System-Phasen
- Health Checks vor/nach Phasen
- Automatische Recovery bei Fehlern
- Metriken-Sammlung

**Phasen:**
1. Initialization - System-Setup
2. Data Preparation - Daten laden und validieren
3. Strategy Execution - Strategie ausführen
4. API Integration - Broker-API Kommunikation
5. Monitoring - Metriken sammeln
6. Cleanup - Ressourcen aufräumen

**Interface:**
```python
orchestrator = SystemOrchestrator(
    dry_run=True,
    enable_health_checks=True,
    enable_recovery=True
)
results = orchestrator.run()
```

### 2. **Adapter System** (`system/adapters/`)

**Verantwortlichkeiten:**
- Einheitliche Broker-API Schnittstelle
- Connection Management
- Error Handling & Retries
- Rate Limiting

**Komponenten:**
- `BaseAdapter` - Abstract base class
- `AdapterFactory` - Factory pattern für Adapter-Erstellung
- Broker-spezifische Implementierungen (Binance, etc.)

**Interface:**
```python
from system.adapters import AdapterFactory

adapter = AdapterFactory.create(
    'binance',
    api_key=key,
    api_secret=secret,
    testnet=True
)
adapter.connect()
balance = adapter.get_account_balance()
```

### 3. **Logging System** (`system/logging/`)

**Verantwortlichkeiten:**
- Zentralisiertes Logging
- Strukturierte Log-Formate
- Log Rotation (10 MB, 5 Backups)
- Multiple Handler (Console, File, JSON)

**Log-Dateien:**
- `logs/system.log` - Hauptlog
- `logs/errors.log` - Nur Fehler
- `logs/trading.log` - Trading-spezifisch
- `logs/system.jsonl` - JSON structured logs

**Interface:**
```python
from system.logging import configure_logging, get_logger, LogLevel

configure_logging(
    log_dir='logs',
    level=LogLevel.INFO,
    enable_json=True
)

logger = get_logger(__name__)
logger.info("System started")
```

### 4. **Error Handling** (`system/errors/`)

**Exception Hierarchy:**
```
SystemError (Base)
├── AdapterError
├── ConfigurationError
├── TradingError
└── ValidationError
```

**Interface:**
```python
from system.errors import TradingError

raise TradingError(
    "Order failed",
    symbol='BTCUSDT',
    order_id='123',
    details={'reason': 'Insufficient funds'}
)
```

### 5. **Core Automation** (`automation/`)

**Bereits vorhanden:**
- `runner.py` - Automation Runner
- `scheduler.py` - Phase Scheduler
- `schemas.py` - Data Schemas
- `validate.py` - Validation

**Integration:**
- Wird vom Orchestrator genutzt
- Erweitert um neue Features
- Bleibt rückwärtskompatibel

### 6. **Session Management** (`core/`)

**Bereits vorhanden:**
- `session_store.py` - Session Event Storage
- `env_helpers.py` - Environment Variable Helpers

**Features:**
- JSONL Event Logging
- Session Summary Generation
- Schema Validation

---

## 🔄 Datenfluss

```
1. User Input / Scheduled Trigger
           ↓
2. System Orchestrator
           ↓
3. Phase Execution
   ├─ Health Check (Pre)
   ├─ Phase Logic
   └─ Health Check (Post)
           ↓
4. Adapter Calls (if needed)
   ├─ Connection Check
   ├─ API Request
   └─ Error Handling
           ↓
5. Logging & Metrics
   ├─ Event Logging
   ├─ Session Store
   └─ Metrics Collection
           ↓
6. Results & Cleanup
```

---

## 🚀 Deployment

### Entwicklungsumgebung
```powershell
# 1. Virtual Environment erstellen
python -m venv venv

# 2. Dependencies installieren
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. System testen
.\venv\Scripts\python.exe system/orchestrator.py
```

### CI/CD Pipeline
- GitHub Actions bei jedem Push/PR
- Windows + Linux Matrix Testing
- Automatische Tests und Coverage
- Nightly Dry-Run Jobs

### Nightly Jobs
```powershell
# Manuell ausführen
.\scripts\nightly_run.ps1

# Automatisch via GitHub Actions (02:00 UTC täglich)
```

---

## 📊 Monitoring & Health

### Health Checks
- **Memory Check** - Speicherverbrauch
- **Disk Check** - Verfügbarer Speicherplatz
- **Connectivity Check** - Netzwerkverbindung

### Metriken
- Phases Completed
- Errors Count
- Execution Duration
- Health Status

### SLOs (Geplant)
- Uptime: 99.5%
- API Response Time: <500ms (P95)
- Trade Execution: <1s (P99)
- Error Rate: <1%

---

## 🔒 Security

### Best Practices
1. **Keine Secrets im Code**
   - API Keys in `.env` oder Credential Manager
   - `.env` in `.gitignore`

2. **DRY_RUN Default**
   - Alle Trading-Ops standardmäßig im Trockenmodus
   - Explizites Opt-In für Live Trading

3. **Testnet First**
   - Primär Testnet-APIs nutzen
   - Produktion nur nach ausgiebigen Tests

4. **Input Validation**
   - Alle User-Inputs validieren
   - Schema-Validierung für Events

---

## 🧪 Testing

### Test-Struktur
```
tests/
├── conftest.py           # Shared fixtures
├── test_orchestrator.py  # Orchestrator tests
├── test_adapters.py      # Adapter tests
└── test_logging.py       # Logging tests (geplant)
```

### Test-Ausführung
```powershell
# Alle Tests
.\venv\Scripts\python.exe -m pytest tests/ -v

# Mit Coverage
.\venv\Scripts\python.exe -m pytest tests/ --cov=. --cov-report=html

# Nur Unit Tests
.\venv\Scripts\python.exe -m pytest tests/ -m unit
```

---

## 📚 Weitere Dokumentation

- **[12h Implementation Plan](../SYSTEM_12H_IMPLEMENTATION.md)** - Vollständiger Implementierungsplan
- **[Changelog](../CHANGELOG.md)** - Änderungsprotokoll
- **[README.md](../README.md)** - Projekt-Übersicht
- **[ROADMAP.md](../ROADMAP.md)** - Entwicklungs-Roadmap

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
