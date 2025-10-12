# automated_setup.ps1 - PowerShell Wrapper für Vollautomatisierten Setup
# ========================================================================
# Führt den vollautomatischen Live Trading Setup durch mit:
# - Python-Umgebungsprüfung
# - API-Key-Abfrage (sicher)
# - Risk-Konfiguration
# - Preflight-Checks
# - Dry-Run-Test
# - Status-Reporting

$ErrorActionPreference = "Stop"

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "🚀 Vollautomatisierter Live Trading Setup" -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dieser Setup-Task führt folgende Schritte automatisch durch:" -ForegroundColor Yellow
Write-Host "  1. Python-Umgebung prüfen" -ForegroundColor White
Write-Host "  2. API-Keys sicher abfragen und speichern" -ForegroundColor White
Write-Host "  3. Risk-Management konfigurieren" -ForegroundColor White
Write-Host "  4. Preflight-Checks durchführen" -ForegroundColor White
Write-Host "  5. Dry-Run-Test ausführen" -ForegroundColor White
Write-Host "  6. Status-Bericht generieren" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  WICHTIG: Keine API-Keys werden außerhalb des lokalen Systems gespeichert!" -ForegroundColor Yellow
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""

# Parse command line arguments
param(
    [switch]$Auto = $false,
    [switch]$SkipDryRun = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "Usage: .\scripts\automated_setup.ps1 [OPTIONS]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Auto          Run in automatic mode (use defaults, skip prompts)" -ForegroundColor White
    Write-Host "  -SkipDryRun    Skip the dry-run test phase" -ForegroundColor White
    Write-Host "  -Help          Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  # Interactive setup (recommended)" -ForegroundColor White
    Write-Host "  .\scripts\automated_setup.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  # Automatic setup with defaults" -ForegroundColor White
    Write-Host "  .\scripts\automated_setup.ps1 -Auto" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  # Skip dry-run test" -ForegroundColor White
    Write-Host "  .\scripts\automated_setup.ps1 -SkipDryRun" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python is not installed!" -ForegroundColor Red
    Write-Host "   Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python found: $(python --version)" -ForegroundColor Green
Write-Host ""

# Set working directory to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "📂 Project root: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Create venv if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
}

Write-Host ""

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: pip upgrade failed, continuing..." -ForegroundColor Yellow
}

# Install required packages
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
Write-Host "   - keyring (Windows Credential Manager)" -ForegroundColor White
Write-Host "   - pyyaml (Config files)" -ForegroundColor White
Write-Host "   - python-dotenv (Environment variables)" -ForegroundColor White
Write-Host "   - requests (API calls)" -ForegroundColor White
Write-Host ""

& ".\venv\Scripts\python.exe" -m pip install keyring pyyaml python-dotenv requests --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install required packages" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""

# Build command line arguments for Python script
$pythonArgs = @("scripts\automated_setup.py")

if ($Auto) {
    Write-Host "🤖 Running in AUTO mode" -ForegroundColor Yellow
    $pythonArgs += "--auto"
}

if ($SkipDryRun) {
    Write-Host "⏭️  Skipping dry-run test" -ForegroundColor Yellow
    $pythonArgs += "--skip-dry-run"
}

Write-Host ""

# Run automated setup
Write-Host "Starting automated setup..." -ForegroundColor Yellow
Write-Host ""

& ".\venv\Scripts\python.exe" @pythonArgs

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "==========================================================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review: config/live_risk.yaml" -ForegroundColor White
    Write-Host "  2. Review: logs/setup_summary.md" -ForegroundColor White
    Write-Host "  3. Set: `$env:LIVE_ACK = `"I_UNDERSTAND`"" -ForegroundColor White
    Write-Host "  4. Run: .\scripts\start_live_prod.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  Before going live:" -ForegroundColor Yellow
    Write-Host "  - Enable IP restrictions on your Binance API keys" -ForegroundColor White
    Write-Host "  - Ensure 2FA is enabled on your account" -ForegroundColor White
    Write-Host "  - Start with minimal capital" -ForegroundColor White
    Write-Host "  - Monitor closely" -ForegroundColor White
} else {
    Write-Host "❌ Setup failed or was cancelled" -ForegroundColor Red
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please check the logs for details:" -ForegroundColor Yellow
    Write-Host "  logs/automated_setup_*.log" -ForegroundColor White
    Write-Host "  logs/setup_summary.md" -ForegroundColor White
}

Write-Host ""
exit $exitCode
