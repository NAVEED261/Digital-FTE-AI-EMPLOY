#!/usr/bin/env python3
"""
Gmail Watcher - Silver Tier
Monitors Gmail for important emails and creates action files
"""

import os
import sys
import json
import time
import pickle
import logging
from pathlib import Path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GmailWatcher:
    """Monitor Gmail and create action files for important emails"""

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'

        # Setup logging
        self.logger = logging.getLogger('GmailWatcher')
        handler = logging.FileHandler(self.logs / 'gmail_watcher.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self.gmail_service = None
        self.processed_emails = set()

    def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        try:
            # Try to use existing token
            token_path = Path.home() / '.gmail_token.pickle'

            if token_path.exists():
                with open(token_path, 'rb') as token_file:
                    creds = pickle.load(token_file)
                    if creds.expired and creds.refresh_token:
                        creds.refresh(Request())
            else:
                # Create new token
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

                # Save token for future use
                with open(token_path, 'wb') as token_file:
                    pickle.dump(creds, token_file)

            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail authentication successful')
            return True

        except FileNotFoundError:
            self.logger.error('credentials.json not found. Run: python setup_gmail_oauth.py')
            print('❌ Gmail OAuth setup required. Run: python setup_gmail_oauth.py')
            return False
        except Exception as e:
            self.logger.error(f'Authentication failed: {e}')
            return False

    def get_important_emails(self) -> list:
        """Fetch important/unread emails from Gmail"""
        try:
            query = 'is:unread is:important OR from:hnaveed264@gmail.com OR from:hafiznaveedchuhan@gmail.com'
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            return messages

        except Exception as e:
            self.logger.error(f'Failed to fetch emails: {e}')
            return []

    def get_email_content(self, message_id: str) -> dict:
        """Get full email content"""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            email_data = {
                'id': message_id,
                'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject'),
                'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
                'to': next((h['value'] for h in headers if h['name'] == 'To'), ''),
                'date': next((h['value'] for h in headers if h['name'] == 'Date'), ''),
                'snippet': message['snippet']
            }

            return email_data

        except Exception as e:
            self.logger.error(f'Failed to get email content: {e}')
            return {}

    def create_action_file(self, email_data: dict) -> Path:
        """Create action file in Needs_Action for unprocessed email"""
        try:
            email_id = email_data['id']

            # Skip if already processed
            if email_id in self.processed_emails:
                return None

            filename = f"EMAIL_{email_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.needs_action / filename

            # Determine priority based on keywords
            priority = 'high' if any(kw in email_data['subject'].lower() for kw in ['urgent', 'important', 'action', 'required']) else 'medium'

            content = f"""---
type: email_received
email_id: {email_id}
status: pending
priority: {priority}
action: process_email
created: {datetime.now().isoformat()}
---

# Email from: {email_data['from']}

## Subject
{email_data['subject']}

## Date
{email_data['date']}

## Preview
{email_data['snippet']}

## Suggested Actions
- [ ] Read full email
- [ ] Classify email type
- [ ] Draft response (if needed)
- [ ] Mark as processed
- [ ] Move to Archive

## System Integration
**MCP Server:** email-mcp (Silver Tier)
**Skills:** email-processor, email-classifier, email-responder
**HITL Status:** Pending human review for response

---
*This email will be automatically processed by Gmail FTE*
*Agent: Fatima Zehra - Email Specialist*
"""

            filepath.write_text(content)
            self.processed_emails.add(email_id)

            self.logger.info(f'Created action file: {filename}')
            print(f'📧 New email action: {filename}')

            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create action file: {e}')
            return None

    def run(self, check_interval: int = 300):
        """Main watcher loop (runs every 5 minutes by default)"""
        self.logger.info('Starting Gmail Watcher')
        print(f'👁️  Gmail Watcher started (checking every {check_interval}s)')

        if not self.authenticate():
            print('❌ Gmail authentication failed. Cannot start watcher.')
            return

        try:
            while True:
                emails = self.get_important_emails()

                for message in emails:
                    email_data = self.get_email_content(message['id'])
                    if email_data:
                        self.create_action_file(email_data)

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info('Gmail Watcher stopped')
            print('\n🛑 Gmail Watcher stopped')
        except Exception as e:
            self.logger.error(f'Watcher error: {e}')
            print(f'❌ Watcher error: {e}')

if __name__ == '__main__':
    vault_path = sys.argv[1] if len(sys.argv) > 1 else '/mnt/d/Hackaton-0/AI_Employee_Vault'
    watcher = GmailWatcher(vault_path)
    watcher.run()
