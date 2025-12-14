# APS Screensaver Uninstallation Script
# Removes the screensaver from Windows

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "=== APS Screensaver Uninstallation ===" -ForegroundColor Cyan
Write-Host ""

# Paths to check
$SystemScr = Join-Path $env:SystemRoot "System32\ApsScreensaver.scr"
$UserScr = Join-Path $env:USERPROFILE "AppData\Local\Screensavers\ApsScreensaver.scr"
$TempWebView = Join-Path $env:TEMP "ApsScreensaver_WebView2"
$RegistryPath = "HKCU:\Software\APS\Screensaver"

$removed = $false

# Remove system installation
if (Test-Path $SystemScr) {
    Write-Host "Removing system screensaver..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $SystemScr -Force
        Write-Host "Removed: $SystemScr" -ForegroundColor Green
        $removed = $true
    } catch {
        Write-Host "ERROR: Failed to remove system screensaver: $_" -ForegroundColor Red
        Write-Host "Make sure no instances of the screensaver are running." -ForegroundColor Yellow
    }
}

# Remove user installation
if (Test-Path $UserScr) {
    Write-Host "Removing user screensaver..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $UserScr -Force
        Write-Host "Removed: $UserScr" -ForegroundColor Green
        $removed = $true
    } catch {
        Write-Host "ERROR: Failed to remove user screensaver: $_" -ForegroundColor Red
    }
}

# Remove WebView2 temp data
if (Test-Path $TempWebView) {
    Write-Host "Removing WebView2 temporary data..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $TempWebView -Recurse -Force
        Write-Host "Removed: $TempWebView" -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Could not remove WebView2 temp data: $_" -ForegroundColor Yellow
    }
}

# Remove registry settings
if (Test-Path $RegistryPath) {
    Write-Host "Removing registry settings..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $RegistryPath -Recurse -Force
        Write-Host "Removed registry settings" -ForegroundColor Green

        # Clean up parent key if empty
        $parentPath = "HKCU:\Software\APS"
        if (Test-Path $parentPath) {
            $children = Get-ChildItem -Path $parentPath -ErrorAction SilentlyContinue
            if ($null -eq $children -or $children.Count -eq 0) {
                Remove-Item -Path $parentPath -Force
                Write-Host "Removed empty parent registry key" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "WARNING: Could not remove registry settings: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
if ($removed) {
    Write-Host "=== Uninstallation Complete ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "The screensaver has been removed." -ForegroundColor Green
    Write-Host "You may need to select a different screensaver in Windows settings." -ForegroundColor Yellow
} else {
    Write-Host "No screensaver installation found." -ForegroundColor Yellow
}
Write-Host ""
