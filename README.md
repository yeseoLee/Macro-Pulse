# Macro Pulse Bot

Bot for daily financial macro data monitoring. It fetches Exchange Rates, Indices, Commodities, Crypto, and Volatility data, generates a clean HTML report with sparkline trends, and sends it via Telegram and Email. It also deploys the latest report to GitHub Pages.

## Features

- **Multi-Source Data Fetching**:
  - **Yahoo Finance**: Indices, Crypto, Commodities, and FX History.
  - **CNBC API**: Real-time Exchange Rates and Bond Yields (Japan 10Y, Korea 10Y, VKOSPI).
  - **Hybrid Logic**: Uses CNBC for real-time FX prices and Yahoo Finance for 7-day trend analysis.
- **Reporting**:
  - Generates a responsive HTML report (`macro_pulse_report.html`).
  - Includes daily change % and 7-day sparkline trends.
  - Handles missing data gracefully (blank cells vs broken charts).
- **Notifications**:
  - **Telegram**: Sends the report file + summary message.
  - **Email**: Sends the report via SMTP (optional).
- **Automation**:
  - **GitHub Actions**: Runs automatically twice daily (06:00 KST for US Close, 17:00 KST for KR Close).
  - **GitHub Pages**: Deploys the latest report to a web URL.

## Setup

### 1. Prerequisites
- Python 3.12+
- GitHub Account (for automation)
- Telegram Bot Token & Chat ID
- RapidAPI Key (CNBC)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Running Locally
Create a `.env` file in the root directory (see `.env-sample`):
```ini
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id
RAPIDAPI_CNBC_KEY=your_key
# Email optional
```

Run the bot:
```bash
# Dry run (generate report only)
python src/main.py --dry-run

# Run and send
python src/main.py
```

### 4. GitHub Actions & Pages
The workflow runs automatically on schedule. You need to configure **Secrets** and **Pages**.

#### Required Secrets
Go to `Settings` -> `Secrets and variables` -> `Actions` and add:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `RAPIDAPI_CNBC_KEY`
- (Optional) `SMTP_USERNAME`, `SMTP_PASSWORD`, `RECIPIENT_EMAIL`

#### GitHub Pages Deployment
To view the report online:
1.  Go to `Settings` -> `Pages`.
2.  Set **Source** to `Deploy from a branch`.
3.  Set **Branch** to `gh-pages` and folder to `/ (root)`.
4.  Your report will be live at `https://<your-username>.github.io/Macro-Pulse/`.

## Troubleshooting
- **GitHub Pages shows README**: Ensure you switched the branch to `gh-pages` in Settings. Try a hard refresh (Cmd+Shift+R) to clear browser cache.
- **Missing Data**: Check API keys and `requirements.txt` dependencies.
- **CI Errors**: Check the Actions tab logs. Common issues are Python version mismatch (requires 3.12+) or missing pip packages.

## Project Structure
- `src/`: Source code (`data_fetcher.py`, `report_generator.py`, `cnbc_fetcher.py`, `main.py`).
- `tests/`: End-to-End tests (`test_e2e.py`) and ticker verification (`test_tickers.py`).
- `.github/workflows/`: Automation configuration.
- `public/`: Output folder for GitHub Pages (created during runtime).
