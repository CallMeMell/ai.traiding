# PowerShell Development Guide

## 🔍 Linting PowerShell Scripts

This repository uses **PSScriptAnalyzer** to ensure PowerShell scripts follow best practices and are free of common errors.

### Prerequisites

PSScriptAnalyzer is typically pre-installed with PowerShell 7+. If not installed:

```powershell
# Install PSScriptAnalyzer (if needed)
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force
```

### Linting via VS Code Task

The easiest way to lint PowerShell scripts is via the VS Code task:

1. Open Command Palette: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type: `Tasks: Run Task`
3. Select: `Lint: PowerShell`

This will check all PowerShell scripts in the `scripts/` directory.

### Manual Linting

You can also lint scripts manually from the command line:

```powershell
# Lint all PowerShell scripts in scripts/
pwsh -Command "Invoke-ScriptAnalyzer -Path scripts/*.ps1 -Settings PSGallery -Recurse"

# Lint a specific script
pwsh -Command "Invoke-ScriptAnalyzer -Path scripts/setup_live.ps1 -Settings PSGallery"
```

### CI/CD Integration

To lint PowerShell scripts in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Lint PowerShell Scripts
  run: |
    pwsh -Command "Invoke-ScriptAnalyzer -Path scripts/*.ps1 -Settings PSGallery -Recurse"
```

### Best Practices

1. **Always lint before committing** - Run the linter to catch issues early
2. **Fix all errors** - PSScriptAnalyzer errors should be fixed before merging
3. **Review warnings** - Warnings may indicate potential issues
4. **Use consistent formatting** - Follow PowerShell best practices

### Common Issues Fixed by Linting

- Missing parameter validation
- Incorrect variable scoping
- Security vulnerabilities (e.g., hardcoded credentials)
- Performance issues
- Code style violations

### PowerShell Scripts in This Repository

- `scripts/setup_live.ps1` - Live trading setup wizard wrapper
- `scripts/start_live.ps1` - Dev live session launcher
- `scripts/start_live_prod.ps1` - Production live trading runner

---

## 🛠️ Development Workflow

### Before Committing

1. **Test your script** - Ensure it works as expected
2. **Run linter** - Use the VS Code task or manual command
3. **Fix any issues** - Address errors and warnings
4. **Document changes** - Update comments and documentation as needed

### VS Code Tasks Available

- `Lint: PowerShell` - Lint all PowerShell scripts
- `Install Dev Deps` - Set up development environment
- `Dev: Live Session` - Start development session
- `Live: Setup` - Run setup wizard
- `Live: Runner` - Start live trading (production)

---

**Made for Windows ⭐ | PowerShell-First | PSScriptAnalyzer**
