# 🚀 Preflight-Checks - Quick Reference

**Schnellübersicht für Nutzer und Entwickler**

---

## 👤 Für Nutzer

### Live Trading starten (mit automatischem Preflight)

```powershell
# 1. Bestätigung setzen
$env:LIVE_ACK = "I_UNDERSTAND"

# 2. Trading starten (Preflight läuft automatisch!)
.\scripts\start_live_prod.ps1
```

**Oder via VS Code:**
```
Ctrl+Shift+P → "Tasks: Run Task" → "Live: Runner"
```

### Preflight manuell testen (ohne Trading)

```powershell
.\venv\Scripts\python.exe scripts\live_preflight.py
```

### Was passiert automatisch?

✅ **8 Checks laufen vor jedem Trading-Start:**
1. Environment Variables (LIVE_ACK, DRY_RUN, etc.)
2. API Credentials (vorhanden & gültig)
3. Time Sync (max 1000ms Abweichung)
4. Exchange Info (Trading-Pairs gültig)
5. Account Balance (mindestens 10 USDT)
6. Risk Configuration (Parameter in gültigen Ranges)
7. Order Types Support (Exchange unterstützt konfigurierte Types)
8. Kill Switch Status (informational)

### Bei Fehlern

❌ Trading wird NICHT gestartet  
📋 Klare Fehlermeldungen im Terminal  
🔧 Fehler beheben und erneut versuchen  

---

## 👨‍💻 Für Entwickler

### Architektur

```
VS Code Task "Live: Runner"
    ↓
start_live_prod.ps1
    ↓
live_preflight.py (run_all_checks)
    ├─ check_environment()
    ├─ check_credentials()
    ├─ check_time_sync()
    ├─ check_exchange_info()
    ├─ check_account_balance()
    ├─ check_risk_configuration()
    ├─ check_order_types_support()
    └─ check_kill_switch()
    ↓
Exit Code 0 (Success) → automation/runner.py
Exit Code 1 (Failure) → Abort
```

### Exit Codes

- `0` - Alle Checks bestanden, Trading kann starten
- `1` - Ein oder mehrere Checks fehlgeschlagen, Trading wird blockiert

### Output Format

**Console:**
```
[OK] ✅ Message  # Success
[ERR] ❌ Message # Error
```

**Log File:** `logs/preflight_checks.log`

### Tests

```bash
# Unit Tests (20 Tests)
python test_live_preflight.py

# Integration Tests (15 Tests)
python test_preflight_integration.py

# Alle Tests
python test_live_preflight.py && python test_preflight_integration.py
```

### Dateien

| Datei | Zweck |
|-------|-------|
| `scripts/live_preflight.py` | Preflight-Checks Implementierung |
| `scripts/start_live_prod.ps1` | PowerShell Live Runner |
| `.vscode/tasks.json` | VS Code Task Definition |
| `test_live_preflight.py` | Unit Tests |
| `test_preflight_integration.py` | Integration Tests |
| `logs/preflight_checks.log` | Audit Log |

### Neue Check hinzufügen

```python
def check_my_new_check() -> Tuple[bool, str]:
    """
    Check description.
    
    Returns:
        Tuple of (success, message)
    """
    print("\n🔍 Checking my new check...")
    
    # Perform check
    if condition_ok:
        print_status(STATUS_OK, "Check passed")
        return True, "Check passed"
    else:
        return False, "Error message"

# Add to run_all_checks()
checks = [
    # ... existing checks ...
    ("My New Check", check_my_new_check),
]
```

---

## 📊 Status

| Komponente | Status |
|-----------|--------|
| Implementierung | ✅ Vollständig |
| Tests | ✅ 35/35 bestanden |
| Dokumentation | ✅ Vollständig |
| Integration | ✅ VS Code Task |
| Automatisierung | ✅ 100% |

---

## 🔗 Weitere Dokumentation

- **Setup-Anleitung:** `LIVE_TRADING_SETUP_GUIDE.md`
- **Technische Details:** `PREFLIGHT_CHECKS_ENHANCEMENT_SUMMARY.md`
- **Verifikation:** `PREFLIGHT_INTEGRATION_VERIFICATION.md`
- **Abschlussbericht:** `PREFLIGHT_AUTOMATION_SUMMARY.md`

---

**Letzte Aktualisierung:** 2025-10-10  
**Version:** 1.0
