#!/usr/bin/env python3
"""
Dockerfile Analyzer - Best Practices Checker

Analyzes a Dockerfile for best practices and provides recommendations.
"""

import sys
import re
from typing import List, Tuple, Optional


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DockerfileAnalyzer:
    """Analyzes Dockerfile for best practices"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lines = []
        self.issues = []
        self.warnings = []
        self.recommendations = []

        try:
            with open(filepath, 'r') as f:
                self.lines = f.readlines()
        except FileNotFoundError:
            print(f"{Colors.RED}Error: Dockerfile not found at {filepath}{Colors.END}")
            sys.exit(1)

    def analyze(self) -> None:
        """Run all analyses"""
        self.check_syntax_directive()
        self.check_base_image()
        self.check_user_directive()
        self.check_health_check()
        self.check_caching()
        self.check_layer_count()
        self.check_comments()
        self.check_multi_stage()
        self.check_size_optimization()

    def check_syntax_directive(self) -> None:
        """Check for syntax directive"""
        content = ''.join(self.lines)
        if not re.search(r'#\s*syntax=', content):
            self.recommendations.append(
                "Add syntax directive for better Dockerfile parsing: "
                "# syntax=docker/dockerfile:1"
            )

    def check_base_image(self) -> None:
        """Check base image choice"""
        for i, line in enumerate(self.lines, 1):
            if line.strip().startswith('FROM'):
                if 'latest' in line:
                    self.warnings.append(
                        f"Line {i}: Avoid using 'latest' tag, specify exact version"
                    )
                if line.strip().endswith('FROM python'):
                    self.recommendations.append(
                        f"Line {i}: Specify Python version, prefer python:3.x-slim"
                    )
                if 'ubuntu' in line.lower() or 'debian' in line.lower():
                    self.recommendations.append(
                        f"Line {i}: Consider using alpine or -slim image for smaller size"
                    )
                break

    def check_user_directive(self) -> None:
        """Check if running as non-root user"""
        content = ''.join(self.lines)
        if not re.search(r'USER\s+(?!root)', content, re.IGNORECASE):
            self.issues.append(
                "No non-root USER directive found. Security best practice: "
                "Create and use non-root user"
            )

    def check_health_check(self) -> None:
        """Check for health check"""
        content = ''.join(self.lines)
        if not re.search(r'HEALTHCHECK', content, re.IGNORECASE):
            self.recommendations.append(
                "No HEALTHCHECK directive found. Add health check for production: "
                "HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/"
            )

    def check_caching(self) -> None:
        """Check layer ordering for caching efficiency"""
        copy_before_run = False
        for i, line in enumerate(self.lines, 1):
            if 'COPY' in line.upper() and not 'requirements' in line.lower():
                copy_before_run = True
            if copy_before_run and 'RUN pip install' in line:
                self.warnings.append(
                    f"Line {i}: COPY appears before RUN pip install. "
                    "Move COPY after RUN install for better caching"
                )
                break

    def check_layer_count(self) -> None:
        """Check if we could reduce layers"""
        run_count = sum(1 for line in self.lines if line.strip().startswith('RUN'))
        if run_count > 5:
            self.recommendations.append(
                f"Many RUN commands ({run_count}). Consider combining with && to reduce layers"
            )

    def check_comments(self) -> None:
        """Check for documentation"""
        comment_count = sum(1 for line in self.lines if line.strip().startswith('#'))
        if comment_count < 2:
            self.recommendations.append(
                "Add comments to document what each section does"
            )

    def check_multi_stage(self) -> None:
        """Check if using multi-stage builds"""
        content = ''.join(self.lines)
        from_count = content.count('FROM ')
        if from_count == 1:
            # Check if we should suggest multi-stage
            if 'pip install' in content.lower():
                self.recommendations.append(
                    "Consider using multi-stage builds to reduce final image size"
                )

    def check_size_optimization(self) -> None:
        """Check for size optimization practices"""
        content = ''.join(self.lines)

        # Check for apt cleanup
        if 'apt-get install' in content and 'rm -rf /var/lib/apt/lists' not in content:
            self.warnings.append(
                "apt-get used but not cleaned up. Add: && rm -rf /var/lib/apt/lists/*"
            )

        # Check for pip cache
        if 'pip install' in content and '--no-cache-dir' not in content:
            self.warnings.append(
                "pip install found but not using --no-cache-dir. "
                "Add flag to reduce image size"
            )

        # Check for .dockerignore
        # Note: we can't check for .dockerignore directly, but we can recommend it
        self.recommendations.append(
            "Ensure you have a .dockerignore file to exclude unnecessary files"
        )

    def print_report(self) -> None:
        """Print analysis report"""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}Dockerfile Analysis Report{Colors.END}")
        print(f"{Colors.BLUE}{self.filepath}{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

        # Issues (Critical)
        if self.issues:
            print(f"{Colors.RED}❌ CRITICAL ISSUES ({len(self.issues)}){Colors.END}")
            for issue in self.issues:
                print(f"  • {issue}")
            print()

        # Warnings
        if self.warnings:
            print(f"{Colors.YELLOW}⚠️  WARNINGS ({len(self.warnings)}){Colors.END}")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        # Recommendations
        if self.recommendations:
            print(f"{Colors.BLUE}💡 RECOMMENDATIONS ({len(self.recommendations)}){Colors.END}")
            for rec in self.recommendations:
                print(f"  • {rec}")
            print()

        # Summary
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        total = len(self.issues) + len(self.warnings) + len(self.recommendations)
        print(f"Total findings: {total}")

        if self.issues:
            print(f"{Colors.RED}Critical issues: {len(self.issues)}{Colors.END}")
        if self.warnings:
            print(f"{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.END}")
        if self.recommendations:
            print(f"{Colors.BLUE}Recommendations: {len(self.recommendations)}{Colors.END}")

        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

        return 0 if not self.issues else 1


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: dockerfile-analyzer.py <Dockerfile>")
        print("Example: dockerfile-analyzer.py Dockerfile")
        sys.exit(1)

    filepath = sys.argv[1]
    analyzer = DockerfileAnalyzer(filepath)
    analyzer.analyze()
    exit_code = analyzer.print_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
