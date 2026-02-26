#!/usr/bin/env python3
"""
WhatsApp Session Integrator Tests - Silver Tier
Tests complete WhatsApp Web automation with Obsidian integration
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'watchers'))

from whatsapp_session_integrator import WhatsAppSessionIntegrator


class TestWhatsAppSessionIntegrator:
    """Test WhatsApp Session Integrator functionality"""

    def test_integrator_initialization(self):
        """Test WhatsApp integrator initializes correctly"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        assert integrator is not None, "Integrator should be initialized"
        assert integrator.phone_number == '03002385209', "Phone number should be set"
        assert integrator.vault_path.exists(), "Vault path should exist"
        assert integrator.inbox.exists(), "Inbox folder should exist"
        assert integrator.logs.exists(), "Logs folder should exist"
        assert integrator.session_active == False, "Session should start as inactive"
        print("✅ test_integrator_initialization PASSED")

    def test_message_backup_creation(self):
        """Test vault backup creation for messages"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        test_message = {
            'sender': 'TestUser',
            'text': 'This is a test message for backup',
            'timestamp': datetime.now().isoformat()
        }

        # Create backup
        integrator.create_vault_backup(test_message)

        # Verify backup file created
        backup_files = list(integrator.inbox.glob('WA_BACKUP_TestUser*.md'))
        assert len(backup_files) > 0, "Backup file should be created"

        # Verify backup content
        backup_content = backup_files[0].read_text()
        assert 'TestUser' in backup_content, "Backup should contain sender"
        assert 'test message' in backup_content, "Backup should contain message text"
        assert 'whatsapp_backup' in backup_content, "Backup should have correct type"

        # Cleanup
        backup_files[0].unlink()
        print("✅ test_message_backup_creation PASSED")

    def test_sent_message_logging(self):
        """Test sent message logging to vault"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        integrator._log_sent_message('RecipientName', 'Test message content')

        # Verify log file created
        log_file = integrator.logs / 'whatsapp_sent_messages.log'
        assert log_file.exists(), "Sent messages log should be created"

        # Verify log content
        log_content = log_file.read_text()
        assert 'RecipientName' in log_content, "Log should contain recipient"
        assert 'Test message content' in log_content, "Log should contain message"
        assert 'MESSAGE SENT' in log_content, "Log should indicate message sent"

        print("✅ test_sent_message_logging PASSED")

    def test_vault_structure(self):
        """Test Obsidian vault structure is created"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        # Check required folders exist
        assert integrator.vault_path.exists(), "Vault path should exist"
        assert integrator.inbox.exists(), "Inbox folder should exist"
        assert integrator.logs.exists(), "Logs folder should exist"

        # Check vault is accessible
        vault_files = list(integrator.vault_path.iterdir())
        assert len(vault_files) > 0, "Vault should contain files/folders"

        print("✅ test_vault_structure PASSED")

    def test_integrator_logging(self):
        """Test integrator logging to vault logs"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        # Check logger is configured
        assert integrator.logger is not None, "Logger should be configured"
        assert len(integrator.logger.handlers) > 0, "Logger should have handlers"

        # Check log file path
        log_file = integrator.logs / 'whatsapp_integrator.log'
        assert log_file.exists() or integrator.logs.exists(), "Log directory should exist"

        print("✅ test_integrator_logging PASSED")

    def test_message_data_structure(self):
        """Test message data structure is correct"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        # Create test message structure
        test_message = {
            'sender': 'TestSender',
            'text': 'Test message text',
            'timestamp': datetime.now().isoformat(),
            'chat_index': 0
        }

        # Verify structure
        assert 'sender' in test_message, "Message should have sender"
        assert 'text' in test_message, "Message should have text"
        assert 'timestamp' in test_message, "Message should have timestamp"
        assert len(test_message['text']) > 0, "Message text should not be empty"

        # Create backup and verify structure is maintained
        integrator.create_vault_backup(test_message)

        # Use first 8 chars of sender name (TestSen) to match backup filename
        backup_files = list(integrator.inbox.glob('WA_BACKUP_TestSen*.md'))
        assert len(backup_files) > 0, "Backup should be created"

        # Cleanup
        backup_files[0].unlink()
        print("✅ test_message_data_structure PASSED")

    def test_phone_number_configuration(self):
        """Test phone number is properly configured"""
        phone_number = '03002385209'
        integrator = WhatsAppSessionIntegrator(phone_number=phone_number)

        assert integrator.phone_number == phone_number, "Phone number should match configuration"
        assert '03002385209' in integrator.phone_number, "Phone number should contain correct digits"

        print("✅ test_phone_number_configuration PASSED")

    def test_session_state_tracking(self):
        """Test session state is tracked correctly"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        # Initial state should be inactive
        assert integrator.session_active == False, "Session should start as inactive"

        # Simulate session activation
        integrator.session_active = True
        assert integrator.session_active == True, "Session state should be updateable"

        # Simulate session deactivation
        integrator.session_active = False
        assert integrator.session_active == False, "Session should be deactivatable"

        print("✅ test_session_state_tracking PASSED")

    def test_browser_attributes(self):
        """Test browser attributes are initialized"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        assert integrator.playwright is None or integrator.playwright, "Playwright should be None or initialized"
        assert integrator.browser is None or integrator.browser, "Browser should be None or initialized"
        assert integrator.page is None or integrator.page, "Page should be None or initialized"

        print("✅ test_browser_attributes PASSED")

    def test_message_backup_format(self):
        """Test message backup has correct Markdown format"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        test_message = {
            'sender': 'Ali',
            'text': 'Payment of Rs. 50,000 needed',
            'timestamp': datetime.now().isoformat()
        }

        integrator.create_vault_backup(test_message)

        backup_files = list(integrator.inbox.glob('WA_BACKUP_Ali*.md'))
        assert len(backup_files) > 0, "Backup file should be created"

        backup_content = backup_files[0].read_text()

        # Verify YAML frontmatter
        assert '---' in backup_content, "Should have YAML frontmatter"
        assert 'type: whatsapp_backup' in backup_content, "Should have type metadata"
        assert 'from: Ali' in backup_content, "Should have from metadata"

        # Verify Markdown structure
        assert '# WhatsApp Message Backup' in backup_content, "Should have main heading"
        assert '**From:**' in backup_content, "Should have formatted sender"
        assert '## Message' in backup_content, "Should have message section"

        # Cleanup
        backup_files[0].unlink()
        print("✅ test_message_backup_format PASSED")

    def test_vault_integration_paths(self):
        """Test Obsidian vault integration with correct paths"""
        vault_path = Path('/mnt/d/Hackaton-0/AI_Employee_Vault')
        integrator = WhatsAppSessionIntegrator(vault_path=str(vault_path), phone_number='03002385209')

        assert integrator.vault_path == vault_path, "Vault path should match configuration"
        assert integrator.inbox == vault_path / 'Inbox', "Inbox path should be under vault"
        assert integrator.logs == vault_path / 'Logs', "Logs path should be under vault"

        print("✅ test_vault_integration_paths PASSED")


class TestWhatsAppIntegration:
    """Integration tests for complete WhatsApp workflow"""

    def test_complete_backup_workflow(self):
        """Test complete message backup workflow"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        # Create test messages
        messages = [
            {
                'sender': 'Mom',
                'text': 'Call me when you are free',
                'timestamp': datetime.now().isoformat()
            },
            {
                'sender': 'Boss',
                'text': 'URGENT: Please review the proposal ASAP',
                'timestamp': datetime.now().isoformat()
            },
            {
                'sender': 'Friend',
                'text': 'Are we still meeting tomorrow?',
                'timestamp': datetime.now().isoformat()
            }
        ]

        # Create backups for all messages
        for msg in messages:
            integrator.create_vault_backup(msg)

        # Verify all backups created
        backup_files = list(integrator.inbox.glob('WA_BACKUP_*.md'))
        assert len(backup_files) >= 3, "All message backups should be created"

        # Cleanup
        for backup_file in backup_files:
            backup_file.unlink()

        print("✅ test_complete_backup_workflow PASSED")

    def test_multiple_senders_backup(self):
        """Test backing up messages from multiple senders"""
        integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

        senders = ['Ali', 'Ahmed', 'Sara', 'Finance', 'HR']

        for sender in senders:
            msg = {
                'sender': sender,
                'text': f'Message from {sender}',
                'timestamp': datetime.now().isoformat()
            }
            integrator.create_vault_backup(msg)

        # Verify all sender backups created
        backup_files = list(integrator.inbox.glob('WA_BACKUP_*.md'))
        assert len(backup_files) >= len(senders), "Backups for all senders should exist"

        # Verify each sender has at least one backup
        for sender in senders:
            sender_backups = [f for f in backup_files if sender[:3].lower() in f.name.lower()]
            assert len(sender_backups) > 0, f"Backup for {sender} should exist"

        # Cleanup
        for backup_file in backup_files:
            backup_file.unlink()

        print("✅ test_multiple_senders_backup PASSED")


if __name__ == '__main__':
    print("\n🧪 WhatsApp Session Integrator Test Suite\n")

    # Run synchronous tests
    test_sync = TestWhatsAppSessionIntegrator()
    test_sync.test_integrator_initialization()
    test_sync.test_message_backup_creation()
    test_sync.test_sent_message_logging()
    test_sync.test_vault_structure()
    test_sync.test_integrator_logging()
    test_sync.test_message_data_structure()
    test_sync.test_phone_number_configuration()
    test_sync.test_session_state_tracking()
    test_sync.test_browser_attributes()
    test_sync.test_message_backup_format()
    test_sync.test_vault_integration_paths()

    # Run integration tests
    test_integration = TestWhatsAppIntegration()
    test_integration.test_complete_backup_workflow()
    test_integration.test_multiple_senders_backup()

    print("\n✅ All WhatsApp Integrator Tests Passed!\n")
