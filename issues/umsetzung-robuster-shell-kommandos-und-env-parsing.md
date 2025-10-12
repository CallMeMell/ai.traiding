# Umsetzung robuster Shell-Kommandos und .env-Parsing

## Beschreibung
Dieses Issue dokumentiert die notwendige Umstellung auf robuste Shell-Kommandos und das sichere Laden von Umgebungsvariablen mittels python-dotenv, wie im Pull Request #65 und der Datei TASKS_JSON_FIXES.md beschrieben.

### Aufgaben
- Tasks in `.vscode/tasks.json` auf direkte venv-Python-Aufrufe und python-dotenv CLI umstellen
- Unsichere Shell- und .env-Parsing-Konstrukte entfernen
- Cross-Plattform-Kompatibilität sicherstellen
- DRY_RUN-Standard für alle Trading-Operationen
- README und Dokumentation für Änderungen aktualisieren

## Hintergrund
PR #65 und TASKS_JSON_FIXES.md liefern wichtige Hinweise für die Umsetzung. Ziel ist eine zuverlässige, sichere und Windows-first Entwicklungsumgebung.
