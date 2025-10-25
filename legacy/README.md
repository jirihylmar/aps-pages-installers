# Legacy PowerShell Screensaver Manager

**DEPRECATED**: This implementation has been replaced with a proper Windows screensaver in C#.

See the main README.md for the new implementation.

## Why This Was Deprecated

The PowerShell implementation had several critical issues:

1. **Gets Stuck**: Cross-origin iframe security blocks user input events from propagating to the parent window, preventing the screensaver from exiting
2. **Browser Process Issues**: Chrome/Edge processes don't clean up properly and can remain stuck
3. **Not a Real Screensaver**: Windows doesn't recognize this as a screensaver - it's just a script launching a browser
4. **Fragile Activity Detection**: Activity detection only works when the main PowerShell loop runs, not when the browser has focus

## Files

- `ScreensaverManager.ps1`: PowerShell script that monitors activity and launches browser
- `screensaver.html`: HTML template with iframe (auto-generated)

## Original Usage

See git history or the main README.md for original documentation.

## Migration

To migrate to the new screensaver:

1. Stop the old PowerShell script (exit from system tray)
2. Remove any Task Scheduler tasks running ScreensaverManager.ps1
3. Delete the desktop shortcut "Screensaver Manager"
4. Build and install the new C# screensaver (see main README.md)
