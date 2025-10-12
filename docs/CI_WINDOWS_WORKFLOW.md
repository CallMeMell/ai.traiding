# 🔄 CI Windows-Fehler Workflow

**Zielgruppe:** Contributors und Maintainer  
**Zweck:** Standardisierter Workflow für die Diagnose und Behebung von Windows CI-Fehlern  
**Version:** 1.0.0

---

## 📊 Workflow-Übersicht

```
┌─────────────────┐
│ CI Failure      │
│ auf Windows     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 1. Logs         │◄────── GitHub Actions → Failed Run → Logs
│    analysieren  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Fehlertyp    │
│    identifizier│
│    en           │
└────────┬────────┘
         │
    ┌────┴────┬─────────────┬──────────────┐
    │         │             │              │
    ▼         ▼             ▼              ▼
┌────────┐ ┌────────┐ ┌────────────┐ ┌────────────┐
│Perm.   │ │Path    │ │Encoding    │ │Andere      │
│Error   │ │Error   │ │Error       │ │Fehler      │
└───┬────┘ └───┬────┘ └─────┬──────┘ └─────┬──────┘
    │          │            │               │
    │          │            │               │
    └──────────┴────────────┴───────────────┘
                     │
                     ▼
         ┌─────────────────────┐
         │ 3. Lösung           │
         │    implementieren   │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ 4. Lokal testen     │
         │    (Windows)        │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ 5. CI-Tests         │
         │    validieren       │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ 6. Dokumentation    │
         │    aktualisieren    │
         └─────────────────────┘
```

---

## 🔍 Schritt 1: Logs analysieren

### A. Zugriff auf CI-Logs

1. Gehe zu: `https://github.com/CallMeMell/ai.traiding/actions`
2. Klicke auf den fehlgeschlagenen Workflow-Run
3. Öffne die fehlgeschlagenen Jobs (rote X-Symbole)
4. Scrolle zum "Run tests" Schritt
5. Suche nach "FAILED" im Log

### B. Relevante Informationen sammeln

Notiere folgende Informationen:

```yaml
Fehlertyp: [PermissionError | PathError | EncodingError | Andere]
Betriebssystem: [windows-latest]
Python-Version: [3.10 | 3.11 | 3.12]
Betroffene Tests: [Liste der fehlgeschlagenen Tests]
Fehlermeldung: [Vollständige Fehlermeldung]
Stack Trace: [Relevanter Teil des Stack Trace]
```

### C. Log-Ausgabe verstehen

**Beispiel Windows PermissionError:**
```
PermissionError: [WinError 32] The process cannot access the file 
because it is being used by another process: 'C:\\Users\\...\\test.log'
```

**Typische Indikatoren:**
- `[WinError 32]` → Datei wird von anderem Prozess verwendet
- `[WinError 5]` → Zugriff verweigert (Permissions)
- `[WinError 3]` → Pfad nicht gefunden
- `UnicodeDecodeError` → Encoding-Problem

---

## 🔍 Schritt 2: Fehlertyp identifizieren

### A. PermissionError ([WinError 32])

**Symptome:**
- Tests schlagen nur auf Windows fehl
- Fehler beim Löschen von Dateien/Verzeichnissen
- Betrifft oft temporäre Dateien
- Häufig in `tearDown()` oder Fixture-Cleanup

**Ursache:**
- Dateien sind noch von Prozessen geöffnet (FileHandler, etc.)
- Windows sperrt geöffnete Dateien

**Lösung:**
- Handler/Connections schließen vor Dateilöschung
- Siehe: `WINDOWS_PERMISSION_ERROR_FIX.md`
- Siehe: `CI_WINDOWS_FIX_GUIDE.md`

### B. PathError / FileNotFoundError ([WinError 3])

**Symptome:**
- Pfade werden nicht gefunden
- Nur auf Windows fehlend

**Ursache:**
- Hardcodierte Linux-Pfade (`/tmp/...`)
- Fehlende Pfad-Normalisierung
- Case-Sensitivity-Probleme

**Lösung:**
```python
# ❌ Vermeiden
path = '/tmp/myfile.txt'

# ✅ Empfohlen
import tempfile
import os

path = os.path.join(tempfile.gettempdir(), 'myfile.txt')
# oder
path = tempfile.mktemp(suffix='.txt')
```

### C. Encoding-Fehler (UnicodeDecodeError)

**Symptome:**
- Fehler beim Lesen von Dateien
- `codec can't decode byte`

**Ursache:**
- Windows verwendet oft andere Encodings
- Dateien ohne explizites Encoding geöffnet

**Lösung:**
```python
# ❌ Vermeiden
with open('file.txt', 'r') as f:
    content = f.read()

# ✅ Empfohlen
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

### D. Andere Windows-spezifische Fehler

**Typische Probleme:**
- Line-Ending-Unterschiede (`\n` vs `\r\n`)
- Case-Sensitivity (Linux case-sensitive, Windows nicht)
- Maximale Pfadlänge (260 Zeichen auf Windows)
- Reserved filenames (`CON`, `PRN`, `AUX`, etc.)

---

## 🔧 Schritt 3: Lösung implementieren

### Allgemeine Prinzipien

#### 1. Cross-Platform Kompatibilität

```python
import os
import sys
import pathlib

# Pfade
path = pathlib.Path('data') / 'file.txt'  # Funktioniert überall

# Temporäre Dateien
import tempfile
temp_dir = tempfile.mkdtemp()  # OS-agnostisch

# Line Endings
text = text.replace('\r\n', '\n').replace('\r', '\n')  # Normalisieren
```

#### 2. Resource Management

```python
# Context Manager nutzen
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
# Datei wird automatisch geschlossen

# Logging Handler
import logging
handler = logging.FileHandler('app.log')
try:
    # Nutze Handler
    pass
finally:
    handler.close()  # Explizit schließen
```

#### 3. Robuste Cleanup-Routinen

```python
import shutil

# ❌ Vermeiden
shutil.rmtree(temp_dir)

# ✅ Empfohlen
shutil.rmtree(temp_dir, ignore_errors=True)

# ✅ Noch besser
def cleanup_directory(path):
    """Remove directory with retries on Windows."""
    import time
    for attempt in range(3):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            if attempt < 2:
                time.sleep(0.5)  # Warte kurz
            else:
                pass  # Ignoriere beim letzten Versuch
```

### Spezifische Lösungen

#### PermissionError bei Logging-Tests

Siehe: `CI_WINDOWS_FIX_GUIDE.md` für vollständige Anleitung

```python
class TestMyFeature(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def _cleanup_logging_handlers(self):
        """Close all logging handlers."""
        import logging
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
        # WICHTIG: Handler schließen VOR rmtree
        self._cleanup_logging_handlers()
        shutil.rmtree(self.test_dir, ignore_errors=True)
```

---

## ✅ Schritt 4: Lokal testen (Windows)

### A. Umgebung vorbereiten

```powershell
# Virtuelle Umgebung aktivieren (nicht mit source!)
# Direkte Nutzung des venv Python

# Dependencies installieren
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pip install pytest pytest-cov
```

### B. Einzelne Tests

```powershell
# Einzelnen Test ausführen
.\venv\Scripts\python.exe -m pytest tests/test_utils.py::TestSetupLogging::test_setup_logging_creates_log_file -v

# Einzelne Testklasse
.\venv\Scripts\python.exe -m pytest tests/test_utils.py::TestSetupLogging -v

# Einzelne Datei
.\venv\Scripts\python.exe -m pytest tests/test_utils.py -v
```

### C. Alle Tests

```powershell
# Alle Tests mit Verbose-Ausgabe
.\venv\Scripts\python.exe -m pytest tests/ -v

# Mit Coverage
.\venv\Scripts\python.exe -m pytest tests/ -v --cov=. --cov-report=term-missing

# Mehrfaches Ausführen (Stabilität testen)
for ($i=1; $i -le 5; $i++) {
    Write-Host "Run $i" -ForegroundColor Cyan
    .\venv\Scripts\python.exe -m pytest tests/ -v
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed on run $i" -ForegroundColor Red
        break
    }
}
```

### D. Debugging

```powershell
# Mit pytest debugging
.\venv\Scripts\python.exe -m pytest tests/test_utils.py -v --pdb

# Mit detaillierter Ausgabe
.\venv\Scripts\python.exe -m pytest tests/test_utils.py -vv -s

# Nur fehlgeschlagene Tests erneut ausführen
.\venv\Scripts\python.exe -m pytest tests/ --lf -v
```

---

## 🚀 Schritt 5: CI-Tests validieren

### A. Änderungen pushen

```powershell
# Status prüfen
git status

# Änderungen stagen
git add .

# Committen mit aussagekräftiger Message
git commit -m "Fix Windows PermissionError in TestSetupLogging"

# Pushen
git push origin <branch-name>
```

### B. CI-Run überwachen

1. Gehe zu: `https://github.com/CallMeMell/ai.traiding/actions`
2. Finde den neuesten Run für deinen Branch
3. Warte bis alle Jobs abgeschlossen sind
4. Prüfe Status:
   - ✅ Grünes Häkchen = Alle Tests bestanden
   - ❌ Rotes X = Tests fehlgeschlagen
   - 🟡 Gelber Kreis = Tests laufen noch

### C. Ergebnisse überprüfen

**Windows-Jobs prüfen:**
- `Test on windows-latest (Python 3.10)`
- `Test on windows-latest (Python 3.11)`
- `Test on windows-latest (Python 3.12)`

**Bei Fehler:**
- Logs analysieren (zurück zu Schritt 1)
- Lokal erneut testen
- Fix anpassen

**Bei Erfolg:**
- Screenshot der erfolgreichen CI-Checks machen
- Weiter zu Schritt 6

---

## 📚 Schritt 6: Dokumentation aktualisieren

### A. ISSUES.md aktualisieren

Füge einen Eintrag hinzu:

```markdown
**Titel:** [Kurze Beschreibung] ✅ **BEHOBEN**

**Beschreibung:**
[Beschreibe das Problem und wo es auftrat]

**Lösung:**
[Beschreibe die implementierte Lösung]

**Ergebnis:**
[Beschreibe die Testergebnisse]

**Referenzen:**
- PR #[Nummer]
- CI Run #[ID]
```

### B. Relevante Guides aktualisieren

Je nach Fehlertyp:

- `WINDOWS_PERMISSION_ERROR_FIX.md` - Für PermissionError
- `docs/TROUBLESHOOTING.md` - Für neue Fehlertypen
- `CI_WINDOWS_FIX_GUIDE.md` - Für neue Fix-Patterns

### C. Code-Kommentare

```python
# Add explanatory comments for non-obvious fixes
def tearDown(self):
    """Clean up test environment"""
    # Close handlers before rmtree to prevent PermissionError on Windows
    # See: WINDOWS_PERMISSION_ERROR_FIX.md
    self._cleanup_logging_handlers()
    shutil.rmtree(self.test_dir, ignore_errors=True)
```

---

## 📋 Checkliste

Verwende diese Checkliste für jeden Windows CI-Fehler:

### Analyse
- [ ] CI-Logs heruntergeladen/angesehen
- [ ] Fehlertyp identifiziert
- [ ] Betroffene Tests dokumentiert
- [ ] Root Cause ermittelt

### Lösung
- [ ] Fix implementiert
- [ ] Code-Review durchgeführt (selbst oder Peer)
- [ ] Kommentare hinzugefügt

### Testing
- [ ] Lokal auf Windows getestet
- [ ] Mehrfache Durchläufe bestanden (mindestens 3x)
- [ ] CI-Tests erfolgreich
- [ ] Screenshot der erfolgreichen CI-Checks erstellt

### Dokumentation
- [ ] ISSUES.md aktualisiert
- [ ] Relevante Guides aktualisiert
- [ ] Code-Kommentare hinzugefügt
- [ ] PR-Beschreibung aktualisiert

---

## 🎯 Best Practices

### DO ✅

1. **Cross-Platform denken**
   - Nutze `pathlib` oder `os.path.join()` für Pfade
   - Nutze `tempfile` für temporäre Dateien
   - Explizite Encodings (`encoding='utf-8'`)

2. **Resource Management**
   - Context Manager nutzen (`with` statement)
   - Explizites Cleanup in `tearDown()` oder Fixtures
   - `ignore_errors=True` bei `shutil.rmtree()`

3. **Testen**
   - Lokal auf Windows testen vor dem Push
   - Mehrfache Durchläufe für Stabilität
   - CI-Results überprüfen

4. **Dokumentieren**
   - Aussagekräftige Commit-Messages
   - Code-Kommentare für non-obvious Fixes
   - Dokumentation aktualisieren

### DON'T ❌

1. **Keine hardcoded Pfade**
   - `❌ '/tmp/file.txt'`
   - `✅ tempfile.mktemp()`

2. **Keine impliziten Annahmen**
   - `❌ Dateien automatisch geschlossen`
   - `✅ Explizites `close()` oder Context Manager`

3. **Keine ignorierenden Fixes**
   - `❌ try: except: pass` ohne Grund
   - `✅ Verstehe das Problem, dann fixe es richtig`

4. **Keine Windows-Ignoration**
   - `❌ @pytest.mark.skip(sys.platform == 'win32')`
   - `✅ Finde einen Cross-Platform Fix`

---

## 📖 Referenzen

### Interne Dokumentation

- **`WINDOWS_PERMISSION_ERROR_FIX.md`** - PermissionError Fix-Guide
- **`CI_WINDOWS_FIX_GUIDE.md`** - Schritt-für-Schritt Anleitung
- **`CI_WINDOWS_FAILURES_ANALYSIS.md`** - Vollständige Fehleranalyse
- **`docs/TROUBLESHOOTING.md`** - Allgemeine Troubleshooting-Tipps
- **`REVIEW_INSTRUCTIONS.md`** - Windows-First Development Guidelines

### Code-Referenzen

- **`tests/conftest.py`** - Globales `cleanup_logging()` Fixture
- **`tests/test_logger.py`** - Referenzimplementierung für Logging-Tests
- **`tests/test_binance_adapter.py`** - Weitere Test-Patterns

### Externe Ressourcen

- [Python tempfile Documentation](https://docs.python.org/3/library/tempfile.html)
- [Python pathlib Documentation](https://docs.python.org/3/library/pathlib.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Windows File Locking](https://learn.microsoft.com/en-us/windows/win32/fileio/file-locking)

---

## 🆘 Hilfe benötigt?

Falls du bei einem Windows CI-Fehler nicht weiterkommst:

1. **Prüfe bestehende Dokumentation**
   - Durchsuche `ISSUES.md` nach ähnlichen Problemen
   - Schaue in relevante Guides

2. **Debugging-Tipps nutzen**
   - Siehe "Debugging-Tipps" Abschnitt in diesem Dokument
   - Nutze `pytest -vv -s` für detaillierte Ausgaben

3. **Issue erstellen**
   - Nutze das "Bug Report" Template
   - Füge CI-Logs bei
   - Dokumentiere bereits versuchte Lösungen

4. **Community fragen**
   - GitHub Discussions
   - PR-Comments für spezifische Probleme

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-10-12  
**Made for Windows ⭐ | PowerShell-First | CI-First Development**
