#!/usr/bin/env python3
"""
Email Processor Skill - Silver Tier
Extracts and processes email content from Gmail
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class EmailProcessor:
    """Process and extract email metadata and content"""

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.logs = self.vault_path / 'Logs'

        # Setup logging
        self.logger = logging.getLogger('EmailProcessor')
        handler = logging.FileHandler(self.logs / 'email_processor.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def extract_email_metadata(self, email_data: Dict) -> Dict:
        """
        Extract metadata from email data

        Args:
            email_data: Raw email data from Gmail API

        Returns:
            Processed email metadata
        """
        try:
            from_addr = self._extract_header(email_data, 'From')
            subject = self._extract_header(email_data, 'Subject')
            to_addr = self._extract_header(email_data, 'To')
            date = self._extract_header(email_data, 'Date')
            body = email_data.get('snippet', '')

            # Extract sender name and email
            from_match = re.match(r'([^<]*)<([^>]*)>', from_addr) if from_addr else None
            sender_name = from_match.group(1).strip() if from_match else 'Unknown'
            sender_email = from_match.group(2) if from_match else from_addr

            metadata = {
                'email_id': email_data.get('id'),
                'from_email': sender_email,
                'from_name': sender_name,
                'to': to_addr,
                'subject': subject or '(No Subject)',
                'date': date,
                'body_preview': body[:200],
                'full_body': body,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'EmailProcessor'
            }

            self.logger.info(f'Processed email from {sender_email} with subject "{subject}"')
            return metadata

        except Exception as e:
            self.logger.error(f'Failed to extract metadata: {e}')
            return {}

    def create_action_file(self, email_metadata: Dict) -> Path:
        """
        Create action file in vault for processed email

        Args:
            email_metadata: Processed email metadata

        Returns:
            Path to created action file
        """
        try:
            inbox = self.vault_path / 'Inbox'
            filename = f"PROC_{email_metadata['email_id'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = inbox / filename

            # Create YAML frontmatter
            frontmatter = f"""---
type: email_processed
email_id: {email_metadata['email_id']}
from_email: {email_metadata['from_email']}
from_name: {email_metadata['from_name']}
subject: {email_metadata['subject']}
status: pending_classification
priority: medium
created: {email_metadata['timestamp']}
---

# Email from: {email_metadata['from_name']} ({email_metadata['from_email']})

## Subject
{email_metadata['subject']}

## Date
{email_metadata['date']}

## Preview
{email_metadata['body_preview']}

## Full Content
{email_metadata['full_body']}

## Processing Status
- [ ] Classified
- [ ] Priority determined
- [ ] Action recommended
- [ ] Approved for response
- [ ] Response sent
- [ ] Moved to Done

## Next Steps
Send to email_classifier.py for categorization

---
*Processed by Email Processor Skill*
*Agent: Fatima Zehra - Email Specialist*
"""

            filepath.write_text(frontmatter)
            self.logger.info(f'Created action file: {filename}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create action file: {e}')
            return None

    def _extract_header(self, email_data: Dict, header_name: str) -> str:
        """Extract header value from email"""
        headers = email_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'] == header_name:
                return header['value']
        return ''

    def batch_process_emails(self, emails: List[Dict]) -> List[Dict]:
        """
        Process multiple emails

        Args:
            emails: List of raw email data

        Returns:
            List of processed email metadata
        """
        processed = []
        for email in emails:
            metadata = self.extract_email_metadata(email)
            if metadata:
                processed.append(metadata)
                self.create_action_file(metadata)

        self.logger.info(f'Batch processed {len(processed)} emails')
        return processed

if __name__ == '__main__':
    import sys

    # Test mode
    processor = EmailProcessor()

    # Sample test
    test_email = {
        'id': 'test123',
        'snippet': 'This is a test email body',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'John Doe <john@example.com>'},
                {'name': 'To', 'value': 'hafiznaveedchuhan@gmail.com'},
                {'name': 'Subject', 'value': 'Test Email'},
                {'name': 'Date', 'value': 'Wed, 26 Feb 2026 23:00:00 +0000'}
            ]
        }
    }

    metadata = processor.extract_email_metadata(test_email)
    print("✅ Email Processor Test")
    print(json.dumps(metadata, indent=2))
