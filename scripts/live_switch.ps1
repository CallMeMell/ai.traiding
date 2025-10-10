# live_switch.ps1 - Live Trading Mode Switcher (PowerShell Wrapper)
# Sichere Umschaltung zwischen DRY_RUN und LIVE Modi

$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory=$false)]
    [switch]$Live,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$Status,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# Set working directory to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Build command
$pythonCmd = ".\venv\Scripts\python.exe"
$args = @("-m", "automation.live_switch")

if ($Help) {
    $args += "--help"
}
elseif ($Status) {
    $args += "--status"
}
elseif ($Live) {
    $args += "--live"
    if ($Force) {
        $args += "--force"
    }
}
elseif ($DryRun) {
    $args += "--dry-run"
}
else {
    # Show help if no args
    $args += "--help"
}

# Execute
& $pythonCmd $args

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Fehler aufgetreten!" -ForegroundColor Red
    exit $LASTEXITCODE
}
