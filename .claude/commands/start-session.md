# Start Development Session

Execute the following procedures to start a development session for APS Screensaver:

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

# Pull latest changes
git pull origin main
```

## 3. Clean Build

```powershell
# Clean previous build artifacts
Remove-Item -Path "build\*" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\ApsScreensaver\bin" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\ApsScreensaver\obj" -Recurse -Force -ErrorAction SilentlyContinue

# Build the project
.\build.ps1
```

**Expected result:** Build succeeds with no errors or warnings

## 4. Verify Build Output

```powershell
# Check that screensaver was created
Test-Path "build\ApsScreensaver.scr"

# Check file size (should be ~148 MB)
(Get-Item "build\ApsScreensaver.scr").Length / 1MB
```

## 5. Quick Test

```powershell
# Test screensaver in preview mode (should exit cleanly with ESC)
.\build\ApsScreensaver.scr /s
```

## Summary

After completing these steps, you should have:
- ✅ Clean working directory
- ✅ Latest code from main branch
- ✅ Fresh build of ApsScreensaver.scr
- ✅ Verified build output

**Ready to develop!**
