"""Test script to verify emoji functionality in ExtendedFormatter."""

import os
import sys

# Add src to path to import beaconled modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from datetime import datetime, timezone

from beaconled.core.models import CommitStats, FileStats
from beaconled.formatters.extended import ExtendedFormatter


def test_emoji_support():
    """Test that emojis are properly supported in ExtendedFormatter."""
    # Create a sample commit stats object
    commit_stats = CommitStats(
        hash="abc123def456",
        author="John Doe <john@example.com>",
        date=datetime(2023, 1, 15, 10, 30, tzinfo=timezone.utc),
        message="Add new feature implementation",
        files=[
            FileStats(
                path="src/main.py",
                lines_added=30,
                lines_deleted=5,
                lines_changed=35,
            ),
            FileStats(
                path="tests/test_main.py",
                lines_added=10,
                lines_deleted=5,
                lines_changed=15,
            ),
        ],
    )

    # Test with emoji support enabled
    formatter_with_emoji = ExtendedFormatter(no_emoji=False)
    result_with_emoji = formatter_with_emoji.format_commit_stats(commit_stats)

    # Test with emoji support disabled
    formatter_without_emoji = ExtendedFormatter(no_emoji=True)
    result_without_emoji = formatter_without_emoji.format_commit_stats(commit_stats)

    # Check that emojis are present when enabled
    emoji_missing_error = "Emoji should be present when enabled"
    if "📊" not in result_with_emoji:
        raise AssertionError(emoji_missing_error)
    if "👤" not in result_with_emoji:
        raise AssertionError(emoji_missing_error)

    # Check that emojis are not present when disabled
    emoji_present_error = "Emoji should not be present when disabled"
    if "📊" in result_without_emoji:
        raise AssertionError(emoji_present_error)
    if "👤" in result_without_emoji:
        raise AssertionError(emoji_present_error)

    return True


if __name__ == "__main__":
    test_emoji_support()
    # Print success message
    import sys

    sys.stdout.write("All emoji tests passed!\n")
