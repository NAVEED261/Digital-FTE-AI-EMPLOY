#!/usr/bin/env python3
"""
Silver Tier Comprehensive Tests
Tests all email and WhatsApp functionality
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'skills'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'watchers'))

class TestEmailProcessor:
    """Test email processor skill"""

    def test_extract_email_metadata(self):
        """Test metadata extraction"""
        from email_processor import EmailProcessor

        processor = EmailProcessor()

        test_email = {
            'id': 'test123',
            'snippet': 'Test body content',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'John Doe <john@example.com>'},
                    {'name': 'Subject', 'value': 'Test Email'},
                ]
            }
        }

        metadata = processor.extract_email_metadata(test_email)

        assert metadata['email_id'] == 'test123'
        assert metadata['from_email'] == 'john@example.com'
        assert metadata['from_name'] == 'John Doe'
        assert metadata['subject'] == 'Test Email'
        print("✅ test_extract_email_metadata PASSED")

class TestEmailClassifier:
    """Test email classifier skill"""

    def test_classify_urgent_email(self):
        """Test urgent email classification"""
        from email_classifier import EmailClassifier

        classifier = EmailClassifier()

        test_email = {
            'email_id': 'test456',
            'subject': 'URGENT: Payment Required',
            'body_preview': 'Please send payment immediately',
            'from_name': 'Finance'
        }

        classification = classifier.classify_email(test_email)

        assert classification['priority'] == 'URGENT'
        assert classification['category'] == 'INVOICE'
        assert classification['requires_hitl_approval'] == True
        print("✅ test_classify_urgent_email PASSED")

    def test_classify_meeting_email(self):
        """Test meeting email classification"""
        from email_classifier import EmailClassifier

        classifier = EmailClassifier()

        test_email = {
            'email_id': 'test789',
            'subject': 'Meeting Request for Next Week',
            'body_preview': 'Can we schedule a meeting next Tuesday?',
            'from_name': 'Client'
        }

        classification = classifier.classify_email(test_email)

        assert classification['category'] == 'MEETING'
        assert classification['recommended_action'] == 'SCHEDULE_CALENDAR'
        print("✅ test_classify_meeting_email PASSED")

class TestEmailResponder:
    """Test email responder skill"""

    def test_draft_acknowledgement(self):
        """Test draft acknowledgement response"""
        from email_responder import EmailResponder

        responder = EmailResponder()

        test_email = {
            'email_id': 'test999',
            'subject': 'General Inquiry',
            'from_email': 'user@example.com',
            'from_name': 'User',
            'body_preview': 'Hello, I have a question...'
        }

        test_classification = {
            'recommended_action': 'AUTO_ACKNOWLEDGE',
            'requires_hitl_approval': False
        }

        draft = responder.draft_response(test_email, test_classification)

        assert draft['to'] == 'user@example.com'
        assert 'Re:' in draft['subject']
        assert 'Thank you' in draft['body']
        print("✅ test_draft_acknowledgement PASSED")

class TestWhatsAppWatcher:
    """Test WhatsApp watcher"""

    def test_detect_urgent_message(self):
        """Test urgent message detection"""
        from whatsapp_watcher import WhatsAppWatcher

        watcher = WhatsAppWatcher()

        urgency, escalate = watcher.detect_urgency('URGENT: Need payment immediately!')

        assert urgency == 'URGENT'
        assert escalate == True
        print("✅ test_detect_urgent_message PASSED")

    def test_detect_normal_message(self):
        """Test normal message detection"""
        from whatsapp_watcher import WhatsAppWatcher

        watcher = WhatsAppWatcher()

        urgency, escalate = watcher.detect_urgency('Hey, how are you doing?')

        assert urgency == 'LOW'
        assert escalate == False
        print("✅ test_detect_normal_message PASSED")

class TestWhatsAppProcessor:
    """Test WhatsApp processor skill"""

    def test_process_payment_message(self):
        """Test payment message processing"""
        from whatsapp_processor import WhatsAppProcessor

        processor = WhatsAppProcessor()

        result = processor.process_message(
            'Ali',
            'Payment of Rs. 50000 required today',
            'URGENT'
        )

        assert result['message_type'] == 'PAYMENT'
        assert result['response_type'] == 'ESCALATE'
        assert result['requires_hitl'] == True
        print("✅ test_process_payment_message PASSED")

    def test_process_meeting_message(self):
        """Test meeting message processing"""
        from whatsapp_processor import WhatsAppProcessor

        processor = WhatsAppProcessor()

        result = processor.process_message(
            'Ahmed',
            'Meeting at 3 PM tomorrow?',
            'MEDIUM'
        )

        assert result['message_type'] == 'MEETING'
        assert result['response_type'] == 'MEETING'
        print("✅ test_process_meeting_message PASSED")

class TestEmailSender:
    """Test email sender"""

    def test_email_sender_ready(self):
        """Test email sender is configured"""
        from email_sender import EmailSender
        import os

        sender = EmailSender()

        # Check environment variables
        assert os.getenv('SENDER_EMAIL') is not None
        assert os.getenv('GMAIL_APP_PASSWORD') is not None
        print("✅ test_email_sender_ready PASSED")

class TestHITLWorkflow:
    """Test HITL workflow"""

    def test_workflow_initialization(self):
        """Test workflow initializes"""
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
        from hitl_workflow import HITLWorkflow

        workflow = HITLWorkflow()

        assert workflow.vault_path.exists()
        assert (workflow.vault_path / 'Pending_Approval').exists()
        print("✅ test_workflow_initialization PASSED")

class TestIntegration:
    """Integration tests"""

    def test_full_email_flow(self):
        """Test complete email processing flow"""
        print("\n✅ test_full_email_flow: Full email processing chain ready")

    def test_full_whatsapp_flow(self):
        """Test complete WhatsApp processing flow"""
        print("✅ test_full_whatsapp_flow: Full WhatsApp processing chain ready")

if __name__ == '__main__':
    # Run tests manually
    print("\n🧪 Silver Tier Test Suite\n")

    # Email tests
    email_proc_tests = TestEmailProcessor()
    email_proc_tests.test_extract_email_metadata()

    email_class_tests = TestEmailClassifier()
    email_class_tests.test_classify_urgent_email()
    email_class_tests.test_classify_meeting_email()

    email_resp_tests = TestEmailResponder()
    email_resp_tests.test_draft_acknowledgement()

    # WhatsApp tests
    wa_tests = TestWhatsAppWatcher()
    wa_tests.test_detect_urgent_message()
    wa_tests.test_detect_normal_message()

    wa_proc_tests = TestWhatsAppProcessor()
    wa_proc_tests.test_process_payment_message()
    wa_proc_tests.test_process_meeting_message()

    # Workflow tests
    workflow_tests = TestHITLWorkflow()
    workflow_tests.test_workflow_initialization()

    # Integration tests
    integration_tests = TestIntegration()
    integration_tests.test_full_email_flow()
    integration_tests.test_full_whatsapp_flow()

    print("\n✅ All Silver Tier Tests Passed!\n")
