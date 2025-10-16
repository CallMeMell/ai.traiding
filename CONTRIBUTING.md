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

## 📊 Merge Policy für Feature-PRs (Nach Sprint 0)

**Status:** ✅ Aktiv seit Sprint 0 (80%+ Coverage erreicht)  
**Gilt für:** Alle Feature-PRs nach Sprint 0 Completion

### 🎯 Übersicht

Nach erfolgreichem Abschluss von Sprint 0 (80%+ Test Coverage für kritische Module) gelten **verschärfte Qualitätsanforderungen** für neue Features, um die erreichte Code-Qualität zu halten und nachhaltig weiterzuentwickeln.

### ✅ Pflicht-Kriterien für Merge

Ein Feature-PR kann **nur gemergt werden**, wenn alle folgenden Kriterien erfüllt sind:

#### 0. PR Synchronisation (Critical!)

**Anforderung:**
- ✅ **PR ist mit main synchronisiert**: Branch muss auf dem aktuellen Stand von `main` basieren
- ✅ **CI/CD prüft automatisch**: GitHub Actions Workflow blockiert Merge bei veralteten PRs
- ✅ **Keine veralteten Branches**: Verhindert Merge-Konflikte und veraltete Tests

**Automatische Prüfung:**
Der Workflow `.github/workflows/require-up-to-date-main.yml` prüft automatisch bei jedem PR:
- Merge-Base wird mit aktuellem main-HEAD verglichen
- Bei Abweichung: PR wird blockiert mit Anleitung zur Synchronisation
- Bei Erfolg: Grünes Häkchen, PR kann weiter geprüft werden

**Synchronisation durchführen:**

Windows PowerShell:
```powershell
# Option 1: Rebase (empfohlen für saubere History)
git fetch origin main
git rebase origin/main
git push --force-with-lease

# Option 2: Merge (einfacher, aber zusätzlicher Merge-Commit)
git fetch origin main
git merge origin/main
git push
```

Linux/macOS:
```bash
# Option 1: Rebase (empfohlen)
git fetch origin main
git rebase origin/main
git push --force-with-lease

# Option 2: Merge
git fetch origin main
git merge origin/main
git push
```

**Warum ist das wichtig?**
- ✅ Tests laufen gegen aktuelle main-Basis
- ✅ Coverage-Checks reflektieren neuesten Stand
- ✅ Keine Merge-Konflikte beim finalen Merge
- ✅ Alle neuen Features/Fixes aus main sind integriert

#### 1. Test Coverage (Critical!)

#### 2. Test Coverage (Critical!)

**Minimum Coverage:**
- ✅ **Neue Code-Files**: Mindestens **80% Coverage**
- ✅ **Geänderte Files**: Coverage darf nicht sinken
- ✅ **Kritische Module** (utils.py, binance_integration.py, broker_api.py): Bleiben ≥80%
- ✅ **Gesamt-Coverage**: Keine Regression (mind. aktuelles Level halten)

**Coverage-Nachweis:**
```markdown
## 📊 Test Coverage Report

### Coverage Summary
| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| new_feature.py | 85% | 80%+ | ✅ |
| utils.py | 82% | 80%+ | ✅ |
| **Total** | **81%** | **80%+** | **✅** |

### Test Statistics
- **New Tests**: 15
- **Total Tests**: 190 (+15)
- **Coverage Report**: [HTML Artifact Link]
```

**Template:** Siehe `.github/COVERAGE_COMMENT_TEMPLATE.md`

#### 3. Test-Qualität

**Anforderungen:**
- ✅ **Unit Tests**: Isolierte Tests für neue Funktionen
- ✅ **Edge Cases**: Grenzfälle getestet (None, leere Listen, Fehler)
- ✅ **Happy Path + Error Path**: Positive und negative Szenarien
- ✅ **Mocking**: Externe Dependencies gemockt (API-Calls, etc.)
- ✅ **Test-Namen**: Beschreibend und selbsterklärend
- ✅ **Keine Flaky Tests**: Tests müssen deterministisch sein

**Test-Struktur Beispiel:**
```python
def test_calculate_sharpe_ratio_positive_returns():
    """Test Sharpe ratio calculation with positive returns."""
    returns = [0.01, 0.02, -0.01, 0.03]
    sharpe = calculate_sharpe_ratio(returns)
    assert sharpe > 0
    assert isinstance(sharpe, float)

def test_calculate_sharpe_ratio_zero_volatility():
    """Test Sharpe ratio edge case: zero volatility."""
    returns = [0.01, 0.01, 0.01, 0.01]
    sharpe = calculate_sharpe_ratio(returns)
    assert sharpe == 0.0
```

#### 4. CI Pipeline

**Alle Checks müssen grün sein:**
- ✅ **PR Synchronization Check**: `require-up-to-date-main.yml` Workflow passing
- ✅ **Feature PR Coverage Check**: `feature-pr-coverage.yml` Workflow passing
- ✅ **Main CI**: `ci.yml` Workflow passing (alle Plattformen + Python-Versionen)
- ✅ **Linting**: Flake8, Black, isort checks passing
- ✅ **System Tests**: Integration Tests erfolgreich

**Matrix Testing:**
- Windows + Ubuntu
- Python 3.10, 3.11, 3.12
- 6 Kombinationen (2 OS × 3 Python)

#### 5. Code-Qualität

**Standards:**
- ✅ **PEP 8**: Code Style Guidelines
- ✅ **Type Hints**: Funktionen haben Type Annotations
- ✅ **Docstrings**: Öffentliche API dokumentiert
- ✅ **DRY-Prinzip**: Keine Code-Duplizierung
- ✅ **Error Handling**: Try-Except für kritische Pfade

#### 6. Dokumentation

**Pflicht-Updates:**
- ✅ **README.md**: Neue Features beschrieben (falls User-facing)
- ✅ **CHANGELOG.md**: Änderungen dokumentiert
- ✅ **.env.example**: Neue ENV-Variablen hinzugefügt
- ✅ **Docstrings**: Code dokumentiert
- ✅ **Guides**: Feature-spezifische Guides (bei Bedarf)

#### 7. Sicherheit

**Security Checks:**
- ✅ **Keine Secrets**: API-Keys, Tokens, Passwörter nicht im Code
- ✅ **DRY_RUN Default**: Trading-Features defaulten zu `DRY_RUN=true`
- ✅ **.env nicht committed**: Nur `.env.example` versioniert

#### 8. Review

**Mindestanforderungen:**
- ✅ **1 Approval**: Von Maintainer oder Core Team Member
- ✅ **Review-Checkliste**: Siehe `.github/REVIEW_CHECKLIST.md`
- ✅ **Alle Kommentare resolved**: Keine offenen Review-Threads
- ✅ **Keine "Changes Requested"**: Alle angefragten Änderungen umgesetzt

### 🚫 Automatic Rejection Criteria

Ein PR wird **sofort abgelehnt** bei:

- ❌ **PR nicht mit main synchronisiert**
- ❌ **Coverage < 80%** für neuen Code
- ❌ **Coverage-Regression** bei kritischen Modulen
- ❌ **CI Tests failing**
- ❌ **Secrets committed** (API-Keys, Tokens)
- ❌ **Keine Tests** für neues Feature
- ❌ **Real Trading ohne DRY_RUN Default**

### 📋 Review-Checkliste

Vollständige Review-Checkliste: **`.github/REVIEW_CHECKLIST.md`**

**Quick Check (für Reviewer):**
```markdown
- [ ] PR mit main synchronisiert
- [ ] Coverage ≥ 80% für neuen Code
- [ ] CI Pipeline grün (alle Plattformen)
- [ ] Tests hinzugefügt (Unit + Edge Cases)
- [ ] Dokumentation aktualisiert
- [ ] Code-Style Guidelines eingehalten
- [ ] Keine Secrets committed
- [ ] DRY_RUN Default korrekt
- [ ] Windows-Kompatibilität getestet
```

### 🔄 Merge-Prozess

#### Schritt 1: Automated Checks (Pre-Review)
Vor manueller Review müssen automatisch laufen:
1. ✅ **CI Pipeline**: Alle Tests passing
2. ✅ **Coverage Check**: 80%+ erreicht
3. ✅ **Linting**: Style checks passing
4. ✅ **System Tests**: Integration funktioniert

**Dauer:** ~5-10 Minuten (automatisch via GitHub Actions)

#### Schritt 2: Manual Review
Maintainer/Core Team reviewen:
1. **Code-Qualität**: Review-Checkliste durchgehen
2. **Architektur**: Passt ins Gesamtbild?
3. **Tests**: Sinnvoll und ausreichend?
4. **Dokumentation**: Klar und vollständig?
5. **Security**: Keine Sicherheitslücken?

**Dauer:** 1-3 Tage (je nach Komplexität)

#### Schritt 3: Feedback & Iteration
Bei "Changes Requested":
1. **Feedback lesen**: Alle Kommentare durchgehen
2. **Änderungen umsetzen**: Code anpassen
3. **Re-Test**: Lokal testen
4. **Push Updates**: Commits pushen (automatisch zu PR hinzugefügt)
5. **Re-Request Review**: Review erneut anfordern

#### Schritt 4: Approval & Merge
Nach Approval und grünen Checks:
1. **Final Check**: Maintainer überprüft nochmals
2. **Squash and Merge**: Commits zu einem zusammenfassen
3. **Commit Message**: Conventional Commits Format
4. **Merge to Dev**: PR in `dev` Branch mergen
5. **Branch Cleanup**: Feature-Branch löschen

### 📊 Coverage-Integration in CI

**Workflow:** `.github/workflows/feature-pr-coverage.yml`

**Features:**
- ✅ Automatische Coverage-Prüfung bei jedem PR
- ✅ Coverage-Threshold Check (80%+)
- ✅ Kritische Module einzeln geprüft
- ✅ HTML Coverage Report als Artifact
- ✅ Coverage Summary im PR (GitHub Step Summary)
- ✅ Upload zu Codecov (optional)

**Beispiel CI-Output:**
```
📊 Coverage Summary
Total Coverage: 81% ✅

Critical Modules:
| Module | Coverage | Status |
|--------|----------|--------|
| utils.py | 82% | ✅ |
| binance_integration.py | 78% | ✅ |
| broker_api.py | 78% | ✅ |
```

### 🎓 Für Contributors

**Vor PR-Erstellung:**
1. ✅ Tests lokal schreiben und ausführen
2. ✅ Coverage lokal prüfen (≥80%)
3. ✅ Linting lokal durchführen
4. ✅ Dokumentation aktualisieren
5. ✅ Self-Review durchführen

**Coverage-Check lokal (Windows):**
```powershell
# Tests mit Coverage
.\venv\Scripts\python.exe -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -v

# HTML Report öffnen
Start-Process htmlcov\index.html
```

**Coverage-Check lokal (Linux/macOS):**
```bash
# Tests mit Coverage
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -v

# HTML Report öffnen
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 📚 Weitere Ressourcen

**Policy-Dokumente:**
- **Review-Checkliste**: `.github/REVIEW_CHECKLIST.md`
- **Coverage-Template**: `.github/COVERAGE_COMMENT_TEMPLATE.md`
- **CI Workflow**: `.github/workflows/feature-pr-coverage.yml`

**Best Practices:**
- **Sprint 0 Validation**: `SPRINT_0_COVERAGE_VALIDATION.md`
- **CI Success Guide**: `CI_SUCCESS_AND_NEXT_STEPS.md`
- **Best Practices**: `BEST_PRACTICES_GUIDE.md`

### 🎯 Ziel dieser Policy

Diese Policy sorgt für:
- ✅ **Nachhaltige Code-Qualität**
- ✅ **Hohe Testabdeckung** (≥80%)
- ✅ **Konsistente Standards**
- ✅ **Vertrauenswürdiger Code**
- ✅ **Schnelle Iteration** (durch klare Kriterien)

**Nach Sprint 0 gilt:** Quality over Speed! 🚀

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
