# APS Screensaver Build Script
# Builds the C# screensaver project and creates a .scr file

param(
    [Parameter(Mandatory=$false)]
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"

Write-Host "=== APS Screensaver Build Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if .NET SDK is installed
try {
    $dotnetVersion = dotnet --version
    Write-Host "Found .NET SDK version: $dotnetVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: .NET SDK not found. Please install .NET 6.0 SDK or later." -ForegroundColor Red
    Write-Host "Download from: https://dotnet.microsoft.com/download" -ForegroundColor Yellow
    exit 1
}

# Project paths
$ProjectDir = Join-Path $PSScriptRoot "src\ApsScreensaver"
$ProjectFile = Join-Path $ProjectDir "ApsScreensaver.csproj"
$OutputDir = Join-Path $PSScriptRoot "build"

# Check if project file exists
if (-not (Test-Path $ProjectFile)) {
    Write-Host "ERROR: Project file not found at $ProjectFile" -ForegroundColor Red
    exit 1
}

Write-Host "Building APS Screensaver..." -ForegroundColor Yellow
Write-Host "Project: $ProjectFile" -ForegroundColor Gray
Write-Host "Configuration: $Configuration" -ForegroundColor Gray
Write-Host ""

# Clean previous build
if (Test-Path $OutputDir) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Path $OutputDir -Recurse -Force
}

# Build the project
try {
    Write-Host "Running dotnet publish..." -ForegroundColor Yellow

    $publishOutput = Join-Path $ProjectDir "bin\$Configuration\net6.0-windows\win-x64\publish"

    dotnet publish $ProjectFile `
        -c $Configuration `
        -r win-x64 `
        --self-contained true `
        -p:PublishSingleFile=true `
        -p:PublishReadyToRun=true `
        -p:IncludeNativeLibrariesForSelfExtract=true `
        -p:DebugType=None `
        -p:DebugSymbols=false

    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }

    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: Build failed: $_" -ForegroundColor Red
    exit 1
}

# Create output directory
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

# Copy and rename to .scr
$exePath = Join-Path $publishOutput "ApsScreensaver.exe"
$scrPath = Join-Path $OutputDir "ApsScreensaver.scr"

if (Test-Path $exePath) {
    Write-Host "Creating screensaver file..." -ForegroundColor Yellow
    Copy-Item -Path $exePath -Destination $scrPath -Force
    Write-Host "Screensaver created: $scrPath" -ForegroundColor Green
} else {
    Write-Host "ERROR: Executable not found at $exePath" -ForegroundColor Red
    exit 1
}

# Get file size
$fileSize = (Get-Item $scrPath).Length / 1MB
Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Build Complete ===" -ForegroundColor Cyan
Write-Host "Screensaver location: $scrPath" -ForegroundColor Green
Write-Host ""
Write-Host "To install, run: .\install.ps1" -ForegroundColor Yellow
Write-Host ""
