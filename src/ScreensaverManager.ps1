param (
    [string]$screensaverPath = "file:///C:/Users/jirih/Documents/aps-pages-installers/src/screensaver.html",
    [string]$browserPath = "C:\Program Files\Google\Chrome\Application\chrome.exe",
    [string]$iframeSrc = "https://main.d14a7pjxtutfzh.amplifyapp.com/c9c6d4e2-e14c-471e-b4f0-ae58e5eecb64",
    [int]$inactivityThreshold = 10
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Screensaver</title>
    <style>
        * { margin: 0; padding: 0; overflow: hidden; }
        body { background: #000; }
        iframe { width: 100vw; height: 100vh; border: 0; }
    </style>
</head>
<body>
    <iframe src=`"$iframeSrc`" allow="autoplay"></iframe>
    <script>
        window.onload = function() {
            document.documentElement.requestFullscreen().catch(console.error);
        };
        function exitScreensaver() {
            if (document.fullscreenElement) {
                document.exitFullscreen().then(function() { window.close(); }).catch(function() { window.close(); });
            } else {
                window.close();
            }
        }
        window.addEventListener("keydown", exitScreensaver);
        window.addEventListener("mousedown", exitScreensaver);
        window.addEventListener("mousemove", exitScreensaver);
        window.addEventListener("click", exitScreensaver);
    </script>
</body>
</html>
"@

$htmlFilePath = $screensaverPath -replace "file:///", ""
$htmlContent | Out-File -FilePath $htmlFilePath -Encoding UTF8

if (-not ([System.Management.Automation.PSTypeName]'WinAPI').Type) {
    Add-Type @'
        using System;
        using System.Runtime.InteropServices;
        public class WinAPI {
            [DllImport("User32.dll")]
            private static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
            
            [DllImport("user32.dll")]
            public static extern bool SetForegroundWindow(IntPtr hWnd);
            
            [DllImport("user32.dll")]
            public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

            [DllImport("user32.dll")]
            public static extern bool BringWindowToTop(IntPtr hWnd);

            [DllImport("user32.dll")] 
            public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

            [DllImport("user32.dll")]
            public static extern IntPtr GetForegroundWindow();

            [DllImport("user32.dll")]
            public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool GetMonitorInfo(IntPtr hMonitor, ref MONITORINFO lpmi);

            [DllImport("user32.dll")]
            public static extern IntPtr MonitorFromWindow(IntPtr hwnd, uint dwFlags);

            public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
            public const uint SWP_NOMOVE = 0x0002;
            public const uint SWP_NOSIZE = 0x0001;
            public const uint SWP_SHOWWINDOW = 0x0040;
            public const int SW_MAXIMIZE = 3;
            public const int SW_RESTORE = 9;
            public const uint MONITOR_DEFAULTTOPRIMARY = 1;
            
            public static uint GetLastInputTime() {
                LASTINPUTINFO lastInput = new LASTINPUTINFO();
                lastInput.cbSize = (uint)Marshal.SizeOf(lastInput);
                GetLastInputInfo(ref lastInput);
                return ((uint)Environment.TickCount - lastInput.dwTime) / 1000;
            }
            
            [StructLayout(LayoutKind.Sequential)]
            private struct LASTINPUTINFO {
                public uint cbSize;
                public uint dwTime;
            }

            [StructLayout(LayoutKind.Sequential)]
            public struct RECT {
                public int Left;
                public int Top;
                public int Right;
                public int Bottom;
            }

            [StructLayout(LayoutKind.Sequential)]
            public struct MONITORINFO {
                public uint cbSize;
                public RECT rcMonitor;
                public RECT rcWork;
                public uint dwFlags;
            }
        }
'@
}

$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Text = "Screensaver Manager"

$iconBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
$iconBytes = [Convert]::FromBase64String($iconBase64)
$iconStream = New-Object IO.MemoryStream($iconBytes, 0, $iconBytes.Length)
$iconStream.Write($iconBytes, 0, $iconBytes.Length)
$trayIcon.Icon = [System.Drawing.Icon]::FromHandle(([System.Drawing.Bitmap]::new($iconStream).GetHIcon()))
$trayIcon.Visible = $true

$contextMenu = New-Object System.Windows.Forms.ContextMenuStrip
$exitMenuItem = New-Object System.Windows.Forms.ToolStripMenuItem
$exitMenuItem.Text = "Exit"
$exitMenuItem.Add_Click({
    $trayIcon.Visible = $false
    Cleanup-ChromeProcesses
    Stop-Process $PID
})

$contextMenu.Items.Add($exitMenuItem)
$trayIcon.ContextMenuStrip = $contextMenu

Write-Host "Starting screensaver monitor..."
Write-Host "Browser Path: $browserPath"
Write-Host "Inactivity Threshold: $inactivityThreshold seconds"

$lastInputTime = [WinAPI]::GetLastInputTime()
$screensaverProcess = $null
$startTime = Get-Date
$wasWinDPressed = $false
$profileDir = Join-Path $env:TEMP "screensaver_$(Get-Random)"

function Cleanup-ChromeProcesses {
    $chromeProcesses = Get-Process chrome -ErrorAction SilentlyContinue | 
        Where-Object { $_.StartTime -gt $startTime }
    
    if ($chromeProcesses) {
        Write-Host "Found $($chromeProcesses.Count) Chrome processes to clean up..."
        foreach ($process in $chromeProcesses) {
            try {
                $currentProcess = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
                if ($currentProcess) {
                    Write-Host "Attempting to stop process $($process.Id)..."
                    
                    if (-not $process.HasExited) {
                        $process.CloseMainWindow() | Out-Null
                        if ($process.WaitForExit(2000)) {
                            Write-Host "Process $($process.Id) closed gracefully"
                            continue
                        }
                    }
                    
                    if (-not $process.HasExited) {
                        $process.Kill()
                        $process.WaitForExit(2000)
                        Write-Host "Process $($process.Id) killed"
                    }
                }
            } catch {
                Write-Warning ("Error killing Chrome process " + $process.Id + ": " + $_.Exception.Message)
            }
        }
        
        # Clean cache directories
        if (Test-Path $profileDir) {
            Get-ChildItem -Path $profileDir -Recurse -Force | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
            Remove-Item -Path $profileDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Set-ScreensaverWindow {
    param (
        [System.Diagnostics.Process]$process
    )
    
    if ($process -and -not $process.HasExited) {
        Start-Sleep -Milliseconds 500

        $hwnd = $process.MainWindowHandle
        $monitor = [WinAPI]::MonitorFromWindow($hwnd, [WinAPI]::MONITOR_DEFAULTTOPRIMARY)
        $monitorInfo = New-Object WinAPI+MONITORINFO
        $monitorInfo.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($monitorInfo)
        [WinAPI]::GetMonitorInfo($monitor, [ref]$monitorInfo)

        [WinAPI]::ShowWindow($hwnd, [WinAPI]::SW_RESTORE)
        [WinAPI]::SetWindowPos(
            $hwnd, 
            [WinAPI]::HWND_TOPMOST,
            $monitorInfo.rcMonitor.Left,
            $monitorInfo.rcMonitor.Top,
            $monitorInfo.rcMonitor.Right - $monitorInfo.rcMonitor.Left,
            $monitorInfo.rcMonitor.Bottom - $monitorInfo.rcMonitor.Top,
            [WinAPI]::SWP_SHOWWINDOW
        )
        [WinAPI]::ShowWindow($hwnd, [WinAPI]::SW_MAXIMIZE)
        [WinAPI]::SetForegroundWindow($hwnd)
        [WinAPI]::BringWindowToTop($hwnd)
    }
}

$browserArgs = @(
    "--user-data-dir=`"$profileDir`"",
    "--kiosk",
    "--app=$screensaverPath",
    "--start-fullscreen",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-mode",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-sync",
    "--always-on-top",
    "--window-position=0,0",
    "--disable-application-cache",
    "--disable-cache",
    "--disable-gpu-shader-disk-cache",
    "--media-cache-size=1",
    "--disk-cache-size=1",
    "--aggressive-cache-discard",
    "--incognito"
)

function Test-UserActivity {
    $currentInputTime = [WinAPI]::GetLastInputTime()
    $activityDetected = $currentInputTime -lt $lastInputTime
    $script:lastInputTime = $currentInputTime
    return $activityDetected
}

Get-ChildItem $env:TEMP -Directory -Filter "screensaver_*" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddHours(-1) } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\Screensaver Manager.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`" -screensaverPath `"$screensaverPath`" -browserPath `"$browserPath`" -inactivityThreshold $inactivityThreshold"
$Shortcut.WorkingDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$Shortcut.WindowStyle = 7
$Shortcut.Save()

while ($true) {
    try {
        $activityDetected = Test-UserActivity

        if ($activityDetected) {
            Write-Host "Activity detected"
            if ($screensaverProcess -and -not $screensaverProcess.HasExited) {
                Write-Host "Stopping screensaver"
                Cleanup-ChromeProcesses
                $screensaverProcess = $null
                
                if (Test-Path $profileDir) {
                    Remove-Item -Path $profileDir -Recurse -Force -ErrorAction SilentlyContinue
                }
            }
        }

        $currentInputTime = [WinAPI]::GetLastInputTime()
        if ($currentInputTime -ge $inactivityThreshold -and 
            (-not $screensaverProcess -or $screensaverProcess.HasExited)) {
            
            Write-Host "Starting screensaver (Current idle time: $currentInputTime seconds)"
            
            $script:startTime = Get-Date
            
            if (Test-Path $profileDir) {
                Remove-Item -Path $profileDir -Recurse -Force -ErrorAction SilentlyContinue
            }
            New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
            
            $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processStartInfo.FileName = $browserPath
            $processStartInfo.Arguments = $browserArgs
            $processStartInfo.UseShellExecute = $false
            
            $screensaverProcess = [System.Diagnostics.Process]::Start($processStartInfo)
            
            if ($screensaverProcess -and -not $screensaverProcess.HasExited) {
                Set-ScreensaverWindow -process $screensaverProcess
                $script:lastWindowCheck = Get-Date
            }
            
            Start-Sleep -Seconds 2
            if (-not $screensaverProcess -or $screensaverProcess.HasExited) {
                Write-Warning "Screensaver process failed to start or exited immediately"
                Cleanup-ChromeProcesses
            }
        }

        if ($screensaverProcess -and -not $screensaverProcess.HasExited) {
            $timeSinceLastCheck = (Get-Date) - $script:lastWindowCheck
            if ($timeSinceLastCheck.TotalSeconds -ge 5) {
                Set-ScreensaverWindow -process $screensaverProcess
                $script:lastWindowCheck = Get-Date
            }
        }
    }
    catch {
        Write-Error "Error in main loop: $_"
        Write-Error $_.ScriptStackTrace
        Cleanup-ChromeProcesses
    }
    
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 100
}