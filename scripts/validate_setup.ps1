# validate_setup.ps1 - Validate Dev Live Session Setup (PowerShell)
# Run this to check if your environment is ready for the one-click start

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔍 Dev Live Session Setup Validator" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$Errors = 0
$Warnings = 0

# Check Python
Write-Host "1. Checking Python installation..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python not found" -ForegroundColor Red
    $Errors++
}

# Check project structure
Write-Host ""
Write-Host "2. Checking project structure..." -ForegroundColor Yellow
$requiredFiles = @(
    "automation/runner.py",
    "tools/view_session_app.py",
    "core/session_store.py",
    ".vscode/tasks.json",
    ".vscode/settings.json",
    "scripts/start_live.ps1"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
        $Errors++
    }
}

# Check virtual environment
Write-Host ""
Write-Host "3. Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ✅ venv exists" -ForegroundColor Green
    
    if (Test-Path "venv/Scripts/Activate.ps1") {
        Write-Host "   ✅ venv/Scripts/Activate.ps1 exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ venv/Scripts/Activate.ps1 not found" -ForegroundColor Red
        $Errors++
    }
} else {
    Write-Host "   ⚠️  venv not found (will be created on first run)" -ForegroundColor Yellow
    $Warnings++
}

# Check data directory
Write-Host ""
Write-Host "4. Checking data directory..." -ForegroundColor Yellow
if (Test-Path "data") {
    Write-Host "   ✅ data directory exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  data directory not found (will be created on first run)" -ForegroundColor Yellow
    $Warnings++
}

# Check for conflicting processes
Write-Host ""
Write-Host "5. Checking for conflicting processes..." -ForegroundColor Yellow
$streamlitProcess = Get-Process -Name "streamlit" -ErrorAction SilentlyContinue
if ($streamlitProcess) {
    Write-Host "   ⚠️  Streamlit process is already running" -ForegroundColor Yellow
    Write-Host "      Run: taskkill /F /IM streamlit.exe" -ForegroundColor White
    $Warnings++
} else {
    Write-Host "   ✅ No conflicting processes found" -ForegroundColor Green
}

# Check PowerShell execution policy
Write-Host ""
Write-Host "6. Checking PowerShell execution policy..." -ForegroundColor Yellow
$policy = Get-ExecutionPolicy -Scope CurrentUser
if ($policy -eq "Restricted") {
    Write-Host "   ⚠️  Execution policy is Restricted" -ForegroundColor Yellow
    Write-Host "      Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
    $Warnings++
} else {
    Write-Host "   ✅ Execution policy: $policy" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 Validation Summary" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($Errors -eq 0 -and $Warnings -eq 0) {
    Write-Host "✅ All checks passed! Your setup is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the dev live session, run:" -ForegroundColor White
    Write-Host "  .\scripts\start_live.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use VS Code Task: 'Dev: Live Session'" -ForegroundColor White
    exit 0
} elseif ($Errors -eq 0) {
    Write-Host "⚠️  Setup is mostly ready with $Warnings warning(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can proceed, but review the warnings above." -ForegroundColor White
    exit 0
} else {
    Write-Host "❌ Setup validation failed with $Errors error(s) and $Warnings warning(s)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the errors above before running the live session." -ForegroundColor Yellow
    exit 1
}
