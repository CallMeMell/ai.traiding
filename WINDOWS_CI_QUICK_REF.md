# 🚀 Windows CI Quick Reference

**Schnellreferenz für Windows CI-Fehler**

---

## 🔥 Häufigste Fehler

### PermissionError: [WinError 32]

**Fehler:**
```
PermissionError: [WinError 32] The process cannot access the file 
because it is being used by another process
```

**Schnell-Fix:**
```python
# In deiner Test-Klasse

import logging

def _cleanup_logging_handlers(self):
    """Close all logging handlers."""
    loggers = [logging.getLogger()] + [
        logging.getLogger(name) 
        for name in logging.root.manager.loggerDict
    ]
    for logger in loggers:
        for handler in logger.handlers[:]:
            try:
                handler.close()
            except Exception:
                pass
            try:
                logger.removeHandler(handler)
            except Exception:
                pass
    logging.getLogger().handlers.clear()

def tearDown(self):
    """Clean up test environment"""
    self._cleanup_logging_handlers()  # ← VOR rmtree!
    shutil.rmtree(self.test_dir, ignore_errors=True)
```

**Siehe:** [CI_WINDOWS_FIX_GUIDE.md](CI_WINDOWS_FIX_GUIDE.md)

---

### PathError / FileNotFoundError

**Fehler:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/...'
```

**Schnell-Fix:**
```python
# ❌ Vermeiden
path = '/tmp/myfile.txt'

# ✅ Nutze
import tempfile
path = tempfile.mktemp(suffix='.txt')
# oder
import os
path = os.path.join(tempfile.gettempdir(), 'myfile.txt')
```

---

### UnicodeDecodeError

**Fehler:**
```
UnicodeDecodeError: 'charmap' codec can't decode byte
```

**Schnell-Fix:**
```python
# ❌ Vermeiden
with open('file.txt', 'r') as f:
    content = f.read()

# ✅ Explizites Encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

---

## 🔍 Diagnose

### 1. CI-Logs abrufen

```bash
# URL
https://github.com/CallMeMell/ai.traiding/actions

# Im Log suchen nach:
"FAILED"
"PermissionError"
"[WinError"
```

### 2. Lokal reproduzieren (Windows)

```powershell
# Einzelner Test
.\venv\Scripts\python.exe -m pytest tests/test_file.py::TestClass::test_method -v

# Alle Tests
.\venv\Scripts\python.exe -m pytest tests/ -v

# Mit Debugging
.\venv\Scripts\python.exe -m pytest tests/ -vv -s --pdb
```

---

## 🛠️ Häufige Commands

### Testing

```powershell
# Schnell-Test
.\venv\Scripts\python.exe -m pytest tests/ -v

# Mit Coverage
.\venv\Scripts\python.exe -m pytest tests/ -v --cov=. --cov-report=term

# Nur fehlgeschlagene Tests
.\venv\Scripts\python.exe -m pytest tests/ --lf -v

# Mehrfach-Test (Stabilität)
for ($i=1; $i -le 3; $i++) {
    .\venv\Scripts\python.exe -m pytest tests/ -v
}
```

### Git

```powershell
# Status prüfen
git status

# Änderungen stagen und committen
git add .
git commit -m "Fix Windows PermissionError in tests"

# Push
git push origin <branch-name>
```

---

## 📚 Dokumentation

### Nach Problem

| Problem | Siehe |
|---------|-------|
| PermissionError | [CI_WINDOWS_FIX_GUIDE.md](CI_WINDOWS_FIX_GUIDE.md) |
| Workflow allgemein | [docs/CI_WINDOWS_WORKFLOW.md](docs/CI_WINDOWS_WORKFLOW.md) |
| Alle Guides | [WINDOWS_CI_INDEX.md](WINDOWS_CI_INDEX.md) |
| Troubleshooting | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |

### Nach Rolle

| Rolle | Start hier |
|-------|-----------|
| Contributor | [CI_WINDOWS_FIX_GUIDE.md](CI_WINDOWS_FIX_GUIDE.md) |
| Reviewer | [REVIEW_INSTRUCTIONS.md](REVIEW_INSTRUCTIONS.md) |
| Maintainer | [docs/CI_WINDOWS_WORKFLOW.md](docs/CI_WINDOWS_WORKFLOW.md) |
| Newcomer | [WINDOWS_CI_INDEX.md](WINDOWS_CI_INDEX.md) |

---

## ✅ Best Practices

### DO

- ✅ `pathlib` oder `os.path.join()` für Pfade
- ✅ `encoding='utf-8'` beim Datei-Öffnen
- ✅ Context Manager (`with`) für Ressourcen
- ✅ Handler schließen vor `rmtree()`
- ✅ `ignore_errors=True` bei `shutil.rmtree()`
- ✅ Lokal auf Windows testen

### DON'T

- ❌ Hardcoded `/tmp/` Pfade
- ❌ Implizite Encodings
- ❌ Ressourcen nicht schließen
- ❌ Windows-Tests skippen
- ❌ `except: pass` ohne Grund

---

## 🆘 Hilfe

### Schnelle Hilfe

1. **[WINDOWS_CI_INDEX.md](WINDOWS_CI_INDEX.md)** - Alle Guides
2. **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Allgemeine Tipps
3. **[ISSUES.md](ISSUES.md)** - Bekannte Probleme

### Community

- **GitHub Issues** - Neue Probleme melden
- **Pull Requests** - Code-Review anfordern
- **Discussions** - Fragen stellen

---

## 📋 Checkliste

### Fix implementieren

- [ ] Fehler in CI-Logs identifiziert
- [ ] Relevante Dokumentation gelesen
- [ ] Fix implementiert
- [ ] Lokal getestet (mindestens 3x)
- [ ] Committed und gepushed
- [ ] CI-Tests überwacht
- [ ] Dokumentation aktualisiert

---

**Made for Windows ⭐ | PowerShell-First**  
**Vollständige Docs:** [WINDOWS_CI_INDEX.md](WINDOWS_CI_INDEX.md)
