## Test Coverage auf ≥85% erhöhen

### Beschreibung:
Die aktuelle Testabdeckung liegt bei 77.3%. Ziel ist es, die Coverage auf mindestens 85% zu bringen.

### Schritte:
1. Führe lokal einen Coverage-Report aus (z.B. `coverage report -m`), um alle ungetesteten Codebereiche zu identifizieren.
2. Schreibe neue Tests für ungetestete oder schlecht getestete Funktionen, Methoden und Branches.
3. Überarbeite bestehende Tests, um auch Randfälle und Fehlerbehandlungen abzudecken.
4. Wiederhole den Coverage-Report, bis der Wert mindestens 85% erreicht.
5. Dokumentiere relevante Änderungen und Commit-Nachrichten.
6. Erstelle einen Pull Request mit dem Ziel „Coverage ≥85%“.

### Optional:
Das Coverage-Threshold in der Workflow-Datei `.github/workflows/feature-pr-coverage.yml` (ref: 1e9463bc45ec2b83e500f4dc6797761d01ad6cfd) von 78% auf 85% anheben, sobald die höhere Abdeckung erreicht ist.