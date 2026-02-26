#!/usr/bin/env python3
"""
WhatsApp Watcher - Silver Tier
Monitors WhatsApp Web for messages and creates action files
Uses Playwright for browser automation
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple

class WhatsAppWatcher:
    """Monitor WhatsApp Web for messages"""

    # Urgency keywords
    URGENT_KEYWORDS = ['urgent', 'asap', 'emergency', 'immediate', 'payment', 'confirm', 'approve']

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'

        # Setup logging
        self.logger = logging.getLogger('WhatsAppWatcher')
        handler = logging.FileHandler(self.logs / 'whatsapp_watcher.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Ensure directories exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        self.processed_messages = set()

    def detect_urgency(self, message_text: str) -> Tuple[str, bool]:
        """
        Detect urgency level from message

        Args:
            message_text: Message content

        Returns:
            Tuple of (urgency_level, requires_escalation)
        """
        text_lower = message_text.lower()

        # Check for urgent keywords
        if any(kw in text_lower for kw in ['payment', 'transfer', 'money', 'urgent']):
            return 'URGENT', True

        if any(kw in text_lower for kw in ['asap', 'immediate', 'emergency']):
            return 'HIGH', True

        if any(kw in text_lower for kw in ['confirm', 'approve', 'needed']):
            return 'MEDIUM', False

        return 'LOW', False

    def create_message_action(self, sender: str, message: str, urgency: str, escalate: bool) -> Path:
        """
        Create action file for WhatsApp message

        Args:
            sender: WhatsApp sender name
            message: Message content
            urgency: Urgency level
            escalate: Whether to escalate

        Returns:
            Path to created file
        """
        try:
            msg_id = hash(f"{sender}{message}{datetime.now().isoformat()}") % 10000
            filename = f"WA_{sender[:8]}_{msg_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.inbox / filename

            content = f"""---
type: whatsapp_message
sender: {sender}
urgency: {urgency}
requires_escalation: {escalate}
status: pending_review
created: {datetime.now().isoformat()}
---

# WhatsApp Message from {sender}

## Message
{message}

## Urgency Level
🔴 {urgency}

## Actions
- [ ] Read and acknowledge
- [ ] Respond with template
- [ ] Escalate if needed
- [ ] Archive

## Response Options
If urgent, consider:
1. Quick acknowledgment: "Got it, will handle soon"
2. Ask for clarification: "Can you provide more details?"
3. Escalate: "Forwarding to appropriate team"

---
*Monitored by WhatsApp Watcher*
*Agent: Fatima Zehra - Message Specialist*
"""

            filepath.write_text(content)
            self.logger.info(f'Created WhatsApp action file: {filename} (urgency: {urgency})')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create message action: {e}')
            return None

    def process_messages(self, messages: list) -> list:
        """
        Process list of WhatsApp messages

        Args:
            messages: List of message dicts with sender, text, timestamp

        Returns:
            List of created action files
        """
        created_files = []

        for msg in messages:
            msg_hash = hash(f"{msg['sender']}{msg['text']}")

            if msg_hash in self.processed_messages:
                continue

            self.processed_messages.add(msg_hash)

            sender = msg.get('sender', 'Unknown')
            text = msg.get('text', '')
            urgency, escalate = self.detect_urgency(text)

            filepath = self.create_message_action(sender, text, urgency, escalate)

            if filepath:
                created_files.append(filepath)

                # Escalate if needed
                if escalate:
                    self.logger.warning(f'ESCALATION: Urgent message from {sender}')
                    self._escalate_message(sender, text, urgency)

        return created_files

    def _escalate_message(self, sender: str, message: str, urgency: str):
        """Log escalation"""
        escalation_log = self.logs / 'whatsapp_escalations.log'

        with open(escalation_log, 'a') as f:
            f.write(f'[{datetime.now().isoformat()}] ESCALATION\n')
            f.write(f'From: {sender}\n')
            f.write(f'Urgency: {urgency}\n')
            f.write(f'Message: {message[:200]}...\n')
            f.write(f'Status: PENDING_HUMAN_REVIEW\n\n')

    def run(self, check_interval: int = 120):
        """
        Main watcher loop (runs every 2 minutes)

        Note: Requires Playwright browser-mcp integration
        """
        self.logger.info('WhatsApp Watcher started (requires browser-mcp)')
        print('👁️ WhatsApp Watcher running (requires Playwright integration)')
        print(f'Check interval: {check_interval}s')

        # Integration with Playwright browser-mcp would go here
        # For now, logging that service is ready

        self.logger.info('WhatsApp Watcher ready for integration with browser-mcp')

if __name__ == '__main__':
    watcher = WhatsAppWatcher()

    # Test message
    test_messages = [
        {
            'sender': 'Ali',
            'text': 'Hey bro, meeting at 5 PM?',
            'timestamp': datetime.now().isoformat()
        },
        {
            'sender': 'Finance',
            'text': 'URGENT: Payment of Rs. 50,000 needed today ASAP',
            'timestamp': datetime.now().isoformat()
        }
    ]

    print("✅ WhatsApp Watcher Test")
    files = watcher.process_messages(test_messages)
    print(f"Created {len(files)} action files")
    for f in files:
        print(f"  - {f.name}")
