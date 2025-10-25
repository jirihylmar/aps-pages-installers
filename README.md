# APS Pages Screensaver

A proper Windows screensaver (.scr) that displays APS Pages content using Microsoft Edge WebView2. This is a native Windows screensaver implementation that replaces the previous browser-based approach.

## Features

- **Proper Windows Screensaver**: Native .scr file with standard Windows screensaver behavior
- **WebView2 Integration**: Uses Microsoft Edge WebView2 for reliable web content rendering
- **No Browser Processes**: Embeds web rendering directly without launching separate browser windows
- **Proper Event Handling**: Reliable mouse and keyboard detection for exiting screensaver
- **Multi-Monitor Support**: Displays across all connected screens
- **Clean Exit**: Properly handles user input without getting stuck
- **Settings Dialog**: Standard Windows screensaver settings interface

## Requirements

- Windows 10/11 (64-bit)
- .NET 6.0 SDK (for building)
- Microsoft Edge WebView2 Runtime (usually pre-installed on Windows 10/11)

## Quick Start

### Option 1: Build and Install (Recommended)

1. **Build the screensaver**:
   ```powershell
   .\build.ps1
   ```

2. **Install the screensaver** (requires administrator):
   ```powershell
   .\install.ps1
   ```

3. **Configure in Windows**:
   - Right-click on desktop → Personalize → Lock screen → Screen saver settings
   - Select "ApsScreensaver" from the dropdown
   - Set your desired wait time
   - Click "Apply" and "OK"

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
   - `/s` → Show screensaver on all monitors
   - `/c` → Show settings dialog
   - `/p [hwnd]` → Preview mode (not implemented)

2. **Screensaver Display** (ScreensaverForm.cs):
   - Creates fullscreen borderless window on each monitor
   - Initializes WebView2 with custom settings
   - Loads APS Pages URL
   - Monitors for user input (mouse move, mouse click, keyboard)
   - Exits cleanly on any input

3. **Settings** (SettingsForm.cs):
   - Simple configuration dialog
   - Shows current URL
   - Future: Allow URL customization

## Building from Source

### Prerequisites

Install .NET 6.0 SDK:
```powershell
# Download from: https://dotnet.microsoft.com/download/dotnet/6.0
```

### Build Process

The `build.ps1` script:
1. Checks for .NET SDK
2. Compiles the C# project
3. Publishes as a self-contained single-file executable
4. Copies the .exe to `build/ApsScreensaver.scr`

Output is a ~100MB self-contained screensaver that includes .NET runtime and WebView2 bootstrapper.

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

If you get an error about WebView2 Runtime:
1. Download from: https://developer.microsoft.com/microsoft-edge/webview2/
2. Install the Evergreen Bootstrapper or Standalone Installer

### Screensaver Won't Start

- Check Windows screensaver settings
- Ensure WebView2 Runtime is installed
- Check Event Viewer for application errors

### Screensaver Won't Exit

This was the main problem with the old implementation. The new implementation:
- Detects mouse movement with threshold (10 pixels)
- Detects mouse clicks
- Detects keyboard input
- Exits immediately on any detected input

If it still gets stuck (unlikely):
- Press Ctrl+Alt+Delete to open Task Manager
- End the "ApsScreensaver.scr" process

### Build Errors

- Ensure .NET 6.0 SDK is installed
- Run `dotnet --version` to verify
- Check that project files are not corrupted

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
| Rendering | Chrome/Edge kiosk mode | Embedded WebView2 |
| Process | Separate browser process | Single process |
| Exit Detection | Fragile (iframe issues) | Reliable (direct events) |
| Installation | Manual/Task Scheduler | Standard Windows |
| Configuration | Command-line parameters | Settings dialog |
| Cleanup | Manual process killing | Automatic |
| Size | ~1 MB + browser | ~100 MB self-contained |
| Getting Stuck | Common | Fixed |

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
