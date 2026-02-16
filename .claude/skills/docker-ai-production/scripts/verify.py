#!/usr/bin/env python3
"""
Verification script for docker-ai-production skill
Checks: Docker, NVIDIA runtime, UV, skill structure
"""

import subprocess
import sys
import os
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_check(message, success, details=""):
    symbol = "✓" if success else "✗"
    color = Colors.GREEN if success else Colors.RED
    status_line = f"{color}{symbol}{Colors.END} {message}"
    if details:
        status_line += f" ({details})"
    print(status_line)
    return success


def run_command(cmd, capture=True):
    """Run command and return (success, output)"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture, text=True, timeout=5
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def check_docker():
    """Check Docker installation and daemon"""
    print(f"\n{Colors.BLUE}Checking Docker...{Colors.END}")

    # Check docker installed
    success, output = run_command("docker --version")
    version = output.split()[-1] if success and output else "not found"
    if not print_check("Docker installed", success, version):
        return False

    # Check daemon running
    success, _ = run_command("docker ps")
    if not print_check("Docker daemon running", success):
        return False

    return True


def check_nvidia():
    """Check NVIDIA runtime and GPU"""
    print(f"\n{Colors.BLUE}Checking NVIDIA Runtime...{Colors.END}")

    # Check nvidia-ctk
    success, version = run_command("nvidia-ctk --version")
    version = version.split()[-1] if success and version else "not found"
    if not print_check("NVIDIA Container Toolkit", success, version):
        return False

    # Check Docker knows about nvidia runtime
    success, output = run_command("docker info | grep -i nvidia")
    if not print_check("Docker nvidia runtime registered", success):
        print(f"  {Colors.YELLOW}Hint: Run 'nvidia-ctk runtime configure --runtime=docker'{Colors.END}")
        return False

    # Test GPU access
    success, output = run_command("docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi")
    gpu_available = success and "NVIDIA-SMI" in output
    if not print_check("GPU accessible in container", gpu_available):
        print(f"  {Colors.YELLOW}Hint: Install NVIDIA drivers and restart Docker{Colors.END}")
        return False

    return True


def check_uv():
    """Check UV package manager"""
    print(f"\n{Colors.BLUE}Checking UV...{Colors.END}")

    success, version = run_command("uv --version")
    version = version.split()[0] if success and version else "not found"
    if not print_check("UV installed", success, version):
        print(f"  {Colors.YELLOW}Hint: curl -LsSf https://astral.sh/uv/install.sh | sh{Colors.END}")
        return False

    return True


def check_skill_structure():
    """Check skill directory structure"""
    print(f"\n{Colors.BLUE}Checking Skill Structure...{Colors.END}")

    base_dir = Path(__file__).parent.parent
    checks = [
        ("SKILL.md", base_dir / "SKILL.md"),
        ("gpu-runtime reference", base_dir / "references" / "gpu-runtime.md"),
        ("model-optimization reference", base_dir / "references" / "model-optimization.md"),
        ("inference-patterns reference", base_dir / "references" / "inference-patterns.md"),
        ("uv-integration reference", base_dir / "references" / "uv-integration.md"),
        ("production-security reference", base_dir / "references" / "production-security-ai.md"),
        ("troubleshooting reference", base_dir / "references" / "troubleshooting-ai.md"),
        ("scripts directory", base_dir / "scripts"),
    ]

    all_exist = True
    for name, path in checks:
        exists = path.exists()
        all_exist = all_exist and exists
        print_check(name, exists, f"{path.relative_to(base_dir)}")

    return all_exist


def main():
    print(f"\n{Colors.BLUE}=== docker-ai-production Skill Verification ==={Colors.END}\n")

    checks = [
        ("Docker", check_docker),
        ("NVIDIA Runtime", check_nvidia),
        ("UV", check_uv),
        ("Skill Structure", check_skill_structure),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n{Colors.RED}Error checking {name}: {e}{Colors.END}")
            results.append((name, False))

    # Summary
    print(f"\n{Colors.BLUE}=== Summary ==={Colors.END}")
    all_passed = all(result for _, result in results)
    for name, result in results:
        symbol = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{symbol} {name}")

    if all_passed:
        print(f"\n{Colors.GREEN}✓ Ready for AI containerization!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}✗ Some checks failed. See errors above.{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
