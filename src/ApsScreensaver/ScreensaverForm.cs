using System;
using System.Drawing;
using System.Windows.Forms;
using Microsoft.Web.WebView2.WinForms;
using Microsoft.Web.WebView2.Core;

namespace ApsScreensaver
{
    public class ScreensaverForm : Form
    {
        private WebView2 webView;
        private Point mouseLocation;
        private bool isInitializing = true;
        private const int MOUSE_MOVE_THRESHOLD = 10; // pixels

        // Default URL - can be configured
        private const string SCREENSAVER_URL = "https://main.d14a7pjxtutfzh.amplifyapp.com/";

        public ScreensaverForm(Rectangle bounds)
        {
            InitializeComponent(bounds);
            SetupEventHandlers();
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
            this.Cursor = Cursors.Default;
            this.BackColor = Color.Black;
            this.KeyPreview = true; // Capture keyboard events before child controls

            // WebView2 setup
            webView = new WebView2
            {
                Dock = DockStyle.Fill,
                Visible = false // Hide until loaded
            };

            // Hook WebView2 keyboard events
            webView.KeyDown += (s, e) => { if (!isInitializing) CloseScreensaver(); };
            webView.PreviewKeyDown += (s, e) => { if (!isInitializing) CloseScreensaver(); };

            this.Controls.Add(webView);

            // Initialize WebView2
            InitializeWebView();
        }

        private async void InitializeWebView()
        {
            try
            {
                // Create a unique temporary user data folder for WebView2
                string userDataFolder = System.IO.Path.Combine(
                    System.IO.Path.GetTempPath(),
                    "ApsScreensaver_WebView2_" + System.Guid.NewGuid().ToString("N").Substring(0, 8)
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

                // Load the URL
                webView.CoreWebView2.Navigate(SCREENSAVER_URL);

                // Show webview after navigation starts
                webView.Visible = true;
                isInitializing = false;
            }
            catch (Exception ex)
            {
                // CRITICAL: Set isInitializing to false so keyboard events work
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

        private void SetupEventHandlers()
        {
            // Store initial mouse position
            mouseLocation = Control.MousePosition;

            // Keyboard events - don't close during initialization
            this.KeyPress += (s, e) => { if (!isInitializing) CloseScreensaver(); };
            this.KeyDown += (s, e) => { if (!isInitializing) CloseScreensaver(); };

            // Mouse events
            this.MouseMove += OnMouseMove;
            this.MouseDown += (s, e) => { if (!isInitializing) CloseScreensaver(); };
            this.MouseClick += (s, e) => { if (!isInitializing) CloseScreensaver(); };

            // Form events - don't close during initialization
            this.Deactivate += (s, e) => { if (!isInitializing) CloseScreensaver(); };
            this.Load += ScreensaverForm_Load;
        }

        private void ScreensaverForm_Load(object sender, EventArgs e)
        {
            // Make sure we're on top and cursor is hidden
            this.TopMost = true;
            Cursor.Hide();
        }

        private void OnMouseMove(object sender, MouseEventArgs e)
        {
            // Don't close during initialization
            if (isInitializing) return;

            // Only close if mouse moved significantly
            if (!mouseLocation.IsEmpty)
            {
                int deltaX = Math.Abs(e.X - mouseLocation.X);
                int deltaY = Math.Abs(e.Y - mouseLocation.Y);

                if (deltaX > MOUSE_MOVE_THRESHOLD || deltaY > MOUSE_MOVE_THRESHOLD)
                {
                    CloseScreensaver();
                }
            }

            mouseLocation = e.Location;
        }

        private void CloseScreensaver()
        {
            Cursor.Show();
            Application.Exit();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
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
