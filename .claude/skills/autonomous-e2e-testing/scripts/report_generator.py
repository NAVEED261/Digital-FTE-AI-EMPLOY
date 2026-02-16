#!/usr/bin/env python3
"""
Report Generator

Creates beautiful HTML reports with test results, issues, and fixes.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate test reports"""

    def __init__(self, report_dir: str):
        """Initialize report generator

        Args:
            report_dir: Directory to save reports
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ReportGenerator initialized for {report_dir}")

    def generate(
        self,
        test_results: Dict[str, Any],
        issues: List[Dict[str, Any]],
        auto_fixes_applied: List[Dict[str, Any]],
        duration: float
    ) -> str:
        """Generate HTML report

        Args:
            test_results: Test execution results
            issues: List of detected issues
            auto_fixes_applied: List of auto-fixes applied
            duration: Test execution duration in seconds

        Returns:
            Path to generated HTML file
        """
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        report_path = self.report_dir / f"report-{timestamp}.html"

        # Count issues by severity
        critical = len([i for i in issues if i.get('severity') == 'critical'])
        high = len([i for i in issues if i.get('severity') == 'high'])
        medium = len([i for i in issues if i.get('severity') == 'medium'])
        low = len([i for i in issues if i.get('severity') == 'low'])

        # Generate HTML
        html = self._generate_html(
            test_results,
            issues,
            auto_fixes_applied,
            duration,
            critical,
            high,
            medium,
            low,
            timestamp
        )

        # Write report
        with open(report_path, 'w') as f:
            f.write(html)

        logger.info(f"Report generated: {report_path}")

        # Also save JSON data
        self.save_json_report(
            report_path.parent / f"data-{timestamp}.json",
            {
                'timestamp': timestamp,
                'test_results': test_results,
                'issues': issues,
                'auto_fixes': auto_fixes_applied,
                'duration': duration,
                'summary': {
                    'critical': critical,
                    'high': high,
                    'medium': medium,
                    'low': low,
                    'total_issues': len(issues),
                    'auto_fixes_applied': len(auto_fixes_applied)
                }
            }
        )

        return str(report_path)

    def _generate_html(
        self,
        test_results: Dict[str, Any],
        issues: List[Dict[str, Any]],
        auto_fixes: List[Dict[str, Any]],
        duration: float,
        critical: int,
        high: int,
        medium: int,
        low: int,
        timestamp: str
    ) -> str:
        """Generate HTML content

        Args:
            All parameters for report generation

        Returns:
            HTML string
        """
        total_issues = len(issues)
        total_tests = test_results.get('total', 0)
        passed_tests = test_results.get('passed', 0)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Severity colors
        severity_colors = {
            'critical': '#dc2626',
            'high': '#ea580c',
            'medium': '#eab308',
            'low': '#22c55e'
        }

        # Build issues HTML
        issues_html = self._build_issues_html(issues, severity_colors)

        # Build fixes HTML
        fixes_html = self._build_fixes_html(auto_fixes)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .timestamp {{
            opacity: 0.9;
            font-size: 0.9em;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            text-align: center;
        }}

        .summary-card.pass {{
            border-left-color: #22c55e;
        }}

        .summary-card.critical {{
            border-left-color: #dc2626;
        }}

        .summary-card.high {{
            border-left-color: #ea580c;
        }}

        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}

        .summary-card.critical .value {{
            color: #dc2626;
        }}

        .summary-card.high .value {{
            color: #ea580c;
        }}

        .summary-card.pass .value {{
            color: #22c55e;
        }}

        section {{
            padding: 40px;
            border-top: 1px solid #eee;
        }}

        h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}

        .issues-list {{
            space-y: 20px;
        }}

        .issue {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }}

        .issue.critical {{
            border-left-color: #dc2626;
            background: #fef2f2;
        }}

        .issue.high {{
            border-left-color: #ea580c;
            background: #fff7ed;
        }}

        .issue.medium {{
            border-left-color: #eab308;
            background: #fefce8;
        }}

        .issue.low {{
            border-left-color: #22c55e;
            background: #f0fdf4;
        }}

        .issue-header {{
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }}

        .severity-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
            text-transform: uppercase;
        }}

        .severity-badge.critical {{ background: #dc2626; }}
        .severity-badge.high {{ background: #ea580c; }}
        .severity-badge.medium {{ background: #eab308; color: #333; }}
        .severity-badge.low {{ background: #22c55e; }}

        .issue-description {{
            color: #666;
            margin-bottom: 10px;
        }}

        .issue-category {{
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .fix-section {{
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}

        .fix-section h3 {{
            color: #22c55e;
            margin-bottom: 10px;
            font-size: 0.95em;
        }}

        code {{
            background: #333;
            color: #0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}

        footer {{
            padding: 20px 40px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }}

        .duration {{
            font-weight: bold;
            color: #667eea;
        }}

        .no-issues {{
            text-align: center;
            padding: 40px;
            color: #22c55e;
        }}

        .no-issues h3 {{
            font-size: 1.5em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧪 Test Report</h1>
            <p class="timestamp">Generated: {timestamp}</p>
        </header>

        <div class="summary">
            <div class="summary-card pass">
                <h3>Pass Rate</h3>
                <div class="value">{pass_rate:.0f}%</div>
            </div>
            <div class="summary-card critical">
                <h3>Critical Issues</h3>
                <div class="value">{critical}</div>
            </div>
            <div class="summary-card high">
                <h3>High Priority</h3>
                <div class="value">{high}</div>
            </div>
            <div class="summary-card">
                <h3>Medium Priority</h3>
                <div class="value">{medium}</div>
            </div>
            <div class="summary-card">
                <h3>Low Priority</h3>
                <div class="value">{low}</div>
            </div>
            <div class="summary-card">
                <h3>Tests Run</h3>
                <div class="value">{total_tests}</div>
            </div>
        </div>

        <section>
            <h2>🔍 Issues Detected</h2>
            {issues_html}
        </section>

        <section>
            <h2>✅ Auto-Fixes Applied</h2>
            {fixes_html}
        </section>

        <footer>
            <p>Test completed in <span class="duration">{duration:.1f}s</span></p>
        </footer>
    </div>
</body>
</html>"""

        return html

    def _build_issues_html(self, issues: List[Dict[str, Any]], colors: Dict[str, str]) -> str:
        """Build issues HTML"""
        if not issues:
            return '<div class="no-issues"><h3>✨ No issues found!</h3><p>Great job!</p></div>'

        html = '<div class="issues-list">'

        for issue in issues:
            severity = issue.get('severity', 'low')
            category = issue.get('category', 'unknown')
            description = issue.get('description', 'Unknown issue')

            html += f"""
            <div class="issue {severity}">
                <div class="issue-header">
                    <span class="severity-badge {severity}">{severity}</span>
                    <span class="issue-category">{category}</span>
                </div>
                <div class="issue-description">{description}</div>
            </div>
            """

        html += '</div>'
        return html

    def _build_fixes_html(self, fixes: List[Dict[str, Any]]) -> str:
        """Build fixes HTML"""
        if not fixes:
            return '<p>No auto-fixes applied in this run.</p>'

        html = '<div class="issues-list">'

        for fix in fixes:
            description = fix.get('description', 'Unknown fix')
            code = fix.get('code', '')

            fix_code = f'<code>{code}</code>' if code else ''

            html += f"""
            <div class="issue low">
                <div class="issue-header">
                    <span class="severity-badge low">✓ Fixed</span>
                </div>
                <div class="issue-description">{description}</div>
                {f'<div class="fix-section"><h3>Applied Fix:</h3>{fix_code}</div>' if code else ''}
            </div>
            """

        html += '</div>'
        return html

    def save_json_report(self, filepath: str, data: Dict[str, Any]) -> None:
        """Save JSON report

        Args:
            filepath: Path to save JSON
            data: Data to save
        """
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"JSON report saved: {filepath}")

    def save_log(self, filepath: str, content: str) -> None:
        """Save log file

        Args:
            filepath: Path to save log
            content: Log content
        """
        with open(filepath, 'w') as f:
            f.write(content)

        logger.info(f"Log saved: {filepath}")

    def generate_all(self, test_results, issues, app_url: str) -> Dict[str, str]:
        """Generate all reports (HTML, JSON, logs)

        Args:
            test_results: Test execution results (dict or list)
            issues: List of detected issues
            app_url: URL of app being tested

        Returns:
            Dictionary with paths to generated reports
        """
        # Handle both dict and list formats
        if isinstance(test_results, list):
            total_tests = len(test_results)
            passed_tests = sum(1 for r in test_results if isinstance(r, dict) and r.get('status') == 'passed')
            duration = 0
        else:
            total_tests = test_results.get('total', 0)
            passed_tests = test_results.get('passed', 0)
            duration = test_results.get('duration', 0)

        # Separate auto-fixable issues
        auto_fixes = []
        if isinstance(issues, list):
            auto_fixes = [i for i in issues if isinstance(i, dict) and i.get('auto_fix', False)]

        # Generate HTML report
        html_path = self.generate(
            test_results={'total': total_tests, 'passed': passed_tests},
            issues=issues if isinstance(issues, list) else [],
            auto_fixes_applied=auto_fixes,
            duration=duration
        )

        return {
            'html': html_path,
            'report_dir': str(self.report_dir)
        }


# CLI usage
if __name__ == "__main__":
    print("ReportGenerator module - use with test-orchestrator")
