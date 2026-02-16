#!/usr/bin/env python3
"""
Speed Tracker for Court Reporting Stenography

Tracks practice sessions and generates performance reports.
Usage: python speed-tracker.py <action> [options]

Actions:
  record <wpm> <accuracy> [notes]  - Record a practice session
  list                             - List all recorded sessions
  stats                            - Show performance statistics
  chart                            - Generate performance chart (requires matplotlib)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Data file location
DATA_FILE = Path.home() / ".steno" / "speed_history.json"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_history():
    """Load speed history from file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []


def save_history(history):
    """Save speed history to file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def record_session(wpm, accuracy, notes=""):
    """Record a new practice session."""
    history = load_history()

    session = {
        "date": datetime.now().isoformat(),
        "wpm": float(wpm),
        "accuracy": float(accuracy),
        "notes": notes
    }

    history.append(session)
    save_history(history)

    print(f"✓ Recorded: {wpm} WPM, {accuracy}% accuracy")
    if notes:
        print(f"  Notes: {notes}")


def list_sessions():
    """List all recorded sessions."""
    history = load_history()

    if not history:
        print("No sessions recorded yet.")
        return

    print(f"\n{'Date':<20} {'WPM':<8} {'Accuracy':<10} {'Notes'}")
    print("-" * 60)

    for session in history[-20:]:  # Show last 20 sessions
        date = datetime.fromisoformat(session['date']).strftime('%Y-%m-%d %H:%M')
        wpm = session['wpm']
        acc = session['accuracy']
        notes = session.get('notes', '')
        print(f"{date:<20} {wpm:<8.0f} {acc:<10.1f} {notes}")


def show_stats():
    """Show performance statistics."""
    history = load_history()

    if not history:
        print("No sessions recorded yet.")
        return

    wpm_values = [s['wpm'] for s in history]
    acc_values = [s['accuracy'] for s in history]

    avg_wpm = sum(wpm_values) / len(wpm_values)
    max_wpm = max(wpm_values)
    min_wpm = min(wpm_values)

    avg_acc = sum(acc_values) / len(acc_values)
    max_acc = max(acc_values)
    min_acc = min(acc_values)

    print("\n=== Performance Statistics ===")
    print(f"Total Sessions: {len(history)}")
    print(f"\nSpeed (WPM):")
    print(f"  Average: {avg_wpm:.0f}")
    print(f"  Maximum: {max_wpm:.0f}")
    print(f"  Minimum: {min_wpm:.0f}")
    print(f"  Improvement: +{max_wpm - min_wpm:.0f}")
    print(f"\nAccuracy (%):")
    print(f"  Average: {avg_acc:.1f}")
    print(f"  Maximum: {max_acc:.1f}")
    print(f"  Minimum: {min_acc:.1f}")
    print(f"  Improvement: +{max_acc - min_acc:.1f}")

    # Trend
    if len(history) > 1:
        first_wpm = history[0]['wpm']
        last_wpm = history[-1]['wpm']
        trend = ((last_wpm - first_wpm) / first_wpm) * 100
        print(f"\nTrend: {trend:+.1f}% speed change")


def generate_chart():
    """Generate a simple text-based chart."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Install with: pip install matplotlib")
        return

    history = load_history()
    if not history:
        print("No data to chart.")
        return

    dates = [datetime.fromisoformat(s['date']).strftime('%m-%d') for s in history]
    wpm_values = [s['wpm'] for s in history]
    acc_values = [s['accuracy'] for s in history]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # WPM chart
    ax1.plot(dates, wpm_values, marker='o', color='blue', label='WPM')
    ax1.set_title('Stenography Speed Progress (WPM)')
    ax1.set_ylabel('Words Per Minute')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Accuracy chart
    ax2.plot(dates, acc_values, marker='s', color='green', label='Accuracy %')
    ax2.set_title('Stenography Accuracy Progress')
    ax2.set_ylabel('Accuracy %')
    ax2.set_xlabel('Date')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()

    # Save chart
    chart_file = DATA_FILE.parent / "speed_chart.png"
    plt.savefig(chart_file, dpi=100)
    print(f"Chart saved: {chart_file}")

    # Show chart
    plt.show()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]

    if action == "record":
        if len(sys.argv) < 4:
            print("Usage: python speed-tracker.py record <wpm> <accuracy> [notes]")
            sys.exit(1)

        wpm = sys.argv[2]
        accuracy = sys.argv[3]
        notes = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""

        record_session(wpm, accuracy, notes)

    elif action == "list":
        list_sessions()

    elif action == "stats":
        show_stats()

    elif action == "chart":
        generate_chart()

    else:
        print(f"Unknown action: {action}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
