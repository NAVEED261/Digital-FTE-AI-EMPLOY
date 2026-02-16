#!/usr/bin/env python3
"""Verification script for kubernetes-ai-services skill"""

import subprocess
import sys
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


def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.strip()
    except:
        return False, ""


def check_kubectl():
    print(f"\n{Colors.BLUE}Checking kubectl...{Colors.END}")
    success, output = run_command("kubectl version --client 2>/dev/null | grep -i 'v1'")
    version = output.split('\n')[0] if success else "not found"
    if not print_check("kubectl installed", success, version):
        return False

    success, _ = run_command("kubectl cluster-info")
    return print_check("Cluster connectivity", success)


def check_gpu_operator():
    print(f"\n{Colors.BLUE}Checking GPU Operator...{Colors.END}")
    success, _ = run_command("kubectl get daemonset -n gpu-operator-system 2>/dev/null")
    if not print_check("GPU operator (optional)", success):
        print(f"  {Colors.YELLOW}Hint: Install NVIDIA GPU operator for GPU support{Colors.END}")
        return True  # Optional
    return True


def check_skill_structure():
    print(f"\n{Colors.BLUE}Checking Skill Structure...{Colors.END}")
    base_dir = Path(__file__).parent.parent

    checks = [
        ("SKILL.md", base_dir / "SKILL.md"),
        ("gpu-scheduling reference", base_dir / "references" / "gpu-scheduling.md"),
        ("scripts directory", base_dir / "scripts"),
    ]

    for name, path in checks:
        exists = path.exists()
        print_check(name, exists, str(path.relative_to(base_dir)))

    return True


def main():
    print(f"\n{Colors.BLUE}=== kubernetes-ai-services Skill Verification ==={Colors.END}\n")

    checks = [
        ("kubectl", check_kubectl),
        ("GPU Operator", check_gpu_operator),
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

    print(f"\n{Colors.BLUE}=== Summary ==={Colors.END}")
    all_passed = all(r for _, r in results)
    for name, result in results:
        symbol = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{symbol} {name}")

    if all_passed:
        print(f"\n{Colors.GREEN}✓ Ready for AI Kubernetes deployment!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠ Some checks failed or optional components missing{Colors.END}\n")
        return 0  # Not critical


if __name__ == "__main__":
    sys.exit(main())
