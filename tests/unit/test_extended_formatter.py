"""Tests for the ExtendedFormatter class."""

from datetime import datetime, timedelta, timezone

import pytest

from beaconled.core.models import CommitStats, FileStats, RangeStats
from beaconled.formatters.extended import ExtendedFormatter


@pytest.fixture
def sample_commit_with_file_types():
    """Provides a sample CommitStats object with various file types."""
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
            FileStats(
                path="config.yaml",
                lines_added=3,
                lines_deleted=1,
                lines_changed=4,
            ),
            FileStats(
                path="requirements.txt",
                lines_added=2,
                lines_deleted=0,
                lines_changed=2,
            ),
        ],
    )


@pytest.fixture
def sample_range_with_commits():
    """Provides a sample RangeStats object with commits for testing."""
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    commits = []

    # Create commits with different authors and dates
    for day in range(5):
        # Create commits for each day
        for i in range(day + 1):  # 1, 2, 3, 4, 5 commits per day
            author = f"Author {day % 2 + 1} <author{day % 2 + 1}@example.com>"
            commit = CommitStats(
                hash=f"hash{day}{i}",
                author=author,
                date=start_date + timedelta(days=day),
                message=f"Commit {day}.{i}",
                files_changed=day + 1,
                lines_added=(day + 1) * 10,
                lines_deleted=(day + 1) * 2,
                files=[
                    FileStats(
                        path=f"src/file{day}_{i}.py",
                        lines_added=(day + 1) * 8,
                        lines_deleted=(day + 1) * 2,
                    ),
                    FileStats(
                        path=f"tests/test_file{day}_{i}.py",
                        lines_added=(day + 1) * 2,
                        lines_deleted=0,
                    ),
                ],
            )
            commits.append(commit)

    # Create a range that includes all commits
    return RangeStats(
        start_date=start_date,
        end_date=start_date + timedelta(days=10),  # 10-day range
        commits=commits,
    )


class TestExtendedFormatter:
    """Tests for the ExtendedFormatter class."""

    def setup_method(self):
        self.formatter = ExtendedFormatter()

    def test_format_commit_stats_file_type_breakdown(
        self,
        sample_commit_with_file_types,
    ):
        """Test that file type breakdown is included in commit stats."""
        result = self.formatter.format_commit_stats(sample_commit_with_file_types)

        # Remove ANSI color codes for easier assertion
        clean_result = self._strip_ansi_codes(result)

        # Check file type breakdown section
        assert "File type breakdown:" in clean_result
        # Note: No leading dot in file extensions in output
        assert "py: 2 files, +40/-10" in clean_result
        assert "md: 1 files, +5/-2" in clean_result
        assert "yaml: 1 files, +3/-1" in clean_result
        assert "txt: 1 files, +2/-0" in clean_result

    def test_format_range_stats_with_commits(self, sample_range_with_commits):
        """Test formatting range stats with commit data."""
        result = self.formatter.format_range_stats(sample_range_with_commits)
        clean_result = self._strip_ansi_codes(result)

        # Check basic sections are present
        assert "Range Analysis:" in clean_result
        assert "Total commits:" in clean_result
        assert "Total files changed:" in clean_result
        assert "Total lines added:" in clean_result
        assert "Total lines deleted:" in clean_result
        assert "Net change:" in clean_result

        # Check author breakdown is included
        assert "Contributors:" in clean_result
        assert "Author 1" in clean_result
        assert "Author 2" in clean_result

        # Note: The current implementation doesn't show file type breakdown in range stats
        # So we'll just verify the basic structure is there
        assert "Range Analysis:" in clean_result
        assert "Total commits: 15" in clean_result
        assert "Total files changed: 55" in clean_result
        assert "Total lines added: 550" in clean_result
        assert "Total lines deleted: 110" in clean_result
        assert "Net change: 440" in clean_result

        # Check author breakdown is included
        assert "Contributors:" in clean_result
        assert "Author 1 <author1@example.com>: 9 commits" in clean_result
        assert "Author 2 <author2@example.com>: 6 commits" in clean_result

    def test_format_empty_commit_stats(self):
        """Test formatting commit stats with no files."""
        empty_commit = CommitStats(
            hash="abc123",
            author="Test User <test@example.com>",
            date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            message="Empty commit",
            files=[],
        )

        result = self.formatter.format_commit_stats(empty_commit)
        clean_result = self._strip_ansi_codes(result)

        assert "Files changed: 0" in clean_result
        # File type breakdown should always be shown in extended format for consistency
        assert "File type breakdown:" in clean_result
        assert "No files changed" in clean_result

    def _strip_ansi_codes(self, text):
        """Helper method to strip ANSI color codes from text."""
        import re

        return re.sub(r"\x1b\[[0-9;]*m", "", text)

    def test_get_frequently_changed_files(self):
        """Test the _get_frequently_changed_files method."""
        # Since this method uses git commands, we'll test it returns a dictionary
        # and handles errors gracefully
        
        # Test with a short time period that should return empty results in most cases
        frequent_files = self.formatter._get_frequently_changed_files("1 second ago")
        
        # Should return a dictionary
        assert isinstance(frequent_files, dict)
        
        # Should have at most 5 entries (top 5)
        assert len(frequent_files) <= 5
        
        # Test with a longer time period
        frequent_files = self.formatter._get_frequently_changed_files("30 days ago")
        
        # Should return a dictionary
        assert isinstance(frequent_files, dict)

    def test_format_frequent_files_with_data(self):
        """Test formatting frequent files with data."""
        frequent_files = {
            "src/beaconled/cli.py": 19,
            "pyproject.toml": 18,
            "src/beaconled/formatters/extended.py": 16,
            "README.md": 11,
            "src/beaconled/core/analyzer.py": 10,
        }

        result = self.formatter._format_frequent_files(frequent_files)
        clean_result = self._strip_ansi_codes("\n".join(result)).split("\n")

        # Should return a list
        assert isinstance(result, list)

        # Should have header and file entries
        assert len(clean_result) == 7  # Empty line + Emoji + Header + 5 files

        # Check header (with emoji)
        assert (
            "🔥 Most Frequently Changed (last 30 days):" in clean_result[1]
        )  # Index 1 because first item is empty string

        # Check file entries
        assert "src/beaconled/cli.py: 19 changes" in clean_result[2]
        assert "pyproject.toml: 18 changes" in clean_result[3]
        assert "src/beaconled/formatters/extended.py: 16 changes" in clean_result[4]
        assert "README.md: 11 changes" in clean_result[5]
        assert "src/beaconled/core/analyzer.py: 10 changes" in clean_result[6]

    def test_format_frequent_files_empty(self):
        """Test formatting frequent files with empty data."""
        result = self.formatter._format_frequent_files({})

        # Should return an empty list
        assert isinstance(result, list)
        assert len(result) == 0
