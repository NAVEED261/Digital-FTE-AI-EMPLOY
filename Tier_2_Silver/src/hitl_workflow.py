#!/usr/bin/env python3
"""
HITL (Human-in-the-Loop) Workflow Orchestrator - Silver Tier
Manages the approval workflow for emails and messages
"""

import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict

class HITLWorkflow:
    """Manage human-in-the-loop approval workflows"""

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.logs = self.vault_path / 'Logs'

        # Setup logging
        self.logger = logging.getLogger('HITLWorkflow')
        handler = logging.FileHandler(self.logs / 'hitl_workflow.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def process_approval_file(self, filepath: Path) -> Dict:
        """
        Process an approval file from Pending_Approval folder

        Args:
            filepath: Path to approval file

        Returns:
            Result of approval processing
        """
        try:
            content = filepath.read_text()

            # Check which action was selected
            if '- [x] APPROVED' in content or '- [x] Approved' in content.replace('X', 'x'):
                return self._execute_approved(filepath, content)
            elif '- [x] REJECT' in content or '- [x] Reject' in content.replace('X', 'x'):
                return self._execute_rejected(filepath, content)
            elif '- [x] EDIT' in content or '- [x] Edit' in content.replace('X', 'x'):
                return {'status': 'WAITING_EDIT', 'file': filepath}
            else:
                return {'status': 'PENDING_ACTION', 'file': filepath}

        except Exception as e:
            self.logger.error(f'Failed to process approval file: {e}')
            return {'status': 'ERROR', 'error': str(e)}

    def _execute_approved(self, filepath: Path, content: str) -> Dict:
        """Execute approved action"""
        try:
            file_type = self._extract_metadata(content, 'type')

            if file_type == 'email_draft_approval':
                return self._send_approved_email(filepath, content)
            elif file_type == 'whatsapp_response':
                return self._send_approved_whatsapp(filepath, content)
            else:
                return {'status': 'UNKNOWN_TYPE', 'file': filepath}

        except Exception as e:
            self.logger.error(f'Failed to execute approval: {e}')
            return {'status': 'ERROR', 'error': str(e)}

    def _send_approved_email(self, filepath: Path, content: str) -> Dict:
        """Send approved email"""
        try:
            to = self._extract_metadata(content, 'to')
            subject = self._extract_metadata(content, 'subject')

            # Mark as approved
            self._move_file_to_approved(filepath)

            # Log the action
            self.logger.info(f'APPROVED: Email to {to} with subject "{subject}"')

            return {
                'status': 'APPROVED_AND_QUEUED',
                'type': 'email',
                'to': to,
                'subject': subject,
                'next_action': 'SEND_EMAIL'
            }

        except Exception as e:
            self.logger.error(f'Failed to process email approval: {e}')
            return {'status': 'ERROR', 'error': str(e)}

    def _send_approved_whatsapp(self, filepath: Path, content: str) -> Dict:
        """Send approved WhatsApp response"""
        try:
            sender = self._extract_metadata(content, 'sender')
            msg_type = self._extract_metadata(content, 'message_type')

            # Mark as approved
            self._move_file_to_approved(filepath)

            # Log the action
            self.logger.info(f'APPROVED: WhatsApp to {sender} ({msg_type})')

            return {
                'status': 'APPROVED_AND_QUEUED',
                'type': 'whatsapp',
                'sender': sender,
                'message_type': msg_type,
                'next_action': 'SEND_WHATSAPP'
            }

        except Exception as e:
            self.logger.error(f'Failed to process WhatsApp approval: {e}')
            return {'status': 'ERROR', 'error': str(e)}

    def _execute_rejected(self, filepath: Path, content: str) -> Dict:
        """Execute rejected action"""
        try:
            file_type = self._extract_metadata(content, 'type')

            # Move to Rejected folder
            rejected = self.vault_path / 'Rejected'
            rejected.mkdir(exist_ok=True)

            new_path = rejected / filepath.name
            shutil.move(str(filepath), str(new_path))

            self.logger.info(f'REJECTED: {file_type} moved to Rejected folder')

            return {
                'status': 'REJECTED',
                'type': file_type,
                'file': new_path
            }

        except Exception as e:
            self.logger.error(f'Failed to process rejection: {e}')
            return {'status': 'ERROR', 'error': str(e)}

    def _move_file_to_approved(self, filepath: Path):
        """Move file from Pending_Approval to Approved"""
        try:
            approved = self.vault_path / 'Approved'
            approved.mkdir(exist_ok=True)

            new_path = approved / filepath.name
            shutil.move(str(filepath), str(new_path))

            self.logger.info(f'Moved to Approved: {filepath.name}')

        except Exception as e:
            self.logger.error(f'Failed to move file: {e}')

    def _extract_metadata(self, content: str, key: str) -> str:
        """Extract metadata from file frontmatter"""
        for line in content.split('\n'):
            if line.startswith(f'{key}:'):
                return line.split(':', 1)[1].strip()
        return ''

    def process_inbox(self) -> Dict:
        """
        Process all pending approval files in workflow

        Returns:
            Summary of processed files
        """
        pending = self.vault_path / 'Pending_Approval'

        if not pending.exists():
            return {'processed': 0, 'approved': 0, 'rejected': 0}

        results = {'processed': 0, 'approved': 0, 'rejected': 0, 'pending': 0}

        for filepath in pending.glob('*.md'):
            result = self.process_approval_file(filepath)

            results['processed'] += 1

            if result.get('status') == 'APPROVED_AND_QUEUED':
                results['approved'] += 1
            elif result.get('status') == 'REJECTED':
                results['rejected'] += 1
            elif result.get('status') == 'PENDING_ACTION':
                results['pending'] += 1

        self.logger.info(
            f'Workflow processed: {results["approved"]} approved, '
            f'{results["rejected"]} rejected, {results["pending"]} pending'
        )

        return results

if __name__ == '__main__':
    workflow = HITLWorkflow()
    print("✅ HITL Workflow Orchestrator Ready")
    print("Monitoring Pending_Approval folder for user actions...")
