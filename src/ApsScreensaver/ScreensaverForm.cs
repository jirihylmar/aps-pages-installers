using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using Microsoft.Web.WebView2.WinForms;
using Microsoft.Web.WebView2.Core;

namespace ApsScreensaver
{
    public class ScreensaverForm : Form
    {
        private WebView2 webView;
        private Point initialMouseLocation;
        private bool isInitializing = true;
        private Timer inputCheckTimer;
        private const int MOUSE_MOVE_THRESHOLD = 5; // pixels

        // For detecting global input
        [DllImport("user32.dll")]
        private static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);

        [StructLayout(LayoutKind.Sequential)]
        private struct LASTINPUTINFO
        {
            public uint cbSize;
            public uint dwTime;
        }

        private uint lastInputTime;

        public ScreensaverForm(Rectangle bounds)
        {
            InitializeComponent(bounds);
            SetupInputMonitoring();
        }

        private void InitializeComponent(Rectangle bounds)
        {
            // Form setup
            this.FormBorderStyle = FormBorderStyle.None;
            this.WindowState = FormWindowState.Normal;
            this.StartPosition = FormStartPosition.Manual;
            this.Bounds = bounds;
            this.TopMost = true;
            this.ShowInTaskbar = false;
            this.BackColor = Color.Black;

            // WebView2 setup
            webView = new WebView2
            {
                Dock = DockStyle.Fill,
                Visible = false // Hide until loaded
            };

            this.Controls.Add(webView);

            // Initialize WebView2
            InitializeWebView();
        }

        private void SetupInputMonitoring()
        {
            // Store initial mouse position
            initialMouseLocation = Cursor.Position;

            // Get initial input time
            LASTINPUTINFO lii = new LASTINPUTINFO();
            lii.cbSize = (uint)Marshal.SizeOf(typeof(LASTINPUTINFO));
            GetLastInputInfo(ref lii);
            lastInputTime = lii.dwTime;

            // Use a timer to check for any user input
            inputCheckTimer = new Timer();
            inputCheckTimer.Interval = 100; // Check every 100ms
            inputCheckTimer.Tick += InputCheckTimer_Tick;

            this.Load += (s, e) =>
            {
                this.TopMost = true;
                Cursor.Hide();

                // Start monitoring after a short delay to avoid initial input noise
                Timer startTimer = new Timer();
                startTimer.Interval = 1000; // 1 second delay
                startTimer.Tick += (ss, ee) =>
                {
                    startTimer.Stop();
                    startTimer.Dispose();
                    isInitializing = false;

                    // Reset initial values after initialization
                    initialMouseLocation = Cursor.Position;
                    LASTINPUTINFO lii2 = new LASTINPUTINFO();
                    lii2.cbSize = (uint)Marshal.SizeOf(typeof(LASTINPUTINFO));
                    GetLastInputInfo(ref lii2);
                    lastInputTime = lii2.dwTime;

                    inputCheckTimer.Start();
                };
                startTimer.Start();
            };
        }

        private void InputCheckTimer_Tick(object sender, EventArgs e)
        {
            if (isInitializing) return;

            // Check for any keyboard or mouse input using GetLastInputInfo
            LASTINPUTINFO lii = new LASTINPUTINFO();
            lii.cbSize = (uint)Marshal.SizeOf(typeof(LASTINPUTINFO));

            if (GetLastInputInfo(ref lii))
            {
                if (lii.dwTime != lastInputTime)
                {
                    // Input detected - but also check mouse movement threshold
                    Point currentMouse = Cursor.Position;
                    int deltaX = Math.Abs(currentMouse.X - initialMouseLocation.X);
                    int deltaY = Math.Abs(currentMouse.Y - initialMouseLocation.Y);

                    // Close if keyboard input OR significant mouse movement
                    if (deltaX > MOUSE_MOVE_THRESHOLD || deltaY > MOUSE_MOVE_THRESHOLD)
                    {
                        CloseScreensaver();
                    }
                    else
                    {
                        // Small mouse movement - update last input time but don't close
                        // This handles mouse jitter
                        // But if it's keyboard input, close immediately
                        uint timeDiff = lii.dwTime - lastInputTime;
                        if (timeDiff > 0)
                        {
                            // Check if mouse barely moved - if so, it's likely keyboard
                            if (deltaX <= 1 && deltaY <= 1)
                            {
                                CloseScreensaver();
                            }
                        }
                        lastInputTime = lii.dwTime;
                    }
                }
            }
        }

        private async void InitializeWebView()
        {
            try
            {
                // Create a unique temporary user data folder for WebView2
                string userDataFolder = System.IO.Path.Combine(
                    System.IO.Path.GetTempPath(),
                    "ApsScreensaver_WebView2_" + Guid.NewGuid().ToString("N").Substring(0, 8)
                );

                // Ensure the folder exists
                System.IO.Directory.CreateDirectory(userDataFolder);

                var environment = await CoreWebView2Environment.CreateAsync(
                    null,
                    userDataFolder,
                    new CoreWebView2EnvironmentOptions()
                );

                await webView.EnsureCoreWebView2Async(environment);

                // Configure WebView2 settings
                webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
                webView.CoreWebView2.Settings.AreDevToolsEnabled = false;
                webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
                webView.CoreWebView2.Settings.AreDefaultScriptDialogsEnabled = false;
                webView.CoreWebView2.Settings.IsZoomControlEnabled = false;

                // Load the URL from settings
                string url = ScreensaverSettings.GetUrl();
                webView.CoreWebView2.Navigate(url);

                // Show webview after navigation starts
                webView.Visible = true;
            }
            catch (Exception ex)
            {
                isInitializing = false;

                // Log detailed error information
                string errorLog = System.IO.Path.Combine(
                    System.IO.Path.GetTempPath(),
                    "ApsScreensaver_Error.log"
                );

                try
                {
                    System.IO.File.WriteAllText(errorLog,
                        $"Error Time: {DateTime.Now}\n" +
                        $"Exception Type: {ex.GetType().Name}\n" +
                        $"Message: {ex.Message}\n" +
                        $"Stack Trace:\n{ex.StackTrace}\n" +
                        $"HRESULT: {ex.HResult:X8}\n"
                    );
                }
                catch { }

                // If WebView2 fails, show error and close
                MessageBox.Show(
                    $"Failed to initialize screensaver:\n{ex.Message}\n\n" +
                    $"Error logged to:\n{errorLog}\n\n" +
                    "Please ensure Microsoft Edge WebView2 Runtime is installed.\n" +
                    "You can press ESC to close this dialog.",
                    "Screensaver Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
                this.Close();
                Application.Exit();
            }
        }

        private void CloseScreensaver()
        {
            inputCheckTimer?.Stop();
            inputCheckTimer?.Dispose();
            Cursor.Show();
            Application.Exit();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                inputCheckTimer?.Stop();
                inputCheckTimer?.Dispose();
                webView?.Dispose();
            }
            base.Dispose(disposing);
        }

        // Prevent form from being moved or resized
        protected override void WndProc(ref Message m)
        {
            const int WM_SYSCOMMAND = 0x0112;
            const int SC_MOVE = 0xF010;
            const int SC_MINIMIZE = 0xF020;
            const int SC_MAXIMIZE = 0xF030;

            if (m.Msg == WM_SYSCOMMAND)
            {
                int command = m.WParam.ToInt32() & 0xfff0;
                if (command == SC_MOVE || command == SC_MINIMIZE || command == SC_MAXIMIZE)
                {
                    return;
                }
            }

            base.WndProc(ref m);
        }
    }
}
