using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace ApsScreensaver
{
    static class Program
    {
        [DllImport("user32.dll")]
        private static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);

        [DllImport("user32.dll")]
        private static extern int SetWindowLong(IntPtr hWnd, int nIndex, IntPtr dwNewLong);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern int GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll")]
        private static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);

        [StructLayout(LayoutKind.Sequential)]
        private struct RECT
        {
            public int Left, Top, Right, Bottom;
        }

        private const int GWL_STYLE = -16;
        private const int WS_CHILD = 0x40000000;

        [STAThread]
        static void Main(string[] args)
        {
            ApplicationConfiguration.Initialize();

            // Parse command line arguments
            // /s - Show screensaver
            // /p [preview_hwnd] - Preview mode (embedded in Windows settings)
            // /c - Configure settings
            // No args - Default to show screensaver

            if (args.Length > 0)
            {
                string firstArg = args[0].ToLower().Trim();
                string arg = firstArg.Length >= 2 ? firstArg.Substring(0, 2) : firstArg;

                switch (arg)
                {
                    case "/s":
                        ShowScreensaver();
                        break;
                    case "/p":
                        // Preview mode - embed in the preview window
                        if (args.Length > 1)
                        {
                            ShowPreview(args[1]);
                        }
                        // If no handle provided, just exit silently
                        break;
                    case "/c":
                        ShowSettings();
                        break;
                    default:
                        ShowScreensaver();
                        break;
                }
            }
            else
            {
                ShowScreensaver();
            }
        }

        static void ShowScreensaver()
        {
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

        static void ShowPreview(string previewHandleStr)
        {
            // Preview mode - embed a simple preview in the Windows screensaver settings dialog
            try
            {
                IntPtr previewHandle = new IntPtr(long.Parse(previewHandleStr));

                // Get the size of the preview window
                RECT parentRect;
                GetClientRect(previewHandle, out parentRect);

                // Create preview form
                Form previewForm = new Form
                {
                    FormBorderStyle = FormBorderStyle.None,
                    BackColor = Color.Black,
                    Location = new Point(0, 0),
                    Size = new Size(parentRect.Right - parentRect.Left, parentRect.Bottom - parentRect.Top),
                    TopLevel = false
                };

                // Add preview label
                Label label = new Label
                {
                    Text = "APS\nScreensaver",
                    ForeColor = Color.White,
                    BackColor = Color.Black,
                    TextAlign = ContentAlignment.MiddleCenter,
                    Dock = DockStyle.Fill,
                    Font = new Font("Segoe UI", 8, FontStyle.Bold)
                };
                previewForm.Controls.Add(label);

                // Set as child of preview window
                SetParent(previewForm.Handle, previewHandle);
                SetWindowLong(previewForm.Handle, GWL_STYLE, new IntPtr(GetWindowLong(previewForm.Handle, GWL_STYLE) | WS_CHILD));

                previewForm.Show();
                Application.Run(previewForm);
            }
            catch
            {
                // Preview failed - just exit silently, don't show any floating windows
            }
        }

        static void ShowSettings()
        {
            // Show settings dialog as a modal dialog
            using (var settingsForm = new SettingsForm())
            {
                settingsForm.ShowDialog();
            }
        }
    }
}
