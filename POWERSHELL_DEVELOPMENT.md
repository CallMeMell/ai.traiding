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
- `scripts/set-executionpolicy.ps1` - Helper wrapper to run scripts with safe execution policy bypass

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

---

## 🧪 Testing the set-executionpolicy.ps1 Wrapper

### What is set-executionpolicy.ps1?

The `set-executionpolicy.ps1` script is a helper wrapper designed to solve a common issue for first-time users: PowerShell's ExecutionPolicy restrictions that prevent script execution.

**Key Features:**
- ✅ Sets ExecutionPolicy to Bypass **only** for the current process (Scope=Process)
- ✅ Automatically starts `start_live.ps1` 
- ✅ Properly forwards exit codes
- ✅ Temporary - reverts automatically when the session ends
- ✅ Safe for development and testing

### When to Use It

Use `set-executionpolicy.ps1` when you encounter errors like:
```
start_live.ps1 cannot be loaded because running scripts is disabled on this system.
```

**Instead of manually running:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\start_live.ps1
```

**Simply run:**
```powershell
.\scripts\set-executionpolicy.ps1
```

### Manual Testing Instructions

#### Test 1: Basic Execution
1. Open PowerShell in the repository root
2. Run the wrapper script:
   ```powershell
   .\scripts\set-executionpolicy.ps1
   ```
3. **Expected Result:**
   - Script displays security notice
   - Sets ExecutionPolicy (Process scope)
   - Starts `start_live.ps1` successfully
   - Shows both processes starting (Automation Runner + Streamlit)

#### Test 2: Exit Code Forwarding
1. Modify `start_live.ps1` temporarily to exit with a specific code (e.g., add `exit 42` at line 5)
2. Run the wrapper script:
   ```powershell
   .\scripts\set-executionpolicy.ps1
   echo $LASTEXITCODE
   ```
3. **Expected Result:**
   - `$LASTEXITCODE` should be 42
   - Wrapper properly forwards the exit code from `start_live.ps1`
4. **Important:** Revert the temporary change to `start_live.ps1`

#### Test 3: ExecutionPolicy Scope Verification
1. Before running the script, check current ExecutionPolicy:
   ```powershell
   Get-ExecutionPolicy -List
   ```
2. Run the wrapper script in a new PowerShell window
3. After script completes, check ExecutionPolicy again:
   ```powershell
   Get-ExecutionPolicy -List
   ```
4. **Expected Result:**
   - ExecutionPolicy is unchanged in the "LocalMachine" and "CurrentUser" scopes
   - Only the Process scope was temporarily modified
   - System-wide settings remain secure

#### Test 4: Error Handling
1. Temporarily rename `start_live.ps1` to `start_live.ps1.bak`
2. Run the wrapper script:
   ```powershell
   .\scripts\set-executionpolicy.ps1
   ```
3. **Expected Result:**
   - PowerShell displays an error (file not found)
   - Exit code is non-zero (error state)
4. **Important:** Rename the file back to `start_live.ps1`

### Automated Testing (Optional)

Since PowerShell script testing requires Windows-specific tooling, you can create a simple test using Pester (PowerShell testing framework) if desired:

```powershell
# Install Pester if not already installed
Install-Module -Name Pester -Force -SkipPublisherCheck

# Run tests (if test file exists)
Invoke-Pester -Path tests/set-executionpolicy.Tests.ps1
```

**Note:** A Pester test file is optional and not required for this issue, as manual testing is sufficient for this helper script.

### Security Considerations

**Q: Is it safe to set ExecutionPolicy to Bypass?**

A: Yes, when using `-Scope Process` as this wrapper does:
- ✅ Only affects the current PowerShell session
- ✅ Automatically reverts when you close PowerShell
- ✅ Does NOT change system-wide security settings
- ✅ Does NOT affect other PowerShell windows
- ✅ Recommended by Microsoft for development scenarios

**Q: Should I use this in production?**

A: No, this wrapper is designed for:
- Development environments
- Testing scenarios  
- First-time setup for new contributors
- Local development machines

For production, properly sign your scripts or adjust ExecutionPolicy at the appropriate scope (CurrentUser or LocalMachine).

### Troubleshooting

**Problem:** Script still won't run even with wrapper

**Solution:** Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Problem:** Exit code is always 0 even when `start_live.ps1` fails

**Solution:** Ensure `start_live.ps1` properly sets exit codes on errors using `exit 1` or similar.

---

**Helper Script for First-Time Users ⭐ | Safe & Temporary | Windows-First**
