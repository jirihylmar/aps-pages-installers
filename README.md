# APS Pages Screensaver

A proper Windows screensaver (.scr) that displays APS Pages content using Microsoft Edge WebView2. This is a native Windows screensaver implementation that replaces the previous browser-based approach.

## Features

- **Proper Windows Screensaver**: Native .scr file with standard Windows screensaver behavior
- **WebView2 Integration**: Uses Microsoft Edge WebView2 for reliable web content rendering
- **No Browser Processes**: Embeds web rendering directly without launching separate browser windows
- **Proper Event Handling**: Reliable mouse and keyboard detection for exiting screensaver
- **Multi-Monitor Support**: Single form spanning all connected displays (works best with duplicate display mode)
- **Clean Exit**: Properly handles user input without getting stuck
- **Settings Dialog**: Standard Windows screensaver settings interface
- **Error Logging**: Detailed error logs for troubleshooting WebView2 issues

## Requirements

- Windows 10/11 (64-bit)
- .NET 8.0 SDK (for building)
- Microsoft Edge WebView2 Runtime (required - see Installation section)
- **Display Settings**: For multi-monitor setups, use **Duplicate** display mode for best results

## Quick Start

### Option 1: Build and Install (Recommended)

1. **Install WebView2 Runtime** (if not already installed):
   - The install script will check and guide you
   - Or download directly: https://go.microsoft.com/fwlink/p/?LinkId=2124703

2. **Install .NET 8.0 SDK**:
   - Download from: https://dotnet.microsoft.com/download/dotnet/8.0
   - Install the Windows x64 SDK installer

3. **Build the screensaver**:
   ```powershell
   .\build.ps1
   ```

4. **Install the screensaver** (requires administrator):
   ```powershell
   # Right-click PowerShell and "Run as Administrator"
   .\install.ps1
   ```
   The script will automatically check for WebView2 Runtime and prompt if missing.

5. **Configure in Windows**:
   - Right-click on desktop → Personalize → Lock screen → Screen saver settings
   - Select "ApsScreensaver" from the dropdown
   - Set your desired wait time
   - Click "Apply" and "OK"

6. **For multi-monitor setups**:
   - Press `Win + P`
   - Select **Duplicate** display mode
   - This ensures the screensaver displays correctly across all monitors

### Option 2: Manual Installation

1. Build the screensaver using `.\build.ps1`
2. Copy `build\ApsScreensaver.scr` to `C:\Windows\System32\`
3. Configure in Windows screensaver settings

## Architecture

### Previous Implementation (Legacy)

The old implementation used PowerShell to:
- Monitor user activity via Windows API
- Launch Chrome/Edge in kiosk mode
- Display web content in an iframe
- **Problems**: Cross-origin iframe issues, browser process cleanup, stuck screensaver

The legacy files are available in the `legacy/` folder.

### New Implementation (Current)

The new implementation uses C# with:
- **Native Windows screensaver** (.scr file format)
- **WebView2** for embedded web rendering
- **Proper command-line arguments**: `/s` (show), `/p` (preview), `/c` (configure)
- **Direct event handling**: No iframe cross-origin issues
- **Clean process management**: No zombie browser processes

#### Project Structure

```
aps-pages-installers/
├── src/
│   └── ApsScreensaver/          # C# screensaver project
│       ├── ApsScreensaver.csproj
│       ├── Program.cs            # Entry point and command-line handling
│       ├── ScreensaverForm.cs   # Main screensaver window with WebView2
│       └── SettingsForm.cs      # Configuration dialog
├── legacy/                       # Old PowerShell implementation
│   ├── ScreensaverManager.ps1
│   └── screensaver.html
├── build/                        # Build output (created by build.ps1)
│   └── ApsScreensaver.scr
├── build.ps1                     # Build script
├── install.ps1                   # Installation script
└── uninstall.ps1                # Uninstallation script
```

#### How It Works

1. **Command-Line Processing** (Program.cs):
   - Windows calls the .scr file with arguments
   - `/s` → Show screensaver (single form spanning all monitors)
   - `/c` → Show settings dialog
   - `/p [hwnd]` → Preview mode (shows simple preview text)

2. **Screensaver Display** (ScreensaverForm.cs):
   - Creates single fullscreen borderless window spanning all monitors
   - Initializes WebView2 with unique temporary user data folder
   - Loads APS Pages URL
   - Monitors for user input with `KeyPreview = true` and WebView2 event hooks
   - Prevents premature exit during initialization with `isInitializing` flag
   - Exits cleanly on any keyboard/mouse input
   - Logs errors to `%TEMP%\ApsScreensaver_Error.log` if WebView2 fails

3. **Settings** (SettingsForm.cs):
   - Simple configuration dialog
   - Shows current URL
   - Future: Allow URL customization

## Building from Source

### Prerequisites

Install .NET 8.0 SDK:
```powershell
# Download from: https://dotnet.microsoft.com/download/dotnet/8.0
# Use the Windows x64 SDK installer
```

### Build Process

The `build.ps1` script:
1. Checks for .NET SDK
2. Compiles the C# project
3. Publishes as a self-contained single-file executable
4. Copies the .exe to `build/ApsScreensaver.scr`

Output is a ~148MB self-contained screensaver that includes .NET 8.0 runtime and WebView2 bootstrapper.

## Installation

### System-Wide Installation (Requires Admin)

```powershell
.\install.ps1
```

Installs to `C:\Windows\System32\ApsScreensaver.scr`

### User Installation (No Admin)

```powershell
.\install.ps1 -User
```

Installs to `%USERPROFILE%\AppData\Local\Screensavers\ApsScreensaver.scr`

## Uninstallation

```powershell
.\uninstall.ps1
```

Removes the screensaver and cleans up temporary WebView2 data.

## Configuration

### Current URL

The screensaver currently displays:
```
https://main.d14a7pjxtutfzh.amplifyapp.com/
```

### Customizing the URL

To change the URL, edit `src/ApsScreensaver/ScreensaverForm.cs`:

```csharp
private const string SCREENSAVER_URL = "https://your-url-here.com/";
```

Then rebuild and reinstall the screensaver.

## Troubleshooting

### WebView2 Runtime Missing

The install script automatically checks for WebView2 Runtime. If you see an error:

1. **Download WebView2 Runtime**:
   - Direct link: https://go.microsoft.com/fwlink/p/?LinkId=2124703
   - Or visit: https://developer.microsoft.com/microsoft-edge/webview2/
   - Install the "Evergreen Standalone Installer"

2. **Verify Installation**:
   ```powershell
   # Check registry for WebView2
   Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" -ErrorAction SilentlyContinue
   ```

### Screensaver Shows Error Dialog

If you see "Failed to initialize screensaver: Operation aborted (0x80004004)":

1. **Check Error Log**:
   - Location: `%TEMP%\ApsScreensaver_Error.log`
   - Open with: `notepad $env:TEMP\ApsScreensaver_Error.log`
   - The log shows detailed error information

2. **Common Causes**:
   - WebView2 Runtime not installed or corrupted
   - Using Extended display mode with multiple monitors
   - WebView2 temporary folder permissions issue

3. **Solutions**:
   - Reinstall WebView2 Runtime
   - Switch to **Duplicate** display mode (`Win + P` → Duplicate)
   - Reinstall the screensaver with `.\install.ps1`

### Screensaver Won't Exit (Keyboard/Mouse Not Working)

This was the main problem with the old implementation. The current version fixes this:

- **Form-level keyboard capture**: `KeyPreview = true` ensures the form receives keyboard events
- **WebView2 keyboard events**: Hooked directly to close screensaver
- **Initialization flag**: Prevents race conditions during WebView2 startup
- **Error handler fix**: Sets `isInitializing = false` so keyboard works even if WebView2 fails

The screensaver exits on:
- Any keyboard press (ESC, Enter, Space, etc.)
- Mouse movement (threshold: 10 pixels)
- Mouse clicks
- Window deactivation

If it still gets stuck (very unlikely):
- Press `Ctrl+Alt+Delete` → Task Manager
- End the "ApsScreensaver.scr" process

### Multi-Monitor Issues

**Recommended Setup for Multiple Monitors**:
1. Press `Win + P`
2. Select **Duplicate** display mode
3. The screensaver will display the same content on all monitors

**Why Duplicate Mode?**
- Single WebView2 instance (more stable, less resource usage)
- Avoids synchronization issues
- Better performance
- Consistent experience across all displays

**Extended Mode**:
Extended display mode is supported (single form spans all monitors), but Duplicate mode is recommended for best stability.

### Build Errors

- **Ensure .NET 8.0 SDK is installed**:
  ```powershell
  dotnet --version  # Should show 8.0.x
  ```

- **If .NET SDK not found**:
  - Download: https://dotnet.microsoft.com/download/dotnet/8.0
  - Install the Windows x64 SDK
  - Restart PowerShell

- **Check build output** for specific errors

## Development

### Testing Without Installing

```powershell
# Build the screensaver
.\build.ps1

# Run in screensaver mode
.\build\ApsScreensaver.scr /s

# Run settings dialog
.\build\ApsScreensaver.scr /c
```

### Debug Mode

For development, build in Debug configuration:
```powershell
.\build.ps1 -Configuration Debug
```

## Comparison: Old vs New

| Aspect | Old (PowerShell + Browser) | New (C# + WebView2) |
|--------|---------------------------|---------------------|
| Type | PowerShell script | Native .scr file |
| Framework | PowerShell 5.1 | .NET 8.0 |
| Rendering | Chrome/Edge kiosk mode | Embedded WebView2 |
| Process | Separate browser process | Single process |
| Exit Detection | Fragile (iframe issues) | Reliable (direct events) |
| Multi-Monitor | Multiple browser windows | Single form spanning all displays |
| Installation | Manual/Task Scheduler | Standard Windows installer |
| Configuration | Command-line parameters | Settings dialog |
| Cleanup | Manual process killing | Automatic |
| Size | ~1 MB + browser | ~148 MB self-contained |
| Getting Stuck | Common | Fixed with initialization flag |
| Error Logging | None | Detailed log file |

## Why the Redesign?

The previous PowerShell implementation had critical issues:

1. **Cross-Origin Iframe Problems**: User input events were blocked by iframe security
2. **Browser Process Cleanup**: Chrome/Edge processes would remain stuck
3. **Not a Real Screensaver**: Windows didn't recognize it as a screensaver
4. **Fragile Exit Logic**: Activity detection was unreliable

The new C# implementation:
- Is a proper Windows screensaver that Windows recognizes
- Embeds web rendering directly (no iframe)
- Handles events reliably
- Cleans up automatically
- Never gets stuck

## License

Internal APS Pages project.

## Legacy Documentation

For the old PowerShell implementation, see `legacy/README.md` (if needed).
