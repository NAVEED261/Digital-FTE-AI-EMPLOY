#!/usr/bin/env python3
"""
Docker Installation Verification Script

Verifies that Docker, docker-compose, and WSL 2 are properly installed and configured.
"""

import subprocess
import sys
import re
from typing import Tuple, Optional


class Colors:
    """ANSI color codes for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_check(status: bool, message: str, details: str = "") -> None:
    """Print a check result"""
    symbol = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"{symbol} {message}")
    if details:
        print(f"  {details}")


def run_command(cmd: list) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_docker() -> bool:
    """Check if Docker is installed and running"""
    print(f"\n{Colors.BLUE}Checking Docker Installation...{Colors.END}")

    # Check docker binary
    success, output = run_command(["docker", "--version"])
    if not success:
        print_check(False, "Docker not installed or not in PATH")
        return False

    # Parse version
    match = re.search(r"Docker version ([\d.]+)", output)
    version = match.group(1) if match else "unknown"
    print_check(success, f"Docker installed", f"version {version}")

    # Check daemon
    success, output = run_command(["docker", "ps"])
    if not success:
        print_check(False, "Docker daemon not running", "Start Docker Desktop")
        return False

    print_check(True, "Docker daemon running")
    return True


def check_compose() -> bool:
    """Check if docker-compose is installed"""
    print(f"\n{Colors.BLUE}Checking Docker Compose...{Colors.END}")

    success, output = run_command(["docker-compose", "--version"])
    if not success:
        print_check(False, "docker-compose not installed")
        return False

    # Parse version
    match = re.search(r"Docker Compose version ([\d.]+)", output)
    version = match.group(1) if match else "unknown"
    print_check(success, f"docker-compose installed", f"version {version}")

    return True


def check_wsl2() -> bool:
    """Check if WSL 2 is enabled (Windows only)"""
    print(f"\n{Colors.BLUE}Checking WSL 2...{Colors.END}")

    success, output = run_command(["wsl", "--version"])
    if not success:
        # WSL command not available, might not be Windows or WSL not installed
        print_check(False, "WSL not available (or not on Windows)", "This is OK if not on Windows")
        return True  # Don't fail on non-Windows systems

    # Check WSL version
    if "WSL version: 2" in output or "2." in output.split("\n")[0]:
        print_check(True, "WSL 2 enabled")
        return True
    else:
        print_check(False, "WSL 2 not enabled, WSL 1 in use", "Run: wsl --set-default-version 2")
        return False


def check_container_runtime() -> bool:
    """Check if we can actually run containers"""
    print(f"\n{Colors.BLUE}Checking Container Runtime...{Colors.END}")

    success, output = run_command(["docker", "run", "--rm", "hello-world"])
    if not success:
        print_check(False, "Cannot run containers", "Check Docker daemon")
        return False

    print_check(True, "Container runtime working")
    return True


def check_file_access() -> bool:
    """Check if Docker can access project files"""
    print(f"\n{Colors.BLUE}Checking File Access...{Colors.END}")

    # Try to run a container that accesses the current directory
    success, output = run_command([
        "docker",
        "run",
        "--rm",
        "-v", "$(pwd):/workspace",
        "busybox",
        "ls",
        "/workspace"
    ])

    if not success:
        print_check(False, "Docker cannot access project files", "Check Docker Desktop file sharing settings")
        return False

    print_check(True, "File access configured")
    return True


def main() -> int:
    """Run all checks"""
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Docker Installation Verification{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    checks = [
        ("Docker Installation", check_docker),
        ("Docker Compose", check_compose),
        ("WSL 2 (Windows)", check_wsl2),
        ("Container Runtime", check_container_runtime),
        ("File Access", check_file_access),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_check(False, f"{name}: {e}")
            results.append((name, False))

    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    all_passed = all(result for _, result in results)

    for name, result in results:
        status = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {name}")

    print()

    if all_passed:
        print(f"{Colors.GREEN}✅ Docker installation verified successfully!{Colors.END}")
        print("\nYou're ready to start learning Docker!")
        print("Next steps:")
        print("1. Read: references/phase1-foundation.md")
        print("2. Start: docker-learning-tutor agent")
        print("3. Build: Your first Docker container")
        return 0
    else:
        print(f"{Colors.RED}❌ Some checks failed. Please address the issues above.{Colors.END}")
        print("\nCommon solutions:")
        print("- Docker Desktop not running? Open the Docker Desktop app")
        print("- WSL 2 not enabled? Run: wsl --install and wsl --set-default-version 2")
        print("- File sharing not configured? Open Docker Desktop Settings → Resources → File Sharing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
