# APS Screensaver Installation Script
# Installs the screensaver to Windows system directory

#Requires -RunAsAdministrator

param(
    [Parameter(Mandatory=$false)]
    [switch]$User = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== APS Screensaver Installation ===" -ForegroundColor Cyan
Write-Host ""

# Paths
$BuildDir = Join-Path $PSScriptRoot "build"
$SourceScr = Join-Path $BuildDir "ApsScreensaver.scr"

# Check if screensaver file exists
if (-not (Test-Path $SourceScr)) {
    Write-Host "ERROR: Screensaver file not found at $SourceScr" -ForegroundColor Red
    Write-Host "Please run build.ps1 first to build the screensaver." -ForegroundColor Yellow
    exit 1
}

# Determine installation directory
if ($User) {
    # User-specific installation (doesn't require admin)
    $DestDir = Join-Path $env:USERPROFILE "AppData\Local\Screensavers"
    Write-Host "Installing to user directory (no admin required)..." -ForegroundColor Yellow
} else {
    # System-wide installation (requires admin)
    $DestDir = Join-Path $env:SystemRoot "System32"
    Write-Host "Installing to system directory (admin required)..." -ForegroundColor Yellow
}

$DestScr = Join-Path $DestDir "ApsScreensaver.scr"

Write-Host "Source: $SourceScr" -ForegroundColor Gray
Write-Host "Destination: $DestScr" -ForegroundColor Gray
Write-Host ""

# Create destination directory if it doesn't exist (for user install)
if ($User -and -not (Test-Path $DestDir)) {
    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
}

# Copy the screensaver
try {
    Write-Host "Copying screensaver..." -ForegroundColor Yellow

    # If file exists, try to close it first
    if (Test-Path $DestScr) {
        Write-Host "Existing screensaver found, replacing..." -ForegroundColor Yellow
    }

    Copy-Item -Path $SourceScr -Destination $DestScr -Force
    Write-Host "Screensaver installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to copy screensaver: $_" -ForegroundColor Red
    Write-Host "Make sure no instances of the screensaver are running." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To configure the screensaver:" -ForegroundColor Yellow
Write-Host "1. Right-click on desktop and select 'Personalize'" -ForegroundColor White
Write-Host "2. Go to 'Lock screen' > 'Screen saver settings'" -ForegroundColor White
Write-Host "3. Select 'ApsScreensaver' from the dropdown" -ForegroundColor White
Write-Host "4. Click 'Apply' and 'OK'" -ForegroundColor White
Write-Host ""
Write-Host "Or run this command to open screensaver settings:" -ForegroundColor Yellow
Write-Host "  control desk.cpl,,@screensaver" -ForegroundColor Cyan
Write-Host ""

# Offer to open settings
$response = Read-Host "Open screensaver settings now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Start-Process "control.exe" "desk.cpl,,@screensaver"
}
