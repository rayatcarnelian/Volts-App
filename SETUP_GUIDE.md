# VOLTS Environment Setup Guide

To get the full results from VOLTS, you need to configure the following keys in your `.env` file.

## 1. Instagram Hunter (Required)
**Purpose:** Scrapes hashtags and users from Instagram.
- **INSTA_USER**: Your Instagram username.
- **INSTA_PASS**: Your Instagram password.
*Tip: Use a secondary/burner account to avoid risk to your main profile.*

## 2. Telegram Infiltrator (Required)
**Purpose:** Scrapes members from Telegram groups.
1. Go to [https://my.telegram.org/auth](https://my.telegram.org/auth).
2. Log in with your phone number.
3. Click "API development tools".
4. Create a new app (any name is fine).
5. Copy the **App api_id** and **App api_hash**.
- **TELEGRAM_API_ID**: Paste the ID here.
- **TELEGRAM_API_HASH**: Paste the Hash here.
- **TELEGRAM_PHONE**: Your phone number with country code (e.g., +60123456789).

## 3. Gemini AI (Required for Enrichment)
**Purpose:** AI Ghostwriter uses this to enrich leads and write emails.
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. Create a free API Key.
- **GEMINI_API_KEY**: Paste the key here.

## 4. Facebook Hunter (Optional)
**Purpose:** Scrapes Facebook Groups.
- **FB_EMAIL**: Your Facebook Login Email.
- **FB_PASS**: Your Facebook Password.
*(Note: The app will try to run silently. If it fails, it will ask you to log in manually via a browser window once.)*

## 5. Google Maps (No Key Required)
**Purpose:** Scrapes business leads from Maps.
- Does **NOT** require an API key. It uses browser automation.

## 6. Voice & Calls (Optional - Advanced)
Only needed if you use the Call Center or Voice Studio.
- **ELEVENLABS_API_KEY**: From [elevenlabs.io](https://elevenlabs.io) (Profile > API Key).
- **TWILIO_SID** & **TOKEN**: From [twilio.com](https://twilio.com) Console.
