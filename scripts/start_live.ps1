# start_live.ps1 - One-click Dev Live Session Launcher (PowerShell)
# Starts Automation Runner (Dry-Run) + Streamlit View Session
# With environment checks, dependency verification, and port finding

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Dev Live Session" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

# Step 1: Run environment checks
Write-Host "Step 1: Environment Check" -ForegroundColor Cyan
Write-Host "--------------------------" -ForegroundColor Cyan
$envCheckResult = & python scripts/env-check.py
$envCheckExit = $LASTEXITCODE

if ($envCheckExit -eq 1) {
    Write-Host ""
    Write-Host "❌ Environment check failed with critical errors." -ForegroundColor Red
    Write-Host "   Please fix the issues above before starting." -ForegroundColor Red
    exit 1
} elseif ($envCheckExit -eq 2) {
    Write-Host ""
    Write-Host "⚠️  Environment check passed with warnings." -ForegroundColor Yellow
    Write-Host "   Proceeding anyway..." -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Verify dependencies
Write-Host "Step 2: Dependency Verification" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan
$depsResult = & python scripts/verify-deps.py --install
$depsExit = $LASTEXITCODE

if ($depsExit -eq 2) {
    Write-Host ""
    Write-Host "⚠️  Some dependencies failed to install." -ForegroundColor Yellow
    Write-Host "   You may encounter issues. Proceeding anyway..." -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Find a free port for Streamlit (8501-8510)
Write-Host "Step 3: Finding Free Port" -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan
$streamlitPort = 8501
$portFound = $false

for ($port = 8501; $port -le 8510; $port++) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if (-not $connection) {
        $streamlitPort = $port
        $portFound = $true
        Write-Host "✅ Found free port: $streamlitPort" -ForegroundColor Green
        break
    }
}

if (-not $portFound) {
    Write-Host "⚠️  All ports 8501-8510 are in use. Using 8501 anyway..." -ForegroundColor Yellow
    $streamlitPort = 8501
}
Write-Host ""

# Step 4: Activate venv if present
Write-Host "Step 4: Virtual Environment" -ForegroundColor Cyan
Write-Host "---------------------------" -ForegroundColor Cyan
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    $pythonExe = ".\venv\Scripts\python.exe"
} else {
    Write-Host "⚠️  No venv found. Using system Python." -ForegroundColor Yellow
    $pythonExe = "python"
}
Write-Host ""

# Set default environment variables for DRY_RUN
$env:DRY_RUN = "true"
$env:BROKER_NAME = "binance"
$env:BINANCE_BASE_URL = "https://testnet.binance.vision"

# Load environment variables from .env file using python-dotenv (if exists)
# This will override the defaults above with values from .env
if (Test-Path ".env") {
    Write-Host "🔧 Loading environment variables from .env file (with override)..." -ForegroundColor Yellow
    # Use python-dotenv to load and override environment variables
    $envVars = & $pythonExe -m dotenv list 2>$null
    if ($LASTEXITCODE -eq 0) {
        $envVars | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                Set-Item -Path "env:$name" -Value $value
            }
        }
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  DRY_RUN: $env:DRY_RUN" -ForegroundColor White
Write-Host "  BROKER_NAME: $env:BROKER_NAME" -ForegroundColor White
Write-Host "  BINANCE_BASE_URL: $env:BINANCE_BASE_URL" -ForegroundColor White
Write-Host "  STREAMLIT_PORT: $streamlitPort" -ForegroundColor White
Write-Host ""
Write-Host "Starting processes in parallel..." -ForegroundColor Yellow
Write-Host "- Automation Runner (Dry-Run mode)" -ForegroundColor White
Write-Host "- Streamlit View Session (http://localhost:$streamlitPort)" -ForegroundColor White
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
        param($projectRoot, $pythonExe, $dryRun, $brokerName, $baseUrl)
        Set-Location $projectRoot
        $env:DRY_RUN = $dryRun
        $env:BROKER_NAME = $brokerName
        $env:BINANCE_BASE_URL = $baseUrl
        # Use python-dotenv to load .env with override, then run automation runner
        & $pythonExe -m dotenv -f .env run --override -- $pythonExe automation/runner.py
    } -ArgumentList $projectRoot, $pythonExe, $env:DRY_RUN, $env:BROKER_NAME, $env:BINANCE_BASE_URL

    # Wait a moment for runner to start
    Start-Sleep -Seconds 2

    # Start Streamlit in background
    Write-Host "📊 Starting Streamlit View Session..." -ForegroundColor Green
    $streamlitJob = Start-Job -ScriptBlock {
        param($projectRoot, $pythonExe, $port)
        Set-Location $projectRoot
        # Use python-dotenv to load .env with override, then run streamlit
        & $pythonExe -m dotenv -f .env run --override -- $pythonExe -m streamlit run tools/view_session_app.py --server.port $port --server.address 0.0.0.0 --server.headless true
    } -ArgumentList $projectRoot, $pythonExe, $streamlitPort

    Write-Host ""
    Write-Host "✅ Both processes started!" -ForegroundColor Green
    Write-Host "   - Automation Runner Job ID: $($runnerJob.Id)" -ForegroundColor White
    Write-Host "   - Streamlit Job ID: $($streamlitJob.Id)" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 View Session available at:" -ForegroundColor Cyan
    Write-Host "   http://localhost:$streamlitPort" -ForegroundColor White
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
