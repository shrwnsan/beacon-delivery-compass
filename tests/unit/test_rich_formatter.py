"""Tests for RichFormatter class."""

from datetime import datetime, timezone
from io import StringIO

import pytest
from rich.console import Console

from beaconled.core.models import CommitStats, FileStats, RangeStats
from beaconled.formatters.rich_formatter import RichFormatter


class TestRichFormatter:
    """Test suite for RichFormatter."""

    @pytest.fixture
    def formatter(self):
        """Create a RichFormatter instance for testing."""
        return RichFormatter()

    @pytest.fixture
    def sample_commit_stats(self):
        """Create sample commit statistics for testing."""
        return CommitStats(
            hash="abc123def456789",
            author="John Doe <john@example.com>",
            date=datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc),
            message="Add new feature for user authentication",
            files_changed=3,
            lines_added=150,
            lines_deleted=25,
            files=[
                FileStats(path="src/auth.py", lines_added=80, lines_deleted=10),
                FileStats(path="tests/test_auth.py", lines_added=60, lines_deleted=5),
                FileStats(path="docs/auth.md", lines_added=10, lines_deleted=10),
            ],
        )

    @pytest.fixture
    def sample_range_stats(self):
        """Create sample range statistics for testing."""
        commits = [
            CommitStats(
                hash="abc123def456789",
                author="John Doe <john@example.com>",
                date=datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc),
                message="Add authentication feature",
                files_changed=2,
                lines_added=100,
                lines_deleted=20,
            ),
            CommitStats(
                hash="def456ghi789012",
                author="Jane Smith <jane@example.com>",
                date=datetime(2023, 6, 16, 10, 15, 30, tzinfo=timezone.utc),
                message="Fix bug in login validation",
                files_changed=1,
                lines_added=5,
                lines_deleted=3,
            ),
        ]

        stats = RangeStats(
            start_date=datetime(2023, 6, 15, tzinfo=timezone.utc),
            end_date=datetime(2023, 6, 16, tzinfo=timezone.utc),
            total_commits=2,
            total_files_changed=3,
            total_lines_added=105,
            total_lines_deleted=23,
            commits=commits,
        )
        stats.calculate_extended_stats()
        return stats

    def test_formatter_initialization(self):
        """Test RichFormatter initialization with and without console."""
        # Test with default console
        formatter = RichFormatter()
        assert formatter.console is not None
        assert isinstance(formatter.console, Console)

        # Test with custom console
        custom_console = Console(file=StringIO())
        formatter = RichFormatter(console=custom_console)
        assert formatter.console is custom_console

    def test_format_commit_stats_basic(self, formatter, sample_commit_stats):
        """Test basic commit stats formatting."""
        result = formatter.format_commit_stats(sample_commit_stats)

        # Verify output contains expected elements
        assert "abc123de" in result  # Shortened hash
        assert "John Doe" in result
        assert "2023-06-15 14:30:45" in result
        assert "Add new feature" in result
        assert "Files Changed" in result
        assert "150" in result  # Lines added
        assert "25" in result  # Lines deleted
        assert "125" in result  # Net change

    def test_format_commit_stats_with_files(self, formatter, sample_commit_stats):
        """Test commit stats formatting with file details."""
        result = formatter.format_commit_stats(sample_commit_stats)

        # Verify file information is present
        assert "src/auth.py" in result
        assert "tests/test_auth.py" in result
        assert "docs/auth.md" in result
        assert "File Changes" in result

    def test_format_commit_stats_file_types(self, formatter, sample_commit_stats):
        """Test file type breakdown in commit stats."""
        result = formatter.format_commit_stats(sample_commit_stats)

        # Should contain file type breakdown
        assert "File Types" in result
        assert ".py" in result
        assert ".md" in result

    def test_format_commit_stats_empty_files(self, formatter):
        """Test commit stats formatting with no files."""
        stats = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc),
            message="Empty commit",
            files_changed=0,
            lines_added=0,
            lines_deleted=0,
            files=[],
        )

        result = formatter.format_commit_stats(stats)

        # Should still format basic info but no file tables
        assert "Test Author" in result
        assert "Empty commit" in result
        assert "File Changes" not in result
        assert "File Types" not in result

    def test_format_range_stats_basic(self, formatter, sample_range_stats):
        """Test basic range stats formatting."""
        result = formatter.format_range_stats(sample_range_stats)

        # Verify overview information
        assert "Range Analysis Overview" in result
        assert "2023-06-15" in result
        assert "2023-06-16" in result
        assert "1 days" in result  # Duration from 15th to 16th is 1 day
        assert "2" in result  # Total commits
        assert "105" in result  # Lines added
        assert "23" in result  # Lines deleted

    def test_format_range_stats_team_overview(self, formatter, sample_range_stats):
        """Test team overview section in range stats."""
        result = formatter.format_range_stats(sample_range_stats)

        # Should contain team overview
        assert "Team Overview" in result
        assert "Contributors" in result
        assert "2" in result  # Number of contributors
        assert "Total Commits" in result

    def test_format_range_stats_contributor_breakdown(self, formatter, sample_range_stats):
        """Test contributor breakdown in range stats."""
        result = formatter.format_range_stats(sample_range_stats)

        # Should contain contributor breakdown
        assert "Contributor Breakdown" in result
        assert "John Doe" in result
        assert "Jane Smith" in result

    def test_format_range_stats_component_activity(self, formatter, sample_range_stats):
        """Test component activity section in range stats."""
        result = formatter.format_range_stats(sample_range_stats)

        # The sample data doesn't have component stats, so this section won't appear
        # This test verifies that the formatter handles missing component stats gracefully
        assert "Component Activity" not in result

    def test_format_range_stats_daily_activity(self, formatter, sample_range_stats):
        """Test daily activity section in range stats."""
        result = formatter.format_range_stats(sample_range_stats)

        # Should contain daily activity
        assert "Daily Activity" in result
        assert "2023-06-15" in result
        assert "2023-06-16" in result

    def test_format_range_stats_empty(self, formatter):
        """Test range stats formatting with minimal data."""
        stats = RangeStats(
            start_date=datetime(2023, 6, 15, tzinfo=timezone.utc),
            end_date=datetime(2023, 6, 15, tzinfo=timezone.utc),
            total_commits=0,
            total_files_changed=0,
            total_lines_added=0,
            total_lines_deleted=0,
            commits=[],
        )

        result = formatter.format_range_stats(stats)

        # Should still format basic overview
        assert "Range Analysis Overview" in result
        assert "2023-06-15" in result
        assert "1 days" in result
        assert "0" in result  # Zero commits

    def test_format_net_change_positive(self, formatter):
        """Test net change formatting for positive values."""
        stats = CommitStats(
            hash="test",
            author="Test",
            date=datetime(2023, 6, 15, tzinfo=timezone.utc),
            message="Test",
            lines_added=100,
            lines_deleted=20,
        )

        result = formatter.format_commit_stats(stats)
        # Net change should be positive and green (though we can't test color in text output)
        assert "80" in result

    def test_format_net_change_negative(self, formatter):
        """Test net change formatting for negative values."""
        stats = CommitStats(
            hash="test",
            author="Test",
            date=datetime(2023, 6, 15, tzinfo=timezone.utc),
            message="Test",
            lines_added=20,
            lines_deleted=100,
        )

        result = formatter.format_commit_stats(stats)
        # Net change should be negative
        assert "-80" in result

    def test_format_date_method(self, formatter):
        """Test the _format_date helper method."""
        dt = datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
        formatted = formatter._format_date(dt)
        assert formatted == "2023-06-15 14:30:45"

    def test_get_file_type_breakdown_method(self, formatter):
        """Test the _get_file_type_breakdown helper method."""
        files = [
            FileStats(path="src/main.py", lines_added=10, lines_deleted=5),
            FileStats(path="src/utils.py", lines_added=20, lines_deleted=3),
            FileStats(path="docs/README.md", lines_added=5, lines_deleted=2),
        ]

        breakdown = formatter._get_file_type_breakdown(files)

        assert "py" in breakdown
        assert breakdown["py"]["count"] == 2
        assert breakdown["py"]["added"] == 30
        assert breakdown["py"]["deleted"] == 8

        assert "md" in breakdown
        assert breakdown["md"]["count"] == 1
        assert breakdown["md"]["added"] == 5
        assert breakdown["md"]["deleted"] == 2

    def test_get_file_type_breakdown_no_extension(self, formatter):
        """Test file type breakdown with files that have no extension."""
        files = [
            FileStats(path="Makefile", lines_added=10, lines_deleted=5),
            FileStats(path="Dockerfile", lines_added=20, lines_deleted=3),
        ]

        breakdown = formatter._get_file_type_breakdown(files)

        assert "no-ext" in breakdown
        assert breakdown["no-ext"]["count"] == 2
        assert breakdown["no-ext"]["added"] == 30
        assert breakdown["no-ext"]["deleted"] == 8

    def test_console_width_setting(self, formatter, sample_commit_stats):
        """Test that console width is properly set for output."""
        result = formatter.format_commit_stats(sample_commit_stats)

        # The formatter sets console width to 120, so output should be formatted accordingly
        # This is a basic check that formatting works
        assert len(result) > 0
        assert "\n" in result  # Should have line breaks

    def test_rich_console_integration(self, sample_commit_stats):
        """Test integration with Rich console for custom output."""
        output_buffer = StringIO()
        custom_console = Console(file=output_buffer, width=100)
        formatter = RichFormatter(console=custom_console)

        result = formatter.format_commit_stats(sample_commit_stats)

        # Result should be the captured output
        assert len(result) > 0
        assert "John Doe" in result

    def test_format_range_stats_with_extended_stats(self, formatter):
        """Test range stats formatting with extended statistics calculated."""
        commits = [
            CommitStats(
                hash="abc123",
                author="Alice",
                date=datetime(2023, 6, 15, 10, 0, 0, tzinfo=timezone.utc),
                message="Feature commit",
                files_changed=5,
                lines_added=50,
                lines_deleted=10,
                files=[
                    FileStats(path="src/feature.py", lines_added=30, lines_deleted=5),
                    FileStats(path="tests/test_feature.py", lines_added=20, lines_deleted=5),
                ],
            ),
            CommitStats(
                hash="def456",
                author="Bob",
                date=datetime(2023, 6, 16, 14, 0, 0, tzinfo=timezone.utc),
                message="Bug fix",
                files_changed=1,
                lines_added=2,
                lines_deleted=2,
                files=[
                    FileStats(path="src/bugfix.py", lines_added=2, lines_deleted=2),
                ],
            ),
        ]

        stats = RangeStats(
            start_date=datetime(2023, 6, 15, tzinfo=timezone.utc),
            end_date=datetime(2023, 6, 16, tzinfo=timezone.utc),
            commits=commits,
        )
        stats.calculate_extended_stats()

        result = formatter.format_range_stats(stats)

        # Should contain extended statistics
        assert "Alice" in result
        assert "Bob" in result
        assert (
            "High Impact" in result or "Medium Impact" in result or "Low Impact" in result
        )  # Impact categories as table headers
        assert "src/" in result  # Component activity
