# 📋 Merge Policy - Quick Reference

**Version:** 1.0  
**Stand:** Oktober 2025  
**Status:** ✅ Aktiv seit Sprint 0

Schnelle Übersicht der Merge-Policy für Feature-PRs nach Sprint 0.

---

## ✅ Merge-Ready Checkliste (Quick Check)

Ein PR ist merge-ready wenn:

```markdown
- [ ] PR mit main synchronisiert ✅
- [ ] Coverage ≥ 80% für neuen Code ✅
- [ ] CI Pipeline grün (Windows + Ubuntu) ✅
- [ ] Kritische Module ≥ 80% (utils, binance_integration, broker_api) ✅
- [ ] Tests hinzugefügt (Unit + Edge Cases) ✅
- [ ] Dokumentation aktualisiert ✅
- [ ] Keine Secrets committed ✅
- [ ] DRY_RUN Default korrekt ✅
- [ ] 1+ Approval von Maintainer ✅
- [ ] Alle Review-Kommentare resolved ✅
```

---

## 🚫 Instant Rejection (Automatic No-Go)

PR wird **sofort abgelehnt** bei:

- ❌ **PR nicht mit main synchronisiert**
- ❌ **Coverage < 80%** für neuen Code
- ❌ **Coverage-Regression** bei kritischen Modulen
- ❌ **CI Tests failing**
- ❌ **Secrets committed** (API-Keys, Tokens)
- ❌ **Keine Tests** für neues Feature
- ❌ **Real Trading ohne DRY_RUN Default**

---

## 🔄 PR Synchronisation

### Warum wichtig?
PRs müssen mit dem aktuellen `main` Branch synchronisiert sein, damit:
- ✅ Tests gegen aktuelle Codebasis laufen
- ✅ Coverage-Checks neuesten Stand reflektieren
- ✅ Keine Merge-Konflikte beim finalen Merge entstehen
- ✅ Alle neuen Features/Fixes aus main integriert sind

### Automatischer Check
Der Workflow `.github/workflows/require-up-to-date-main.yml` prüft automatisch:
- ✅ Merge-Base = main HEAD? → Grün
- ❌ Merge-Base ≠ main HEAD? → Rot mit Anleitung

### Synchronisation durchführen

**Windows PowerShell:**
```powershell
# Option 1: Rebase (empfohlen)
git fetch origin main
git rebase origin/main
git push --force-with-lease

# Option 2: Merge (einfacher)
git fetch origin main
git merge origin/main
git push
```

**Linux/macOS:**
```bash
# Option 1: Rebase (empfohlen)
git fetch origin main
git rebase origin/main
git push --force-with-lease

# Option 2: Merge (einfacher)
git fetch origin main
git merge origin/main
git push
```

---

## 📊 Coverage-Requirements

### Minimum Coverage
| Kategorie | Requirement |
|-----------|-------------|
| Neue Files | ≥ 80% |
| Geänderte Files | Keine Regression |
| Kritische Module | ≥ 80% (utils, binance_integration, broker_api) |
| Gesamt | Keine Regression |

### Coverage-Nachweis
```markdown
## 📊 Test Coverage Report

| Module | Coverage | Status |
|--------|----------|--------|
| new_feature.py | 85% | ✅ |
| utils.py | 82% | ✅ |
| **Total** | **81%** | ✅ |
```

**Template:** `.github/COVERAGE_COMMENT_TEMPLATE.md`

---

## 🔄 Merge-Prozess (4 Schritte)

### 1. Automated Checks (~5-10 Min)
- ✅ PR Synchronization Check
- ✅ CI Pipeline (Tests, Linting)
- ✅ Coverage Check (80%+)
- ✅ System Integration Tests

### 2. Manual Review (1-3 Tage)
- ✅ Code-Qualität Review
- ✅ Review-Checkliste durchgehen
- ✅ Architektur-Fit prüfen

### 3. Feedback & Iteration
- ✅ Changes umsetzen
- ✅ Re-Test lokal
- ✅ Push Updates
- ✅ Re-Request Review

### 4. Merge
- ✅ Squash and Merge
- ✅ Branch Cleanup

---

## 🛠️ Lokale Checks (Vor PR)

### Windows PowerShell
```powershell
# Tests mit Coverage
.\venv\Scripts\python.exe -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -v

# HTML Report öffnen
Start-Process htmlcov\index.html

# Linting
.\venv\Scripts\python.exe -m flake8 . --max-line-length=100
.\venv\Scripts\python.exe -m black . --line-length=100 --check
```

### Linux/macOS
```bash
# Tests mit Coverage
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -v

# HTML Report öffnen
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Linting
python -m flake8 . --max-line-length=100
python -m black . --line-length=100 --check
```

---

## 📚 Policy-Dokumente

### Vollständige Dokumentation
- 📋 **Review-Checkliste**: `.github/REVIEW_CHECKLIST.md`
- 📊 **Coverage-Template**: `.github/COVERAGE_COMMENT_TEMPLATE.md`
- 🔄 **Merge Policy**: `CONTRIBUTING.md` (Abschnitt "Merge Policy für Feature-PRs")
- ✅ **CI Workflow**: `.github/workflows/feature-pr-coverage.yml`

### Best Practices
- **Sprint 0 Validation**: `SPRINT_0_COVERAGE_VALIDATION.md`
- **CI Success Guide**: `CI_SUCCESS_AND_NEXT_STEPS.md`
- **Best Practices**: `BEST_PRACTICES_GUIDE.md`
- **Contributing**: `CONTRIBUTING.md`

---

## 🎯 Für Contributors (TL;DR)

**Vor PR-Erstellung:**
1. ✅ Tests schreiben (≥80% Coverage)
2. ✅ Lokal testen (alle Tests passing)
3. ✅ Linting durchführen
4. ✅ Dokumentation aktualisieren
5. ✅ Coverage-Report vorbereiten

**In PR Description:**
- Coverage-Report mit Template
- Alle Checkboxen im PR-Template abgehakt
- Screenshots (falls UI-Änderungen)

**Nach Review:**
- Feedback zeitnah umsetzen
- Re-Test nach Änderungen
- Re-Request Review

---

## 🎓 Für Reviewer (TL;DR)

**Review-Fokus:**
1. ✅ Coverage ≥ 80%? → Check Artifact/Screenshot
2. ✅ Tests sinnvoll? → Edge Cases geprüft?
3. ✅ Code-Qualität? → DRY, Type Hints, Docstrings
4. ✅ Security? → Keine Secrets, DRY_RUN Default
5. ✅ Docs? → README, CHANGELOG aktualisiert

**Approval nur wenn:**
- Alle Pflicht-Kriterien erfüllt
- CI grün
- Coverage ≥ 80%
- Review-Checkliste durchgegangen

---

## ❓ FAQ

### "Warum 80% Coverage?"
Nach Sprint 0 haben wir 80%+ für kritische Module erreicht. Das ist unser neuer Qualitäts-Standard.

### "Was wenn Coverage < 80%?"
PR wird nicht gemerged. Entweder mehr Tests schreiben oder Begründung im PR warum bestimmte Code-Teile nicht testbar sind.

### "Gilt das für alle PRs?"
Nein, nur für **Feature-PRs**. Bugfixes und Docs haben etwas lockere Anforderungen.

### "Was ist mit Edge Cases?"
Pflicht! Tests müssen Happy Path + Error Path + Edge Cases abdecken.

### "Wie lange dauert Review?"
1-3 Tage je nach Komplexität. Bei dringenden PRs: Priorität im Team-Meeting besprechen.

### "Was wenn Reviewer nicht antwortet?"
Nach 3 Tagen: Gentle Reminder. Nach 5 Tagen: Anderen Reviewer zuweisen.

---

## 🚀 Ziel

Diese Policy sorgt für:
- ✅ **Nachhaltige Code-Qualität**
- ✅ **Hohe Testabdeckung** (≥80%)
- ✅ **Konsistente Standards**
- ✅ **Vertrauenswürdiger Code**
- ✅ **Schnelle Iteration**

**Quality over Speed! 🎯**

---

**Erstellt:** Oktober 2025 | **Nach Sprint 0** | **Windows-First** ⭐
