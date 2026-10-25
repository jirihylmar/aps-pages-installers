<!-- Local overlay applied on top of the canonical start-session.md
     by /distribute-defaults in syndicate-playbooks-examples.
     Edit only the splice content; the directives drive placement.
     Project-specific session steps live HERE, never as direct edits to
     .claude/commands/start-session.md (those are flagged divergent and block
     distribution). Validate with /overlay-check after every edit. -->

<!-- splice-before: "### 1. Read Orchestration Files" -->
### 0.9. APS Screensaver Environment and Build (this project; Windows-native)

**This app is developed on this computer only.** The checkout lives on the Windows drive
(`C:\Users\jirih\aps-pages-installers`) because the build is Windows-native. Skip unnecessary
rebuilds if a build already exists.

The blocks below are PowerShell. From a WSL session, run each through
`powershell.exe -NoProfile -Command '...'`.

**Environment verification:**

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

**Check the existing build.** Only rebuild if necessary (code changes or no build exists):

```powershell
if (Test-Path "build\ApsScreensaver.scr") {
    $size = [math]::Round((Get-Item "build\ApsScreensaver.scr").Length / 1MB, 2)
    $lastModified = (Get-Item "build\ApsScreensaver.scr").LastWriteTime
    Write-Host "Build exists: $size MB (modified: $lastModified)"
} else {
    Write-Host "No build found - rebuild required"
}
```

If a rebuild is needed: `.\build.ps1`

Report the .NET, gh, WebView2 and build results in the Step 9 ready block.

