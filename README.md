# APS Pages Screensaver

A Windows screensaver that displays APS Pages content using Microsoft Edge WebView2. Native .scr file with standard Windows screensaver behavior.

## Features

- **Native Windows Screensaver**: Standard .scr file recognized by Windows
- **Configurable URL**: Set any web page URL via Windows screensaver settings
- **WebView2 Integration**: Uses Microsoft Edge WebView2 for reliable web rendering
- **Multi-Monitor Support**: Single display spanning all connected monitors (works best with duplicate display mode)
- **Reliable Exit**: Press any key, move mouse, or click to exit
- **Error Logging**: Detailed error logs for troubleshooting

> **Note**: This screensaver displays content from the internet. An active internet connection is required for the screensaver to work.

## For End Users

### Requirements

- Windows 10/11 (64-bit)
- Microsoft Edge WebView2 Runtime ([download here](https://go.microsoft.com/fwlink/p/?LinkId=2124703))
- **Internet connection** (content is loaded from the web each time the screensaver starts)
- **Multi-monitor setup**: Use **Duplicate** display mode (`Win + P` → Duplicate)

### Installation

1. **Download the screensaver**:
   - Get `ApsScreensaver.scr` from the latest release

2. **Install WebView2 Runtime** (if not already installed):
   - Download: https://go.microsoft.com/fwlink/p/?LinkId=2124703
   - Double-click the installer
   - Follow the prompts

3. **Install the screensaver**:
   - Right-click on `ApsScreensaver.scr`
   - Select **"Install"**
   - Windows will copy it to `C:\Windows\System32\`
   - **After installation, you can delete the downloaded file** - it's no longer needed

4. **Configure the screensaver**:
   - Right-click on desktop → "Personalize"
   - Click "Lock screen" (Windows 11) or "Screen Saver" (Windows 10)
   - In Windows 11: Click "Screen saver"
   - Select **"ApsScreensaver"** from the dropdown
   - Click **"Settings..."** to configure the URL
   - Set wait time (e.g., 5 minutes)
   - Click "Apply" then "OK"

5. **Set a custom URL** (optional):
   - In the screensaver selection dialog, click **"Settings..."**
   - Enter your custom URL (e.g., `https://main.d14a7pjxtutfzh.amplifyapp.com/your-page-id`)
   - Click "OK" to save

6. **For multiple monitors**:
   - Press `Win + P`
   - Select **Duplicate**
   - This ensures stable performance across all displays

### Testing

- Click "Preview" in screensaver settings to test
- Press `ESC` or any key to exit
- Move mouse to exit

### Uninstall

1. Open screensaver settings
2. Change to a different screensaver (e.g., "Blank")
3. Delete `C:\Windows\System32\ApsScreensaver.scr` (requires administrator access)

The screensaver stores its URL setting in the Windows Registry at `HKEY_CURRENT_USER\Software\APS\Screensaver`. This is automatically cleaned up if you use the `uninstall.ps1` script.

### Troubleshooting

#### Error: "Failed to initialize screensaver"

1. **Install WebView2 Runtime**:
   - Download: https://go.microsoft.com/fwlink/p/?LinkId=2124703
   - Run the installer

2. **Check display mode**:
   - Press `Win + P`
   - Select **Duplicate** (not Extended)

3. **Check error log**:
   - Press `Win + R`
   - Type: `%TEMP%\ApsScreensaver_Error.log`
   - Press Enter
   - Share the log contents for support

#### Can't exit screensaver

- Press `ESC` or any key
- Move the mouse
- If still stuck: Press `Ctrl+Alt+Delete` → Task Manager → End "ApsScreensaver.scr"

#### Preview shows error or doesn't work

- This is normal during first installation
- Try the full screensaver activation instead
- Make sure WebView2 Runtime is installed

---

## For Developers

### Requirements

- Windows 10/11 (64-bit)
- .NET 8.0 SDK ([download](https://dotnet.microsoft.com/download/dotnet/8.0))
- Microsoft Edge WebView2 Runtime
- Git (optional)

### Building from Source

1. **Install .NET 8.0 SDK**:
   ```powershell
   # Download from: https://dotnet.microsoft.com/download/dotnet/8.0
   # Install the Windows x64 SDK
   ```

2. **Clone or download the repository**:
   ```powershell
   git clone <repository-url>
   cd aps-pages-installers
   ```

3. **Build**:
   ```powershell
   .\build.ps1
   ```
   Output: `build\ApsScreensaver.scr` (~148 MB)

4. **Install** (requires administrator):
   ```powershell
   # Right-click PowerShell → "Run as Administrator"
   .\install.ps1
   ```

5. **Test without installing**:
   ```powershell
   # Run in screensaver mode
   .\build\ApsScreensaver.scr /s

   # Run settings dialog
   .\build\ApsScreensaver.scr /c

   # Preview mode
   .\build\ApsScreensaver.scr /p
   ```

### Project Structure

```
aps-pages-installers/
├── src/
│   └── ApsScreensaver/          # C# screensaver project
│       ├── ApsScreensaver.csproj
│       ├── Program.cs            # Entry point and command-line handling
│       ├── ScreensaverForm.cs   # Main screensaver window with WebView2
│       └── SettingsForm.cs      # Configuration dialog
├── build/                        # Build output (created by build.ps1)
│   └── ApsScreensaver.scr
├── build.ps1                     # Build script
├── install.ps1                   # Installation script
└── uninstall.ps1                # Uninstallation script
```

### How It Works

1. **Command-Line Processing** (Program.cs):
   - Windows calls the .scr file with arguments:
     - `/s` → Show screensaver (single form spanning all monitors)
     - `/c` → Show settings dialog
     - `/p [hwnd]` → Preview mode (shows simple preview text)

2. **Screensaver Display** (ScreensaverForm.cs):
   - Creates single fullscreen borderless window spanning all monitors
   - Initializes WebView2 with unique temporary user data folder
   - Loads APS Pages URL: `https://main.d14a7pjxtutfzh.amplifyapp.com/`
   - Monitors for user input with `KeyPreview = true` and WebView2 event hooks
   - Prevents premature exit during initialization with `isInitializing` flag
   - Exits cleanly on any keyboard/mouse input
   - Logs errors to `%TEMP%\ApsScreensaver_Error.log` if WebView2 fails

3. **Settings** (SettingsForm.cs):
   - Configuration dialog accessible from Windows screensaver settings
   - Allows users to set a custom URL
   - URL validation (must be valid HTTP/HTTPS)
   - Settings stored in Windows Registry

4. **Settings Persistence** (ScreensaverSettings.cs):
   - Stores URL in `HKCU\Software\APS\Screensaver`
   - Provides default URL if none configured

### Customizing the URL

The URL can be configured by end users via the Settings dialog (accessed from Windows screensaver settings).

Settings are stored in the Windows Registry at `HKEY_CURRENT_USER\Software\APS\Screensaver`.

To change the default URL, edit `src/ApsScreensaver/ScreensaverSettings.cs`:

```csharp
public const string DefaultUrl = "https://your-url-here.com/";
```

Then rebuild and reinstall.

### Build Process

The `build.ps1` script:
1. Checks for .NET 8.0 SDK
2. Compiles the C# project in Release configuration
3. Publishes as a self-contained single-file executable
4. Copies the .exe to `build/ApsScreensaver.scr`

Output is a ~148MB self-contained screensaver that includes .NET 8.0 runtime.

### Installation Scripts

**install.ps1** (requires administrator):
- Checks for WebView2 Runtime installation
- Prompts to download if missing
- Copies .scr to `C:\Windows\System32\`
- Can use `-User` flag to install to user directory instead

**uninstall.ps1**:
- Removes the screensaver from system directory
- Cleans up temporary WebView2 data

### Development Tips

**Verify .NET SDK**:
```powershell
dotnet --version  # Should show 8.0.x
```

**Check WebView2 Installation**:
```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" -ErrorAction SilentlyContinue
```

**Build in Debug Mode**:
```powershell
dotnet build src/ApsScreensaver/ApsScreensaver.csproj -c Debug
```

### Technical Details

**Multi-Monitor Handling**:
- Single form spans entire virtual screen area
- Single WebView2 instance (avoids conflicts)
- Recommended: Duplicate display mode for best stability
- Extended mode supported but may have performance impact

**WebView2 Configuration**:
- Unique temporary folder per instance: `%TEMP%\ApsScreensaver_WebView2_[GUID]`
- Disabled context menus, dev tools, zoom controls
- No script dialogs or status bar

**Keyboard Event Handling**:
- `KeyPreview = true` on form (captures before child controls)
- WebView2 control keyboard events
- `isInitializing` flag prevents race conditions
- Events hooked: KeyPress, KeyDown, PreviewKeyDown

**Error Logging**:
- Log file: `%TEMP%\ApsScreensaver_Error.log`
- Contains: timestamp, exception type, message, stack trace, HRESULT
- Created automatically on WebView2 initialization errors

### Troubleshooting (Developers)

**Build Errors**:
```powershell
# Ensure .NET 8.0 SDK is installed
dotnet --version  # Should show 8.0.x

# If not found
# Download: https://dotnet.microsoft.com/download/dotnet/8.0
# Restart PowerShell after installation
```

**WebView2 Issues**:
- Check error log: `%TEMP%\ApsScreensaver_Error.log`
- Common HRESULT: `0x80004004` (E_ABORT) = operation cancelled
- Usually caused by: missing WebView2, multi-monitor conflicts, or permissions

**Testing**:
```powershell
# Quick test without installation
.\build\ApsScreensaver.scr /s

# Test on specific monitor setup
# Use Duplicate mode: Win+P → Duplicate
```

## Architecture

### Technology Stack

- **Framework**: .NET 8.0 (C#)
- **UI**: Windows Forms
- **Web Rendering**: Microsoft Edge WebView2
- **Target**: Windows 10/11 (x64)
- **Deployment**: Self-contained single-file executable

### Why These Technologies?

**Native Windows Screensaver**:
- Proper .scr file format recognized by Windows
- Standard installation and configuration
- No background processes or scheduled tasks

**WebView2 over Browser Launch**:
- Embedded rendering (no separate browser windows)
- No iframe cross-origin issues
- Better resource cleanup
- Direct event handling
- Single process

**Single Form Multi-Monitor**:
- One WebView2 instance (stable, efficient)
- No synchronization issues
- Lower memory footprint
- Simpler event handling

**Self-Contained Deployment**:
- No .NET runtime installation required
- Works on any Windows 10/11 machine
- Larger file size (~148MB) but simpler deployment

## License

Internal APS Pages project.
