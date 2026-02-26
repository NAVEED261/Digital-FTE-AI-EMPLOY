#!/usr/bin/env python3
"""
WhatsApp Processor Skill - Silver Tier
Processes WhatsApp messages and generates responses
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

class WhatsAppProcessor:
    """Process WhatsApp messages and draft responses"""

    # Response templates
    TEMPLATES = {
        'ACKNOWLEDGE': 'Got it, thanks for the message!',
        'CONFIRM': 'Yes, confirmed. Will do.',
        'CLARIFY': 'Can you provide more details? Will respond shortly.',
        'ESCALATE': 'This is urgent and being escalated to the right team.',
        'PAYMENT': 'Payment details received. Will process shortly.',
        'MEETING': 'Got the meeting request. Checking calendar and will confirm.'
    }

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.logs = self.vault_path / 'Logs'

        # Setup logging
        self.logger = logging.getLogger('WhatsAppProcessor')
        handler = logging.FileHandler(self.logs / 'whatsapp_processor.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def process_message(self, sender: str, message: str, urgency: str) -> Dict:
        """
        Process WhatsApp message and determine response

        Args:
            sender: Message sender name
            message: Message text
            urgency: Urgency level (LOW, MEDIUM, HIGH, URGENT)

        Returns:
            Processing result with recommended response
        """
        msg_lower = message.lower()

        # Detect message type
        msg_type = self._detect_message_type(msg_lower)
        response_type = self._get_response_type(msg_type, urgency)
        response = self.TEMPLATES.get(response_type, self.TEMPLATES['ACKNOWLEDGE'])

        # Determine if needs HITL
        requires_hitl = urgency in ['HIGH', 'URGENT']

        result = {
            'sender': sender,
            'original_message': message,
            'message_type': msg_type,
            'urgency': urgency,
            'response_type': response_type,
            'response_text': response,
            'requires_hitl': requires_hitl,
            'processed_at': datetime.now().isoformat()
        }

        self.logger.info(f'Processed message from {sender}: {msg_type}, response: {response_type}')
        return result

    def _detect_message_type(self, text_lower: str) -> str:
        """Detect type of message"""
        if any(kw in text_lower for kw in ['meeting', 'call', 'zoom', 'teams', 'time']):
            return 'MEETING'
        elif any(kw in text_lower for kw in ['confirm', 'approve', 'yes', 'no', 'ok']):
            return 'CONFIRMATION'
        elif any(kw in text_lower for kw in ['payment', 'transfer', 'money', 'bill', 'cost']):
            return 'PAYMENT'
        elif any(kw in text_lower for kw in ['question', '?', 'help', 'info']):
            return 'QUESTION'
        else:
            return 'GENERAL'

    def _get_response_type(self, msg_type: str, urgency: str) -> str:
        """Get appropriate response type"""
        if urgency == 'URGENT':
            return 'ESCALATE'
        elif msg_type == 'PAYMENT':
            return 'PAYMENT'
        elif msg_type == 'MEETING':
            return 'MEETING'
        elif msg_type == 'CONFIRMATION':
            return 'CONFIRM'
        elif msg_type == 'QUESTION':
            return 'CLARIFY'
        else:
            return 'ACKNOWLEDGE'

    def create_response_file(self, processed: Dict) -> Path:
        """
        Create WhatsApp response file

        Args:
            processed: Processed message result

        Returns:
            Path to response file
        """
        try:
            pending = self.vault_path / 'Pending_Approval'
            filename = f"WA_RESP_{processed['sender'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = pending / filename

            content = f"""---
type: whatsapp_response
sender: {processed['sender']}
message_type: {processed['message_type']}
urgency: {processed['urgency']}
status: pending_approval
requires_approval: {processed['requires_hitl']}
created: {processed['processed_at']}
---

# WhatsApp Response Draft

## From
{processed['sender']}

## Original Message
{processed['original_message']}

## Drafted Response
```
{processed['response_text']}
```

## Message Type
{processed['message_type']}

## Urgency
{processed['urgency']}

## Actions
- [ ] APPROVED - Send this response
- [ ] EDIT - Modify and send
- [ ] REJECT - Don't respond
- [ ] CUSTOM - Write custom response

## Next Steps
1. Review the drafted response
2. Select action above
3. Save file
4. Auto-responder will process within 1 minute

---
*Processed by WhatsApp Processor Skill*
*Agent: Fatima Zehra - Message Specialist*
"""

            filepath.write_text(content)
            self.logger.info(f'Created response file: {filename}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create response file: {e}')
            return None

if __name__ == '__main__':
    processor = WhatsAppProcessor()

    # Test message
    test_msg = {
        'sender': 'Ahmed',
        'message': 'Can we meet tomorrow at 3 PM?',
        'urgency': 'MEDIUM'
    }

    result = processor.process_message(test_msg['sender'], test_msg['message'], test_msg['urgency'])
    print("✅ WhatsApp Processor Test")
    print(json.dumps(result, indent=2))
