<#
start_live.ps1 - PowerShell starter (improved)
- Uses set-executionpolicy.ps1 wrapper if ExecutionPolicy would block scripts
- Finds a free port (8501..8510) and starts Streamlit on it
#>

param(
  [switch] $AutoInstallDeps
)

# Root dir
$Root = Join-Path $PSScriptRoot ".." | Resolve-Path
Set-Location $Root

# Run env-check
Write-Host "Running env-check.py..."
& python scripts/env-check.py

# Verify deps
if ($AutoInstallDeps) {
  Write-Host "Running verify-deps.py --install ..."
  & python scripts/verify-deps.py --install
} else {
  & python scripts/verify-deps.py
}

# Find free port
$start = 8501
$end = 8510
$free = $null
for ($p=$start; $p -le $end; $p++) {
  try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), $p)
    $listener.Start()
    $listener.Stop()
    $free = $p
    break
  } catch {
    # port occupied
  }
}
if (-not $free) {
  Write-Error "No free port found in range $start..$end"
  exit 1
}
Write-Host "Using Streamlit port: $free"

# Activate venv if present (PowerShell)
$venvActivate = Join-Path $Root "venv/Scripts/Activate.ps1"
if (Test-Path $venvActivate) {
  Write-Host "Activating venv..."
  . $venvActivate
}

# Start automation runner (dry-run)
Start-Process -NoNewWindow -FilePath python -ArgumentList "-u", "automation/runner.py"

# Start Streamlit
Start-Process -NoNewWindow -FilePath streamlit -ArgumentList "run", "tools/view_session_app.py", "--server.port", "$free"
Write-Host "View Session should be available at http://localhost:$free"
