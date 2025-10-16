## 📝 Summary

<!-- Provide a brief description of what this PR does -->

### What changed?
<!-- List the main changes in this PR -->

### Why?
<!-- Explain the motivation for these changes -->

---

## ✅ Windows-First Dev Live Session Checklist

<!-- Check all that apply to this PR -->

### PR Synchronization
- [ ] **PR is synchronized with main branch** (required before merge)
- [ ] CI synchronization check is passing

### Environment & Configuration
- [ ] Code uses `venv\Scripts\python.exe` directly (Windows paths)
- [ ] Environment variables loaded via `python-dotenv` CLI with `--override` flag
- [ ] `.env` file updates documented (if applicable)
- [ ] No secrets or API keys committed

### Safety & Defaults
- [ ] Trading operations default to `DRY_RUN=true`
- [ ] Real trading is opt-in only (if applicable)
- [ ] Port 8501 auto-forward configuration preserved (if applicable)

### Code Quality
- [ ] No unintended trading logic changes
- [ ] Existing tests pass
- [ ] New tests added for new functionality (if applicable)
- [ ] PowerShell scripts work on Windows

### Documentation
- [ ] User-facing changes documented
- [ ] README updated (if applicable)
- [ ] Windows-specific instructions included
- [ ] German documentation follows repo conventions

---

## 🧪 Testing

<!-- Describe how you tested these changes -->

### Tested on Windows?
- [ ] Yes, tested on Windows with PowerShell
- [ ] N/A (documentation/configuration only)

### Test commands used:
```powershell
# Example:
# .\scripts\start_live.ps1
# Or via VS Code: Ctrl+Shift+P -> "Tasks: Run Task" -> "Dev: Live Session"
```

### Test Coverage (für Feature-PRs)
<!-- 
Für Feature-PRs: Füge einen Coverage-Report hinzu (siehe .github/COVERAGE_COMMENT_TEMPLATE.md)
Minimum: 80% Coverage für neuen Code
-->

- [ ] Coverage ≥ 80% für neue Code
- [ ] Coverage-Report als Kommentar oder Artifact hinzugefügt
- [ ] Keine Coverage-Regression bei kritischen Modulen (utils, binance_integration, broker_api)

**Coverage Summary:**
```
# Füge Coverage-Statistik ein (Beispiel):
# Total Coverage: 81% (Target: 80%+) ✅
# New Tests: +15 tests
# Coverage Report: [Link to artifact]
```

---

## 📎 Additional Context

<!-- Add any other context, screenshots, or relevant information -->

### Related Issues
<!-- Link related issues using #issue_number -->

### Screenshots (if applicable)
<!-- Add screenshots to show UI changes or test results -->

---

**Made for Windows ⭐ | PowerShell-First | python-dotenv CLI | DRY_RUN Default**
