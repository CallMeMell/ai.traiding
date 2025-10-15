# 📊 Coverage Comment Template für PRs

Diese Vorlage dient zur Dokumentation der Test-Coverage in Feature-PRs.

---

## Standard Coverage-Kommentar

Kopiere diese Vorlage und fülle die Werte aus:

```markdown
## 📊 Test Coverage Report

### Coverage Summary
| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| [dein_modul].py | XX% | 80%+ | ✅/❌ |
| utils.py | 82% | 80%+ | ✅ |
| binance_integration.py | 78% | 80%+ | ✅ |
| broker_api.py | 78% | 80%+ | ✅ |
| **Total** | **XX%** | **80%+** | **✅/❌** |

### Test Statistics
- **New Tests**: XX
- **Total Tests**: XXX (+XX)
- **Statements Tested**: XXX / XXX
- **Test Execution Time**: XX.Xs

### Coverage Details
📂 **HTML Report**: [Coverage Report Artifact](link-to-artifact)
📈 **Coverage Trend**: +X% (XX% → XX%)

### Test Files Added/Modified
- `tests/test_[feature].py` - XX tests
- `tests/test_[module].py` - Updated XX tests

### Missing Coverage (falls <100%)
- `[modul].py:XX-XX` - [Beschreibung] (geplant für Follow-up)
- `[modul].py:XX` - [Edge Case Beschreibung]

### Manual Testing
- [x] Tested on Windows PowerShell
- [x] Tested with DRY_RUN=true
- [x] Tested error scenarios
```

---

## Beispiel: Ausgefüllter Coverage-Kommentar

```markdown
## 📊 Test Coverage Report

### Coverage Summary
| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| kelly_criterion.py | 92% | 80%+ | ✅ |
| utils.py | 83% | 80%+ | ✅ |
| binance_integration.py | 78% | 80%+ | ✅ |
| broker_api.py | 78% | 80%+ | ✅ |
| **Total** | **81%** | **80%+** | **✅** |

### Test Statistics
- **New Tests**: 18
- **Total Tests**: 193 (+18)
- **Statements Tested**: 945 / 1,167
- **Test Execution Time**: 13.2s

### Coverage Details
📂 **HTML Report**: [Coverage Report Artifact](https://github.com/CallMeMell/ai.traiding/actions/runs/12345/artifacts/67890)
📈 **Coverage Trend**: +1% (80% → 81%)

### Test Files Added/Modified
- `tests/test_kelly_criterion.py` - 15 new tests (unit + integration)
- `tests/test_utils.py` - Updated 3 tests for Kelly integration

### Missing Coverage
- `kelly_criterion.py:145-152` - Complex error recovery (planned for Sprint 2)
- `kelly_criterion.py:180` - Edge case: Zero win rate (documented as invalid)

### Manual Testing
- [x] Tested on Windows PowerShell
- [x] Tested with DRY_RUN=true
- [x] Tested error scenarios (negative values, zero division)
- [x] Backtested with historical data (100+ samples)
```

---

## Coverage Check Commands

### Lokale Coverage-Prüfung (Windows)

```powershell
# Alle Tests mit Coverage
.\venv\Scripts\python.exe -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -v

# Spezifisches Modul
.\venv\Scripts\python.exe -m pytest tests/test_[feature].py --cov=[modul] --cov-report=term-missing -v

# HTML Report öffnen
Start-Process htmlcov\index.html
```

### Lokale Coverage-Prüfung (Linux/macOS)

```bash
# Alle Tests mit Coverage
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -v

# Spezifisches Modul
python -m pytest tests/test_[feature].py --cov=[modul] --cov-report=term-missing -v

# HTML Report öffnen
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Coverage-Badges (Optional)

Für README.md Coverage-Badges:

```markdown
![Coverage](https://img.shields.io/badge/coverage-81%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-193%20passed-brightgreen)
```

---

## CI Coverage-Integration

Der CI-Workflow prüft automatisch Coverage:

```yaml
- name: Run tests with coverage
  run: |
    pytest tests/ --cov=. --cov-report=term-missing --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    fail_ci_if_error: false
```

---

## Tipps für hohe Coverage

### ✅ Do's
- **Test-First Development**: Tests vor Implementierung schreiben
- **Edge Cases**: Grenzfälle explizit testen
- **Mocking**: Externe Dependencies mocken
- **Happy + Error Path**: Beide Pfade testen
- **Descriptive Tests**: Klare Test-Namen

### ❌ Don'ts
- **Coverage Gaming**: Tests nur für Coverage-Zahlen
- **Leere Tests**: Tests ohne Assertions
- **Flaky Tests**: Unzuverlässige Tests
- **Langsame Tests**: Tests > 1s Laufzeit (ohne Grund)

---

## Weitere Ressourcen

- [REVIEW_CHECKLIST.md](.github/REVIEW_CHECKLIST.md) - Review Guidelines
- [SPRINT_0_COVERAGE_VALIDATION.md](../SPRINT_0_COVERAGE_VALIDATION.md) - Coverage Best Practices
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution Guidelines
- [pytest Documentation](https://docs.pytest.org/) - pytest Docs
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/) - Coverage Plugin

---

**Stand:** Oktober 2025 | **Nach Sprint 0** | **Windows-First** ⭐
