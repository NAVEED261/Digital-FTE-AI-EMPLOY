#!/usr/bin/env python3
"""
Email Classifier Skill - Silver Tier
Classifies emails by priority, category, and required action
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

class EmailClassifier:
    """Classify emails by priority, category, and urgency"""

    # Priority keywords
    URGENT_KEYWORDS = ['urgent', 'asap', 'emergency', 'critical', 'immediate', 'critical', 'high priority']
    HIGH_KEYWORDS = ['important', 'action required', 'payment due', 'invoice', 'deadline', 'required']
    LOW_KEYWORDS = ['fyi', 'for your information', 'update', 'newsletter', 'notification']

    # Category keywords
    INVOICE_KEYWORDS = ['invoice', 'bill', 'payment', 'amount due', 'receipt', 'order']
    MEETING_KEYWORDS = ['meeting', 'call', 'zoom', 'teams', 'schedule', 'availability']
    URGENT_ACTION_KEYWORDS = ['confirm', 'approve', 'urgent', 'asap', 'immediate']
    PERSONAL_KEYWORDS = ['personal', 'private', 'confidential', 'family']

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.logs = self.vault_path / 'Logs'

        # Setup logging
        self.logger = logging.getLogger('EmailClassifier')
        handler = logging.FileHandler(self.logs / 'email_classifier.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def classify_email(self, email_metadata: Dict) -> Dict:
        """
        Classify email and return priority and category

        Args:
            email_metadata: Email metadata from processor

        Returns:
            Classification result with priority, category, and actions
        """
        subject = email_metadata.get('subject', '').lower()
        body = email_metadata.get('body_preview', '').lower()
        from_name = email_metadata.get('from_name', '').lower()

        # Combine text for analysis
        combined_text = f"{subject} {body} {from_name}"

        # Determine priority
        priority, priority_reason = self._determine_priority(combined_text)

        # Determine category
        category, category_reason = self._determine_category(combined_text)

        # Determine action
        action, action_reason = self._determine_action(priority, category, subject)

        # Determine HITL requirement
        requires_hitl = self._requires_hitl(priority, category)

        classification = {
            'email_id': email_metadata.get('email_id'),
            'priority': priority,
            'priority_reason': priority_reason,
            'category': category,
            'category_reason': category_reason,
            'recommended_action': action,
            'action_reason': action_reason,
            'requires_hitl_approval': requires_hitl,
            'classified_at': datetime.now().isoformat()
        }

        self.logger.info(
            f"Classified email: {priority} priority, {category} category, "
            f"action: {action}, HITL: {requires_hitl}"
        )

        return classification

    def _determine_priority(self, text: str) -> Tuple[str, str]:
        """Determine priority level"""
        if any(keyword in text for keyword in self.URGENT_KEYWORDS):
            return 'URGENT', 'Contains urgent keywords'
        elif any(keyword in text for keyword in self.HIGH_KEYWORDS):
            return 'HIGH', 'Contains high-priority keywords'
        elif any(keyword in text for keyword in self.LOW_KEYWORDS):
            return 'LOW', 'Contains low-priority keywords'
        else:
            return 'MEDIUM', 'Default medium priority'

    def _determine_category(self, text: str) -> Tuple[str, str]:
        """Determine email category"""
        if any(keyword in text for keyword in self.INVOICE_KEYWORDS):
            return 'INVOICE', 'Contains invoice/payment keywords'
        elif any(keyword in text for keyword in self.MEETING_KEYWORDS):
            return 'MEETING', 'Contains meeting/scheduling keywords'
        elif any(keyword in text for keyword in self.URGENT_ACTION_KEYWORDS):
            return 'ACTION_REQUIRED', 'Requires user action'
        elif any(keyword in text for keyword in self.PERSONAL_KEYWORDS):
            return 'PERSONAL', 'Personal/confidential email'
        else:
            return 'GENERAL', 'General correspondence'

    def _determine_action(self, priority: str, category: str, subject: str) -> Tuple[str, str]:
        """Determine recommended action"""
        if priority == 'URGENT':
            return 'ESCALATE_IMMEDIATELY', 'Urgent priority requires immediate escalation'
        elif category == 'INVOICE':
            return 'REVIEW_PAYMENT', 'Invoice received - review and approve payment'
        elif category == 'MEETING':
            return 'SCHEDULE_CALENDAR', 'Meeting request - check calendar and respond'
        elif category == 'ACTION_REQUIRED':
            return 'DRAFT_RESPONSE', 'Action required - draft and send response'
        elif priority == 'HIGH':
            return 'DRAFT_RESPONSE', 'High priority - draft response for approval'
        else:
            return 'AUTO_ACKNOWLEDGE', 'Low priority - send acknowledgment'

    def _requires_hitl(self, priority: str, category: str) -> bool:
        """Determine if HITL approval is needed"""
        # Always require HITL for: urgent, invoices, payments, action required
        if priority in ['URGENT']:
            return True
        if category in ['INVOICE', 'ACTION_REQUIRED']:
            return True
        return False

    def update_action_file(self, email_id: str, classification: Dict) -> Path:
        """
        Update action file with classification results

        Args:
            email_id: Email ID
            classification: Classification result

        Returns:
            Path to updated file
        """
        try:
            # Find the action file
            inbox = self.vault_path / 'Inbox'
            for file in inbox.glob(f'PROC_{email_id[:8]}*.md'):
                content = file.read_text()

                # Update frontmatter
                updated = content.replace(
                    'status: pending_classification',
                    f'status: classified\n'
                    f'priority: {classification["priority"]}\n'
                    f'category: {classification["category"]}\n'
                    f'action: {classification["recommended_action"]}\n'
                    f'requires_hitl: {classification["requires_hitl_approval"]}'
                )

                # Add classification details
                updated += f'\n\n## Classification Results\n'
                updated += f'**Priority:** {classification["priority"]}\n'
                updated += f'**Category:** {classification["category"]}\n'
                updated += f'**Action:** {classification["recommended_action"]}\n'
                updated += f'**HITL Required:** {classification["requires_hitl_approval"]}\n'
                updated += f'**Classified At:** {classification["classified_at"]}\n'

                file.write_text(updated)
                self.logger.info(f'Updated action file with classification')
                return file

            return None

        except Exception as e:
            self.logger.error(f'Failed to update action file: {e}')
            return None

if __name__ == '__main__':
    classifier = EmailClassifier()

    # Test email
    test_email = {
        'email_id': 'test456',
        'subject': 'URGENT: Invoice Payment Due Today',
        'body_preview': 'Your invoice INV-2026-001 requires immediate payment',
        'from_name': 'Finance Team'
    }

    classification = classifier.classify_email(test_email)
    print("✅ Email Classifier Test")
    print(json.dumps(classification, indent=2))
