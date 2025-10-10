# setup_live.ps1 - Live Trading Setup Wizard Wrapper (PowerShell)
# Ensures venv and installs keyring, then runs setup_live.py

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔐 Live Trading Setup Wizard" -ForegroundColor Green
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

# Create venv if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet

# Install required packages
Write-Host "📦 Installing required packages (keyring, pyyaml, python-dotenv)..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install keyring pyyaml python-dotenv requests --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install required packages" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Environment ready" -ForegroundColor Green
Write-Host ""

# Run setup wizard
Write-Host "Starting setup wizard..." -ForegroundColor Yellow
Write-Host ""
& ".\venv\Scripts\python.exe" "scripts\setup_live.py"

$exitCode = $LASTEXITCODE
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "✅ Setup wizard completed successfully" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
} else {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "❌ Setup wizard failed or was cancelled" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
}

exit $exitCode
