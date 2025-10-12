# 📋 Repository Review Instructions

**Guidance for GitHub Copilot and human reviewers**

This document outlines the key expectations and standards for reviewing pull requests in this repository.

---

## 🎯 Review Focus Areas

### ✅ Windows-First Development
This repository prioritizes **Windows development** with PowerShell-first tooling:

- **Virtual Environment**: Code should use `venv\Scripts\python.exe` directly (Windows paths)
  - ✅ Good: `.\\venv\\Scripts\\python.exe -m pytest`
  - ❌ Avoid: `source venv/bin/activate && python -m pytest`
- **python-dotenv CLI**: Environment variables should be loaded using `python-dotenv` CLI with `--override` flag
  - ✅ Good: `dotenv -f .env --override run python script.py`
  - ❌ Avoid: Manual `.env` parsing in scripts
- **PowerShell Scripts**: Shell scripts should be PowerShell (`.ps1`) first
  - Bash scripts (`.sh`) are acceptable for macOS/Linux compatibility but not required

### ✅ Safety & Configuration Defaults

- **DRY_RUN Mode**: All trading operations must default to `DRY_RUN=true`
  - Real trading should be opt-in only
  - Documentation must clearly state this default
- **Environment Files**: Always use `.env` files for sensitive configuration
  - Never commit actual `.env` files (only `.env.example`)
  - Use python-dotenv for loading
- **Port Configuration**: Port 8501 should auto-forward for Streamlit View Session
  - VS Code configuration: `"portsAttributes": {"8501": {"label": "View Session", "onAutoForward": "openBrowser"}}`

### ✅ Code Quality & Testing

- **No Trading Logic Changes**: Unless explicitly stated in the PR, trading logic should remain unchanged
- **Tests**: Critical functionality should have tests
  - Focus on new features and bug fixes
  - Existing tests should pass
- **Documentation**: 
  - User-facing changes need documentation updates
  - Prefer German for documentation (repo convention)
  - Windows-specific instructions should come first

### ✅ Architecture & Maintainability

- **DRY Principle**: Avoid code duplication
  - Use functions, classes, and modules appropriately
- **Error Handling**: Critical paths should have proper error handling
- **Logging**: Use the existing logging infrastructure
  - Don't add new logging frameworks without discussion

---

## 🚫 Out of Scope for Blocking Reviews

The following are **NOT** blocking concerns (can be addressed in follow-up PRs):

- Performance optimizations (unless causing critical issues)
- UI/UX refinements (unless broken functionality)
- Additional features not mentioned in the PR description
- Code style nitpicks (unless severely impacting readability)
- Comprehensive test coverage (focus on critical paths)
- Linux/macOS-specific enhancements (Windows-first is priority)

---

## 📝 Review Checklist

Use this checklist when reviewing PRs:

- [ ] **Windows Compatibility**: Does it work on Windows? Are PowerShell commands used?
- [ ] **Direct venv Calls**: Are Python commands calling `venv\Scripts\python.exe` directly?
- [ ] **python-dotenv CLI**: Is `.env` loading done via python-dotenv CLI with `--override`?
- [ ] **DRY_RUN Default**: Are trading operations defaulting to dry-run mode?
- [ ] **No Secrets**: Are API keys, tokens, or sensitive data excluded?
- [ ] **Tests Pass**: Do existing tests still pass? Are new tests added for new features?
- [ ] **Documentation Updated**: Are README or other docs updated for user-facing changes?
- [ ] **No Trading Logic Changes**: Unless intended, trading logic should be untouched

---

## 🔍 How to Test PRs Locally (Windows)

```powershell
# Clone the PR branch
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
git checkout pr-<PR_NUMBER>

# Set execution policy if needed
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Run the Dev Live Session to test
.\scripts\start_live.ps1

# Or use VS Code tasks
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Dev: Live Session"
```

---

## 💡 Tips for Contributors

- **Small, Focused PRs**: Easier to review and merge
- **Clear Descriptions**: Explain what changed and why
- **Test on Windows**: Ensure your changes work on Windows PowerShell
- **Follow Conventions**: Match existing code style and structure
- **Update Documentation**: Keep docs in sync with code changes

---

**Made for Windows ⭐ | PowerShell-First | python-dotenv CLI | DRY_RUN Default**
