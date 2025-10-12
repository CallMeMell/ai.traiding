# Issue: Umsetzung robuster Shell-Kommandos und .env-Parsing

## Beschreibung
Dieses Issue dokumentiert die Umsetzung robuster Shell-Kommandos und des .env-Parsing, wie im Pull Request #65 beschrieben, sowie die Hinweise aus der Datei TASKS_JSON_FIXES.md.

### Aufgaben
- Alle Tasks in `.vscode/tasks.json` sollen auf `python-dotenv` und direkte `venv` Python-Aufrufe umgestellt werden.
- Ziel ist es, die Cross-Plattform-Kompatibilität zu verbessern und zuverlässige Umgebungsvariablen zu gewährleisten.

## Hintergrund
Der Pull Request #65 liefert wichtige Änderungen und Verbesserungen, die für die zukünftige Entwicklung und Wartung des Projekts entscheidend sind. Die Informationen aus der TASKS_JSON_FIXES.md Datei bieten weitere wertvolle Hinweise zur Implementierung dieser Änderungen.