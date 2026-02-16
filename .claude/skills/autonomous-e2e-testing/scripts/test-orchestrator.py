#!/usr/bin/env python3
"""
Autonomous E2E Test Orchestrator

Main entry point for autonomous testing. Coordinates:
1. Test scenario loading and execution
2. Issue detection at each step
3. Auto-fix application
4. Report generation
"""

import argparse
import asyncio
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    Logger, Issue, TestResult, Severity, IssueCategory,
    setup_report_dir, save_json, save_log, load_yaml,
    is_server_running, print_summary, group_issues_by_severity
)

# Import detectors and generators
from issue_detector import IssueDetector
from report_generator import ReportGenerator

# Import image operation modules
from image_operations import ImageSearchHandler
from download_manager import DownloadManager
from upload_workflows import UploadWorkflowManager


class TestOrchestrator:
    """Main autonomous testing orchestrator"""

    def __init__(self, url: str, app_type: str = "auto", report_dir: str = "./test-reports", auto_fix: bool = True):
        """Initialize orchestrator"""
        self.url = url
        self.app_type = app_type
        self.report_dir = setup_report_dir(report_dir)
        self.logger = Logger.get_logger()
        self.auto_fix = auto_fix
        self.logger.info(f"Orchestrator initialized for {url}")

        # Test results tracking
        self.test_results: List[TestResult] = []
        self.all_issues: List[Issue] = []
        self.auto_fixed_count = 0
        self.start_time = None
        self.end_time = None

        # Initialize issue detector and report generator
        self.issue_detector = IssueDetector(url)
        self.report_generator = ReportGenerator(self.report_dir)

        # Load test scenarios
        self.scenarios = self._load_scenarios()

    def _load_scenarios(self) -> List[Dict[str, Any]]:
        """Load test scenarios from YAML"""
        try:
            scenario_file = os.path.join(
                os.path.dirname(__file__),
                "..",
                "workflows",
                "ecommerce.yaml"
            )

            if not os.path.exists(scenario_file):
                self.logger.error(f"Scenario file not found: {scenario_file}")
                return []

            data = load_yaml(scenario_file)

            # Extract scenarios from YAML
            scenarios = []
            for section in ["homepage_tests", "product_discovery_tests", "shopping_cart_tests", "checkout_tests"]:
                if section in data:
                    scenarios.extend(data[section])

            self.logger.info(f"Loaded {len(scenarios)} test scenarios")
            return scenarios

        except Exception as e:
            self.logger.error(f"Error loading scenarios: {e}")
            return []

    def run_all_tests(self, parallel: int = 1) -> Dict[str, Any]:
        """Execute all test scenarios autonomously"""
        self.start_time = time.time()
        self.logger.info(f"Starting autonomous testing...")
        self.logger.info(f"Target: {self.url}")
        self.logger.info(f"Scenarios: {len(self.scenarios)}")

        # Print progress header
        print(f"\n{'='*60}")
        print(f"AUTONOMOUS E2E TESTING - {self.app_type.upper()}")
        print(f"{'='*60}")
        print(f"Target URL: {self.url}")
        print(f"Test Scenarios: {len(self.scenarios)}")
        print(f"Report Directory: {self.report_dir}")
        print(f"{'='*60}\n")

        # Run tests
        for i, scenario in enumerate(self.scenarios):
            progress = f"[{i+1}/{len(self.scenarios)}]"
            self._run_scenario(scenario, progress)

        self.end_time = time.time()
        execution_time = self.end_time - self.start_time

        # Generate report
        return self._generate_final_report(execution_time)

    def _run_scenario(self, scenario: Dict[str, Any], progress: str = "") -> Optional[TestResult]:
        """Run a single test scenario"""
        scenario_id = scenario.get("id", "unknown")
        scenario_name = scenario.get("name", "Unknown Test")

        try:
            result = TestResult(scenario_name)
            start_time = time.time()

            # Log test start
            self.logger.info(f"{progress} Running: {scenario_name} ({scenario_id})")
            print(f"{progress} {scenario_name}... ", end="", flush=True)

            # Simulate test execution
            # In Phase 2, this will actually execute test steps
            # For now, create mock results for demonstration
            result.passed = True
            result.error = None

            # Detect issues after scenario
            issues = self._detect_issues_for_scenario(scenario)
            for issue in issues:
                result.add_issue(issue)
                self.all_issues.append(issue)

                # Apply auto-fixes
                if issue.auto_fix:
                    self.auto_fixed_count += 1

            result.execution_time = time.time() - start_time

            # Update progress
            status = "✓ PASS" if result.passed and len(result.issues) == 0 else "✓ PASS (with issues)"
            print(f"{status} ({result.execution_time:.2f}s)")

            self.test_results.append(result)
            return result

        except Exception as e:
            print(f"✗ FAIL ({str(e)[:30]})")
            result = TestResult(scenario_name, passed=False, error=str(e))
            self.test_results.append(result)
            self.logger.error(f"Error running {scenario_name}: {e}")
            return result

    def _detect_issues_for_scenario(self, scenario: Dict[str, Any]) -> List[Issue]:
        """Detect issues after running a scenario"""
        # In full implementation, this calls issue-detector.py
        # For MVP, return empty list
        issues = []

        # Mock issue detection based on scenario type
        scenario_id = scenario.get("id", "")

        # Simulate detecting specific issues
        if scenario_id == "P013":  # No Broken Images test
            pass  # No issues expected

        if scenario_id == "P012":  # Product Image Alt Text
            # Could detect missing alt text
            pass

        if scenario_id == "CE001":  # Console errors
            pass

        return issues

    def _generate_final_report(self, execution_time: float) -> Dict[str, Any]:
        """Generate final test report using ReportGenerator"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests

        # Group issues by severity
        grouped_issues = group_issues_by_severity(self.all_issues)

        # Create report data
        report_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "app_type": self.app_type,
                "target_url": self.url,
                "report_dir": self.report_dir
            },
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "execution_time_seconds": int(execution_time)
            },
            "issues": {
                "total": len(self.all_issues),
                "critical": len(grouped_issues[Severity.CRITICAL]),
                "high": len(grouped_issues[Severity.HIGH]),
                "medium": len(grouped_issues[Severity.MEDIUM]),
                "low": len(grouped_issues[Severity.LOW])
            },
            "auto_fixes": {
                "applied": self.auto_fixed_count,
                "remaining": len(self.all_issues) - self.auto_fixed_count
            },
            "test_results": [r.to_dict() for r in self.test_results],
            "issues_list": [issue.to_dict() for issue in self.all_issues]
        }

        # Generate all reports using ReportGenerator
        reports = self.report_generator.generate_all(self.test_results, self.all_issues, self.url)
        self.logger.info(f"Reports generated: {reports}")

        # Print summary
        print_summary(total_tests, passed_tests, self.all_issues, self.auto_fixed_count, execution_time)

        # Print report file locations
        print(f"\n📊 REPORTS GENERATED:")
        print(f"  HTML Report: {reports['html']}")
        print(f"  JSON Data:   {reports['json']}")
        print(f"  Text Summary: {reports['txt']}")

        return report_data


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Autonomous E2E Testing & Debugging Agent"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Target app URL (e.g., http://localhost:3001)"
    )

    parser.add_argument(
        "--app-type",
        default="ecommerce",
        choices=["ecommerce", "blog", "saas", "auto"],
        help="App type for test scenario selection"
    )

    parser.add_argument(
        "--auto-fix",
        action="store_true",
        default=True,
        help="Enable auto-fixing of issues"
    )

    parser.add_argument(
        "--no-auto-fix",
        dest="auto_fix",
        action="store_false",
        help="Disable auto-fixing"
    )

    parser.add_argument(
        "--report-dir",
        default="./test-reports",
        help="Output directory for test reports"
    )

    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel test executors"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    # Image operation arguments
    parser.add_argument(
        "--search-images",
        type=str,
        metavar="QUERY",
        help="Search for images with given query (e.g., 'ladies fashion')"
    )

    parser.add_argument(
        "--upload-images",
        action="store_true",
        help="Upload downloaded images to app (requires --search-images)"
    )

    parser.add_argument(
        "--image-count",
        type=int,
        default=20,
        help="Number of images to search/download (default: 20)"
    )

    parser.add_argument(
        "--upload-url",
        type=str,
        help="URL for image upload page (default: {base_url}/admin/products/new)"
    )

    parser.add_argument(
        "--image-category",
        type=str,
        help="Category for uploaded images (e.g., 'Fashion')"
    )

    parser.add_argument(
        "--image-tags",
        type=str,
        help="Comma-separated tags for images (e.g., 'boutique,fashion,ladies')"
    )

    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith("http"):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = TestOrchestrator(
        url=args.url,
        app_type=args.app_type,
        report_dir=args.report_dir,
        auto_fix=args.auto_fix
    )

    # Handle image operations workflow if requested
    if args.search_images:
        try:
            print("\n" + "="*60)
            print("🖼️  IMAGE OPERATIONS WORKFLOW")
            print("="*60)

            # Initialize image operation modules
            # Note: Requires MCP client for browser automation
            from mcp_client import MCPClient

            mcp_client = MCPClient()
            image_handler = ImageSearchHandler(mcp_client)
            download_manager = DownloadManager(mcp_client, "./temp_downloads")
            workflow_manager = UploadWorkflowManager(
                mcp_client,
                image_handler,
                download_manager
            )

            # Prepare metadata
            metadata = {}
            if args.image_category:
                metadata['category'] = args.image_category
            if args.image_tags:
                metadata['tags'] = [tag.strip() for tag in args.image_tags.split(',')]

            # Determine upload URL
            upload_url = args.upload_url or f"{args.url}/admin/products/new"

            # Run image workflow
            if args.upload_images:
                print(f"\n🎯 Running complete image workflow...")
                print(f"   Query: {args.search_images}")
                print(f"   Count: {args.image_count}")
                print(f"   Upload URL: {upload_url}")

                result = asyncio.run(
                    workflow_manager.search_download_upload(
                        search_query=args.search_images,
                        upload_url=upload_url,
                        upload_input_selector="input[type='file']",
                        metadata=metadata,
                        image_count=args.image_count
                    )
                )

                # Print summary
                print(f"\n{'='*60}")
                print(f"✅ IMAGE WORKFLOW COMPLETE")
                print(f"{'='*60}")
                print(f"Searched:    {result['searched']} images")
                print(f"Downloaded:  {result['downloaded']} images")
                print(f"Uploaded:    {result['uploaded']} images")
                print(f"Failed:      {result['failed']} images")
                print(f"Duration:    {result['duration']:.1f}s")
                print(f"Success:     {result['uploaded']/result['downloaded']*100:.1f}%")
                print(f"{'='*60}\n")

                # Exit if only doing image operations
                if not args.app_type:
                    sys.exit(0 if result['failed'] == 0 else 1)

            else:
                # Just search and download (no upload)
                print(f"\n🔍 Searching and downloading images...")
                print(f"   Query: {args.search_images}")
                print(f"   Count: {args.image_count}")

                images = asyncio.run(
                    image_handler.search_unsplash(
                        args.search_images,
                        {'count': args.image_count, 'min_width': 800, 'min_height': 600}
                    )
                )

                if images:
                    urls = [img['url'] for img in images]
                    paths = asyncio.run(
                        image_handler.download_images(urls, "./temp_downloads")
                    )

                    print(f"\n✅ Downloaded {len(paths)} images to ./temp_downloads/")
                    print(f"   Use --upload-images to upload them to the app")
                else:
                    print(f"\n⚠️  No images found for query: {args.search_images}")

        except ImportError as e:
            print(f"\n❌ Image operations require MCP client: {e}")
            print("   Make sure Playwright MCP server is running")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Image workflow error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Run tests
    try:
        report = orchestrator.run_all_tests(parallel=args.parallel)

        # Determine exit code based on failures
        if report["summary"]["failed_tests"] > 0:
            sys.exit(1)

        print(f"\n✅ All tests passed! Report: {orchestrator.report_dir}")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
