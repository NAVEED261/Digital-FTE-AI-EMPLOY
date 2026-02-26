#!/usr/bin/env python3
"""
Email Sender - Silver Tier
Sends emails via SMTP (Gmail)
Can use App Password for Gmail accounts
"""

import smtplib
import ssl
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

class EmailSender:
    """Send emails via SMTP"""

    def __init__(self, sender_email: str = None, app_password: str = None, vault_path: str = None):
        """
        Initialize email sender

        Args:
            sender_email: Gmail address to send from
            app_password: Gmail App Password (not regular password)
            vault_path: Path to vault for logging
        """
        self.sender_email = sender_email or os.getenv('SENDER_EMAIL')
        self.app_password = app_password or os.getenv('GMAIL_APP_PASSWORD')
        self.vault_path = Path(vault_path or os.getenv('VAULT_PATH', '/mnt/d/Hackaton-0/AI_Employee_Vault'))

        # Setup logging
        self.logger = logging.getLogger('EmailSender')
        log_file = self.vault_path / 'Logs' / 'email_sender.log'
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def validate_credentials(self) -> bool:
        """Validate that we have credentials"""
        if not self.sender_email or not self.app_password:
            self.logger.error('Missing email credentials')
            return False
        return True

    def send_email(self, recipient: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send email via SMTP

        Args:
            recipient: Email address to send to
            subject: Email subject
            body: Email body
            html: Whether body is HTML

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.validate_credentials():
                return False

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient

            # Add body
            if html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            # Connect to Gmail SMTP server
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, recipient, message.as_string())

            # Log successful send
            self.logger.info(f'Email sent to {recipient} with subject "{subject}"')
            print(f'✅ Email sent to {recipient}')

            # Create audit log entry
            self._log_email_action(recipient, subject, 'SENT')

            return True

        except smtplib.SMTPAuthenticationError:
            error_msg = 'SMTP Authentication failed. Check email and app password.'
            self.logger.error(error_msg)
            print(f'❌ {error_msg}')
            return False

        except Exception as e:
            error_msg = f'Failed to send email: {e}'
            self.logger.error(error_msg)
            print(f'❌ {error_msg}')
            return False

    def _log_email_action(self, recipient: str, subject: str, status: str):
        """Log email action to audit trail"""
        log_entry = f"""[{datetime.now().isoformat()}] EMAIL ACTION
To: {recipient}
Subject: {subject}
Status: {status}
From: {self.sender_email}
Component: Silver Tier Email Sender
"""
        log_file = self.vault_path / 'Logs' / 'email_actions.log'
        with open(log_file, 'a') as f:
            f.write(log_entry + '\n')

    def draft_email(self, recipient: str, subject: str, body: str) -> dict:
        """
        Draft an email without sending (for HITL approval)

        Returns:
            Dictionary with draft email content
        """
        draft = {
            'to': recipient,
            'subject': subject,
            'body': body,
            'from': self.sender_email,
            'timestamp': datetime.now().isoformat(),
            'status': 'draft'
        }

        self.logger.info(f'Email drafted for {recipient}')
        return draft

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python email_sender.py <recipient> <subject> [body]")
        sys.exit(1)

    recipient = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3] if len(sys.argv) > 3 else "This is a test email from Digital FTE"

    print("📧 Silver Tier Email Sender")
    print("=" * 50)
    print()
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print()

    # For testing, you would set these in .env
    # SENDER_EMAIL=your_email@gmail.com
    # GMAIL_APP_PASSWORD=your_app_password
    sender = EmailSender()

    if not sender.sender_email or not sender.app_password:
        print("❌ Credentials not configured!")
        print()
        print("To use this script:")
        print("1. Set SENDER_EMAIL and GMAIL_APP_PASSWORD in .env")
        print("2. For Gmail:")
        print("   - Enable 2-Factor Authentication")
        print("   - Create App Password: https://myaccount.google.com/apppasswords")
        print("   - Use App Password (not regular password)")
        print()
        sys.exit(1)

    if sender.send_email(recipient, subject, body):
        print()
        print("✅ Email sent successfully!")
    else:
        print()
        print("❌ Failed to send email")
