# 📋 Review Checklist für Feature-PRs

**Version:** 1.0  
**Stand:** Oktober 2025  
**Sprint:** Nach Sprint 0 Coverage-Validierung

Diese Checkliste dient als Leitfaden für Code-Reviews von Feature-PRs nach erfolgreichem Abschluss von Sprint 0 (80%+ Test Coverage).

---

## ✅ Pflicht-Kriterien (Blocking)

### 1. Code-Qualität & Standards

#### Windows-First Development
- [ ] **Windows-Kompatibilität**: Code funktioniert auf Windows PowerShell
- [ ] **Direct venv Calls**: Python-Befehle nutzen `venv\Scripts\python.exe` direkt
- [ ] **python-dotenv CLI**: `.env`-Loading via `python-dotenv` CLI mit `--override` Flag
- [ ] **Path-Handling**: Cross-Platform Paths via `os.path.join()` oder `pathlib`

#### Code Style
- [ ] **PEP 8**: Code folgt PEP 8 Guidelines (max 100 Zeichen)
- [ ] **Flake8**: Keine Linting-Fehler (`flake8 .`)
- [ ] **Black**: Code ist formatiert (`black . --line-length 100`)
- [ ] **Type Hints**: Funktionen haben Type Hints (wo sinnvoll)
- [ ] **Docstrings**: Öffentliche Funktionen/Klassen sind dokumentiert

### 2. Test-Abdeckung (Critical!)

#### Coverage-Anforderungen
- [ ] **Neue Features**: Mindestens **80% Coverage** für neuen Code
- [ ] **Bugfixes**: Test reproduziert Bug (vor Fix failing, nach Fix passing)
- [ ] **Keine Coverage-Regression**: Gesamt-Coverage darf nicht sinken
- [ ] **Critical Modules**: utils.py, binance_integration.py, broker_api.py bleiben >80%

#### Test-Qualität
- [ ] **Unit Tests**: Isolierte Tests für neue Funktionen
- [ ] **Edge Cases**: Grenzfälle getestet (None, leere Listen, Fehleingaben)
- [ ] **Happy Path + Error Path**: Positive und negative Testfälle
- [ ] **Mocking**: Externe Dependencies gemockt (API-Calls, etc.)
- [ ] **Test-Namen**: Beschreibend und eindeutig

#### Coverage-Nachweis
- [ ] **Coverage-Report**: HTML Coverage Report als Artefakt oder Screenshot
- [ ] **Coverage-Kommentar**: PR enthält Coverage-Statistik im Kommentar
- [ ] **CI-Status**: GitHub Actions Coverage Check ist grün ✅

### 3. Sicherheit & Konfiguration

#### Safety Defaults
- [ ] **DRY_RUN Default**: Trading-Operationen defaulten zu `DRY_RUN=true`
- [ ] **Real Trading Opt-In**: Echtes Trading nur mit expliziter Konfiguration
- [ ] **Keine Secrets**: Keine API-Keys, Tokens oder Passwörter im Code
- [ ] **.env nicht committed**: Nur `.env.example` ist versioniert

#### Error Handling
- [ ] **Try-Except**: Kritische Pfade haben Error Handling
- [ ] **Logging**: Fehler werden geloggt (mit Context)
- [ ] **Graceful Degradation**: Fehler führen nicht zu Crashes

### 4. Dokumentation

#### User-Facing Changes
- [ ] **README Update**: Neue Features in README.md beschrieben
- [ ] **ENV-Variablen**: Neue Variablen in `.env.example` und dokumentiert
- [ ] **Deutsche Dokumentation**: Folgt Repo-Konvention (Deutsch bevorzugt)
- [ ] **Windows-First**: Windows-Instruktionen stehen an erster Stelle

#### Code-Dokumentation
- [ ] **Inline-Kommentare**: Komplexe Logik ist kommentiert
- [ ] **CHANGELOG.md**: Änderungen in CHANGELOG dokumentiert
- [ ] **Guides**: Neue Features haben ggf. eigene Guides (z.B. FEATURE_GUIDE.md)

### 5. Continuous Integration

#### CI Pipeline
- [ ] **PR Synchronized**: PR ist mit main Branch synchronisiert (automatischer Check)
- [ ] **All Tests Pass**: Alle CI-Tests sind grün (Windows + Ubuntu)
- [ ] **Matrix Testing**: Tests laufen auf allen Python-Versionen (3.10, 3.11, 3.12)
- [ ] **Linting Pass**: Flake8, Black, isort checks bestehen
- [ ] **System Tests Pass**: Orchestrator und Integration Tests funktionieren

---

## 🟡 Empfehlungen (Non-Blocking)

### Code-Verbesserungen
- [ ] **DRY-Prinzip**: Code-Duplizierung vermieden
- [ ] **SOLID-Prinzipien**: Besonders Single Responsibility Principle
- [ ] **Performance**: Keine offensichtlichen Performance-Probleme
- [ ] **Lesbarkeit**: Code ist selbsterklärend

### Testing
- [ ] **Integration Tests**: Feature-Interaktion getestet
- [ ] **Stress Tests**: Performance unter Last getestet (falls relevant)
- [ ] **Memory Leak Check**: Langläufiger Code auf Memory Leaks geprüft

### Dokumentation
- [ ] **Screenshots**: UI-Änderungen haben Screenshots
- [ ] **Beispiele**: Code-Beispiele in Dokumentation
- [ ] **Use Cases**: Typische Anwendungsfälle beschrieben

---

## 🔴 No-Gos (Sofort ablehnen)

### Absolute Blockers
- ❌ **API-Keys committed**: Secret im Code vorhanden
- ❌ **Trading ohne DRY_RUN**: Real Trading ohne Opt-In Default
- ❌ **Coverage < 80%**: Neue Code-Abdeckung unter 80%
- ❌ **Tests failing**: CI-Tests schlagen fehl
- ❌ **Breaking Changes**: Unkommunizierte Breaking Changes
- ❌ **Keine Tests**: Feature-PR ohne neue Tests

---

## 📊 Coverage-Kommentar Template

Jeder Feature-PR sollte einen Coverage-Kommentar enthalten:

```markdown
## 📊 Test Coverage Report

### Coverage Summary
| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| new_feature.py | 85% | 80%+ | ✅ |
| utils.py | 82% | 80%+ | ✅ |
| Total | 81% | 80%+ | ✅ |

### Test Statistics
- **New Tests**: 15
- **Total Tests**: 190 (+15)
- **Statements Tested**: 920 / 1,142
- **Test Execution Time**: 12.3s

### Coverage Details
📂 **HTML Report**: [Coverage Report Artifact](link-to-artifact)
📈 **Coverage Trend**: +1% (80% → 81%)

### Missing Coverage
- `new_feature.py:45-52` - Error handling edge case (planned for follow-up)
```

---

## 🔄 Review-Prozess

### 1. Automated Checks (Pre-Review)
Vor manueller Review müssen diese automatisch laufen:
- ✅ PR Synchronization Check grün
- ✅ CI Pipeline grün
- ✅ Coverage Check grün (80%+)
- ✅ Linting Pass
- ✅ Tests Pass (alle Plattformen)

### 2. Manual Review
Reviewer prüfen:
1. **Code-Qualität**: Dieser Checkliste folgen
2. **Architektur**: Passt es ins Gesamtbild?
3. **Tests**: Sinnvoll und ausreichend?
4. **Dokumentation**: Klar und vollständig?
5. **Security**: Keine Sicherheitslücken?

### 3. Feedback & Iteration
- **Konstruktives Feedback**: Klar, respektvoll, mit Beispielen
- **Changes Requested**: Konkrete Action Items
- **Re-Review**: Nach Updates erneut reviewen

### 4. Approval & Merge
- **Mindestens 1 Approval**: Von Maintainer oder Core Team
- **Alle Checks grün**: CI, Coverage, Linting
- **Merge-Strategie**: Squash and Merge (für saubere History)
- **Branch Cleanup**: Branch nach Merge löschen

---

## 📝 Reviewer-Notizen

### Häufige Probleme
- ❌ **Coverage-Report fehlt**: PR hat keinen Coverage-Nachweis
- ❌ **Windows nicht getestet**: "Works on my machine" (Linux/Mac)
- ❌ **Fehlende Tests**: "Tests kommen später"
- ❌ **Schlechte Test-Namen**: `test_1()`, `test_function()`
- ❌ **Keine Docs**: Feature ohne Dokumentation

### Best Practices Reminder
- ✅ **Test-First Development**: Tests vor Implementierung schreiben
- ✅ **Small PRs**: Lieber mehrere kleine PRs als einen großen
- ✅ **Clear Commit Messages**: Conventional Commits nutzen
- ✅ **Self-Review**: Vor Submit selbst reviewen

---

## 🎯 Merge-Kriterien Zusammenfassung

Ein PR ist **merge-ready** wenn:

1. ✅ **Alle Pflicht-Kriterien erfüllt** (siehe oben)
2. ✅ **PR mit main synchronisiert**
3. ✅ **Coverage ≥ 80%** für neue Code
4. ✅ **CI Pipeline grün** (alle Plattformen)
4. ✅ **Mindestens 1 Approval** von Maintainer
5. ✅ **Dokumentation vollständig**
6. ✅ **Keine offenen Review-Kommentare**

---

## 📞 Hilfe & Fragen

Bei Fragen zur Review-Checkliste:
- 💬 **GitHub Discussions**: Allgemeine Fragen
- 📖 **CONTRIBUTING.md**: Contribution Guidelines
- 🔍 **SPRINT_0_COVERAGE_VALIDATION.md**: Coverage Best Practices

---

**Stand:** Oktober 2025 | **Nach Sprint 0** | **Windows-First** ⭐
