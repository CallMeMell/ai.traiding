# auto_select_strategy.ps1 - Automatische Strategie-Auswahl (PowerShell Wrapper)
# Führt die automatische Strategie-Auswahl aus und aktualisiert die Live-Konfiguration

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎯 Automatische Strategie-Auswahl" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python is not installed!" -ForegroundColor Red
    Write-Host "   Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Set working directory to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Install required packages if needed
Write-Host "📦 Checking required packages..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install --quiet pandas numpy pyyaml python-dotenv matplotlib plotly

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install required packages" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Environment ready" -ForegroundColor Green
Write-Host ""

# Run auto selection script
Write-Host "Starting automated strategy selection..." -ForegroundColor Yellow
Write-Host ""
& ".\venv\Scripts\python.exe" "scripts\auto_select_strategy.py" $args

$exitCode = $LASTEXITCODE
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "✅ Strategy selection completed successfully" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
} else {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "❌ Strategy selection failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
}

exit $exitCode
