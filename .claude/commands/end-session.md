# End Development Session

Execute the following procedures to properly close a development session for APS Screensaver:

## 1. Final Build

Clean and rebuild the project to ensure all changes are compiled:

```powershell
# Clean build artifacts
Remove-Item -Path "build\*" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\ApsScreensaver\bin" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\ApsScreensaver\obj" -Recurse -Force -ErrorAction SilentlyContinue

# Build release version
.\build.ps1
```

**Expected:** No errors or warnings, clean build output

## 2. Test the Build

```powershell
# Verify screensaver file exists and has correct size
if (Test-Path "build\ApsScreensaver.scr") {
    $size = (Get-Item "build\ApsScreensaver.scr").Length / 1MB
    Write-Host "Build successful! Size: $([math]::Round($size, 2)) MB"
} else {
    Write-Error "Build failed - ApsScreensaver.scr not found"
}

# Test screensaver execution
.\build\ApsScreensaver.scr /s
```

## 3. Code Quality Check

Review recent changes:

```powershell
# Show uncommitted changes
git status

# Show diff of changes
git diff

# Check for common issues
# - No hardcoded credentials
# - No debug code left in
# - Proper error handling
# - Clean code formatting
```

## 4. Documentation Updates

If you made significant changes:

- [ ] Update README.md with new features or changes
- [ ] Update version number if applicable
- [ ] Document any new configuration options
- [ ] Update troubleshooting section if needed

## 5. Git Commit

Commit changes following the established convention:

```powershell
# Stage all changes
git add -A

# Review what will be committed
git status

# Commit with descriptive message
git commit -m "Brief description of changes"
```

**Commit message guidelines:**
- Use simple, descriptive messages (like existing commits)
- Examples: "Fix keyboard input handling", "Update README", "Add error logging"
- Keep it concise and clear

## 6. Push to GitHub

```powershell
# Push to main branch
git push origin main
```

## 7. Create Release (If Version Changed)

**Only if this is a new version release:**

```powershell
# Create and publish GitHub release with binary
gh release create v1.x.x "build\ApsScreensaver.scr" `
    --title "APS Screensaver v1.x.x" `
    --notes "**Changes in this version:**
- Change 1
- Change 2
- Change 3

**Requirements:**
- Windows 10/11 (64-bit)
- Microsoft Edge WebView2 Runtime ([download link](https://go.microsoft.com/fwlink/p/?LinkId=2124703))

See [README](https://github.com/jirihylmar/aps-pages-installers/blob/main/README.md) for installation and troubleshooting."
```

## 8. Cleanup

```powershell
# Remove temporary files
Remove-Item -Path "$env:TEMP\ApsScreensaver_*" -Recurse -Force -ErrorAction SilentlyContinue

# Check for any lingering processes
Get-Process | Where-Object { $_.ProcessName -like "*ApsScreensaver*" }
```

## Final Checklist

Before closing:

- [ ] Final build completed successfully
- [ ] Build output tested and working
- [ ] All changes committed with clear message
- [ ] Changes pushed to GitHub
- [ ] Release created (if applicable)
- [ ] No uncommitted changes (`git status` clean)
- [ ] No debug/test files left behind
- [ ] Documentation updated if needed

## Summary

Your session is complete when:
- ✅ Code is built, tested, and working
- ✅ All changes are committed and pushed
- ✅ GitHub repository is up to date
- ✅ Release published (if version changed)
- ✅ Working directory is clean

**Session closed successfully!**
