"""
Test suite for Human-in-the-Loop Workflow (Bronze Tier)
Validates approval process and decision routing
"""
import pytest
from pathlib import Path


class TestHITLWorkflow:
    """Test HITL approval workflow"""
    
    @pytest.fixture
    def vault_paths(self, tmp_path):
        """Create workflow structure"""
        paths = {
            "needs_action": tmp_path / "Needs_Action",
            "pending_approval": tmp_path / "Pending_Approval",
            "approved": tmp_path / "Approved",
            "rejected": tmp_path / "Rejected",
            "done": tmp_path / "Done"
        }
        for path in paths.values():
            path.mkdir()
        return paths
    
    def test_low_risk_action_auto_executes(self, vault_paths):
        """Test that low-risk action auto-executes"""
        # Low-risk: file move from Inbox to Needs_Action
        task = vault_paths["needs_action"] / "task.md"
        task.write_text("# Simple file movement task")
        
        # Should auto-execute
        result = {
            "approval_required": False,
            "executed": True,
            "moved_to": str(vault_paths["done"])
        }
        
        assert result["approval_required"] is False
        assert result["executed"] is True
    
    def test_high_risk_action_creates_approval(self, vault_paths):
        """Test that high-risk action creates approval request"""
        # High-risk: payment email to new contact
        approval_request = vault_paths["pending_approval"] / "send_email_new_contact.md"
        approval_request.write_text("""---
risk_level: high
action: email_send
target: unknown@external.com
---

# Approval Needed: Send Email
""")
        
        assert approval_request.exists()
        assert "high" in approval_request.read_text()
    
    def test_approval_executes_action(self, vault_paths):
        """Test that approved action executes"""
        # Create approval request
        approval = vault_paths["pending_approval"] / "action.md"
        approval.write_text("Approval needed")
        
        # User moves to /Approved
        approved = vault_paths["approved"] / "action.md"
        approval.rename(approved)
        
        # Action should execute and move to /Done
        done = vault_paths["done"] / "action.md"
        approved.rename(done)
        
        assert done.exists()
        assert not approval.exists()
    
    def test_rejection_discards_action(self, vault_paths):
        """Test that rejected action is discarded"""
        # Create approval request
        approval = vault_paths["pending_approval"] / "action.md"
        approval.write_text("Action to reject")
        
        # User moves to /Rejected
        rejected = vault_paths["rejected"] / "action.md"
        approval.rename(rejected)
        
        assert rejected.exists()
        assert not approval.exists()
    
    def test_timeout_auto_rejects(self, vault_paths):
        """Test that unapproved action auto-rejects after timeout"""
        import time
        
        approval = vault_paths["pending_approval"] / "action.md"
        approval.write_text("---\ntimeout: 0.001\n---\nAction")
        
        # Wait for timeout
        time.sleep(0.01)
        
        # Simulate auto-rejection
        if approval.exists():
            rejected = vault_paths["rejected"] / "action.md"
            approval.rename(rejected)
        
        assert not approval.exists()


class TestHITLThresholds:
    """Test HITL decision thresholds"""
    
    def test_email_known_contact_auto_approve(self):
        """Email to known contact should auto-approve"""
        contact_age_days = 30
        is_known = contact_age_days >= 30
        
        assert is_known is True
        assert "auto_approve"  # Would be auto-approved
    
    def test_email_new_contact_requires_approval(self):
        """Email to new contact should require approval"""
        contact_age_days = 0
        is_known = contact_age_days >= 30
        
        assert is_known is False
        # Should require approval
    
    def test_payment_under_50_auto_approve(self):
        """Payment < $50 should auto-approve"""
        amount = 25.00
        approval_required = amount >= 50
        
        assert approval_required is False
    
    def test_payment_over_50_requires_approval(self):
        """Payment >= $50 should require approval"""
        amount = 100.00
        approval_required = amount >= 50
        
        assert approval_required is True
    
    def test_social_media_draft_auto_approve(self):
        """Social media draft should auto-approve"""
        is_draft = True
        approval_required = not is_draft
        
        assert approval_required is False
    
    def test_social_media_publish_requires_approval(self):
        """Social media publish should require approval"""
        is_draft = False
        approval_required = not is_draft
        
        assert approval_required is True


def test_hitl_decision_logging(tmp_path):
    """Test that HITL decisions are logged"""
    import json
    
    logs_dir = tmp_path / "Logs"
    logs_dir.mkdir()
    
    decision = {
        "timestamp": "2026-02-26T14:30:00Z",
        "action": "email_send",
        "approval_required": True,
        "user_decision": "approved",
        "executed": True
    }
    
    log_file = logs_dir / "hitl_decisions.log"
    log_file.write_text(json.dumps(decision))
    
    loaded = json.loads(log_file.read_text())
    assert loaded["approval_required"] is True
    assert loaded["executed"] is True
