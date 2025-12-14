# Start Development Session

Execute the following procedures to start a development session for APS Screensaver.

**Note:** This app is developed on this computer only. Skip unnecessary rebuilds if build already exists.

## 1. Environment Verification

Check that all required tools are installed and properly configured:

```powershell
# Verify .NET SDK version (should be 8.0.x)
dotnet --version

# Verify Git is configured
git config user.name
git config user.email

# Verify GitHub CLI authentication
gh auth status

# Check WebView2 Runtime installation
Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" -ErrorAction SilentlyContinue | Select-Object pv
```

**Expected results:**
- .NET SDK 8.0.x installed
- Git user configured
- GitHub CLI authenticated
- WebView2 Runtime version displayed

## 2. Git Status Check

```powershell
# Check current branch and status
git status

# Check for unpushed commits
git log origin/main..main --oneline

# Pull latest changes (if needed)
git pull origin main
```

## 3. Check Existing Build

Only rebuild if necessary (code changes or no build exists):

```powershell
# Check if build exists
if (Test-Path "build\ApsScreensaver.scr") {
    $size = [math]::Round((Get-Item "build\ApsScreensaver.scr").Length / 1MB, 2)
    $lastModified = (Get-Item "build\ApsScreensaver.scr").LastWriteTime
    Write-Host "Build exists: $size MB (modified: $lastModified)"
} else {
    Write-Host "No build found - rebuild required"
}
```

**If rebuild is needed:**

```powershell
.\build.ps1
```

## 4. Summary

After completing these steps, you should have:
- ✅ Environment verified
- ✅ Git status checked
- ✅ Build available (existing or fresh)

**Ready to develop!**
