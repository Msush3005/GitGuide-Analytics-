"""
Email Report Delivery Subsystem
GitGuide Analytics

Delivers structured text and HTML reports via SMTP with credentials read
strictly from environment variables. Includes non-blocking error handling.
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_report_email(report_text, recipient):
    """
    Delivers structured report via SMTP using environment variable credentials.
    Non-blocking: logs errors on failure and returns False without crashing application.

    Args:
        report_text (str): Report body text
        recipient (str): Recipient email address

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    if not sender_email or not sender_password:
        print("[WARNING] Email credentials not configured in environment variables (SENDER_EMAIL, SENDER_PASSWORD). Skipping email send.")
        return False

    if not recipient or "@" not in recipient:
        print(f"[WARNING] Invalid recipient email address: '{recipient}'. Skipping email send.")
        return False

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = "Weekly Executive Analytics Report — GitGuide Intelligence"

    msg.attach(MIMEText(report_text, "plain", "utf-8"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"[OK] Email report successfully sent to: {recipient}")
        return True
    except Exception as e:
        print(f"[ERROR] Email send failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing email_sender.py with non-configured environment credentials...")
    success = send_report_email("TEST REPORT CONTENT", "test@example.com")
    print(f"Send result (expected False without env vars): {success}")
