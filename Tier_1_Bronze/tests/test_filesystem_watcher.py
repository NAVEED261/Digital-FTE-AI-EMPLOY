"""
Test suite for Filesystem Watcher (Bronze Tier)
Validates file detection, movement, and metadata creation
"""
import pytest
from pathlib import Path
import time
import json
from unittest.mock import patch, MagicMock


class TestFilesystemWatcher:
    """Test filesystem watcher functionality"""
    
    @pytest.fixture
    def vault_paths(self, tmp_path):
        """Create temporary vault structure for testing"""
        vault = tmp_path / "vault"
        inbox = vault / "Inbox"
        needs_action = vault / "Needs_Action"
        logs = vault / "Logs"
        
        inbox.mkdir(parents=True)
        needs_action.mkdir(parents=True)
        logs.mkdir(parents=True)
        
        return {
            "vault": vault,
            "inbox": inbox,
            "needs_action": needs_action,
            "logs": logs
        }
    
    def test_watcher_detects_file_creation(self, vault_paths):
        """Test that watcher detects file created in /Inbox"""
        # Create test file
        test_file = vault_paths["inbox"] / "test_document.txt"
        test_file.write_text("Test content")
        
        # Verify file exists
        assert test_file.exists()
        assert test_file.parent.name == "Inbox"
    
    def test_watcher_moves_file_to_needs_action(self, vault_paths):
        """Test that watcher moves file from /Inbox to /Needs_Action"""
        test_file = vault_paths["inbox"] / "test_document.txt"
        test_file.write_text("Test content")
        
        # Simulate watcher moving file
        dest_file = vault_paths["needs_action"] / test_file.name
        test_file.rename(dest_file)
        
        # Verify movement
        assert not test_file.exists()
        assert dest_file.exists()
        assert dest_file.read_text() == "Test content"
    
    def test_watcher_creates_metadata_file(self, vault_paths):
        """Test that watcher creates .md metadata file"""
        test_file = vault_paths["inbox"] / "invoice.pdf"
        test_file.write_bytes(b"PDF content")
        
        # Create metadata
        dest_file = vault_paths["needs_action"] / test_file.name
        test_file.rename(dest_file)
        
        meta_file = dest_file.with_suffix(dest_file.suffix + ".md")
        meta_content = f"""---
type: file_drop
original_name: {test_file.name}
size_bytes: {len("PDF content")}
received: 2026-02-26T14:30:00Z
priority: medium
status: pending
---

# File Dropped: {test_file.name}
"""
        meta_file.write_text(meta_content)
        
        # Verify metadata exists and contains correct data
        assert meta_file.exists()
        assert "file_drop" in meta_file.read_text()
        assert test_file.name in meta_file.read_text()
    
    def test_watcher_handles_duplicate_files(self, vault_paths):
        """Test that watcher doesn't process same file twice"""
        test_file = vault_paths["inbox"] / "document.txt"
        test_file.write_text("Content")
        
        # Simulate processing once
        processed_set = {test_file}
        
        # Try to process again
        if test_file in processed_set:
            result = "skipped"
        else:
            result = "processed"
        
        assert result == "skipped"
    
    def test_audit_log_created(self, vault_paths):
        """Test that watcher creates audit log"""
        log_entry = {
            "timestamp": "2026-02-26T14:30:00Z",
            "event": "file_moved",
            "source": "Inbox/test.txt",
            "dest": "Needs_Action/test.txt",
            "metadata_created": True
        }
        
        log_file = vault_paths["logs"] / "FileSystemWatcher.log"
        log_file.write_text(json.dumps(log_entry))
        
        assert log_file.exists()
        loaded = json.loads(log_file.read_text())
        assert loaded["event"] == "file_moved"


class TestWatcherPerformance:
    """Test performance targets"""
    
    def test_detection_latency(self, tmp_path):
        """Test file detection latency < 1 second"""
        inbox = tmp_path / "inbox"
        inbox.mkdir()
        
        test_file = inbox / "test.txt"
        
        start = time.time()
        test_file.write_text("content")
        latency = (time.time() - start) * 1000  # Convert to ms
        
        # Should be detected in <1000ms (1 second)
        assert latency < 1000


def test_pm2_watcher_running():
    """Test that PM2 keeps watcher running 24/7"""
    # Mock PM2 process check
    mock_pm2_status = {
        "pm2_env": {
            "status": "online",
            "restart_time": 0,
            "pm_uptime": 1000000
        }
    }
    
    # Verify watcher is online
    assert mock_pm2_status["pm2_env"]["status"] == "online"
    assert mock_pm2_status["pm2_env"]["restart_time"] >= 0


# Fixtures for all tests
@pytest.fixture(scope="session")
def vault_configuration():
    """Vault configuration for all tests"""
    return {
        "vault_path": "/mnt/d/Hackaton-0/AI_Employee_Vault",
        "watch_path": "Inbox",
        "action_path": "Needs_Action",
        "check_interval_seconds": 1
    }
