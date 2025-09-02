from datetime import datetime, timezone

import pytest
from freezegun import freeze_time

from beaconled.core.models import CommitStats, FileStats, RangeStats
from beaconled.formatters.extended import ExtendedFormatter
from beaconled.formatters.standard import StandardFormatter


@pytest.fixture
def sample_commit_stats():
    """Provides a sample CommitStats object for testing."""
    return CommitStats(
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
            FileStats(
                path="docs/README.md",
                lines_added=5,
                lines_deleted=2,
                lines_changed=7,
            ),
        ],
    )


@pytest.fixture
def sample_range_stats():
    """Provides a sample RangeStats object for testing."""
    # Create proper CommitStats objects instead of mocks
    commits = [
        CommitStats(
            hash="commit1",
            author="John Doe",
            date=datetime(2023, 1, 10, tzinfo=timezone.utc),
            message="First commit",
            files_changed=3,
            lines_added=30,
            lines_deleted=5,
            files=[FileStats("src/file1.py", 30, 5, 35)],
        ),
        CommitStats(
            hash="commit2",
            author="Jane Smith",
            date=datetime(2023, 1, 12, tzinfo=timezone.utc),
            message="Second commit",
            files_changed=2,
            lines_added=20,
            lines_deleted=10,
            files=[FileStats("src/file2.py", 20, 10, 30)],
        ),
        CommitStats(
            hash="commit3",
            author="John Doe",
            date=datetime(2023, 1, 15, tzinfo=timezone.utc),
            message="Third commit",
            files_changed=4,
            lines_added=50,
            lines_deleted=15,
            files=[FileStats("src/file3.py", 50, 15, 65)],
        ),
        CommitStats(
            hash="commit4",
            author="Jane Smith",
            date=datetime(2023, 1, 20, tzinfo=timezone.utc),
            message="Fourth commit",
            files_changed=2,
            lines_added=25,
            lines_deleted=8,
            files=[FileStats("docs/file4.md", 25, 8, 33)],
        ),
        CommitStats(
            hash="commit5",
            author="Bob Johnson",
            date=datetime(2023, 1, 25, tzinfo=timezone.utc),
            message="Fifth commit",
            files_changed=1,
            lines_added=31,
            lines_deleted=7,
            files=[FileStats("tests/file5.py", 31, 7, 38)],
        ),
    ]
    return RangeStats(
        start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
        total_commits=5,
        total_files_changed=12,
        total_lines_added=156,
        total_lines_deleted=45,
        commits=commits,
    )


class TestStandardFormatter:
    def test_format_commit_stats(self, sample_commit_stats):
        formatter = StandardFormatter()
        result = formatter.format_commit_stats(sample_commit_stats)
        import re

        clean_result = re.sub(r"\x1b\[[0-9;]*m", "", result)
        assert "Commit: abc123de" in clean_result
        assert "Author: John Doe" in clean_result
        assert "Date: 2023-01-15" in clean_result
        assert "Files changed: 3" in clean_result
        assert "Lines added: 45" in clean_result
        assert "Lines deleted: 12" in clean_result

    def test_format_range_stats(self, sample_range_stats):
        # Calculate extended stats for enhanced formatting
        formatter = StandardFormatter()
        sample_range_stats.calculate_extended_stats()
        result = formatter.format_range_stats(sample_range_stats)
        import re

        clean_result = re.sub(r"\x1b\[[0-9;]*m", "", result)
        assert "Analysis Period: 2023-01-01 to 2023-01-31" in clean_result
        assert "Total commits: 5" in clean_result
        assert "John Doe: 2 commits (40%)" in clean_result
        assert "=== TEAM OVERVIEW ===" in clean_result
        assert "=== CONTRIBUTOR BREAKDOWN ===" in clean_result
        assert "Total lines added: 156" in clean_result
        assert "Total lines deleted: 45" in clean_result
        assert "Net change: 111" in clean_result

    def test_format_commit_stats_with_emoji(self, sample_commit_stats):
        formatter = StandardFormatter(no_emoji=False)
        result = formatter.format_commit_stats(sample_commit_stats)
        # Assuming a UTF-8 environment for testing emojis
        assert "📊" in result
        assert "👤" in result

    def test_format_commit_stats_no_emoji(self, sample_commit_stats):
        formatter = StandardFormatter(no_emoji=True)
        result = formatter.format_commit_stats(sample_commit_stats)
        assert "📊" not in result
        assert "👤" not in result

    def test_format_range_stats_with_emoji(self, sample_range_stats):
        formatter = StandardFormatter(no_emoji=False)
        sample_range_stats.calculate_extended_stats()
        result = formatter.format_range_stats(sample_range_stats)
        # Assuming a UTF-8 environment for testing emojis
        assert "🗓️" in result
        assert "🚀" in result

    def test_format_range_stats_no_emoji(self, sample_range_stats):
        formatter = StandardFormatter(no_emoji=True)
        sample_range_stats.calculate_extended_stats()
        result = formatter.format_range_stats(sample_range_stats)
        assert "🗓️" not in result
        assert "🚀" not in result


class TestExtendedFormatter:
    def setup_method(self):
        self.formatter = ExtendedFormatter()

    def test_format_commit_stats_with_file_types(self, sample_commit_stats):
        result = self.formatter.format_commit_stats(sample_commit_stats)
        import re

        clean_result = re.sub(r"\x1b\[[0-9;]*m", "", result)
        assert "Commit: abc123de" in clean_result
        assert "Files changed: 3" in clean_result
        assert "md: 1 files, +5/-2" in clean_result

    def test_format_range_stats_with_author_breakdown(self, sample_range_stats):
        # Calculate extended stats for enhanced formatting
        sample_range_stats.calculate_extended_stats()
        result = self.formatter.format_range_stats(sample_range_stats)
        import re

        clean_result = re.sub(r"\x1b\[[0-9;]*m", "", result)
        assert "Jane Smith: 2 commits" in clean_result
        assert "Bob Johnson: 1 commit" in clean_result

    @freeze_time("2023-01-31")
    def test_format_range_stats_with_temporal_analysis(self, sample_range_stats):
        # Calculate extended stats to populate commits_by_day
        sample_range_stats.calculate_extended_stats()
        result = self.formatter.format_range_stats(sample_range_stats)
        import re

        clean_result = re.sub(r"\x1b\[[0-9;]*m", "", result)
        assert "Temporal Analysis - Daily Activity Timeline:" in clean_result
        # Check for specific dates from the sample data
        assert "2023-01-10: 1 commit" in clean_result
        assert "2023-01-12: 1 commit" in clean_result
        assert "2023-01-15: 1 commit" in clean_result
        assert "2023-01-20: 1 commit" in clean_result
        assert "2023-01-25: 1 commit" in clean_result
