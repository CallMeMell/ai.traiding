**Titel:** Windows PermissionError beim Logging in Tests ✅ **BEHOBEN**

**Beschreibung:**
Im CI-Job traten folgende Fehler auf:

```
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
```

Die Fehler entstanden in mehreren Logging-Tests (z.B. test_setup_logging_creates_log_directory, test_setup_logging_creates_log_file, test_setup_logging_creates_logger, test_setup_logging_respects_log_level). Ursache war, dass FileHandler in Python nicht korrekt geschlossen wurden und dadurch beim Zugriff auf die Logdateien Konflikte entstanden.

**Lösung (implementiert):**

1. **Globales Cleanup-Fixture in `tests/conftest.py`:**
   - Auto-use fixture `cleanup_logging()` wurde hinzugefügt
   - Wird nach jedem Test automatisch ausgeführt
   - Schließt und entfernt alle Logger-Handler systematisch

2. **Spezifische Cleanup-Methoden in `tests/test_logger.py`:**
   - `_cleanup_logging_handlers()` in TestConfigureLogging
   - `_cleanup_logging_handlers()` in TestLoggingIntegration
   - Beide Klassen nutzen diese Methode in ihren `temp_log_dir` Fixtures

**Implementierung:**
```python
@pytest.fixture(autouse=True)
def cleanup_logging():
    """Auto-use fixture to clean up logging handlers after each test."""
    yield
    
    # Close and remove all logging handlers after each test
    loggers = [logging.getLogger()] + [
        logging.getLogger(name) for name in logging.root.manager.loggerDict
    ]
    
    for logger in loggers:
        for handler in logger.handlers[:]:
            try:
                handler.close()
            except Exception:
                pass  # Ignore errors during cleanup
            try:
                logger.removeHandler(handler)
            except Exception:
                pass  # Ignore errors during cleanup
    
    # Clear root logger handler list
    logging.getLogger().handlers.clear()
```

**Testergebnisse:**
- Alle 141 Tests bestehen erfolgreich
- Mehrfache Test-Durchläufe zeigen keine PermissionError mehr
- Handler werden ordnungsgemäß geschlossen und Dateien freigegeben

**Referenz:**
- Pull Request: https://github.com/CallMeMell/ai.traiding/pull/155
- Job Log: ref:68f0041b88eb310e5f3e00d6155c6561ddac300c
- Fix Commit: ref:3c97130