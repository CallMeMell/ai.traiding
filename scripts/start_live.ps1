# start_live.ps1 - One-click Dev Live Session Launcher (PowerShell)
# Starts Automation Runner (Dry-Run) + Streamlit View Session

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Dev Live Session" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python is not installed!" -ForegroundColor Red
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
}

# Activate venv
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Warning: Some requirements.txt packages failed" -ForegroundColor Yellow
    }
}

# Install Streamlit and required packages
Write-Host "📦 Installing Streamlit and visualization packages..." -ForegroundColor Yellow
python -m pip install streamlit plotly pandas requests python-dotenv pydantic jsonschema --quiet

# Load environment variables from .env file (if exists)
if (Test-Path ".env") {
    Write-Host "🔧 Loading environment variables from .env file..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.+)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Set default environment variables for DRY_RUN (if not set in .env)
if (-not $env:DRY_RUN) { $env:DRY_RUN = "true" }
if (-not $env:BROKER_NAME) { $env:BROKER_NAME = "binance" }
if (-not $env:BINANCE_BASE_URL) { $env:BINANCE_BASE_URL = "https://testnet.binance.vision" }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  DRY_RUN: $env:DRY_RUN" -ForegroundColor White
Write-Host "  BROKER_NAME: $env:BROKER_NAME" -ForegroundColor White
Write-Host "  BINANCE_BASE_URL: $env:BINANCE_BASE_URL" -ForegroundColor White
Write-Host ""
Write-Host "Starting processes in parallel..." -ForegroundColor Yellow
Write-Host "- Automation Runner (Dry-Run mode)" -ForegroundColor White
Write-Host "- Streamlit View Session (http://localhost:8501)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all processes" -ForegroundColor Yellow
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
        param($projectRoot, $dryRun, $brokerName, $baseUrl)
        Set-Location $projectRoot
        & ".\venv\Scripts\Activate.ps1"
        $env:DRY_RUN = $dryRun
        $env:BROKER_NAME = $brokerName
        $env:BINANCE_BASE_URL = $baseUrl
        python automation/runner.py
    } -ArgumentList $projectRoot, $env:DRY_RUN, $env:BROKER_NAME, $env:BINANCE_BASE_URL

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
