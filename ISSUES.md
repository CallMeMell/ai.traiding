**Titel:** Windows PermissionError beim Logging in Tests

**Beschreibung:**
Im CI-Job treten folgende Fehler auf:

```
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
```

Die Fehler entstehen in mehreren Logging-Tests (z.B. test_setup_logging_creates_log_directory, test_setup_logging_creates_log_file, test_setup_logging_creates_logger, test_setup_logging_respects_log_level). Ursache ist vermutlich, dass FileHandler in Python nicht korrekt geschlossen werden und dadurch beim parallelen Zugriff auf die Logdateien Konflikte entstehen. 

**Lösungsvorschlag:**
- Nach jedem Test alle Logger-Handler schließen und entfernen, z.B. in der tearDown-Methode:

```python
import logging
class TestSetupLogging(unittest.TestCase):
    def tearDown(self):
        logger = logging.getLogger("my_logger")
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
```
- Sicherstellen, dass keine Handler offen bleiben und keine Logdateien von mehreren Tests gleichzeitig verwendet werden.

**Referenz:**
- Pull Request: https://github.com/CallMeMell/ai.traiding/pull/155
- Job Log: ref:68f0041b88eb310e5f3e00d6155c6561ddac300c

Bitte prüfen und fixen!