# start_live.ps1 - One-click Dev Live Session Launcher (PowerShell)
# Starts Automation Runner (Dry-Run) + Streamlit View Session

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Dev Live Session" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Pre-flight checks
Write-Host "🔍 Running pre-flight checks..." -ForegroundColor Yellow

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python is not installed!" -ForegroundColor Red
    Write-Host "   Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = (python --version 2>&1) -replace 'Python ', ''
Write-Host "✅ Python $pythonVersion detected" -ForegroundColor Green

# Set working directory to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot
Write-Host "📁 Project root: $projectRoot" -ForegroundColor White

# Verify we're in the correct directory
if (-not (Test-Path "automation/runner.py")) {
    Write-Host "❌ Error: Cannot find automation/runner.py" -ForegroundColor Red
    Write-Host "   Please run this script from the project root or scripts directory" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Project structure validated" -ForegroundColor Green

# Create venv if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate venv
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "   If you see 'execution policy' error, run:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet 2>&1 | Out-Null

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Some requirements.txt packages may have failed (non-critical)" -ForegroundColor Yellow
    }
}

# Install Streamlit and required packages
Write-Host "📦 Installing Streamlit and visualization packages..." -ForegroundColor Yellow
python -m pip install streamlit plotly pandas requests python-dotenv pydantic jsonschema --quiet 2>&1 | Out-Null
Write-Host "✅ All packages installed" -ForegroundColor Green

# Set environment variables for DRY_RUN
$env:DRY_RUN = "true"
$env:BROKER_NAME = "binance"
$env:BINANCE_BASE_URL = "https://testnet.binance.vision"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ℹ️  Configuration:" -ForegroundColor Cyan
Write-Host "   - DRY_RUN: true (no real trading)" -ForegroundColor White
Write-Host "   - BROKER: binance (testnet)" -ForegroundColor White
Write-Host "   - Events: data/session/events.jsonl" -ForegroundColor White
Write-Host ""
Write-Host "Starting processes in parallel..." -ForegroundColor Yellow
Write-Host "- Automation Runner (Dry-Run mode)" -ForegroundColor White
Write-Host "- Streamlit View Session (http://localhost:8501)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: Wait 5-10 seconds for processes to start" -ForegroundColor Yellow
Write-Host "🛑 Press Ctrl+C to stop all processes" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Cleanup function
$cleanupBlock = {
    Write-Host ""
    Write-Host "🛑 Stopping all processes..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "streamlit"} | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Register cleanup on Ctrl+C
Register-EngineEvent PowerShell.Exiting -Action $cleanupBlock | Out-Null

try {
    # Start Automation Runner in background
    Write-Host "🤖 Starting Automation Runner..." -ForegroundColor Green
    $runnerJob = Start-Job -ScriptBlock {
        param($projectRoot)
        Set-Location $projectRoot
        & ".\venv\Scripts\Activate.ps1"
        $env:DRY_RUN = "true"
        $env:BROKER_NAME = "binance"
        $env:BINANCE_BASE_URL = "https://testnet.binance.vision"
        python automation/runner.py
    } -ArgumentList $projectRoot

    # Wait a moment for runner to start
    Start-Sleep -Seconds 2

    # Start Streamlit in background
    Write-Host "📊 Starting Streamlit View Session..." -ForegroundColor Green
    $streamlitJob = Start-Job -ScriptBlock {
        param($projectRoot)
        Set-Location $projectRoot
        & ".\venv\Scripts\Activate.ps1"
        streamlit run tools/view_session_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
    } -ArgumentList $projectRoot

    Write-Host ""
    Write-Host "✅ Both processes started!" -ForegroundColor Green
    Write-Host "   - Automation Runner Job ID: $($runnerJob.Id)" -ForegroundColor White
    Write-Host "   - Streamlit Job ID: $($streamlitJob.Id)" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 View Session available at:" -ForegroundColor Cyan
    Write-Host "   http://localhost:8501" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Events are being generated and can be viewed in real-time" -ForegroundColor Yellow
    Write-Host "🛑 Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""

    # Monitor jobs and display output
    while ($runnerJob.State -eq "Running" -or $streamlitJob.State -eq "Running") {
        # Receive output from jobs
        Receive-Job -Job $runnerJob -ErrorAction SilentlyContinue
        Receive-Job -Job $streamlitJob -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }

    # Wait for jobs to complete
    Wait-Job -Job $runnerJob, $streamlitJob
    Receive-Job -Job $runnerJob, $streamlitJob

} catch {
    Write-Host "❌ Error occurred: $_" -ForegroundColor Red
} finally {
    # Cleanup
    Write-Host ""
    Write-Host "🛑 Stopping all processes..." -ForegroundColor Yellow
    Stop-Job -Job $runnerJob, $streamlitJob -ErrorAction SilentlyContinue
    Remove-Job -Job $runnerJob, $streamlitJob -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}
