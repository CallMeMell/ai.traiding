# set-executionpolicy.ps1 - PowerShell Execution Policy Wrapper
# ================================================================
# SECURITY NOTICE / SICHERHEITSHINWEIS:
# 
# This script temporarily sets the PowerShell ExecutionPolicy to "Bypass"
# for the current process only (Scope=Process). This allows PowerShell
# scripts to run without changing system-wide security settings.
#
# Dieses Skript setzt die PowerShell-Ausführungsrichtlinie vorübergehend
# auf "Bypass" nur für den aktuellen Prozess (Scope=Process). Dies ermöglicht
# die Ausführung von PowerShell-Skripten ohne Änderung systemweiter
# Sicherheitseinstellungen.
#
# The policy change:
# - Applies ONLY to the current PowerShell session
# - Does NOT affect other PowerShell windows or processes
# - Automatically reverts when the process exits
# - Is safe for development and testing purposes
#
# Die Richtlinienänderung:
# - Gilt NUR für die aktuelle PowerShell-Sitzung
# - Beeinflusst KEINE anderen PowerShell-Fenster oder Prozesse
# - Wird automatisch zurückgesetzt, wenn der Prozess beendet wird
# - Ist sicher für Entwicklungs- und Testzwecke
#
# IMPORTANT: Only run scripts from trusted sources!
# WICHTIG: Führen Sie nur Skripte aus vertrauenswürdigen Quellen aus!
# ================================================================

# Display information message
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔓 Setting ExecutionPolicy (Process Scope)" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Set ExecutionPolicy to Bypass for current process only
# This is temporary and only affects this PowerShell session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

Write-Host "✅ ExecutionPolicy set to Bypass (Process scope)" -ForegroundColor Green
Write-Host "   This setting applies only to this PowerShell session." -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Starting main script..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Execute the main script (start_live.ps1) using PSScriptRoot to get correct path
# PSScriptRoot contains the directory where this script is located
& "${PSScriptRoot}\start_live.ps1"

# Capture and forward the exit code from the executed script
# This ensures that any errors or success codes are properly propagated
# Use 0 as default if LASTEXITCODE is null or undefined
$exitCode = if ($null -eq $LASTEXITCODE) { 0 } else { $LASTEXITCODE }

# Display completion message
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🏁 Script execution completed" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })
Write-Host "   Exit Code: $exitCode" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan

# Exit with the same code as the executed script
exit $exitCode
