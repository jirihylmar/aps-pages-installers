using System;
using System.Drawing;
using System.Windows.Forms;

namespace ApsScreensaver
{
    public class SettingsForm : Form
    {
        private Label lblTitle;
        private Label lblUrl;
        private TextBox txtUrl;
        private Label lblValidation;
        private Label lblInternet;
        private Label lblInfo;
        private Button btnOk;
        private Button btnCancel;
        private Button btnReset;

        public SettingsForm()
        {
            InitializeComponent();
            LoadSettings();
        }

        private void InitializeComponent()
        {
            // Form settings - large size for good readability
            this.Text = "APS Screensaver Settings";
            this.ClientSize = new Size(800, 500);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.AutoScaleMode = AutoScaleMode.Dpi;
            this.Font = new Font("Segoe UI", 12F);
            this.Padding = new Padding(40);

            int margin = 40;
            int contentWidth = 720;
            int y = 30;

            // Title
            lblTitle = new Label
            {
                Text = "APS Pages Screensaver",
                Font = new Font("Segoe UI", 24, FontStyle.Bold),
                Location = new Point(margin, y),
                Size = new Size(contentWidth, 45),
                TextAlign = ContentAlignment.MiddleCenter
            };
            y += 70;

            // URL Label
            lblUrl = new Label
            {
                Text = "Web Page URL:",
                Font = new Font("Segoe UI", 14),
                Location = new Point(margin, y),
                AutoSize = true
            };
            y += 35;

            // URL TextBox
            txtUrl = new TextBox
            {
                Font = new Font("Segoe UI", 14),
                Location = new Point(margin, y),
                Size = new Size(contentWidth, 35),
                ReadOnly = false,
                TabIndex = 0
            };
            txtUrl.TextChanged += TxtUrl_TextChanged;
            y += 50;

            // Validation Label
            lblValidation = new Label
            {
                Text = "",
                Location = new Point(margin, y),
                Size = new Size(contentWidth, 30),
                Font = new Font("Segoe UI", 11)
            };
            y += 45;

            // Internet requirement notice
            lblInternet = new Label
            {
                Text = "Internet connection required",
                Font = new Font("Segoe UI", 13, FontStyle.Bold),
                ForeColor = Color.FromArgb(200, 100, 0),
                Location = new Point(margin, y),
                AutoSize = true
            };
            y += 40;

            // Info Label
            lblInfo = new Label
            {
                Text = "This screensaver displays content from the web URL above.\n\n" +
                       "The content is loaded from the internet each time the screensaver\n" +
                       "starts. Without an internet connection, the screensaver will show\n" +
                       "an error.\n\n" +
                       "To exit the screensaver: Move your mouse, press any key, or click.",
                Font = new Font("Segoe UI", 11),
                Location = new Point(margin, y),
                Size = new Size(contentWidth, 140),
                ForeColor = Color.FromArgb(80, 80, 80)
            };

            // Buttons row - at bottom
            int buttonY = 430;
            int buttonHeight = 45;

            // Reset Button
            btnReset = new Button
            {
                Text = "Reset to Default",
                Font = new Font("Segoe UI", 12),
                Location = new Point(margin, buttonY),
                Size = new Size(180, buttonHeight),
                TabIndex = 3
            };
            btnReset.Click += BtnReset_Click;

            // Cancel Button
            btnCancel = new Button
            {
                Text = "Cancel",
                Font = new Font("Segoe UI", 12),
                Location = new Point(520, buttonY),
                Size = new Size(120, buttonHeight),
                DialogResult = DialogResult.Cancel,
                TabIndex = 2
            };
            btnCancel.Click += (s, e) => this.Close();

            // OK Button
            btnOk = new Button
            {
                Text = "OK",
                Font = new Font("Segoe UI", 12),
                Location = new Point(650, buttonY),
                Size = new Size(110, buttonHeight),
                DialogResult = DialogResult.OK,
                TabIndex = 1
            };
            btnOk.Click += BtnOk_Click;

            // Add controls
            this.Controls.Add(lblTitle);
            this.Controls.Add(lblUrl);
            this.Controls.Add(txtUrl);
            this.Controls.Add(lblValidation);
            this.Controls.Add(lblInternet);
            this.Controls.Add(lblInfo);
            this.Controls.Add(btnReset);
            this.Controls.Add(btnOk);
            this.Controls.Add(btnCancel);

            this.AcceptButton = btnOk;
            this.CancelButton = btnCancel;

            // Focus the URL textbox when form loads
            this.Load += (s, e) => txtUrl.Focus();
        }

        private void LoadSettings()
        {
            txtUrl.Text = ScreensaverSettings.GetUrl();
            ValidateUrl();
        }

        private void TxtUrl_TextChanged(object sender, EventArgs e)
        {
            ValidateUrl();
        }

        private void ValidateUrl()
        {
            if (string.IsNullOrWhiteSpace(txtUrl.Text))
            {
                lblValidation.Text = "URL cannot be empty";
                lblValidation.ForeColor = Color.Red;
                btnOk.Enabled = false;
            }
            else if (!ScreensaverSettings.IsValidUrl(txtUrl.Text))
            {
                lblValidation.Text = "Please enter a valid URL (starting with http:// or https://)";
                lblValidation.ForeColor = Color.Red;
                btnOk.Enabled = false;
            }
            else
            {
                lblValidation.Text = "Valid URL";
                lblValidation.ForeColor = Color.FromArgb(0, 150, 0);
                btnOk.Enabled = true;
            }
        }

        private void BtnOk_Click(object sender, EventArgs e)
        {
            if (ScreensaverSettings.IsValidUrl(txtUrl.Text))
            {
                if (ScreensaverSettings.SetUrl(txtUrl.Text.Trim()))
                {
                    this.Close();
                }
                else
                {
                    MessageBox.Show(
                        "Failed to save settings. Please try again.",
                        "Error",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error
                    );
                }
            }
        }

        private void BtnReset_Click(object sender, EventArgs e)
        {
            txtUrl.Text = ScreensaverSettings.DefaultUrl;
        }
    }
}
