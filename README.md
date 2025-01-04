
# PowerShell Screensaver Manager

A PowerShell script that manages a web-based screensaver using a browser in kiosk mode. Supports multiple browsers including Chrome and Edge.

## Parameters
- `screensaverPath`: Path to the HTML screensaver file (will be created if doesn't exist)
- `browserPath`: Path to browser executable (Chrome or Edge recommended)
- `inactivityThreshold`: Number of seconds of inactivity before screensaver starts (default: 10)
- `iframeSrc`: URL of the content to display in screensaver

## Examples

Gold Sport Rýžoviště Office Single Slide Video

```shell
. C:\Users\jirih\Documents\aps-pages-installers\src\ScreensaverManager.ps1 -screensaverPath "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html" -browserPath "C:\Program Files\Google\Chrome\Application\chrome.exe" -iframeSrc "https://main.d14a7pjxtutfzh.amplifyapp.com/c9c6d4e2-e14c-471e-b4f0-ae58e5eecb64" -inactivityThreshold 10
```
T Quarters Video

```shell
. C:\Users\jirih\Documents\aps-pages-installers\src\ScreensaverManager.ps1 -screensaverPath "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html" -browserPath "C:\Program Files\Google\Chrome\Application\chrome.exe" -iframeSrc "https://main.d14a7pjxtutfzh.amplifyapp.com/aeeef41a-eb54-42a0-9316-706ce2d5231e" -inactivityThreshold 10
```

Edge:
```shell
. C:\Users\jirih\Documents\aps-pages-installers\src\ScreensaverManager.ps1 -screensaverPath "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html" -browserPath "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -inactivityThreshold 10
```

## Browser Paths Examples

```
browser_paths = {
        'opera': "/mnt/c/Users/jirih/AppData/Local/Programs/Opera/opera.exe",
        'edge': "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        'firefox': "/mnt/c/Program Files/Mozilla Firefox/firefox.exe",
        'chrome': "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
    }
```


## Key Features

1. **Reliable Activity Detection**
   - Uses Windows API for accurate user activity monitoring
   - Handles mouse movement, keyboard input, and system events
   - Prevents false triggers and ensures smooth activation

2. **Browser Process Management**
   - Clean process handling and termination
   - Automatic cleanup of temporary profiles
   - Regular process refresh for content updates (every 15 minutes)

3. **Window Management**
   - Proper fullscreen handling across multiple monitors
   - Window positioning and z-order management
   - Automatic window restoration after system events

4. **System Integration**
   - Creates desktop shortcut for easy access
   - System tray icon with exit option
   - Temporary file cleanup

## Architecture
- Uses Windows API (User32.dll) for system monitoring
- HTML-based screensaver with fullscreen iframe
- Browser in kiosk mode for display
- PowerShell-based process and window management
- Regular content refresh mechanism

## System Requirements
- Windows operating system
- PowerShell 5.1 or higher
- Supported browser (Chrome or Edge recommended)
- Internet connection for remote content

## Common Issues & Solutions
1. **Browser Compatibility**
   - Chrome and Edge are fully supported
   - Other browsers may have limited functionality
   - Ensure correct browser path is provided

2. **Display Issues**
   - Multiple monitors are supported via Windows API
   - Screensaver automatically adjusts to monitor resolution
   - Window position is maintained during display changes

3. **Process Management**
   - Automatic cleanup of old processes
   - Handles unexpected browser termination
   - Manages temporary profiles and cache

4. **Content Updates**
   - Regular refresh cycle every 15 minutes
   - Clean process restart for fresh content
   - Maintains user activity detection during updates