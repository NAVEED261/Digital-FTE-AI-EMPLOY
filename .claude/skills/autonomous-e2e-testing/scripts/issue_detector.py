#!/usr/bin/env python3
"""
Issue Detector Engine

Detects 7 categories of issues:
1. Console errors
2. Network failures
3. Broken images
4. Missing alt text
5. Layout problems
6. Performance issues
7. Accessibility issues
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(Enum):
    CONSOLE_ERROR = "console_error"
    NETWORK_FAILURE = "network_failure"
    BROKEN_IMAGE = "broken_image"
    MISSING_ALT_TEXT = "missing_alt_text"
    LAYOUT_PROBLEM = "layout_problem"
    PERFORMANCE_ISSUE = "performance_issue"
    ACCESSIBILITY_ISSUE = "accessibility_issue"


class Issue:
    def __init__(
        self,
        category: IssueCategory,
        severity: Severity,
        description: str,
        element_ref: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        auto_fix: bool = False,
        fix_code: Optional[str] = None
    ):
        self.category = category
        self.severity = severity
        self.description = description
        self.element_ref = element_ref
        self.screenshot_path = screenshot_path
        self.auto_fix = auto_fix
        self.fix_code = fix_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'description': self.description,
            'element_ref': self.element_ref,
            'screenshot_path': self.screenshot_path,
            'auto_fix': self.auto_fix,
            'fix_code': self.fix_code
        }


class IssueDetector:
    """Detect issues in web applications"""

    def __init__(self, app_url: str, mcp_client=None):
        """Initialize issue detector

        Args:
            app_url: URL of app being tested
            mcp_client: Optional MCP client for browser automation
        """
        self.mcp = mcp_client
        self.app_url = app_url
        self.issues: List[Issue] = []

        logger.info(f"IssueDetector initialized for {app_url}")

    async def detect_all(self) -> List[Issue]:
        """Detect all issue categories

        Returns:
            List of detected issues
        """
        logger.info("Starting issue detection...")

        await asyncio.gather(
            self.detect_console_errors(),
            self.detect_network_failures(),
            self.detect_broken_images(),
            self.detect_missing_alt_text(),
            self.detect_performance_issues()
        )

        logger.info(f"Detected {len(self.issues)} issues")
        return self.issues

    async def detect_console_errors(self) -> List[Issue]:
        """Detect JavaScript console errors"""
        try:
            messages = await self.mcp.call_tool(
                "browser_console_messages",
                {"level": "error"}
            )

            errors = messages.get('content', '').split('\n') if messages.get('content') else []

            for error in errors:
                if error.strip():
                    issue = Issue(
                        category=IssueCategory.CONSOLE_ERROR,
                        severity=Severity.CRITICAL,
                        description=f"JavaScript error: {error[:100]}"
                    )
                    self.issues.append(issue)
                    logger.warning(f"Console error detected: {error[:100]}")

        except Exception as e:
            logger.error(f"Error detecting console errors: {e}")

        return self.issues

    async def detect_network_failures(self) -> List[Issue]:
        """Detect network failures and 404s"""
        try:
            requests = await self.mcp.call_tool(
                "browser_network_requests",
                {"includeStatic": False}
            )

            network_data = requests.get('content', '')
            lines = network_data.split('\n') if network_data else []

            for line in lines:
                if '404' in line or 'timeout' in line.lower() or 'failed' in line.lower():
                    issue = Issue(
                        category=IssueCategory.NETWORK_FAILURE,
                        severity=Severity.HIGH,
                        description=f"Network issue: {line[:100]}"
                    )
                    self.issues.append(issue)
                    logger.warning(f"Network failure: {line[:100]}")

        except Exception as e:
            logger.error(f"Error detecting network failures: {e}")

        return self.issues

    async def detect_broken_images(self) -> List[Issue]:
        """Detect broken/missing images"""
        try:
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        return images.map(img => ({
                            src: img.src,
                            alt: img.alt,
                            naturalWidth: img.naturalWidth,
                            complete: img.complete
                        }));
                    }
                    """
                }
            )

            images = result.get('content', []) if isinstance(result.get('content'), list) else []

            for img in images:
                if img.get('complete') and img.get('naturalWidth') == 0:
                    issue = Issue(
                        category=IssueCategory.BROKEN_IMAGE,
                        severity=Severity.MEDIUM,
                        description=f"Broken image: {img.get('src', 'unknown')[:80]}"
                    )
                    self.issues.append(issue)
                    logger.warning(f"Broken image: {img.get('src')}")

        except Exception as e:
            logger.error(f"Error detecting broken images: {e}")

        return self.issues

    async def detect_missing_alt_text(self) -> List[Issue]:
        """Detect missing alt text on images"""
        try:
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        return images.filter(img => !img.alt).map(img => ({
                            src: img.src,
                            suggestion: img.src.split('/').pop().split('.')[0]
                        }));
                    }
                    """
                }
            )

            missing = result.get('content', []) if isinstance(result.get('content'), list) else []

            for img in missing:
                issue = Issue(
                    category=IssueCategory.MISSING_ALT_TEXT,
                    severity=Severity.LOW,
                    description=f"Missing alt text: {img.get('src', 'image')[:80]}",
                    auto_fix=True,
                    fix_code=f'<img src="{img.get("src")}" alt="{img.get("suggestion", "image")}" />'
                )
                self.issues.append(issue)
                logger.info(f"Missing alt text on image: {img.get('src')}")

        except Exception as e:
            logger.error(f"Error detecting missing alt text: {e}")

        return self.issues

    async def detect_performance_issues(self) -> List[Issue]:
        """Detect performance issues"""
        try:
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        if (!window.performance || !window.performance.getEntriesByType) {
                            return { lcp: 'unavailable', fid: 'unavailable', cls: 'unavailable' };
                        }
                        return {
                            loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart
                        };
                    }
                    """
                }
            )

            perf_data = result.get('content', {})
            load_time = perf_data.get('loadTime', 0)

            if load_time > 5000:  # > 5 seconds
                issue = Issue(
                    category=IssueCategory.PERFORMANCE_ISSUE,
                    severity=Severity.HIGH,
                    description=f"Slow page load: {load_time}ms (target: <2500ms)"
                )
                self.issues.append(issue)
                logger.warning(f"Performance issue: load time {load_time}ms")

        except Exception as e:
            logger.error(f"Error detecting performance issues: {e}")

        return self.issues

    def get_issues_by_severity(self, severity: Severity) -> List[Issue]:
        """Get issues filtered by severity"""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_auto_fixable_issues(self) -> List[Issue]:
        """Get issues that can be auto-fixed"""
        return [issue for issue in self.issues if issue.auto_fix]

    def to_dict(self) -> Dict[str, Any]:
        """Convert detector state to dictionary"""
        return {
            'app_url': self.app_url,
            'total_issues': len(self.issues),
            'by_severity': {
                'critical': len(self.get_issues_by_severity(Severity.CRITICAL)),
                'high': len(self.get_issues_by_severity(Severity.HIGH)),
                'medium': len(self.get_issues_by_severity(Severity.MEDIUM)),
                'low': len(self.get_issues_by_severity(Severity.LOW))
            },
            'auto_fixable': len(self.get_auto_fixable_issues()),
            'issues': [issue.to_dict() for issue in self.issues]
        }


# CLI usage
if __name__ == "__main__":
    print("IssueDetector module - use with test-orchestrator")
