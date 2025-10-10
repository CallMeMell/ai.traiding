# 🔧 Troubleshooting Guide - ai.traiding

**Version:** 1.1.0  
**Last Updated:** 2025-10-10

## 📋 Übersicht

Dieser Guide hilft bei der Diagnose und Behebung häufiger Probleme im ai.traiding System.

---

## 🚨 Häufige Probleme

### 1. System Orchestrator startet nicht

**Problem:**
```
ModuleNotFoundError: No module named 'automation'
```

**Lösung:**
```powershell
# Virtual Environment aktivieren
.\venv\Scripts\Activate.ps1

# Oder direkt venv-Python verwenden
.\venv\Scripts\python.exe system\orchestrator.py
```

---

### 2. Import-Fehler mit logging Module

**Problem:**
```
ModuleNotFoundError: No module named 'logging.handlers'
```

**Ursache:** Konflikt zwischen lokalem `logging/` Verzeichnis und Python's built-in `logging` Modul.

**Lösung:** Bereits behoben - System verwendet `log_system/` statt `logging/`

---

### 3. Tests schlagen fehl

**Problem:**
```
pytest: command not found
```

**Lösung:**
```powershell
# pytest installieren
.\venv\Scripts\python.exe -m pip install pytest pytest-cov

# Tests ausführen
.\venv\Scripts\python.exe -m pytest tests/ -v
```

---

### 4. API Connection Timeout

**Problem:**
```
AdapterError: Connection timeout to binance API
```

**Lösung:**
1. **Netzwerk prüfen:**
   ```powershell
   Test-NetConnection testnet.binance.vision -Port 443
   ```

2. **Testnet URL korrekt:**
   ```powershell
   $env:BINANCE_BASE_URL = "https://testnet.binance.vision"
   ```

3. **Firewall prüfen:**
   - Windows Firewall könnte ausgehende Verbindungen blockieren
   - Corporate Proxy könnte Crypto-Sites blockieren

---

### 5. DRY_RUN Mode funktioniert nicht

**Problem:** System führt Live-Trades aus obwohl DRY_RUN gesetzt ist

**Lösung:**
```powershell
# Explizit DRY_RUN setzen
$env:DRY_RUN = "true"

# Oder in .env Datei
echo "DRY_RUN=true" > .env

# Verifizieren
.\venv\Scripts\python.exe -c "import os; print(os.getenv('DRY_RUN', 'not set'))"
```

---

### 6. Session Store Fehler

**Problem:**
```
ValidationError: Event does not match schema
```

**Lösung:**
1. **Validation deaktivieren (Debugging):**
   ```python
   runner = AutomationRunner(enable_validation=False)
   ```

2. **Schema prüfen:**
   ```powershell
   .\venv\Scripts\python.exe -c "from automation.schemas import EVENT_SCHEMA; print(EVENT_SCHEMA)"
   ```

3. **Session-Dateien löschen:**
   ```powershell
   Remove-Item data\session\* -Force
   ```

---

### 7. VSCode Tasks funktionieren nicht

**Problem:** Tasks werden nicht angezeigt oder schlagen fehl

**Lösung:**
1. **Tasks neu laden:**
   - `Ctrl+Shift+P` → "Tasks: Run Task"

2. **venv existiert:**
   ```powershell
   Test-Path venv\Scripts\python.exe
   ```

3. **PowerShell Execution Policy:**
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

---

### 8. CI/CD Pipeline Fehler

**Problem:** GitHub Actions schlagen fehl

**Lösung:**
1. **Logs prüfen:**
   - GitHub → Actions → Failed Run → Logs

2. **Lokal reproduzieren:**
   ```powershell
   # Gleiche Befehle wie in CI
   .\venv\Scripts\python.exe -m pytest tests/ -v
   ```

3. **Dependencies aktualisieren:**
   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade
   ```

---

### 9. Nightly Job schlägt fehl

**Problem:** Nightly test failed notification

**Lösung:**
1. **Logs prüfen:**
   ```powershell
   Get-Content logs\system.log -Tail 100
   Get-Content logs\errors.log
   ```

2. **Manuell ausführen:**
   ```powershell
   .\scripts\nightly_run.ps1
   ```

3. **GitHub Issue öffnen:** Falls Problem bestehen bleibt

---

### 10. Permissions Fehler (Windows)

**Problem:**
```
PermissionError: [WinError 5] Access is denied
```

**Lösung:**
1. **Als Administrator ausführen:**
   - PowerShell als Administrator öffnen

2. **Antivirus prüfen:**
   - Windows Defender könnte Scripts blockieren
   - Ausnahme für Projekt-Verzeichnis hinzufügen

3. **Datei-Locks lösen:**
   ```powershell
   # Prozesse finden die Dateien locken
   handle.exe -a <dateiname>
   ```

---

## 🔍 Debugging

### Logging aktivieren

**Erhöhtes Log-Level:**
```python
from system.log_system.logger import configure_logging, LogLevel

configure_logging(
    level=LogLevel.DEBUG,  # Statt INFO
    enable_console=True,
    enable_json=True
)
```

**Environment Variable:**
```powershell
$env:LOG_LEVEL = "DEBUG"
```

---

### Trace Mode

**Aktivieren:**
```powershell
$env:PYTHONVERBOSE = "1"
.\venv\Scripts\python.exe system\orchestrator.py
```

---

### Interactive Debugging

**Mit pdb:**
```python
import pdb; pdb.set_trace()
```

**Mit VS Code:**
1. `.vscode/launch.json` erstellen
2. Breakpoints setzen
3. F5 drücken

---

## 📊 System Health Check

**Script ausführen:**
```powershell
.\venv\Scripts\python.exe -c "
from system.orchestrator import SystemOrchestrator
orch = SystemOrchestrator(dry_run=True)
print('Health Check:', orch._health_check('system'))
"
```

---

## 🆘 Hilfe bekommen

### 1. GitHub Issues
- **URL:** https://github.com/CallMeMell/ai.traiding/issues
- **Template:** Bug Report nutzen
- **Logs beifügen:** `logs/system.log` und `logs/errors.log`

### 2. Logs sammeln
```powershell
# Alle relevanten Logs sammeln
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path logs\*.log -DestinationPath "logs_$timestamp.zip"
```

### 3. System-Informationen sammeln
```powershell
# System-Info
python --version
pip list
Get-ComputerInfo | Select-Object CsName, WindowsVersion, OsArchitecture
```

---

## 📚 Weitere Ressourcen

- **[System Architecture](SYSTEM_ARCHITECTURE.md)** - System-Übersicht
- **[README.md](../README.md)** - Setup & Usage
- **[CHANGELOG.md](../CHANGELOG.md)** - Änderungshistorie

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
