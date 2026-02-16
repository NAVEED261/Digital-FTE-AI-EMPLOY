#!/usr/bin/env python3
"""
Practice Exercise Validator

Validates that practice exercises are completed correctly.
"""

import sys
import os
import subprocess
from typing import List


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def validate_dockerfile(exercise_path: str) -> bool:
    """Validate that Dockerfile exists and has required lines"""
    dockerfile = os.path.join(exercise_path, "Dockerfile")

    if not os.path.exists(dockerfile):
        print(f"  {Colors.RED}✗{Colors.END} Dockerfile not found at {dockerfile}")
        return False

    with open(dockerfile, 'r') as f:
        content = f.read()

    required = [
        ("FROM", "Base image specification"),
        ("WORKDIR", "Working directory setup"),
        ("COPY", "Copy files to container"),
    ]

    for keyword, description in required:
        if keyword not in content:
            print(f"  {Colors.RED}✗{Colors.END} Missing {keyword} instruction ({description})")
            return False

    print(f"  {Colors.GREEN}✓{Colors.END} Dockerfile valid")
    return True


def validate_exercise_01(exercise_path: str) -> bool:
    """Validate Exercise 01: Basic Dockerfile"""
    print(f"\n{Colors.BLUE}Validating Exercise 01: Basic Dockerfile{Colors.END}")
    return validate_dockerfile(exercise_path)


def validate_exercise_02(exercise_path: str) -> bool:
    """Validate Exercise 02: Multi-stage build"""
    print(f"\n{Colors.BLUE}Validating Exercise 02: Multi-stage Build{Colors.END}")

    dockerfile = os.path.join(exercise_path, "Dockerfile")
    if not os.path.exists(dockerfile):
        print(f"  {Colors.RED}✗{Colors.END} Dockerfile not found")
        return False

    with open(dockerfile, 'r') as f:
        content = f.read()

    # Check for multi-stage build
    if content.count("FROM ") < 2:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Not using multi-stage build (requires 2+ FROM statements)")
        return False

    # Check for COPY --from
    if "COPY --from=" not in content:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Not copying from first stage (use COPY --from=)")
        return False

    print(f"  {Colors.GREEN}✓{Colors.END} Multi-stage build detected")
    return True


def validate_exercise_03(exercise_path: str) -> bool:
    """Validate Exercise 03: Containerize Task API"""
    print(f"\n{Colors.BLUE}Validating Exercise 03: Containerize Task API{Colors.END}")

    # Check files exist
    files_required = ["Dockerfile", "main.py", "requirements.txt"]
    for file in files_required:
        filepath = os.path.join(exercise_path, file)
        if not os.path.exists(filepath):
            print(f"  {Colors.RED}✗{Colors.END} {file} not found")
            return False

    print(f"  {Colors.GREEN}✓{Colors.END} Required files present")

    # Try to build
    if try_build(exercise_path):
        print(f"  {Colors.GREEN}✓{Colors.END} Dockerfile builds successfully")
        return True
    else:
        print(f"  {Colors.RED}✗{Colors.END} Dockerfile build failed")
        return False


def validate_exercise_04(exercise_path: str) -> bool:
    """Validate Exercise 04: docker-compose with PostgreSQL"""
    print(f"\n{Colors.BLUE}Validating Exercise 04: docker-compose Multi-Container{Colors.END}")

    # Check files exist
    files_required = ["docker-compose.yml", "Dockerfile", "main.py", "requirements.txt"]
    for file in files_required:
        filepath = os.path.join(exercise_path, file)
        if not os.path.exists(filepath):
            print(f"  {Colors.RED}✗{Colors.END} {file} not found")
            return False

    print(f"  {Colors.GREEN}✓{Colors.END} Required files present")

    # Validate docker-compose.yml
    compose_file = os.path.join(exercise_path, "docker-compose.yml")
    with open(compose_file, 'r') as f:
        content = f.read()

    required_keys = ["services:", "api:", "db:", "volumes:"]
    for key in required_keys:
        if key not in content:
            print(f"  {Colors.RED}✗{Colors.END} docker-compose.yml missing '{key}'")
            return False

    print(f"  {Colors.GREEN}✓{Colors.END} docker-compose.yml valid")

    # Check for PostgreSQL service
    if "postgres" not in content.lower():
        print(f"  {Colors.YELLOW}⚠{Colors.END} PostgreSQL service not found in docker-compose.yml")

    return True


def try_build(exercise_path: str) -> bool:
    """Try to build a Docker image from the exercise"""
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "exercise:test", exercise_path],
            capture_output=True,
            timeout=60
        )
        return result.returncode == 0
    except Exception:
        return False


def validate_exercise(exercise_num: int, exercise_path: str) -> bool:
    """Route to appropriate validator"""
    validators = {
        1: validate_exercise_01,
        2: validate_exercise_02,
        3: validate_exercise_03,
        4: validate_exercise_04,
    }

    if exercise_num not in validators:
        print(f"{Colors.RED}Unknown exercise: {exercise_num}{Colors.END}")
        return False

    return validators[exercise_num](exercise_path)


def main():
    """Main validation"""
    if len(sys.argv) < 2:
        print("Usage: practice-validator.py <exercise_number_or_path>")
        print("Examples:")
        print("  python practice-validator.py 3")
        print("  python practice-validator.py 03-fastapi-container")
        sys.exit(1)

    arg = sys.argv[1]

    # Determine exercise number and path
    if arg.isdigit():
        exercise_num = int(arg)
        exercise_dir = f"{exercise_num:02d}-*"
    else:
        # Extract number from path like "03-fastapi-container"
        exercise_num = int(arg.split("-")[0])
        exercise_dir = arg

    # Find exercise directory
    skills_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exercises_path = os.path.join(skills_path, "assets", "practice-exercises")

    # Search for matching exercise
    import glob
    matching = glob.glob(os.path.join(exercises_path, exercise_dir))

    if not matching:
        print(f"{Colors.RED}Exercise directory not found{Colors.END}")
        print(f"Looking in: {exercises_path}")
        sys.exit(1)

    exercise_path = matching[0]

    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Exercise Validator{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    success = validate_exercise(exercise_num, exercise_path)

    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")

    if success:
        print(f"{Colors.GREEN}✅ Exercise {exercise_num:02d} validation passed!{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}❌ Exercise {exercise_num:02d} validation failed{Colors.END}")
        print(f"Address the issues above and try again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
