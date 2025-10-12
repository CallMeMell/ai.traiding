# Fehler im CI-Workflow: "undefined name 'os'" beim Zugriff auf Umgebungsvariable

## Beschreibung

Im CI-Workflow tritt folgender Fehler auf:
```
self.is_dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
F821 undefined name 'os'
```
Das Modul `os` wird verwendet, aber nicht importiert. Dadurch schlägt der Build fehl.

## Lösungsvorschlag

Füge am Anfang der betroffenen Python-Datei folgende Zeile hinzu:
```python
import os
```

Dadurch wird das Modul korrekt eingebunden und der Fehler behoben. Nach dem Fix sollte der CI-Workflow wieder erfolgreich durchlaufen.