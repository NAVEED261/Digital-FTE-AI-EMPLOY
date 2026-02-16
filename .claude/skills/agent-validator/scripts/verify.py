#!/usr/bin/env python3
"""
Verification script for agent-validator skill installation.
Checks that all required files are present and properly formatted.
"""

import os
import sys
from pathlib import Path
import yaml


def verify_agent_validator_skill():
    """Verify agent-validator skill is properly installed."""

    skill_dir = Path(__file__).parent.parent
    errors = []
    warnings = []

    print("Verifying agent-validator skill installation...\n")

    # Check 1: SKILL.md exists and has frontmatter
    print("✓ Checking SKILL.md...")
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.exists():
        errors.append("SKILL.md not found")
    else:
        content = skill_file.read_text()

        # Check frontmatter
        if not content.startswith("---"):
            errors.append("SKILL.md missing YAML frontmatter")
        else:
            # Parse frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                errors.append("SKILL.md frontmatter malformed")
            else:
                try:
                    frontmatter = yaml.safe_load(parts[1])

                    # Check required fields
                    if not frontmatter.get("name"):
                        errors.append("SKILL.md frontmatter missing 'name'")
                    elif frontmatter["name"] != "agent-validator":
                        errors.append(f"Skill name mismatch: {frontmatter['name']} != agent-validator")

                    if not frontmatter.get("description"):
                        errors.append("SKILL.md frontmatter missing 'description'")

                    print(f"  - Name: {frontmatter.get('name', 'N/A')} ✓")
                    print(f"  - Description: {frontmatter.get('description', 'N/A')[:60]}... ✓")

                except yaml.YAMLError as e:
                    errors.append(f"SKILL.md frontmatter YAML error: {e}")

        # Check file size
        lines = content.split("\n")
        line_count = len(lines)
        if line_count < 50:
            warnings.append(f"SKILL.md is quite short ({line_count} lines)")
        elif line_count > 600:
            errors.append(f"SKILL.md too large ({line_count} lines, should be <500)")
        else:
            print(f"  - Line count: {line_count} ✓")

    # Check 2: References directory and files
    print("\n✓ Checking references/...")
    references_dir = skill_dir / "references"

    if not references_dir.exists():
        errors.append("references/ directory not found")
    else:
        required_files = [
            "detailed-criteria.md",
            "agent-patterns.md",
            "scoring-examples.md",
            "improvement-patterns.md"
        ]

        for ref_file in required_files:
            ref_path = references_dir / ref_file
            if not ref_path.exists():
                errors.append(f"references/{ref_file} not found")
            else:
                lines = ref_path.read_text().split("\n")
                print(f"  - {ref_file} ({len(lines)} lines) ✓")

        # Check for unexpected files
        for item in references_dir.iterdir():
            if item.is_file() and item.name not in required_files:
                warnings.append(f"Unexpected file in references/: {item.name}")

    # Check 3: Scripts directory
    print("\n✓ Checking scripts/...")
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.exists():
        errors.append("scripts/ directory not found")
    else:
        verify_py = scripts_dir / "verify.py"
        if not verify_py.exists():
            errors.append("scripts/verify.py not found")
        else:
            print(f"  - verify.py ✓")

    # Summary
    print("\n" + "="*60)

    if errors:
        print(f"\n❌ {len(errors)} error(s) found:\n")
        for error in errors:
            print(f"  • {error}")
        return False
    else:
        print("\n✅ All checks passed!")

        if warnings:
            print(f"\n⚠️  {len(warnings)} warning(s):\n")
            for warning in warnings:
                print(f"  • {warning}")

        return True


if __name__ == "__main__":
    success = verify_agent_validator_skill()
    sys.exit(0 if success else 1)
