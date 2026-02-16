#!/usr/bin/env python3
"""
Verification script for building-fastapi-apps skill.

Validates:
1. Skill structure (SKILL.md and references exist)
2. Reference file content (code blocks, proper formatting)
3. Official documentation links are valid
4. Topics coverage completeness
"""

import os
import re
import sys
from pathlib import Path

# ASCII-compatible symbols for Windows compatibility
CHECK = "[OK]"
CROSS = "[FAIL]"


def get_skill_root() -> Path:
    """Get the skill root directory."""
    return Path(__file__).parent.parent


def check_structure() -> tuple[bool, list[str]]:
    """Check that all required files exist."""
    root = get_skill_root()
    errors = []

    # Check SKILL.md
    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing SKILL.md")
    elif skill_md.stat().st_size < 1000:
        errors.append("SKILL.md seems too small (< 1KB)")

    # Check references directory
    refs_dir = root / "references"
    if not refs_dir.exists():
        errors.append("Missing references/ directory")
    else:
        # Expected reference files
        expected_refs = [
            "01-pydantic-models.md",
            "02-crud-operations.md",
            "03-error-handling.md",
            "04-dependency-injection.md",
            "05-environment-config.md",
            "06-database-integration.md",
            "07-user-management.md",
            "08-jwt-authentication.md",
            "09-middleware-patterns.md",
            "10-lifespan-events.md",
            "11-streaming-sse.md",
            "12-agent-integration.md",
            "13-pytest-testing.md",
        ]

        for ref in expected_refs:
            ref_path = refs_dir / ref
            if not ref_path.exists():
                errors.append(f"Missing reference: {ref}")
            elif ref_path.stat().st_size < 500:
                errors.append(f"Reference seems too small: {ref}")

    return len(errors) == 0, errors


def check_code_blocks(file_path: Path) -> tuple[bool, list[str]]:
    """Check that markdown files have proper code blocks."""
    errors = []
    content = file_path.read_text(encoding="utf-8")

    # Check for Python code blocks
    python_blocks = re.findall(r"```python\n(.*?)```", content, re.DOTALL)
    if not python_blocks:
        errors.append(f"{file_path.name}: No Python code blocks found")

    # Check for unclosed code blocks by counting all ``` markers
    # Every code block has opening ``` and closing ```, so total should be even
    all_fences = re.findall(r"^```", content, re.MULTILINE)
    if len(all_fences) % 2 != 0:
        errors.append(f"{file_path.name}: Unclosed code block detected")

    return len(errors) == 0, errors


def check_skill_md_sections() -> tuple[bool, list[str]]:
    """Check SKILL.md has required sections."""
    root = get_skill_root()
    skill_md = root / "SKILL.md"
    errors = []

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check for YAML frontmatter
    if not content.startswith("---"):
        errors.append("SKILL.md missing YAML frontmatter")

    # Check for required sections
    required_sections = [
        "Quick Start",
        "Core Patterns",
        "Decision Tree",
        "References",
    ]

    for section in required_sections:
        if section.lower() not in content.lower():
            errors.append(f"SKILL.md missing section: {section}")

    # Check for proper metadata
    if "name:" not in content:
        errors.append("SKILL.md missing name in frontmatter")
    if "description:" not in content:
        errors.append("SKILL.md missing description in frontmatter")

    return len(errors) == 0, errors


def check_topics_coverage() -> tuple[bool, list[str]]:
    """Check that all major topics are covered."""
    root = get_skill_root()
    refs_dir = root / "references"
    errors = []

    # Topics that must be mentioned in reference files
    required_topics = {
        "Pydantic": ["BaseModel", "Field", "validator"],
        "CRUD": ["GET", "POST", "PUT", "DELETE", "status_code"],
        "Error": ["HTTPException", "status", "404", "422"],
        "Dependency": ["Depends", "lru_cache", "yield"],
        "Settings": ["BaseSettings", ".env", "env_file"],
        "Database": ["SQLModel", "Session", "create_engine"],
        "Password": ["hash", "Argon2", "pwdlib"],
        "JWT": ["token", "OAuth2", "encode", "decode"],
        "Middleware": ["middleware", "CORS", "CORSMiddleware"],
        "Lifespan": ["lifespan", "asynccontextmanager", "app.state"],
        "SSE": ["EventSourceResponse", "yield", "stream"],
        "Agent": ["Agent", "function_tool", "Runner"],
        "Pytest": ["TestClient", "fixture", "pytest"],
    }

    if not refs_dir.exists():
        return False, ["References directory not found"]

    all_content = ""
    for ref_file in refs_dir.glob("*.md"):
        all_content += ref_file.read_text(encoding="utf-8")

    for topic, keywords in required_topics.items():
        found = False
        for keyword in keywords:
            if keyword in all_content:
                found = True
                break
        if not found:
            errors.append(f"Topic '{topic}' may be missing (keywords: {keywords})")

    return len(errors) == 0, errors


def check_doc_links() -> tuple[bool, list[str]]:
    """Check that official documentation links are present."""
    root = get_skill_root()
    errors = []

    # Required documentation references
    required_docs = [
        "fastapi.tiangolo.com",
        "docs.pydantic.dev",
        "sqlmodel.tiangolo.com",
    ]

    all_content = ""
    skill_md = root / "SKILL.md"
    if skill_md.exists():
        all_content += skill_md.read_text(encoding="utf-8")

    refs_dir = root / "references"
    if refs_dir.exists():
        for ref_file in refs_dir.glob("*.md"):
            all_content += ref_file.read_text(encoding="utf-8")

    for doc in required_docs:
        if doc not in all_content:
            errors.append(f"Missing official doc reference: {doc}")

    return len(errors) == 0, errors


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Building FastAPI Apps Skill - Verification")
    print("=" * 60)

    all_passed = True
    total_errors = []

    # Check 1: Structure
    print("\n[1/5] Checking skill structure...")
    passed, errors = check_structure()
    if passed:
        print(f"  {CHECK} All required files present")
    else:
        print(f"  {CROSS} Structure issues found:")
        for err in errors:
            print(f"    - {err}")
        all_passed = False
        total_errors.extend(errors)

    # Check 2: Code blocks
    print("\n[2/5] Checking code blocks...")
    root = get_skill_root()
    code_errors = []
    refs_dir = root / "references"
    if refs_dir.exists():
        for ref_file in refs_dir.glob("*.md"):
            _, errs = check_code_blocks(ref_file)
            code_errors.extend(errs)
    if not code_errors:
        print(f"  {CHECK} All code blocks properly formatted")
    else:
        print(f"  {CROSS} Code block issues found:")
        for err in code_errors:
            print(f"    - {err}")
        all_passed = False
        total_errors.extend(code_errors)

    # Check 3: SKILL.md sections
    print("\n[3/5] Checking SKILL.md structure...")
    passed, errors = check_skill_md_sections()
    if passed:
        print(f"  {CHECK} SKILL.md has required sections")
    else:
        print(f"  {CROSS} SKILL.md issues found:")
        for err in errors:
            print(f"    - {err}")
        all_passed = False
        total_errors.extend(errors)

    # Check 4: Topics coverage
    print("\n[4/5] Checking topics coverage...")
    passed, errors = check_topics_coverage()
    if passed:
        print(f"  {CHECK} All major topics covered")
    else:
        print(f"  {CROSS} Coverage gaps found:")
        for err in errors:
            print(f"    - {err}")
        all_passed = False
        total_errors.extend(errors)

    # Check 5: Documentation links
    print("\n[5/5] Checking documentation references...")
    passed, errors = check_doc_links()
    if passed:
        print(f"  {CHECK} Official documentation links present")
    else:
        print(f"  {CROSS} Missing documentation links:")
        for err in errors:
            print(f"    - {err}")
        all_passed = False
        total_errors.extend(errors)

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print(f"{CHECK} VERIFICATION PASSED - Skill is ready for use")
        print("=" * 60)
        return 0
    else:
        print(f"{CROSS} VERIFICATION FAILED - {len(total_errors)} issue(s) found")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
