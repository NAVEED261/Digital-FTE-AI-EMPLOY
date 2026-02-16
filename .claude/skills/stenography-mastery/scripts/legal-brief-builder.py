#!/usr/bin/env python3
"""
Legal Brief Builder for Court Stenography

Analyzes court transcripts to identify frequently-used phrases and suggests briefs.
Usage: python legal-brief-builder.py <transcript_file> [--min-frequency N]

Options:
  --min-frequency N   Minimum occurrences to suggest (default: 5)
  --output           Save suggestions to file (briefs.json)
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter


def load_transcript(filepath):
    """Load a court transcript file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Transcript file not found: {filepath}")
        sys.exit(1)


def extract_phrases(text, min_words=1, max_words=5):
    """Extract common phrases from transcript."""
    # Clean text: remove speaker labels, timestamps
    text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed content
    text = re.sub(r'\(.*?\)', '', text)  # Remove parenthetical content
    text = re.sub(r'MR\.|MS\.|DR\.|JUDGE|WITNESS|ATTORNEY', '', text)  # Remove titles

    # Split into words
    words = text.lower().split()

    # Extract phrases of various lengths
    phrases = []

    for length in range(min_words, max_words + 1):
        for i in range(len(words) - length + 1):
            phrase = ' '.join(words[i:i + length])
            # Filter out common non-legal words
            if not is_filler_phrase(phrase):
                phrases.append(phrase)

    return phrases


def is_filler_phrase(phrase):
    """Check if phrase is just filler words."""
    filler_words = {'the', 'and', 'or', 'a', 'an', 'is', 'are', 'was', 'were', 'be',
                    'it', 'that', 'this', 'there', 'to', 'of', 'in', 'at', 'on'}

    words = phrase.split()
    if not words:
        return True

    # If all words are filler, skip
    if all(w in filler_words for w in words):
        return True

    return False


def suggest_briefs(phrases, min_frequency=5):
    """Suggest briefs for frequently-used phrases."""
    phrase_counts = Counter(phrases)

    # Filter by minimum frequency
    frequent_phrases = {p: c for p, c in phrase_counts.items() if c >= min_frequency}

    # Sort by frequency
    sorted_phrases = sorted(frequent_phrases.items(), key=lambda x: x[1], reverse=True)

    return sorted_phrases


def generate_brief(phrase):
    """Generate a suggested brief for a phrase."""
    words = phrase.split()

    # Use first letter of each word
    brief = ''.join(w[0].upper() for w in words)

    # If too short, use more letters
    if len(brief) < 3 and len(words) > 0:
        brief = (words[0][:2] + ''.join(w[0].upper() for w in words[1:])).upper()

    return brief


def build_brief_dictionary(phrases_with_count, output_file=None):
    """Build dictionary of brief suggestions."""
    briefs = {}

    for phrase, count in phrases_with_count:
        brief = generate_brief(phrase)
        briefs[brief] = phrase

    # Convert to JSON format for import into Plover
    brief_dict = {k: v for k, v in briefs.items()}

    report = []
    report.append("=" * 70)
    report.append("LEGAL BRIEF SUGGESTIONS")
    report.append("=" * 70)
    report.append(f"\nTotal Briefs Suggested: {len(briefs)}")
    report.append("\nTop 20 Most Frequent Phrases:")
    report.append("-" * 70)
    report.append(f"{'Count':<8} {'Brief':<20} {'Phrase'}")
    report.append("-" * 70)

    for phrase, count in phrases_with_count[:20]:
        brief = generate_brief(phrase)
        report.append(f"{count:<8} {brief:<20} {phrase}")

    report_text = "\n".join(report)

    if output_file:
        # Save dictionary JSON
        dict_file = output_file.replace('.txt', '.json')
        with open(dict_file, 'w', encoding='utf-8') as f:
            json.dump(brief_dict, f, indent=2)
        print(f"Brief dictionary saved to: {dict_file}")

        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report saved to: {output_file}")
    else:
        print(report_text)

    return brief_dict


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    filepath = sys.argv[1]
    min_frequency = 5
    output_file = None

    # Parse options
    if "--min-frequency" in sys.argv:
        idx = sys.argv.index("--min-frequency")
        min_frequency = int(sys.argv[idx + 1])

    if "--output" in sys.argv:
        output_file = "brief_suggestions.txt"

    # Load and analyze
    print(f"Loading transcript: {filepath}")
    transcript = load_transcript(filepath)

    print(f"Extracting phrases...")
    phrases = extract_phrases(transcript)
    print(f"Found {len(phrases)} phrases")

    print(f"Identifying frequent phrases (min {min_frequency} occurrences)...")
    frequent_phrases = suggest_briefs(phrases, min_frequency)
    print(f"Found {len(frequent_phrases)} frequent phrases")

    print(f"\nGenerating briefs...")
    build_brief_dictionary(frequent_phrases, output_file)


if __name__ == "__main__":
    main()
