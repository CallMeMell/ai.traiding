# 🤝 Contributing to ai.traiding

Vielen Dank für dein Interesse, zum ai.traiding Projekt beizutragen! Dieses Dokument beschreibt die Richtlinien und Best Practices für Beiträge.

---

## 📋 Inhaltsverzeichnis

- [Code of Conduct](#code-of-conduct)
- [Wie kann ich beitragen?](#wie-kann-ich-beitragen)
- [Development Setup](#development-setup)
- [Workflow & Branches](#workflow--branches)
- [Code Style & Standards](#code-style--standards)
- [Testing & QA](#testing--qa)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Dokumentation](#dokumentation)

---

## 📜 Code of Conduct

Wir erwarten von allen Contributors:

- ✅ Respektvoller und konstruktiver Umgang
- ✅ Fokus auf technische Qualität und Lösungen
- ✅ Offenheit für Feedback und Code-Reviews
- ✅ Keine persönlichen Angriffe oder unangemessene Kommentare

Bei Verstößen: Melde das Problem an die Maintainer über GitHub Issues (privat).

---

## 🎯 Wie kann ich beitragen?

### 1. 🐛 Bug Reports

Gefunden einen Bug? Erstelle ein Issue mit:

- **Titel**: Kurze, prägnante Beschreibung
- **Reproduktion**: Schritt-für-Schritt Anleitung
- **Expected vs. Actual**: Was sollte passieren? Was passiert tatsächlich?
- **Environment**: OS, Python-Version, relevante Konfiguration
- **Logs**: Relevante Log-Ausgaben (ohne API-Keys!)

**Verwende das Issue Template**: `Bug Report` (falls vorhanden)

### 2. ✨ Feature Requests

Idee für ein neues Feature? Öffne ein Issue mit:

- **Problem**: Welches Problem löst das Feature?
- **Lösung**: Wie sollte die Lösung aussehen?
- **Alternativen**: Welche anderen Ansätze gibt es?
- **Use Case**: Wer profitiert davon? Warum ist es wichtig?

**Verwende das Issue Template**: `[Auto] Automation Task` oder `[Manual] Manual Task`

### 3. 🔧 Code Contributions

Bereit zu coden? Folge dem [Pull Request Process](#pull-request-process).

### 4. 📖 Dokumentation

Dokumentation verbessern ist immer willkommen:

- README.md Klarstellungen
- Code-Kommentare
- Guides und Tutorials
- API-Dokumentation

---

## 🛠️ Development Setup

### Windows (PowerShell) - Empfohlen ⭐

**1. Repository klonen:**
```powershell
git clone https://github.com/CallMeMell/ai.traiding.git
cd ai.traiding
```

**2. Virtual Environment erstellen:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**3. Dependencies installieren:**
```powershell
# Production Dependencies
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Development Dependencies (optional)
.\venv\Scripts\python.exe -m pip install pytest pytest-cov black flake8
```

**4. .env Datei erstellen:**
```powershell
Copy-Item .env.example .env
# Bearbeite .env für deine lokale Konfiguration (DRY_RUN=true ist Standard)
```

**5. Tests ausführen:**
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

### Linux / macOS

**1. Repository klonen:**
```bash
git clone https://github.com/CallMeMell/ai.traiding.git
cd ai.traiding
```

**2. Virtual Environment erstellen:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Dependencies installieren:**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8  # Dev dependencies
```

**4. .env Datei erstellen:**
```bash
cp .env.example .env
# Edit .env für lokale Konfiguration
```

**5. Tests ausführen:**
```bash
python -m pytest tests/ -v
```

---

## 🌿 Workflow & Branches

### Branch-Strategie

- **`main`**: Produktions-Branch (stable)
- **`dev`**: Development-Branch (aktuelle Features)
- **`feature/*`**: Feature-Branches für neue Features
- **`fix/*`**: Bugfix-Branches
- **`docs/*`**: Dokumentations-Branches

### Development Workflow

**1. Branch erstellen:**
```powershell
# Windows PowerShell
git checkout dev
git pull origin dev
git checkout -b feature/mein-feature-name
```

**2. Änderungen commiten:**
```powershell
git add .
git commit -m "feat: Add new feature XYZ

- Implemented feature XYZ
- Added tests for feature XYZ
- Updated documentation
"
```

**3. Push und PR erstellen:**
```powershell
git push origin feature/mein-feature-name
# Dann erstelle Pull Request auf GitHub
```

### Commit Message Konventionen

Wir nutzen [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Neues Feature
- `fix`: Bugfix
- `docs`: Dokumentation
- `style`: Code-Formatierung (keine Logik-Änderungen)
- `refactor`: Code-Refactoring (keine Features/Fixes)
- `test`: Tests hinzufügen/ändern
- `chore`: Build, Dependencies, Tooling

**Beispiele:**
```
feat(binance): Add retry logic with exponential backoff
fix(runner): Handle NoneType in session_store.get_events()
docs(readme): Add ENV variable reference table
test(adapter): Add unit tests for BinanceAdapter
```

---

## 🎨 Code Style & Standards

### Python Code Style

Wir folgen **PEP 8** mit einigen Anpassungen:

- **Line Length**: Max 100 Zeichen (nicht 79)
- **Indentation**: 4 Spaces
- **Quotes**: Double quotes `"` bevorzugt
- **Imports**: Gruppiert (stdlib, third-party, local)

**Formatierung mit Black:**
```powershell
# Windows
.\venv\Scripts\python.exe -m black . --line-length 100

# Linux/macOS
python -m black . --line-length 100
```

**Linting mit Flake8:**
```powershell
# Windows
.\venv\Scripts\python.exe -m flake8 . --max-line-length=100 --extend-ignore=E203,W503

# Linux/macOS
python -m flake8 . --max-line-length=100 --extend-ignore=E203,W503
```

### Code-Qualität

**✅ Best Practices:**
- **DRY** (Don't Repeat Yourself): Vermeide Code-Duplizierung
- **SOLID-Prinzipien**: Besonders Single Responsibility
- **Type Hints**: Nutze Type Hints für Funktionen/Methoden
- **Docstrings**: Dokumentiere öffentliche Funktionen/Klassen
- **Error Handling**: Try-Except für kritische Bereiche
- **Logging**: Nutze das zentrale Logging-System

**❌ Vermeide:**
- Globale Variablen
- Magic Numbers (nutze Konstanten)
- Tief verschachtelte Logik (max 3-4 Ebenen)
- Hardcoded Paths (nutze `pathlib` oder relative Pfade)
- API-Keys oder Secrets im Code

### Beispiel: Guter Code

```python
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_moving_average(
    prices: List[float],
    window_size: int = 20
) -> Optional[float]:
    """
    Calculate moving average for given price list.
    
    Args:
        prices: List of price values
        window_size: Number of periods for MA calculation
        
    Returns:
        Moving average value or None if insufficient data
    """
    if len(prices) < window_size:
        logger.warning(f"Insufficient data for MA calculation: {len(prices)} < {window_size}")
        return None
    
    recent_prices = prices[-window_size:]
    moving_average = sum(recent_prices) / window_size
    
    logger.debug(f"MA({window_size}): {moving_average:.2f}")
    return moving_average
```

---

## 🧪 Testing & QA

### Test-Strategie

Wir nutzen **pytest** für alle Tests:

- **Unit Tests**: Einzelne Funktionen/Klassen isoliert testen
- **Integration Tests**: Module zusammen testen
- **Smoke Tests**: Kritische Pfade durchlaufen (Runner, View)

### Tests ausführen

**Alle Tests:**
```powershell
# Windows
.\venv\Scripts\python.exe -m pytest tests/ -v

# Linux/macOS
python -m pytest tests/ -v
```

**Spezifische Test-Datei:**
```powershell
.\venv\Scripts\python.exe -m pytest tests/test_config.py -v
```

**Mit Coverage:**
```powershell
.\venv\Scripts\python.exe -m pytest tests/ --cov=. --cov-report=html
# Öffne htmlcov/index.html im Browser
```

### Test-Anforderungen

**Für neue Features:**
- ✅ Mindestens 1 Unit Test pro neue Funktion
- ✅ Edge Cases abdecken (None, leere Listen, etc.)
- ✅ Happy Path + Error Path

**Für Bugfixes:**
- ✅ Test der den Bug reproduziert (sollte vor Fix fehlschlagen)
- ✅ Test sollte nach Fix erfolgreich sein

**Test-Struktur:**
```python
import pytest
from mymodule import my_function

def test_my_function_success():
    """Test successful case."""
    result = my_function(valid_input)
    assert result == expected_output

def test_my_function_empty_input():
    """Test with empty input."""
    result = my_function([])
    assert result is None

def test_my_function_invalid_type():
    """Test with invalid type."""
    with pytest.raises(TypeError):
        my_function("invalid")
```

### QA Checklist vor PR

- [ ] **Alle Tests laufen durch**: `pytest tests/ -v`
- [ ] **Keine Linting-Fehler**: `flake8 .`
- [ ] **Code formatiert**: `black .`
- [ ] **Neue Tests hinzugefügt** (falls Feature/Bugfix)
- [ ] **Dokumentation aktualisiert** (README, Docstrings)
- [ ] **Keine Secrets im Code** (API-Keys, Passwörter)
- [ ] **.env nicht committet** (nur .env.example)
- [ ] **Manuelle Tests durchgeführt** (falls UI/CLI-Änderungen)

---

## 🔄 Pull Request Process

### 1. PR erstellen

**Titel:** Verwende Conventional Commits Format
```
feat(binance): Add retry logic with exponential backoff
```

**Beschreibung:** Nutze das PR-Template
```markdown
## 🎯 Änderungen

- Implemented retry logic for Binance API calls
- Added exponential backoff (1s, 2s, 4s, 8s)
- Updated BinanceAdapter tests

## 🧪 Tests

- [x] Unit tests added (`test_binance_retry.py`)
- [x] All existing tests pass
- [x] Manual testing completed

## 📋 Checklist

- [x] Code follows project style guidelines
- [x] Tests added/updated
- [x] Documentation updated
- [x] No secrets or API keys in code
- [x] PR targets correct branch (`dev`)

## 📸 Screenshots (falls UI-Änderungen)

[Screenshot einfügen]
```

### 2. PR Review

**Reviewer prüfen:**
- ✅ Code-Qualität und Style
- ✅ Tests vorhanden und sinnvoll
- ✅ Keine Breaking Changes (außer dokumentiert)
- ✅ Dokumentation aktualisiert
- ✅ Keine Sicherheitsprobleme

**Contributor reagiert auf Feedback:**
- Änderungen umsetzen
- Commits pushen (werden automatisch zum PR hinzugefügt)
- Review erneut anfordern

### 3. Merge

Nach Approval:
- **Squash and Merge** bevorzugt (für saubere History)
- Commit-Message editieren (falls nötig)
- PR wird in `dev` gemergt
- Branch löschen nach Merge

---

## 📝 Issue Guidelines

### Issue erstellen

Wir nutzen **GitHub Issue Forms** für standardisierte Issues:

**Verfügbare Templates:**

1. **[Auto] Automation Task** - Für automatisierte Aufgaben
   - Outcome-orientierter Titel
   - Messbare Acceptance Criteria
   - Klar definierter Scope

2. **[Manual] Manual Task** - Für manuelle Schritte
   - Schritt-für-Schritt Checklist
   - Proof/Nachweis für Abschluss
   - Voraussetzungen dokumentiert

3. **[Epic] Epic Tracking** - Für größere Initiativen
   - Milestones und Sub-Issues
   - Definition of Done (DoD)
   - Success Metrics

**Beispiel-Titel:**
- ✅ `[Auto] Live-Observability mit strukturierten Events und Real-time Monitoring`
- ✅ `[Manual] API Keys für Binance Testnet einrichten`
- ❌ `View Session verbessern` (zu vage)

### Issue Labels

**Standard Labels:**
- `automation` - Automatisierte Tasks
- `manual` - Manuelle Tasks
- `epic` - Größere Initiativen
- `bug` - Fehlerbehebung
- `enhancement` - Verbesserung
- `documentation` - Dokumentation
- `help wanted` - Community-Hilfe erwünscht
- `good first issue` - Gut für Einsteiger

### Issue Best Practices

**✅ Gute Issues:**
- Messbare Acceptance Criteria
- Klarer Scope und Non-Goals
- Referenzen zu verwandten Issues/PRs
- Konkrete Beispiele

**❌ Schlechte Issues:**
- Vage Beschreibungen ("Code funktioniert nicht")
- Fehlende Reproduktionsschritte
- Keine Acceptance Criteria
- Zu breiter Scope

---

## 📚 Dokumentation

### Dokumentations-Standards

**README.md:**
- Quickstart-Anleitung
- Feature-Übersicht
- ENV-Variablen-Referenz
- Windows-first Fokus

**Code-Dokumentation:**
- Docstrings für öffentliche Funktionen/Klassen
- Inline-Kommentare für komplexe Logik
- Type Hints für bessere IDE-Unterstützung

**Guides:**
- Schritt-für-Schritt Anleitungen
- Screenshots/Diagramme (falls hilfreich)
- Windows + Linux/macOS Befehle

### Dokumentation aktualisieren

**Bei Code-Änderungen:**
- [ ] README.md aktualisieren (falls User-facing)
- [ ] Docstrings anpassen
- [ ] CHANGELOG.md ergänzen (siehe [CHANGELOG.md](CHANGELOG.md))

**Bei neuen Features:**
- [ ] Feature in README.md beschreiben
- [ ] Beispiele hinzufügen
- [ ] Neuen Guide erstellen (falls nötig)
- [ ] ENV-Variablen dokumentieren (falls hinzugefügt)

---

## 🚀 Windows-First Development

Dieses Projekt priorisiert **Windows-Entwicklung** mit PowerShell:

### ✅ Best Practices

**PowerShell-Scripts verwenden:**
```powershell
# Direct venv calls (Windows-first)
.\venv\Scripts\python.exe -m pytest tests/
.\venv\Scripts\python.exe -m black .

# Nicht: source venv/bin/activate (Linux-only)
```

**python-dotenv CLI nutzen:**
```powershell
# Load .env with override flag
.\venv\Scripts\python.exe -m dotenv -f .env --override run python main.py

# Nicht: Manual .env parsing in scripts
```

**Cross-Platform Support:**
- Primär: Windows PowerShell
- Sekundär: Linux/macOS Bash (via `pathlib`, `os.path`)

### 📦 Dependencies verwalten

**Packages installieren (Windows):**
```powershell
.\venv\Scripts\python.exe -m pip install <package>
.\venv\Scripts\python.exe -m pip freeze > requirements.txt
```

**Neue Dependencies:**
- [ ] Zu `requirements.txt` hinzufügen
- [ ] Begründung im PR angeben
- [ ] Lizenz prüfen (MIT, Apache 2.0 bevorzugt)

---

## ❓ FAQ für Contributors

### "Wie finde ich ein gutes erstes Issue?"

Suche nach Label: `good first issue` oder `help wanted`

### "Darf ich mehrere Issues gleichzeitig bearbeiten?"

Ja, aber erstelle separate Branches und PRs für jedes Issue.

### "Mein PR wurde abgelehnt - was nun?"

- Lies das Feedback der Reviewer
- Frag nach, falls etwas unklar ist
- Implementiere die gewünschten Änderungen
- Pushe Updates (werden automatisch zum PR hinzugefügt)

### "Wie teste ich Live-Trading Features?"

**Niemals mit echtem Geld testen!**
- Nutze `DRY_RUN=true` (Standard)
- Nutze Binance Testnet für Paper Trading
- Siehe [LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md)

### "Brauche ich API-Keys für Development?"

**Nein!** DRY_RUN-Modus funktioniert ohne API-Keys:
- Simulierte Daten werden generiert
- Events werden lokal gespeichert
- View Session funktioniert einwandfrei

---

## 📞 Kontakt & Hilfe

**Fragen oder Probleme?**

- 💬 **GitHub Discussions** - Community Q&A
- 🐛 **GitHub Issues** - Bug Reports & Feature Requests
- 📖 **Dokumentation** - README.md, Guides, SECURITY.md

**Danke für deinen Beitrag! 🙏**

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
