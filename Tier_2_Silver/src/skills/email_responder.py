#!/usr/bin/env python3
"""
Email Responder Skill - Silver Tier
Auto-drafts responses to classified emails
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

class EmailResponder:
    """Draft automatic responses to emails"""

    # Response templates
    TEMPLATES = {
        'AUTO_ACKNOWLEDGE': {
            'subject': 'Re: {original_subject}',
            'body': '''Dear {sender_name},

Thank you for your email. We have received your message and will respond shortly.

Best regards,
{signature}'''
        },
        'REVIEW_PAYMENT': {
            'subject': 'Re: {original_subject}',
            'body': '''Dear {sender_name},

Thank you for sending the invoice. We have received it and will process the payment shortly.

Invoice Details:
{preview}

Best regards,
{signature}'''
        },
        'SCHEDULE_CALENDAR': {
            'subject': 'Re: {original_subject}',
            'body': '''Dear {sender_name},

Thank you for the meeting request. We will check our calendar and confirm availability shortly.

Meeting Details:
{preview}

Best regards,
{signature}'''
        },
        'DRAFT_RESPONSE': {
            'subject': 'Re: {original_subject}',
            'body': '''Dear {sender_name},

Thank you for your message. Here is our response:

[WAITING FOR HITL INPUT - Please draft response]

{preview}

Best regards,
{signature}'''
        },
        'ESCALATE_IMMEDIATELY': {
            'subject': 'Re: {original_subject}',
            'body': '''Dear {sender_name},

Your email has been marked as URGENT and requires immediate attention.

This message will be escalated to the appropriate team member.

Email Content:
{preview}

Best regards,
{signature}'''
        }
    }

    def __init__(self, vault_path: str = None, signature: str = 'Fatima Zehra\nDigital Employee'):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.logs = self.vault_path / 'Logs'
        self.signature = signature

        # Setup logging
        self.logger = logging.getLogger('EmailResponder')
        handler = logging.FileHandler(self.logs / 'email_responder.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def draft_response(self, email_metadata: Dict, classification: Dict) -> Dict:
        """
        Draft response to email

        Args:
            email_metadata: Email metadata
            classification: Classification result

        Returns:
            Draft response with subject and body
        """
        try:
            action = classification['recommended_action']
            template = self.TEMPLATES.get(action, self.TEMPLATES['AUTO_ACKNOWLEDGE'])

            # Prepare template variables
            variables = {
                'original_subject': email_metadata.get('subject', 'Your Email'),
                'sender_name': email_metadata.get('from_name', 'User'),
                'preview': email_metadata.get('body_preview', ''),
                'signature': self.signature
            }

            # Format template
            draft_subject = template['subject'].format(**variables)
            draft_body = template['body'].format(**variables)

            draft = {
                'email_id': email_metadata.get('email_id'),
                'to': email_metadata.get('from_email'),
                'subject': draft_subject,
                'body': draft_body,
                'action_type': action,
                'requires_approval': classification['requires_hitl_approval'],
                'drafted_at': datetime.now().isoformat()
            }

            self.logger.info(f'Drafted response: {action} for {email_metadata.get("from_email")}')
            return draft

        except Exception as e:
            self.logger.error(f'Failed to draft response: {e}')
            return {}

    def create_pending_approval_file(self, draft: Dict) -> Path:
        """
        Create file in /Pending_Approval for HITL review

        Args:
            draft: Draft response

        Returns:
            Path to approval file
        """
        try:
            pending = self.vault_path / 'Pending_Approval'
            filename = f"DRAFT_{draft['email_id'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = pending / filename

            content = f"""---
type: email_draft_approval
email_id: {draft['email_id']}
to: {draft['to']}
status: pending_approval
requires_approval: {draft['requires_approval']}
action_type: {draft['action_type']}
created: {draft['drafted_at']}
---

# Draft Response for Review

## Original Email From
{draft['to']}

## Drafted Subject
{draft['subject']}

## Drafted Body
```
{draft['body']}
```

## Actions
- [ ] APPROVED - Send this response
- [ ] EDIT - Modify and then send
- [ ] REJECT - Don't send
- [ ] FORWARD - Send to someone else

## Instructions
1. Review the draft response above
2. Select one action checkbox
3. Save file
4. Auto-sender will process within 1 minute

---
*Drafted by Email Responder Skill*
*Agent: Fatima Zehra - Email Specialist*
"""

            filepath.write_text(content)
            self.logger.info(f'Created approval file: {filename}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create approval file: {e}')
            return None

    def create_auto_send_file(self, draft: Dict) -> Path:
        """
        Create file for auto-sending (no approval needed)

        Args:
            draft: Draft response

        Returns:
            Path to auto-send file
        """
        try:
            inbox = self.vault_path / 'Inbox'
            filename = f"AUTOSEND_{draft['email_id'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = inbox / filename

            content = f"""---
type: email_autosend
email_id: {draft['email_id']}
to: {draft['to']}
subject: {draft['subject']}
action: send_email
priority: {draft['action_type']}
created: {draft['drafted_at']}
---

# Auto-Send Response

**To:** {draft['to']}
**Subject:** {draft['subject']}

## Body
{draft['body']}

---
*Scheduled for auto-sending*
*Agent: Fatima Zehra - Email Specialist*
"""

            filepath.write_text(content)
            self.logger.info(f'Created auto-send file: {filename}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create auto-send file: {e}')
            return None

if __name__ == '__main__':
    responder = EmailResponder()

    # Test email
    test_email = {
        'email_id': 'test789',
        'subject': 'Meeting Request',
        'from_email': 'client@example.com',
        'from_name': 'John Client',
        'body_preview': 'Can we schedule a meeting next week?'
    }

    test_classification = {
        'recommended_action': 'SCHEDULE_CALENDAR',
        'requires_hitl_approval': True
    }

    draft = responder.draft_response(test_email, test_classification)
    print("✅ Email Responder Test")
    print(json.dumps(draft, indent=2))
