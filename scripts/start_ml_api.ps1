# start_ml_api.ps1 - Start ML/RL API Server
# PowerShell script for Windows-first development

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ML/RL API Server" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    Write-Host "   Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Load environment variables
if (Test-Path ".env") {
    Write-Host "🔐 Loading environment variables from .env..." -ForegroundColor Green
    & venv\Scripts\python.exe -m dotenv -f .env --override run echo "Environment loaded"
}

# Set default port if not set
if (-not $env:ML_API_PORT) {
    $env:ML_API_PORT = "5001"
}

Write-Host "🚀 Starting ML/RL API on port $env:ML_API_PORT..." -ForegroundColor Green
Write-Host "   Health check: http://localhost:$env:ML_API_PORT/health" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start API
& venv\Scripts\python.exe ml_api.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ API stopped successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ API failed with exit code: $LASTEXITCODE" -ForegroundColor Red
}
