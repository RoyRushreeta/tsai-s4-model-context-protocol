# Gmail SMTP Setup Guide

## Overview
The system has been updated to use Gmail's SMTP server instead of SendGrid. Gmail SMTP uses built-in Python libraries, so no additional packages are needed beyond what's in requirements.txt.

## Step 1: Enable 2-Factor Authentication on Your Gmail Account

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "How you sign in to Google", click on **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification (you'll need your phone)

## Step 2: Generate an App Password

**Important:** You must have 2-Factor Authentication enabled first!

1. Go to: https://myaccount.google.com/apppasswords
   - Or navigate: Google Account → Security → 2-Step Verification → App passwords
2. You may need to sign in again
3. In the "Select app" dropdown, choose **Mail**
4. In the "Select device" dropdown, choose **Windows Computer** (or Other)
5. Click **Generate**
6. Google will show you a 16-character password (e.g., `abcd efgh ijkl mnop`)
7. **Copy this password immediately** - you won't be able to see it again!

## Step 3: Update Your .env File

Update your `.env` file in the `Assignment4` folder with these variables:

```env
# Gmail Configuration (REQUIRED)
GMAIL_ADDRESS = "your-gmail-address@gmail.com"
GMAIL_APP_PASSWORD = "your-16-character-app-password"

# Gemini API Key (keep existing)
GEMINI_API_KEY = "your-existing-gemini-key"

# You can remove these (no longer needed):
# SENDGRID_API_KEY
# SENDGRID_FROM_EMAIL
# FROM_EMAIL
```

**Example:**
```env
GMAIL_ADDRESS = "rushreetar@gmail.com"
GMAIL_APP_PASSWORD = "abcd efgh ijkl mnop"
GEMINI_API_KEY = "AIzaSyD4pFm-COC3r5qAdPMo13CayWvO-Ale4yI"
```

**Note:** Remove the quotes if you want, the code now handles both formats.

## Step 4: Test the Setup

Run your orchestrator:
```powershell
python talk2mcp_gmail.py
```

You should see:
1. Prompt for recipient email (press Enter to use your Gmail address as default)
2. LLM processing iterations
3. "DEBUG send_email: from=your-gmail@gmail.com, to=recipient@email.com"
4. Success message: "Email sent to recipient@email.com from your-gmail@gmail.com"

## Troubleshooting

### Error: "Username and Password not accepted"
- **Cause:** Wrong app password or 2FA not enabled
- **Fix:** 
  1. Verify 2-Step Verification is ON in your Google Account
  2. Generate a new app password
  3. Copy it exactly (no spaces needed in .env, code strips them)

### Error: "GMAIL_ADDRESS not set in environment"
- **Cause:** .env file not loaded or variable name wrong
- **Fix:** 
  1. Make sure .env is in the same folder as talk2mcp_gmail.py
  2. Check variable names match exactly: `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`

### Error: "SMTPAuthenticationError: (535, '5.7.8 Username and Password not accepted'"
- **Cause:** App password expired or incorrect
- **Fix:** Delete old app password in Google Account and generate a new one

### Less Secure Apps
- **Gmail SMTP with App Passwords does NOT require "Less Secure Apps"**
- App Passwords are the modern, secure way to authenticate
- If you see any "Less secure app access" settings, ignore them (deprecated)

## How It Works

1. **SMTP Connection:** Uses `smtp.gmail.com:587` with TLS encryption
2. **Authentication:** Gmail address + app password (not your regular password!)
3. **Email Format:** Sends both plain text and HTML versions
4. **Built-in Libraries:** Uses Python's `smtplib` and `email.mime` (no external packages)

## Security Notes

- **Never commit your .env file to git** - it contains your app password
- App passwords bypass 2FA for specific apps - keep them secure
- You can revoke app passwords anytime in your Google Account settings
- Each app password is unique - generate separate ones for different projects

## Comparison: SendGrid vs Gmail SMTP

| Feature | SendGrid | Gmail SMTP |
|---------|----------|------------|
| Setup Complexity | Medium (API key, verify sender) | Easy (app password) |
| External Dependencies | `sendgrid` package | None (built-in) |
| Cost | Free tier: 100 emails/day | Free: 500 emails/day |
| Deliverability | High (dedicated service) | Good (personal use) |
| Rate Limits | Strict | Generous for personal |
| Best For | Production apps | Development, testing, personal projects |

## Next Steps

After confirming it works, you can optionally:
1. Clean up .env by removing old SendGrid variables
2. Update any documentation that references SendGrid
3. Consider keeping both implementations and switching via environment variable if needed
