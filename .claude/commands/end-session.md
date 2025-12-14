# End Development Session

Execute the following procedures to properly close a development session for APS Screensaver.

**Note:** This app is developed on this computer only.

## 1. Build (If Code Changed)

Only rebuild if source code was modified:

```powershell
# Check if source is newer than build
$buildTime = if (Test-Path "build\ApsScreensaver.scr") { (Get-Item "build\ApsScreensaver.scr").LastWriteTime } else { [datetime]::MinValue }
$srcTime = (Get-ChildItem "src\ApsScreensaver\*.cs" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime

if ($srcTime -gt $buildTime) {
    Write-Host "Source changed - rebuilding..."
    .\build.ps1
} else {
    Write-Host "Build is up to date"
}
```

## 2. Verify Build

```powershell
# Verify screensaver file exists
if (Test-Path "build\ApsScreensaver.scr") {
    $size = [math]::Round((Get-Item "build\ApsScreensaver.scr").Length / 1MB, 2)
    Write-Host "Build OK: $size MB"
} else {
    Write-Error "Build not found!"
}
```

## 3. Git Status and Commit

```powershell
# Show uncommitted changes
git status

# Show diff summary
git diff --stat
```

**If there are changes to commit:**

```powershell
# Stage changes (exclude local settings)
git add src/ build.ps1 install.ps1 uninstall.ps1 README.md LICENSE

# Review staged changes
git status

# Commit with descriptive message
git commit -m "Brief description of changes"

# Push to GitHub
git push origin main
```

## 4. Create/Update Release

**Always ask user if a new release should be created.**

If releasing a new version:

1. Determine version number (check existing releases):
```powershell
gh release list
```

2. Create zip file for release:
```powershell
Compress-Archive -Path "build\ApsScreensaver.scr" -DestinationPath "build\ApsScreensaver-v1.x.x.zip" -Force
```

3. Create GitHub release:
```powershell
gh release create v1.x.x "build\ApsScreensaver-v1.x.x.zip" `
    --title "APS Screensaver v1.x.x" `
    --notes "## What's New in v1.x.x

- Change 1
- Change 2

## Requirements

- Windows 10/11 (64-bit)
- Microsoft Edge WebView2 Runtime ([download](https://go.microsoft.com/fwlink/p/?LinkId=2124703))
- **Internet connection required**

## Installation

1. Download and extract `ApsScreensaver-v1.x.x.zip`
2. Right-click `ApsScreensaver.scr` → **Install**
3. Configure in Windows screensaver settings

See [README](https://github.com/jirihylmar/aps-pages-installers/blob/main/README.md) for full instructions."
```

## 5. Cleanup

```powershell
# Remove temporary files
Remove-Item -Path "$env:TEMP\ApsScreensaver_*" -Recurse -Force -ErrorAction SilentlyContinue

# Remove release zip (already uploaded)
Remove-Item -Path "build\*.zip" -Force -ErrorAction SilentlyContinue
```

## 6. Final Checklist

- [ ] Build is up to date
- [ ] All changes committed
- [ ] Changes pushed to GitHub
- [ ] Release created/updated (if applicable)
- [ ] `git status` shows clean working directory

## Summary

Session is complete when:
- ✅ Code committed and pushed
- ✅ GitHub repository up to date
- ✅ Release published (if new version)

**Session closed successfully!**
