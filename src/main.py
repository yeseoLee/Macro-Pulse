import os
import argparse
import asyncio
from data_fetcher import fetch_all_data
from report_generator import generate_html_report, generate_telegram_summary
from notifier import send_telegram_report, send_email_report
from screenshot_utils import take_finviz_screenshot
import warnings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore")

from datetime import datetime, timezone


async def main():
    parser = argparse.ArgumentParser(description="Macro Pulse Bot")
    parser.add_argument(
        "--dry-run", action="store_true", help="Generate report but do not send"
    )
    parser.add_argument(
        "--market", type=str, default="Global", help="Market context (US/KR)"
    )
    args = parser.parse_args()

    # Determine mode based on Time (if no explicit arg provided or just default)
    # KR Close (17:00 KST) = 08:00 UTC
    # US Close (06:00 KST) = 21:00 UTC
    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour

    if 7 <= hour < 20:
        mode = "KR"
    else:
        mode = "US"

    print(f"Starting Macro Pulse Bot (Mode: {mode})...")

    # 1. Fetch Data
    print("Fetching data...")
    data = fetch_all_data()

    # 2. Generate Report
    print("Generating report...")
    html_report = generate_html_report(data)

    # Generate Telegram Summary text
    telegram_summary = generate_telegram_summary(data, mode)
    print(f"Telegram Summary ({mode}):\n{telegram_summary}\n")

    # Save locally
    output_path = "macro_pulse_report.html"
    with open(output_path, "w") as f:
        f.write(html_report)
    print(f"Report saved to {output_path}")

    if args.dry_run:
        print("Dry run complete. No notifications sent.")
        return

    # 3. Take Screenshot (Only for US Close / 06:30 KST)
    screenshot_path = None
    if mode == "US":
        print("Taking Finviz screenshot...")
        screenshot_path = take_finviz_screenshot()

    # 4. Notify
    # Load secrets from env
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient_email = os.environ.get(
        "RECIPIENT_EMAIL"
    )  # User can set this or use SMTP_USERNAME

    # Telegram
    if telegram_token and telegram_chat_id:
        await send_telegram_report(
            telegram_token,
            telegram_chat_id,
            output_path,
            telegram_summary,
            image_path=screenshot_path,
        )

    # Email
    if smtp_user and smtp_password:
        target_email = recipient_email if recipient_email else smtp_user
        send_email_report(smtp_user, smtp_password, target_email, html_report)


if __name__ == "__main__":
    asyncio.run(main())
