import os
import argparse
import asyncio
from data_fetcher import fetch_all_data
from report_generator import generate_html_report
from notifier import send_telegram_report, send_email_report
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

async def main():
    parser = argparse.ArgumentParser(description="Macro Pulse Bot")
    parser.add_argument('--dry-run', action='store_true', help="Generate report but do not send")
    parser.add_argument('--market', type=str, default='Global', help="Market context (US/KR)")
    args = parser.parse_args()

    print(f"Starting Macro Pulse Bot ({args.market})...")

    # 1. Fetch Data
    print("Fetching data...")
    data = fetch_all_data()

    # 2. Generate Report
    print("Generating report...")
    html_report = generate_html_report(data)
    
    # Save locally
    output_path = "macro_pulse_report.html"
    with open(output_path, "w") as f:
        f.write(html_report)
    print(f"Report saved to {output_path}")

    if args.dry_run:
        print("Dry run complete. No notifications sent.")
        return

    # 3. Notify
    # Load secrets from env
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient_email = os.environ.get("RECIPIENT_EMAIL") # User can set this or use SMTP_USERNAME

    # Telegram
    if telegram_token and telegram_chat_id:
        summary = f"Macro Pulse Report ({args.market})\n"
        # Add quick summary metrics if needed
        await send_telegram_report(telegram_token, telegram_chat_id, output_path, summary)

    # Email
    if smtp_user and smtp_password:
        target_email = recipient_email if recipient_email else smtp_user
        send_email_report(smtp_user, smtp_password, target_email, html_report)

if __name__ == "__main__":
    asyncio.run(main())
