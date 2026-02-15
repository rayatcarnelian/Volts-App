# 📘 VOLTS Command Center - User Guide

Welcome to **VOLTS**, your automated acquisition system. This guide will help you install, configure, and operate the platform.

---

## 📦 Installation (First Time Only)
1.  **Extract the Zip Folder**: Unzip the `Leads app` folder to your Desktop or Documents.
2.  **Double-click `INSTALL_VOLTS.bat`**:
    *   This script will check for Python, install all necessary libraries, and set up the secure environment.
    *   Wait for it to say **"✅ INSTALLATION COMPLETE!"**.
    *   *Note: If Windows Defender pops up, click "More Info" > "Run Anyway". It allows the script to install libraries.*

## 🚀 How to Launch
*   **Double-click `LAUNCH_VOLTS.bat`**: This will open the Command Center in your default browser (usually `http://localhost:8501`).

---

## ⚙️ Configuration & API Keys
To activate the AI and Scrapers, you need to input your keys.

1.  Open the App (`LAUNCH_VOLTS.bat`).
2.  In the left sidebar, click **7. SETTINGS**.
3.  Enter your keys (see below on how to get them) and click **Save**.
4.  Restart the app to apply changes.

---


## 🔑 Getting Your API Keys

### 1. 🧠 AI & Intelligence (Mandatory)
These keys power the "Brain" of the system (Email writing, Lead scoring, Vision).

*   **Google Gemini API Key** (For Text/Logic)
    *   Go to: [aistudio.google.com](https://aistudio.google.com/app/apikey)
    *   Click "Create API Key".
    *   Copy the key (starts with `AIza...`).
    *   Paste into **Settings > AI Engines > Gemini API Key**.

*   **Replicate API Token** (For Vision/Image Analysis)
    *   Go to: [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)
    *   Sign in with GitHub.
    *   Create a token named "Volts".
    *   Paste into **Settings > AI Engines > Replicate API Token**.

### 2. 📞 Call Center (Vapi.ai)
Required if you want to use the AI Voice Caller.

*   **Vapi API Key (Private)**
    *   Go to: [dashboard.vapi.ai/org](https://dashboard.vapi.ai/org) -> Click **API Keys**.
    *   Create a **Private Key**. Copy it.
*   **Vapi Phone ID**
    *   Go to **Phone Numbers** in Vapi Dashboard.
    *   Buy/Import a number.
    *   Click the ID (clipboard icon) next to the number.
    *   Paste into **Settings > Voice > Vapi Phone ID**.

### 3. 📱 Social Media Scrapers
**WARNING:** Use burner/secondary accounts for scraping to protect your personal profiles.

*   **Instagram / Facebook / X (Twitter)**
    *   Simply enter the **Username/Email** and **Password** of the account you want the bot to use.
    *   **Tip:** Log in to these accounts manually on Chrome once to handle any "New Device" verifications before running the bot.

### 4. 📧 Email Outreach (Gmail)
**Do NOT use your login password.** You must generate an App Password.

*   **Gmail App Password**
    1.  Go to [myaccount.google.com/security](https://myaccount.google.com/security).
    2.  Enable **2-Step Verification**.
    3.  Search for "App Passwords".
    4.  Create one named "Volts App".
    5.  Copy the 16-character code (e.g., `abcd efgh ijkl mnop`).
    6.  Paste into **Settings > System > Gmail App Password**.

---

## 🚀 Troubleshooting
- **"Driver Crash" / "Browser Closed":** Ensure you have Google Chrome installed.
- **"Authentication Failed":** Check your passwords in Settings. Try logging in manually to clear security checks.
- **"API Error 401/403":** Your API Key is likely invalid or has expired. Generate a new one.

**Enjoy using VOLTS!**
