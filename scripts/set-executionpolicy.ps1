param(
  [Parameter(Mandatory=$true)]
  [string] $ScriptPath,
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]] $ScriptArgs
)

# Temporär ExecutionPolicy für diese Session setzen und das Ziel-Skript aufrufen
Write-Host "Temporarily setting ExecutionPolicy=Bypass for this session..."
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

Write-Host "Running script: $ScriptPath $ScriptArgs"
# Aufruf des Ziel-Skripts mit allen Argumenten
& $ScriptPath @ScriptArgs
$exitCode = $LASTEXITCODE

Write-Host "Child script exited with code $exitCode"
exit $exitCode
