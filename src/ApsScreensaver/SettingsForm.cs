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
        private Label lblInfo;
        private Button btnOk;
        private Button btnCancel;

        public SettingsForm()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Text = "APS Screensaver Settings";
            this.Size = new Size(500, 300);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.MaximizeBox = false;
            this.MinimizeBox = false;

            // Title
            lblTitle = new Label
            {
                Text = "APS Pages Screensaver Configuration",
                Font = new Font("Segoe UI", 14, FontStyle.Bold),
                Location = new Point(20, 20),
                Size = new Size(450, 30),
                TextAlign = ContentAlignment.MiddleCenter
            };

            // URL Label
            lblUrl = new Label
            {
                Text = "Screensaver URL:",
                Location = new Point(20, 70),
                Size = new Size(120, 20)
            };

            // URL TextBox
            txtUrl = new TextBox
            {
                Text = "https://main.d14a7pjxtutfzh.amplifyapp.com/",
                Location = new Point(20, 95),
                Size = new Size(450, 25),
                ReadOnly = true
            };

            // Info Label
            lblInfo = new Label
            {
                Text = "This screensaver displays APS Pages content.\n\n" +
                       "To exit the screensaver, move your mouse or press any key.\n\n" +
                       "URL configuration coming in future version.",
                Location = new Point(20, 135),
                Size = new Size(450, 80),
                TextAlign = ContentAlignment.TopLeft
            };

            // OK Button
            btnOk = new Button
            {
                Text = "OK",
                Location = new Point(295, 225),
                Size = new Size(80, 30),
                DialogResult = DialogResult.OK
            };
            btnOk.Click += (s, e) => this.Close();

            // Cancel Button
            btnCancel = new Button
            {
                Text = "Cancel",
                Location = new Point(390, 225),
                Size = new Size(80, 30),
                DialogResult = DialogResult.Cancel
            };
            btnCancel.Click += (s, e) => this.Close();

            // Add controls
            this.Controls.Add(lblTitle);
            this.Controls.Add(lblUrl);
            this.Controls.Add(txtUrl);
            this.Controls.Add(lblInfo);
            this.Controls.Add(btnOk);
            this.Controls.Add(btnCancel);

            this.AcceptButton = btnOk;
            this.CancelButton = btnCancel;
        }
    }
}
