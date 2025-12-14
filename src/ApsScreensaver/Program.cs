using System;
using System.Drawing;
using System.Windows.Forms;

namespace ApsScreensaver
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            ApplicationConfiguration.Initialize();

            // Parse command line arguments
            // /s - Show screensaver
            // /p [preview_hwnd] - Preview mode
            // /c - Configure settings
            // No args - Default to show screensaver

            if (args.Length > 0)
            {
                string firstArg = args[0].ToLower().Trim();
                string arg = firstArg.Substring(0, 2);

                switch (arg)
                {
                    case "/s":
                        // Show screensaver
                        ShowScreensaver();
                        break;
                    case "/p":
                        // Preview mode
                        if (args.Length > 1)
                        {
                            ShowPreview(args[1]);
                        }
                        break;
                    case "/c":
                        // Configuration
                        ShowSettings();
                        break;
                    default:
                        // Default to screensaver
                        ShowScreensaver();
                        break;
                }
            }
            else
            {
                // No arguments - show screensaver
                ShowScreensaver();
            }
        }

        static void ShowScreensaver()
        {
            // Show screensaver on primary screen only (multi-monitor causes WebView2 conflicts)
            Screen primaryScreen = Screen.PrimaryScreen;

            // Create a single form that spans all screens
            Rectangle bounds = new Rectangle(
                SystemInformation.VirtualScreen.Left,
                SystemInformation.VirtualScreen.Top,
                SystemInformation.VirtualScreen.Width,
                SystemInformation.VirtualScreen.Height
            );

            ScreensaverForm screensaver = new ScreensaverForm(bounds);
            Application.Run(screensaver);
        }

        static void ShowPreview(string previewHandle)
        {
            // Preview mode (in display settings)
            // Show a simple message or blank form for preview
            try
            {
                // Create a small preview form
                Form previewForm = new Form
                {
                    FormBorderStyle = FormBorderStyle.None,
                    BackColor = System.Drawing.Color.Black,
                    Size = new System.Drawing.Size(200, 150)
                };

                Label label = new Label
                {
                    Text = "APS Screensaver\nPreview",
                    ForeColor = System.Drawing.Color.White,
                    TextAlign = System.Drawing.ContentAlignment.MiddleCenter,
                    Dock = DockStyle.Fill,
                    Font = new System.Drawing.Font("Segoe UI", 10)
                };

                previewForm.Controls.Add(label);
                Application.Run(previewForm);
            }
            catch
            {
                // If preview fails, just exit
                Application.Exit();
            }
        }

        static void ShowSettings()
        {
            // Show settings dialog
            Application.Run(new SettingsForm());
        }
    }
}
