"""Tests for emoji functionality in ExtendedFormatter."""

from datetime import datetime, timezone

from beaconled.core.models import CommitStats, FileStats
from beaconled.formatters.extended import ExtendedFormatter


class TestExtendedFormatterEmoji:
    """Tests for emoji functionality in ExtendedFormatter."""

    def test_format_commit_stats_with_emoji(self):
        """Test that emojis are displayed when enabled."""
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

        # Check that emojis are present when enabled
        assert "📊" in result_with_emoji, "Commit emoji should be present when enabled"
        assert "👤" in result_with_emoji, "Author emoji should be present when enabled"
        assert "📅" in result_with_emoji, "Date emoji should be present when enabled"
        assert "💬" in result_with_emoji, "Message emoji should be present when enabled"
        assert "📂" in result_with_emoji, "Files emoji should be present when enabled"
        assert "📈" in result_with_emoji, "Added lines emoji should be present when enabled"
        assert "📉" in result_with_emoji, "Deleted lines emoji should be present when enabled"

    def test_format_commit_stats_no_emoji(self):
        """Test that emojis are not displayed when disabled."""
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
            ],
        )

        # Test with emoji support disabled
        formatter_without_emoji = ExtendedFormatter(no_emoji=True)
        result_without_emoji = formatter_without_emoji.format_commit_stats(commit_stats)

        # Check that emojis are not present when disabled
        assert "📊" not in result_without_emoji, "Commit emoji should not be present when disabled"
        assert "👤" not in result_without_emoji, "Author emoji should not be present when disabled"
        assert "📅" not in result_without_emoji, "Date emoji should not be present when disabled"
        assert "💬" not in result_without_emoji, "Message emoji should not be present when disabled"
        assert "📂" not in result_without_emoji, "Files emoji should not be present when disabled"
        assert "📈" not in result_without_emoji, (
            "Added lines emoji should not be present when disabled"
        )
        assert "📉" not in result_without_emoji, (
            "Deleted lines emoji should not be present when disabled"
        )

    def test_format_range_stats_with_emoji(self):
        """Test that emojis are displayed in range stats when enabled."""
        # Create a sample range stats object
        range_stats = CommitStats(
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
            ],
        )

        # Convert to RangeStats
        from beaconled.core.models import RangeStats

        range_stats_obj = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            total_commits=1,
            total_files_changed=1,
            total_lines_added=30,
            total_lines_deleted=5,
            commits=[range_stats],
            authors={"John Doe <john@example.com>": 1},
        )

        # Test with emoji support enabled
        formatter_with_emoji = ExtendedFormatter(no_emoji=False)
        result_with_emoji = formatter_with_emoji.format_range_stats(range_stats_obj)

        # Check that emojis are present when enabled
        assert "📊" in result_with_emoji, "Range emoji should be present when enabled"
        assert "👥" in result_with_emoji, "Contributors emoji should be present when enabled"
        assert "📈" in result_with_emoji, "Added lines emoji should be present when enabled"
        assert "📉" in result_with_emoji, "Deleted lines emoji should be present when enabled"

    def test_format_range_stats_no_emoji(self):
        """Test that emojis are not displayed in range stats when disabled."""
        # Create a sample range stats object
        range_stats = CommitStats(
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
            ],
        )

        # Convert to RangeStats
        from beaconled.core.models import RangeStats

        range_stats_obj = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            total_commits=1,
            total_files_changed=1,
            total_lines_added=30,
            total_lines_deleted=5,
            commits=[range_stats],
            authors={"John Doe <john@example.com>": 1},
        )

        # Test with emoji support disabled
        formatter_without_emoji = ExtendedFormatter(no_emoji=True)
        result_without_emoji = formatter_without_emoji.format_range_stats(range_stats_obj)

        # Check that emojis are not present when disabled
        assert "📊" not in result_without_emoji, "Range emoji should not be present when disabled"
        assert "👥" not in result_without_emoji, (
            "Contributors emoji should not be present when disabled"
        )
        assert "📈" not in result_without_emoji, (
            "Added lines emoji should not be present when disabled"
        )
        assert "📉" not in result_without_emoji, (
            "Deleted lines emoji should not be present when disabled"
        )
