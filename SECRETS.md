# Required GitHub Secrets for Deployment

To ensure the Macro-Pulse Bot works correctly via GitHub Actions, please add the following secrets in your repository settings (**Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**).

## 1. Telegram Notifications (Required)
These are essential for receiving the daily reports.
- **`TELEGRAM_BOT_TOKEN`**: The token you received from BotFather when creating your bot.
- **`TELEGRAM_CHAT_ID`**: The unique identifier for the chat/channel where reports will be sent.

## 2. CNBC Data Integration (Required for full data)
This is needed to fetch real-time bond yields and exchange rates.
- **`RAPIDAPI_CNBC_KEY`**: Your API key from RapidAPI (CNBC API).

## 3. Email Notifications (Optional)
Only required if you want to receive reports via email (in addition to or instead of Telegram).
- **`SMTP_USERNAME`**: Your email address (e.g., `yourname@gmail.com`).
- **`SMTP_PASSWORD`**: Your email app password (not your login password).
- **`RECIPIENT_EMAIL`**: The email address where the report should be sent.

---
**Note:** The GitHub Action workflow is configured to use these exact names. Please ensure the spelling matches exactly.
