"""
Utility functions for autonomous e2e testing framework
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from enum import Enum


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(Enum):
    """Issue categories"""
    CONSOLE_ERROR = "console-error"
    NETWORK_FAILURE = "network-failure"
    BROKEN_IMAGE = "broken-image"
    MISSING_ALT_TEXT = "missing-alt-text"
    LAYOUT_PROBLEM = "layout-problem"
    PERFORMANCE_ISSUE = "performance-issue"
    ACCESSIBILITY_ISSUE = "accessibility-issue"


class Issue:
    """Represents a detected issue"""

    def __init__(
        self,
        category: IssueCategory,
        severity: Severity,
        description: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        screenshot_path: Optional[str] = None,
        auto_fix: bool = False,
        fix_code: Optional[str] = None,
        fix_suggestion: Optional[str] = None,
        confidence: float = 1.0
    ):
        self.category = category
        self.severity = severity
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.screenshot_path = screenshot_path
        self.auto_fix = auto_fix
        self.fix_code = fix_code
        self.fix_suggestion = fix_suggestion
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary"""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "screenshot_path": self.screenshot_path,
            "auto_fix": self.auto_fix,
            "fix_code": self.fix_code,
            "fix_suggestion": self.fix_suggestion,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        return f"<Issue {self.severity.value}: {self.description[:50]}...>"


class TestResult:
    """Represents a test execution result"""

    def __init__(self, scenario_name: str, passed: bool = True, error: Optional[str] = None):
        self.scenario_name = scenario_name
        self.passed = passed
        self.error = error
        self.timestamp = datetime.now().isoformat()
        self.issues: List[Issue] = []
        self.execution_time = 0.0  # seconds

    def add_issue(self, issue: Issue) -> None:
        """Add an issue to this test result"""
        self.issues.append(issue)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "scenario_name": self.scenario_name,
            "passed": self.passed,
            "error": self.error,
            "timestamp": self.timestamp,
            "execution_time": self.execution_time,
            "issue_count": len(self.issues),
            "issues": [issue.to_dict() for issue in self.issues]
        }


class Logger:
    """Centralized logging utility"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("autonomous-e2e-testing")
            self._logger.setLevel(logging.DEBUG)

            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            self._logger.addHandler(ch)

    def info(self, message: str) -> None:
        """Log info message"""
        self._logger.info(message)

    def error(self, message: str) -> None:
        """Log error message"""
        self._logger.error(message)

    def debug(self, message: str) -> None:
        """Log debug message"""
        self._logger.debug(message)

    def warning(self, message: str) -> None:
        """Log warning message"""
        self._logger.warning(message)

    @staticmethod
    def get_logger():
        """Get the logger instance"""
        return Logger()._logger


def setup_report_dir(base_dir: str = "./test-reports") -> str:
    """Create report directory with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    report_dir = os.path.join(base_dir, timestamp)

    os.makedirs(os.path.join(report_dir, "screenshots"), exist_ok=True)
    os.makedirs(os.path.join(report_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(report_dir, "fixes"), exist_ok=True)

    return report_dir


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_log(message: str, log_file: str) -> None:
    """Append message to log file"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'a') as f:
        timestamp = datetime.now().isoformat()
        f.write(f"[{timestamp}] {message}\n")


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load YAML file (requires PyYAML)"""
    try:
        import yaml
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        raise RuntimeError("PyYAML not installed. Run: pip install pyyaml")


def run_command(command: str, cwd: Optional[str] = None) -> tuple[str, str, int]:
    """Run shell command and return stdout, stderr, returncode"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timeout", 1
    except Exception as e:
        return "", str(e), 1


def is_server_running(host: str = "localhost", port: int = 8808) -> bool:
    """Check if MCP server is running"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def format_severity(severity: Severity) -> str:
    """Format severity as emoji + text"""
    emoji_map = {
        Severity.CRITICAL: "🔴",
        Severity.HIGH: "🟠",
        Severity.MEDIUM: "🟡",
        Severity.LOW: "🟢"
    }
    return f"{emoji_map.get(severity, '•')} {severity.value.upper()}"


def format_category(category: IssueCategory) -> str:
    """Format category as readable text"""
    mapping = {
        IssueCategory.CONSOLE_ERROR: "Console Error",
        IssueCategory.NETWORK_FAILURE: "Network Failure",
        IssueCategory.BROKEN_IMAGE: "Broken Image",
        IssueCategory.MISSING_ALT_TEXT: "Missing Alt Text",
        IssueCategory.LAYOUT_PROBLEM: "Layout Problem",
        IssueCategory.PERFORMANCE_ISSUE: "Performance Issue",
        IssueCategory.ACCESSIBILITY_ISSUE: "Accessibility Issue"
    }
    return mapping.get(category, category.value)


def group_issues_by_severity(issues: List[Issue]) -> Dict[Severity, List[Issue]]:
    """Group issues by severity level"""
    grouped = {
        Severity.CRITICAL: [],
        Severity.HIGH: [],
        Severity.MEDIUM: [],
        Severity.LOW: []
    }
    for issue in issues:
        grouped[issue.severity].append(issue)
    return grouped


def group_issues_by_category(issues: List[Issue]) -> Dict[IssueCategory, List[Issue]]:
    """Group issues by category"""
    grouped = {}
    for issue in issues:
        if issue.category not in grouped:
            grouped[issue.category] = []
        grouped[issue.category].append(issue)
    return grouped


def create_relative_path(target: str, base: str) -> str:
    """Create relative path from base to target"""
    return os.path.relpath(target, base)


class MCPClientWrapper:
    """Wrapper for MCP client HTTP communication"""

    def __init__(self, host: str = "localhost", port: int = 8808):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        self.logger = Logger.get_logger()

    def is_available(self) -> bool:
        """Check if MCP server is available"""
        return is_server_running(self.host, self.port)

    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server"""
        # This will be implemented by the orchestrator
        # which has access to the actual MCP client via Python script
        pass


def print_summary(
    total_tests: int,
    passed_tests: int,
    issues: List[Issue],
    auto_fixed_count: int,
    execution_time: float
) -> None:
    """Print test execution summary"""
    from datetime import timedelta

    failed = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Group issues
    grouped = group_issues_by_severity(issues)

    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    print(f"\nTests Run:      {total_tests}")
    print(f"Passed:         {passed_tests} ({pass_rate:.1f}%)")
    print(f"Failed:         {failed}")
    print(f"Execution Time: {timedelta(seconds=int(execution_time))}")

    print(f"\nIssues Detected:")
    print(f"  🔴 Critical: {len(grouped[Severity.CRITICAL])}")
    print(f"  🟠 High:     {len(grouped[Severity.HIGH])}")
    print(f"  🟡 Medium:   {len(grouped[Severity.MEDIUM])}")
    print(f"  🟢 Low:      {len(grouped[Severity.LOW])}")

    print(f"\nAuto-Fixes Applied: {auto_fixed_count}")
    print("="*60 + "\n")
