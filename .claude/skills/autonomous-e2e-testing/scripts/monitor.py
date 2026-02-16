#!/usr/bin/env python3
"""
Continuous Monitoring Engine (Phase 4)

Monitors app in real-time and alerts on issues:
1. Periodic test execution
2. Real-time issue detection
3. Alert notifications
4. Trend analysis
5. Auto-remediation triggers
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

sys.path.insert(0, os.path.dirname(__file__))

from utils import Logger, Issue, Severity, save_json
from issue_detector import IssueDetector
from report_generator import ReportGenerator


class AlertLevel(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Alert:
    """Represents a monitoring alert"""

    def __init__(self, level: AlertLevel, message: str, issue: Optional[Issue] = None):
        """Initialize alert"""
        self.level = level
        self.message = message
        self.issue = issue
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "issue": self.issue.to_dict() if self.issue else None
        }


class MonitoringConfig:
    """Configuration for monitoring"""

    def __init__(
        self,
        app_url: str,
        interval_seconds: int = 300,  # 5 minutes default
        duration_seconds: int = 3600,  # 1 hour default
        alert_on_severities: List[Severity] = None,
        max_retries: int = 3
    ):
        """Initialize monitoring config"""
        self.app_url = app_url
        self.interval_seconds = interval_seconds
        self.duration_seconds = duration_seconds
        self.alert_on_severities = alert_on_severities or [Severity.CRITICAL, Severity.HIGH]
        self.max_retries = max_retries


class MonitoringStats:
    """Tracks monitoring statistics"""

    def __init__(self):
        """Initialize stats"""
        self.checks_run = 0
        self.issues_detected = 0
        self.alerts_sent = 0
        self.start_time = datetime.now()
        self.last_check = None
        self.issue_history: List[Dict[str, Any]] = []

    def add_check(self, issues_found: int, issues: List[Issue]) -> None:
        """Record a check result"""
        self.checks_run += 1
        self.issues_detected += issues_found
        self.last_check = datetime.now()

        # Add to history
        for issue in issues:
            self.issue_history.append({
                "timestamp": datetime.now().isoformat(),
                "issue": issue.to_dict()
            })

    def get_summary(self) -> Dict[str, Any]:
        """Get statistics summary"""
        duration = datetime.now() - self.start_time
        return {
            "total_checks": self.checks_run,
            "total_issues": self.issues_detected,
            "total_alerts": self.alerts_sent,
            "duration_seconds": duration.total_seconds(),
            "average_check_interval": (
                duration.total_seconds() / self.checks_run if self.checks_run > 0 else 0
            ),
            "last_check": self.last_check.isoformat() if self.last_check else None
        }


class Monitor:
    """Continuous monitoring orchestrator"""

    def __init__(self, config: MonitoringConfig):
        """Initialize monitor"""
        self.config = config
        self.logger = Logger.get_logger()
        self.detector = IssueDetector(config.app_url)
        self.stats = MonitoringStats()
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable[[Alert], None]] = []

    def register_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """Register callback for alerts"""
        self.alert_handlers.append(handler)

    def send_alert(self, alert: Alert) -> None:
        """Send alert through all registered handlers"""
        self.stats.alerts_sent += 1
        self.alerts.append(alert)

        # Call all registered handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")

        # Log alert
        emoji = "🔴" if alert.level == AlertLevel.CRITICAL else "🟡" if alert.level == AlertLevel.WARNING else "ℹ️"
        self.logger.info(f"{emoji} {alert.level.value.upper()}: {alert.message}")

    def check_health(self) -> tuple[List[Issue], bool]:
        """Perform single health check"""
        self.logger.info("Performing health check...")

        try:
            # In production, would actually run tests and detect issues
            # For MVP, simulate detection
            test_state = self._get_app_state()
            issues = self.detector.detect_all_issues(test_state)

            # Categorize issues for alerts
            for issue in issues:
                if issue.severity in self.config.alert_on_severities:
                    self._create_alert_for_issue(issue)

            # Update stats
            self.stats.add_check(len(issues), issues)

            return issues, True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            alert = Alert(
                AlertLevel.CRITICAL,
                f"Health check failed: {str(e)}"
            )
            self.send_alert(alert)
            return [], False

    def _create_alert_for_issue(self, issue: Issue) -> None:
        """Create alert for detected issue"""
        if issue.severity == Severity.CRITICAL:
            level = AlertLevel.CRITICAL
            message = f"🔴 CRITICAL: {issue.description}"
        elif issue.severity == Severity.HIGH:
            level = AlertLevel.WARNING
            message = f"🟠 HIGH: {issue.description}"
        else:
            level = AlertLevel.INFO
            message = f"🟡 {issue.description}"

        alert = Alert(level, message, issue)
        self.send_alert(alert)

    def _get_app_state(self) -> Dict[str, Any]:
        """Get current app state (mock for MVP)"""
        return {
            "console_messages": [],
            "network_requests": [],
            "page_state": {},
            "page_metrics": {}
        }

    def start_monitoring(self) -> None:
        """Start continuous monitoring loop"""
        self.logger.info(f"Starting monitoring for {self.config.duration_seconds}s")
        self.logger.info(f"Check interval: {self.config.interval_seconds}s")

        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=self.config.duration_seconds)

        try:
            while datetime.now() < end_time:
                # Perform health check
                issues, success = self.check_health()

                if success:
                    emoji = "✅" if not issues else "⚠️"
                    print(f"{emoji} Check complete: {len(issues)} issues detected")

                # Calculate next check time
                time_remaining = (end_time - datetime.now()).total_seconds()
                sleep_time = min(self.config.interval_seconds, time_remaining)

                if time_remaining > 0:
                    self.logger.info(f"Next check in {sleep_time:.0f}s...")
                    time.sleep(sleep_time)
                else:
                    break

        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self._print_monitoring_summary()

    def _print_monitoring_summary(self) -> None:
        """Print monitoring summary"""
        stats = self.stats.get_summary()

        print(f"\n{'='*60}")
        print(f"MONITORING SUMMARY")
        print(f"{'='*60}")
        print(f"Duration: {stats['duration_seconds']:.0f}s")
        print(f"Checks Run: {stats['total_checks']}")
        print(f"Issues Detected: {stats['total_issues']}")
        print(f"Alerts Sent: {stats['total_alerts']}")
        print(f"Avg Interval: {stats['average_check_interval']:.1f}s")
        print(f"{'='*60}\n")


class TerminalAlertHandler:
    """Sends alerts to terminal"""

    @staticmethod
    def handle(alert: Alert) -> None:
        """Handle alert in terminal"""
        # Color codes
        colors = {
            AlertLevel.CRITICAL: "\033[91m",  # Red
            AlertLevel.WARNING: "\033[93m",   # Yellow
            AlertLevel.INFO: "\033[94m"       # Blue
        }
        reset = "\033[0m"

        color = colors.get(alert.level, "")
        timestamp = alert.timestamp.strftime("%H:%M:%S")

        print(f"{color}[{timestamp}] {alert.message}{reset}")


class SlackAlertHandler:
    """Sends alerts to Slack (requires webhook URL)"""

    def __init__(self, webhook_url: str):
        """Initialize Slack handler"""
        self.webhook_url = webhook_url

    def handle(self, alert: Alert) -> None:
        """Send alert to Slack"""
        # In production, would send via webhook
        # For MVP, just log intent
        print(f"[SLACK] Would send: {alert.message}")


class EmailAlertHandler:
    """Sends alerts via email"""

    def __init__(self, email_address: str):
        """Initialize email handler"""
        self.email_address = email_address

    def handle(self, alert: Alert) -> None:
        """Send alert via email"""
        # In production, would send email
        # For MVP, just log intent
        print(f"[EMAIL] Would send to {self.email_address}: {alert.message}")


def main():
    """Test monitoring"""
    # Create config
    config = MonitoringConfig(
        app_url="http://localhost:3001",
        interval_seconds=30,  # 30 seconds for testing
        duration_seconds=300,  # 5 minutes monitoring
        alert_on_severities=[Severity.CRITICAL, Severity.HIGH]
    )

    # Create monitor
    monitor = Monitor(config)

    # Register alert handlers
    monitor.register_alert_handler(TerminalAlertHandler.handle)

    # Start monitoring
    print(f"Monitoring {config.app_url}")
    print(f"Duration: {config.duration_seconds}s")
    print(f"Interval: {config.interval_seconds}s")
    print("Press Ctrl+C to stop\n")

    monitor.start_monitoring()


if __name__ == "__main__":
    main()
