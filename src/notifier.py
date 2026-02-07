import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import asyncio
from telegram import Bot

async def send_telegram_report(token, chat_id, html_file_path=None, message_text="Daily Macro Pulse Report"):
    """
    Sends the report to Telegram.
    Can send a message and/or a file (PDF/HTML).
    """
    if not token or not chat_id:
        print("Telegram token or chat_id missing. Skipping Telegram.")
        return

    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message_text)
        
        if html_file_path and os.path.exists(html_file_path):
            with open(html_file_path, 'rb') as f:
                # Send as document
                await bot.send_document(chat_id=chat_id, document=f, filename="macro_pulse_report.html")
                print("Telegram report sent.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def send_email_report(smtp_user, smtp_password, recipient_email, html_content):
    """
    Sends the report via Email.
    """
    if not smtp_user or not smtp_password or not recipient_email:
        print("SMTP credentials or recipient email missing. Skipping Email.")
        return

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Daily Macro Pulse Report"
        msg['From'] = smtp_user
        msg['To'] = recipient_email

        part1 = MIMEText(html_content, 'html')
        msg.attach(part1)

        # Standard Gmail SMTP port 587
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient_email, msg.as_string())
        server.quit()
        print("Email report sent.")
    except Exception as e:
        print(f"Failed to send Email: {e}")
