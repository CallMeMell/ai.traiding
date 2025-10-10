# nightly_run.ps1 - PowerShell Nightly Runner
# ===========================================
# Windows-first nightly system test runner

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Nightly System Test Runner" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\scripts\nightly_run.ps1"
    Write-Host ""
    Write-Host "Description:"
    Write-Host "  Runs a complete system test in DRY_RUN mode"
    Write-Host "  Logs results to logs/ directory"
    Write-Host ""
    exit 0
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🌙 Nightly System Test (Windows)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:DRY_RUN = "true"
$env:BROKER_NAME = "binance"
$env:BINANCE_BASE_URL = "https://testnet.binance.vision"

# Check if venv exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Virtual environment found" -ForegroundColor Green
Write-Host "✓ DRY_RUN mode enabled" -ForegroundColor Green
Write-Host ""

# Run nightly test
Write-Host "Running nightly system test..." -ForegroundColor Yellow
.\venv\Scripts\python.exe scripts\nightly_run.py

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Nightly test completed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Nightly test failed with exit code $exitCode" -ForegroundColor Red
}

exit $exitCode
