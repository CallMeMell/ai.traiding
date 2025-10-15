# check_coverage.ps1
# PowerShell script to check test coverage for critical modules
# 
# Usage: .\scripts\check_coverage.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Coverage Check - Critical Modules" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if pytest-cov is installed
$pytestCovCheck = & ".\venv\Scripts\python.exe" -c "import pytest_cov" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ pytest-cov not installed!" -ForegroundColor Red
    Write-Host "   Installing pytest-cov..." -ForegroundColor Yellow
    & ".\venv\Scripts\python.exe" -m pip install pytest pytest-cov --quiet
}

Write-Host "Running tests for critical modules..." -ForegroundColor Green
Write-Host ""

# Run tests with coverage
& ".\venv\Scripts\python.exe" -m pytest `
    tests/test_utils.py `
    tests/test_binance_integration.py `
    tests/test_broker_api_comprehensive.py `
    --cov=utils `
    --cov=binance_integration `
    --cov=broker_api `
    --cov-report=term-missing `
    --cov-report=html `
    --cov-config=pytest.ini `
    -v

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ Tests passed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 HTML Coverage Report: htmlcov\index.html" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ Tests failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
