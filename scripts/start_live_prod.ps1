# start_live_prod.ps1 - Live Production Trading Runner (PowerShell)
# Loads secrets from Windows Credential Manager and starts live trading

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚨 LIVE PRODUCTION TRADING" -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  WARNING: This will trade with REAL MONEY" -ForegroundColor Yellow
Write-Host ""

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python is not installed!" -ForegroundColor Red
    exit 1
}

# Set working directory to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

# Verify venv exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run: scripts\setup_live.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Upgrade pip and install required packages
Write-Host "📦 Ensuring dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
& ".\venv\Scripts\python.exe" -m pip install python-dotenv keyring requests pyyaml --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check LIVE_ACK
if ($env:LIVE_ACK -ne "I_UNDERSTAND") {
    Write-Host "❌ Error: LIVE_ACK not set correctly" -ForegroundColor Red
    Write-Host ""
    Write-Host "You must explicitly acknowledge live trading by setting:" -ForegroundColor Yellow
    Write-Host '  $env:LIVE_ACK = "I_UNDERSTAND"' -ForegroundColor White
    Write-Host ""
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host '  $env:LIVE_ACK = "I_UNDERSTAND"' -ForegroundColor White
    Write-Host "  .\scripts\start_live_prod.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ LIVE_ACK acknowledged" -ForegroundColor Green
Write-Host ""

# Load secrets from Windows Credential Manager via keyring
Write-Host "🔐 Loading API keys from Windows Credential Manager..." -ForegroundColor Yellow

$getKeysScript = @"
import keyring
import sys

SERVICE_NAME = 'ai.traiding'
try:
    api_key = keyring.get_password(SERVICE_NAME, 'binance_api_key')
    api_secret = keyring.get_password(SERVICE_NAME, 'binance_api_secret')
    
    if not api_key or not api_secret:
        print('ERROR: Credentials not found', file=sys.stderr)
        sys.exit(1)
    
    # Print keys on separate lines (will be read by PowerShell)
    print(api_key)
    print(api_secret)
    sys.exit(0)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"@

$keysOutput = & ".\venv\Scripts\python.exe" -c $getKeysScript 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to load credentials from Windows Credential Manager" -ForegroundColor Red
    Write-Host "   $keysOutput" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Did you run the setup wizard?" -ForegroundColor Yellow
    Write-Host "  Run: scripts\setup_live.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Parse keys (split by newline)
$keyLines = $keysOutput -split "`n"
$env:BINANCE_API_KEY = $keyLines[0].Trim()
$env:BINANCE_API_SECRET = $keyLines[1].Trim()

if (-not $env:BINANCE_API_KEY -or -not $env:BINANCE_API_SECRET) {
    Write-Host "❌ Error: Failed to parse credentials" -ForegroundColor Red
    exit 1
}

Write-Host "✅ API keys loaded (keys not displayed)" -ForegroundColor Green

# Set production flags
$env:DRY_RUN = "false"
$env:LIVE_TRADING = "true"
$env:BINANCE_BASE_URL = "https://api.binance.com"
$env:BROKER_NAME = "binance"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  LIVE_ACK: $env:LIVE_ACK" -ForegroundColor White
Write-Host "  DRY_RUN: $env:DRY_RUN" -ForegroundColor White
Write-Host "  LIVE_TRADING: $env:LIVE_TRADING" -ForegroundColor White
Write-Host "  BINANCE_BASE_URL: $env:BINANCE_BASE_URL" -ForegroundColor White
Write-Host "  BROKER_NAME: $env:BROKER_NAME" -ForegroundColor White
Write-Host ""

# Check KILL_SWITCH
if ($env:KILL_SWITCH -eq "true") {
    Write-Host "🛑 KILL_SWITCH ENABLED" -ForegroundColor Red
    Write-Host "   Preflight will pass but live orders will be blocked" -ForegroundColor Yellow
    Write-Host "   Open orders will be cancelled (if implemented)" -ForegroundColor Yellow
    Write-Host ""
}

# Run preflight checks
Write-Host "🚀 Running preflight checks..." -ForegroundColor Yellow
Write-Host ""

& ".\venv\Scripts\python.exe" "scripts\live_preflight.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Preflight checks failed!" -ForegroundColor Red
    Write-Host "   Cannot start live trading" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# If KILL_SWITCH is enabled, stop here
if ($env:KILL_SWITCH -eq "true") {
    Write-Host ""
    Write-Host "🛑 KILL_SWITCH is enabled - not starting runner" -ForegroundColor Red
    Write-Host "   To disable: Remove or set KILL_SWITCH=false" -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# Start live trading
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Live Trading Runner" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  LIVE TRADING IN PROGRESS" -ForegroundColor Red
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

try {
    # Start automation runner with production flags
    & ".\venv\Scripts\python.exe" automation\runner.py
} catch {
    Write-Host ""
    Write-Host "❌ Error occurred: $_" -ForegroundColor Red
    exit 1
} finally {
    Write-Host ""
    Write-Host "🛑 Live trading stopped" -ForegroundColor Yellow
}
