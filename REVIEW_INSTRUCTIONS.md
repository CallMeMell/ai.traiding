# 📋 Repository Review Instructions

**Guidance for GitHub Copilot und menschliche Reviewer**

Dieses Dokument beschreibt die wichtigsten Erwartungen und Standards für das Reviewen von Pull Requests in diesem Repository.

## 🎯 Review Schwerpunkte

### ✅ Windows-First Entwicklung
Dieses Repository priorisiert die **Windows-Entwicklung** mit PowerShell-First-Tooling:

- **Virtuelle Umgebung**: Code soll `venv\Scripts\python.exe` direkt nutzen (Windows-Pfade)
  - ✅ Gut: `.\\venv\Scripts\python.exe -m pytest`
  - ❌ Vermeiden: `source venv/bin/activate && python -m pytest`
- **python-dotenv CLI**: Environment-Variablen sollen mit python-dotenv CLI und `--override` geladen werden
  - ✅ Gut: `dotenv -f .env --override run python script.py`
  - ❌ Vermeiden: Manuelles `.env`-Parsing in Skripten
- **PowerShell-Skripte**: Shell-Skripte sollten bevorzugt PowerShell (`.ps1`) sein

### ✅ Sicherheit & Konfigurations-Defaults

- **DRY_RUN Modus**: Alle Trading-Operationen müssen standardmäßig auf `DRY_RUN=true` stehen
  - Echter Handel nur als Opt-In
  - Dokumentation muss diesen Default klar nennen
- **Environment Files**: Immer `.env` für sensible Konfiguration nutzen
  - Niemals echte `.env` Dateien committen (nur `.env.example`)
  - python-dotenv zum Laden verwenden
- **Port-Konfiguration**: Port 8501 soll für Streamlit-View-Session automatisch weitergeleitet werden
  - VS Code: `portsAttributes` für 8501 konfigurieren

### ✅ Code-Qualität & Tests

- **Keine Trading-Logik-Änderung**: Ohne explizite Angabe keine Trading-Logik ändern
- **Tests**: Kritische Funktionen sollen getestet sein
  - Fokus auf neue Features/Bugfixes
  - Bestehende Tests müssen bestehen
- **Dokumentation**:
  - Änderungen mit Nutzer-Auswirkung müssen dokumentiert werden
  - Deutsch bevorzugt
  - Windows-Anleitung zuerst

### ✅ Architektur & Wartbarkeit

- **DRY-Prinzip**: Code-Duplikate vermeiden
- **Fehlerbehandlung**: Kritische Pfade mit Fehlerbehandlung versehen
- **Logging**: Bestehende Logging-Struktur nutzen

## 🚫 Nicht-blockierende Themen

Folgende Punkte blockieren keine Reviews, können später behandelt werden:
- Performance-Optimierung (sofern nicht kritisch)
- UI/UX-Verbesserungen (sofern kein Defekt)
- Zusätzliche Features (wenn nicht im PR genannt)
- Code-Stil (außer bei starker Unleserlichkeit)
- Vollständige Testabdeckung (Kritische Pfade im Fokus)
- Linux/macOS-spezifische Erweiterungen (Windows zuerst)

## 📝 Review Checkliste

- [ ] Windows-Kompatibilität
- [ ] Direkter venv-Aufruf
- [ ] python-dotenv CLI mit --override
- [ ] DRY_RUN Default
- [ ] Keine Secrets
- [ ] Tests bestehen
- [ ] Doku für Nutzer-Änderungen
- [ ] Keine Trading-Logik-Änderung (sofern nicht gewünscht)

## 🔍 PRs lokal testen (Windows)

```powershell
# PR-Branch clonen
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
git checkout pr-<PR_NUMBER>

# Execution Policy setzen
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Dev Live Session starten
.\scripts\start_live.ps1

# Oder VS Code Tasks nutzen
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Dev: Live Session"
```

## 💡 Tipps für Contributor

- Kleine, fokussierte PRs
- Klare Beschreibung der Änderungen
- Test auf Windows PowerShell
- Konventionen einhalten
- Doku aktualisieren

---

**Made for Windows ⭐ | PowerShell-First | python-dotenv CLI | DRY_RUN Default**