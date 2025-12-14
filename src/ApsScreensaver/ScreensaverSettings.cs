using System;
using Microsoft.Win32;

namespace ApsScreensaver
{
    /// <summary>
    /// Manages screensaver settings persistence using the Windows Registry.
    /// Settings are stored in HKEY_CURRENT_USER\Software\APS\Screensaver
    /// </summary>
    public static class ScreensaverSettings
    {
        private const string RegistryPath = @"Software\APS\Screensaver";
        private const string UrlValueName = "Url";

        // Default URL if none is configured
        public const string DefaultUrl = "https://main.d14a7pjxtutfzh.amplifyapp.com/";

        /// <summary>
        /// Gets the configured screensaver URL from the registry.
        /// Returns the default URL if not configured.
        /// </summary>
        public static string GetUrl()
        {
            try
            {
                using (var key = Registry.CurrentUser.OpenSubKey(RegistryPath))
                {
                    if (key != null)
                    {
                        var value = key.GetValue(UrlValueName) as string;
                        if (!string.IsNullOrWhiteSpace(value))
                        {
                            return value;
                        }
                    }
                }
            }
            catch
            {
                // If registry access fails, return default
            }

            return DefaultUrl;
        }

        /// <summary>
        /// Saves the screensaver URL to the registry.
        /// </summary>
        /// <param name="url">The URL to save</param>
        /// <returns>True if successful, false otherwise</returns>
        public static bool SetUrl(string url)
        {
            try
            {
                using (var key = Registry.CurrentUser.CreateSubKey(RegistryPath))
                {
                    if (key != null)
                    {
                        key.SetValue(UrlValueName, url ?? DefaultUrl, RegistryValueKind.String);
                        return true;
                    }
                }
            }
            catch
            {
                // Registry write failed
            }

            return false;
        }

        /// <summary>
        /// Validates that a string is a valid HTTP/HTTPS URL.
        /// </summary>
        /// <param name="url">The URL to validate</param>
        /// <returns>True if valid, false otherwise</returns>
        public static bool IsValidUrl(string url)
        {
            if (string.IsNullOrWhiteSpace(url))
                return false;

            return Uri.TryCreate(url, UriKind.Absolute, out Uri result) &&
                   (result.Scheme == Uri.UriSchemeHttp || result.Scheme == Uri.UriSchemeHttps);
        }
    }
}
