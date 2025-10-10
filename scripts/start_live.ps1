# start_live.ps1 - Start both Automation Runner (dry-run) and View Session
# This script runs both processes in parallel for live monitoring

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " 🚀 Dev: Live Session Starter" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ ERROR: Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ to continue." -ForegroundColor Yellow
    exit 1
}

# Check if required files exist
if (-not (Test-Path "automation\runner.py")) {
    Write-Host "❌ ERROR: automation\runner.py not found!" -ForegroundColor Red
    Write-Host "Make sure you're running this script from the project root." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "tools\view_session_app.py")) {
    Write-Host "❌ ERROR: tools\view_session_app.py not found!" -ForegroundColor Red
    Write-Host "Make sure you're running this script from the project root." -ForegroundColor Yellow
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt -q
}
if (Test-Path "requirements\dev.txt") {
    pip install -r requirements\dev.txt -q
}
pip install streamlit plotly pandas requests python-dotenv -q
Write-Host "✅ Dependencies installed!" -ForegroundColor Green
Write-Host ""

# Load .env file if it exists (for additional environment variables)
if (Test-Path ".env") {
    Write-Host "📄 Loading .env file..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

# Set default environment variables (dry-run mode by default)
if (-not $env:DRY_RUN) { $env:DRY_RUN = "true" }
if (-not $env:BROKER_NAME) { $env:BROKER_NAME = "binance" }
if (-not $env:BINANCE_BASE_URL) { $env:BINANCE_BASE_URL = "https://testnet.binance.vision" }

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " ⚙️  Configuration:" -ForegroundColor Cyan
Write-Host "   DRY_RUN: $env:DRY_RUN" -ForegroundColor White
Write-Host "   BROKER_NAME: $env:BROKER_NAME" -ForegroundColor White
Write-Host "   BINANCE_BASE_URL: $env:BINANCE_BASE_URL" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Start both processes
Write-Host "🚀 Starting Automation Runner (Dry-Run)..." -ForegroundColor Yellow
$runnerJob = Start-Job -ScriptBlock {
    param($workDir)
    Set-Location $workDir
    & ".\venv\Scripts\Activate.ps1"
    $env:DRY_RUN = "true"
    $env:BROKER_NAME = "binance"
    $env:BINANCE_BASE_URL = "https://testnet.binance.vision"
    python automation\runner.py
} -ArgumentList $PWD

Write-Host "🌐 Starting View Session Dashboard on port 8501..." -ForegroundColor Yellow
$streamlitJob = Start-Job -ScriptBlock {
    param($workDir)
    Set-Location $workDir
    & ".\venv\Scripts\Activate.ps1"
    streamlit run tools\view_session_app.py --server.port 8501 --server.address 0.0.0.0
} -ArgumentList $PWD

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " ✅ Both processes started!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 View Session Dashboard: http://localhost:8501" -ForegroundColor White
Write-Host "🤖 Runner Job ID: $($runnerJob.Id)" -ForegroundColor White
Write-Host "🌐 Streamlit Job ID: $($streamlitJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop both processes..." -ForegroundColor Yellow
Write-Host ""

# Wait for both jobs and show output
try {
    while ($runnerJob.State -eq 'Running' -or $streamlitJob.State -eq 'Running') {
        Receive-Job -Job $runnerJob -ErrorAction SilentlyContinue
        Receive-Job -Job $streamlitJob -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}
finally {
    # Clean up jobs
    Write-Host ""
    Write-Host "🛑 Stopping processes..." -ForegroundColor Yellow
    Stop-Job -Job $runnerJob -ErrorAction SilentlyContinue
    Stop-Job -Job $streamlitJob -ErrorAction SilentlyContinue
    Remove-Job -Job $runnerJob -ErrorAction SilentlyContinue
    Remove-Job -Job $streamlitJob -ErrorAction SilentlyContinue
    Write-Host "✅ Processes stopped!" -ForegroundColor Green
}
