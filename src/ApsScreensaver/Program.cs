using System;
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
            // Show screensaver on all screens
            foreach (Screen screen in Screen.AllScreens)
            {
                ScreensaverForm screensaver = new ScreensaverForm(screen.Bounds);
                screensaver.Show();
            }
            Application.Run();
        }

        static void ShowPreview(string previewHandle)
        {
            // Preview mode (in display settings)
            // For simplicity, we'll skip preview implementation
            // Most modern screensavers don't implement preview
            Application.Exit();
        }

        static void ShowSettings()
        {
            // Show settings dialog
            Application.Run(new SettingsForm());
        }
    }
}
