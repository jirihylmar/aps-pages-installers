
# PowerShell Screensaver Manager

A PowerShell script that manages a web-based screensaver using a browser in kiosk mode. Supports multiple browsers including Chrome and Edge.

## Parameters
- `screensaverPath`: Path to the HTML screensaver file (will be created if doesn't exist)
- `browserPath`: Path to browser executable (Chrome or Edge recommended)
- `inactivityThreshold`: Number of seconds of inactivity before screensaver starts (default: 10)
- `iframeSrc`: URL of the content to display in screensaver

## Implementation to trigger from Desktop

0. Open Powershell
1. Enter command with parameters, see example commands
2. html template is created in the location `file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html`
3. Desktop shortcut called `Screensaver Manager` is created
4. Icon (dark grey square) in tray task bar is available
5. Let it run to reach timeout, test.
6. Right click tray icon and exit.
7. From now on, double click on shortcut `Screensaver Manager` will silently trigger service
8. Right click tray icon and exit.

Example commands

`Gold Sport Rýžoviště Office Single Slide Video`

```powershell
. C:\Users\jirih\Documents\aps-pages-installers\src\ScreensaverManager.ps1 -screensaverPath "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html" -browserPath "C:\Program Files\Google\Chrome\Application\chrome.exe" -iframeSrc "https://main.d14a7pjxtutfzh.amplifyapp.com/c9c6d4e2-e14c-471e-b4f0-ae58e5eecb64" -inactivityThreshold 10
```

`T Quarters Video`

```powershell
. C:\Users\jirih\Documents\aps-pages-installers\src\ScreensaverManager.ps1 -screensaverPath "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html" -browserPath "C:\Program Files\Google\Chrome\Application\chrome.exe" -iframeSrc "https://main.d14a7pjxtutfzh.amplifyapp.com/aeeef41a-eb54-42a0-9316-706ce2d5231e" -inactivityThreshold 10
```

Edge (not used):
```powershell
. C:\Users\jirih\Documents\aps-pages-installers\src\ScreensaverManager.ps1 -screensaverPath "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html" -browserPath "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -iframeSrc "https://main.d14a7pjxtutfzh.amplifyapp.com/aeeef41a-eb54-42a0-9316-706ce2d5231e" -inactivityThreshold 10
```

## Implementation Using Task Scheduler

- Win key, Search, Open Task Scheduler

**In Task Scheduler**

Right-click on "Task Scheduler Library"
Choose "Create Task" (not Basic Task)
Name it `ScreensaverManager`

**General tab**

- Name: "ScreensaverManager"
- Description: "ScreensaverManager task"
- Select "Run only when user is logged on"
- Select "Run with highest privileges"
- Configure for: Windows 10 (or your Windows version)

**Triggers tab**

- Click "New"
- Begin the task: "At logon of any user"

**Conditions tab**

- Uncheck "Start the task only if the computer is on AC power"

**Actions tab**

- Click "New"
- Action: "Start a program"
- In "Program/script" enter: `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe`
- In "Add arguments" enter: `-WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\Users\jirih\Documents\aps-pages-installers\src\ScreensaverManager.ps1" -screensaverPath "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html"`
- In "Start in" enter: `C:\Users\jirih\Documents\aps-pages-installers\src`

The Task Scheduler method is preferred because:

- It runs with system privileges
- Runs before user login
- Offers more control over execution conditions
- Provides logging and history

**Test**

In task scheduler you can test with icons on the right `run`, `end`.

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

## Browser Paths Examples

```
browser_paths = {
        'opera': "/mnt/c/Users/jirih/AppData/Local/Programs/Opera/opera.exe",
        'edge': "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        'firefox': "/mnt/c/Program Files/Mozilla Firefox/firefox.exe",
        'chrome': "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
    }
```