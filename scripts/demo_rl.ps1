# demo_rl.ps1 - Run RL Training Demo
# PowerShell script for Windows-first development

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  RL Training Demo" -ForegroundColor Cyan
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

# Run demo
Write-Host "🚀 Starting RL Training Demo..." -ForegroundColor Green
Write-Host ""

& venv\Scripts\python.exe demo_rl_training.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Demo completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Demo failed with exit code: $LASTEXITCODE" -ForegroundColor Red
}
