#!/usr/bin/env python3
"""
Dictionary Validator for Steno Dictionaries

Checks Plover dictionaries for conflicts, formatting errors, and optimization opportunities.
Usage: python validate-dictionary.py <dictionary_file> [--strict]

Options:
  --strict    Show all warnings including minor issues
  --output    Save report to file (report.txt)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


def load_dictionary(filepath):
    """Load a dictionary JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Dictionary file not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in dictionary: {e}")
        sys.exit(1)


def find_conflicts(dictionary):
    """Find entries that map to the same chord."""
    chord_map = defaultdict(list)

    for chord, word in dictionary.items():
        chord_map[chord].append(word)

    conflicts = {k: v for k, v in chord_map.items() if len(v) > 1}
    return conflicts


def find_duplicates(dictionary):
    """Find words that are mapped by multiple chords."""
    word_map = defaultdict(list)

    for chord, word in dictionary.items():
        word_map[word].append(chord)

    duplicates = {k: v for k, v in word_map.items() if len(v) > 1}
    return duplicates


def find_formatting_issues(dictionary):
    """Find formatting problems in dictionary entries."""
    issues = []

    for chord, word in dictionary.items():
        # Check chord format
        if not chord or not isinstance(chord, str):
            issues.append(f"Invalid chord: {chord!r}")

        # Check word format
        if not word or not isinstance(word, str):
            issues.append(f"Invalid word for {chord}: {word!r}")

        # Check for extra spaces
        if '  ' in word:
            issues.append(f"Extra spaces in '{chord}' -> '{word}'")

        # Check for empty strings
        if not word.strip():
            issues.append(f"Empty word for chord: {chord}")

    return issues


def find_inefficient_briefs(dictionary, strict=False):
    """Find briefs that could be optimized."""
    issues = []

    for chord, word in dictionary.items():
        # Check for excessive stroke briefs
        stroke_count = len(chord.split())
        word_length = len(word.split())

        if stroke_count > 3 and word_length <= 2:
            if strict or stroke_count > 5:
                issues.append(
                    f"Inefficient brief: '{chord}' ({stroke_count} strokes) -> '{word}' ({word_length} words)"
                )

        # Check for common words that should have shorter briefs
        if word in ['the', 'and', 'that', 'is', 'are', 'was'] and stroke_count > 1:
            if strict:
                issues.append(f"Common word '{word}' could use shorter brief: '{chord}'")

    return issues


def find_unused_entries(dictionary, min_length=50):
    """Find entries that might be rarely used."""
    candidates = []

    for chord, word in dictionary.items():
        # Very long chords for short words
        if len(chord) > 20 and len(word) < 10:
            candidates.append(f"Possible unused: '{chord}' -> '{word}'")

    return candidates[:min_length]  # Return top 50


def generate_report(filepath, dictionary, output_file=None, strict=False):
    """Generate a comprehensive validation report."""
    report = []

    # Header
    report.append("=" * 70)
    report.append(f"STENO DICTIONARY VALIDATION REPORT")
    report.append(f"Dictionary: {filepath}")
    report.append(f"Total Entries: {len(dictionary)}")
    report.append("=" * 70)

    # Conflicts
    conflicts = find_conflicts(dictionary)
    if conflicts:
        report.append(f"\n⚠ CONFLICTS FOUND ({len(conflicts)})")
        report.append("-" * 70)
        for chord, words in sorted(conflicts.items())[:10]:
            report.append(f"  Chord: '{chord}'")
            for word in words:
                report.append(f"    -> {word}")
        if len(conflicts) > 10:
            report.append(f"  ... and {len(conflicts) - 10} more conflicts")
    else:
        report.append("\n✓ No conflicts found")

    # Duplicates
    duplicates = find_duplicates(dictionary)
    if duplicates:
        report.append(f"\n⚠ DUPLICATE WORDS ({len(duplicates)})")
        report.append("-" * 70)
        for word, chords in sorted(duplicates.items())[:10]:
            report.append(f"  Word: '{word}'")
            for chord in chords:
                report.append(f"    <- {chord}")
        if len(duplicates) > 10:
            report.append(f"  ... and {len(duplicates) - 10} more duplicates")
    else:
        report.append("\n✓ No duplicate words found")

    # Formatting Issues
    formatting = find_formatting_issues(dictionary)
    if formatting:
        report.append(f"\n❌ FORMATTING ISSUES ({len(formatting)})")
        report.append("-" * 70)
        for issue in formatting[:10]:
            report.append(f"  {issue}")
        if len(formatting) > 10:
            report.append(f"  ... and {len(formatting) - 10} more issues")
    else:
        report.append("\n✓ No formatting issues found")

    # Inefficient Briefs
    inefficient = find_inefficient_briefs(dictionary, strict)
    if inefficient:
        report.append(f"\n⚡ OPTIMIZATION OPPORTUNITIES ({len(inefficient)})")
        report.append("-" * 70)
        for issue in inefficient[:10]:
            report.append(f"  {issue}")
        if len(inefficient) > 10:
            report.append(f"  ... and {len(inefficient) - 10} more opportunities")
    else:
        report.append("\n✓ Dictionary is well optimized")

    # Unused Entries
    unused = find_unused_entries(dictionary)
    if unused:
        report.append(f"\n🔍 POSSIBLE UNUSED ENTRIES (Sample of {len(unused)})")
        report.append("-" * 70)
        for entry in unused[:10]:
            report.append(f"  {entry}")
        if len(unused) > 10:
            report.append(f"  ... showing first {10} of {len(unused)}")

    # Summary
    report.append("\n" + "=" * 70)
    report.append("SUMMARY")
    report.append("=" * 70)
    total_issues = len(conflicts) + len(duplicates) + len(formatting) + len(inefficient)
    report.append(f"Total Issues Found: {total_issues}")

    if total_issues == 0:
        report.append("✓ Dictionary is in good condition!")
    else:
        report.append(f"⚠ Found {total_issues} issues that may need attention")

    report.append("\nRecommendations:")
    if conflicts:
        report.append("1. Resolve conflicts by reassigning chord priority")
    if duplicates:
        report.append("2. Consolidate duplicate words (keep most efficient brief)")
    if formatting:
        report.append("3. Fix formatting errors before court use")
    if inefficient:
        report.append("4. Optimize briefs for faster typing")

    # Output
    report_text = "\n".join(report)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report saved to: {output_file}")
    else:
        print(report_text)

    return report_text


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    filepath = sys.argv[1]
    strict = "--strict" in sys.argv
    output_file = None

    if "--output" in sys.argv:
        output_file = "dictionary_report.txt"

    # Load and validate
    dictionary = load_dictionary(filepath)
    generate_report(filepath, dictionary, output_file, strict)


if __name__ == "__main__":
    main()
