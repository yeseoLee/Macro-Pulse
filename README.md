# Macro Pulse Bot

A Telegram/Email bot that sends daily financial macro reports (Exchange rates, Indices, Commodities, Crypto).

## Features
- **Data Collection**: Fetches latest data from Yahoo Finance.
- **Reporting**: Generates an HTML report with sparkline graphs and daily changes.
- **Notification**: Sends the report via Telegram (message + HTML file) and Email.
- **Automation**: Runs automatically via GitHub Actions (Morning and Evening KST).

## Setup

### 1. Prerequisites
- Python 3.11+
- GitHub Account (for automation)
- Telegram Bot Token & Chat ID (optional but recommended)
- Gmail Account (for SMTP, optional)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Running Locally
```bash
# Dry run (generate report only, no sending)
python src/main.py --dry-run

# Run and send (requires env vars)
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python src/main.py
```

### 4. GitHub Actions Setup
To enable automatic daily reports, you must configure the following **Secrets** in your GitHub repository settings (`Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`):

| Secret Name | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | (Optional) Your Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | (Optional) Your Telegram Chat ID |
| `SMTP_USERNAME` | (Optional) Your Gmail address (e.g., user@gmail.com) |
| `SMTP_PASSWORD` | (Optional) Your Gmail App Password (not your login password) |
| `RECIPIENT_EMAIL` | (Optional) Email address to receive the report |
| `RAPIDAPI_CNBC_KEY` | (Required for complete data) RapidAPI Key for CNBC API |

## Schedule
The bot runs automatically at:
- **6:30 AM KST** (21:30 UTC): Covers US market close.
- **4:30 PM KST** (07:30 UTC): Covers Asian market close.
