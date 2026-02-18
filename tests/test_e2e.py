import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from data_fetcher import fetch_all_data
from report_generator import generate_html_report
from notifier import send_telegram_report


async def run_e2e_test():
    print("--- Starting E2E Test ---")

    # 1. Fetch Data
    print("1. Fetching Data...")
    data = fetch_all_data()
    if not data:
        print("[FAIL] No data fetched")
        return

    # 2. Generate Report
    print("2. Generating HTML Report...")
    try:
        html_content = generate_html_report(data)
        report_path = "test_report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[OK] Report generated at {report_path}")
    except Exception as e:
        print(f"[FAIL] Report generation failed: {e}")
        return

    # 3. Send Telegram
    print("3. Sending Telegram Message...")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[SKIP] Telegram credentials not found in .env")
    else:
        try:
            await send_telegram_report(
                token,
                chat_id,
                report_path,
                message_text="[E2E Test] Macro Pulse Report",
            )
            print("[OK] Telegram message sent (Check your app)")
        except Exception as e:
            print(f"[FAIL] Telegram send failed: {e}")

    print("--- E2E Test Completed ---")


if __name__ == "__main__":
    asyncio.run(run_e2e_test())
