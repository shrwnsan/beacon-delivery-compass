"""Tests for the ExtendedFormatter class."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

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

    def test_format_file_lifecycle_stats(self):
        """Test formatting of file lifecycle statistics."""
        # Mock the _get_file_lifecycle_stats method to return specific values
        with patch.object(self.formatter, "_get_file_lifecycle_stats") as mock_get_stats:
            mock_get_stats.return_value = {
                "added": 15,
                "modified": 245,
                "deleted": 12,
                "renamed": 3,
            }

            # Create a range stats object with date information
            start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
            end_date = datetime(2023, 1, 31, tzinfo=timezone.utc)
            range_stats = RangeStats(
                start_date=start_date,
                end_date=end_date,
                total_commits=100,
                total_files_changed=200,
                total_lines_added=1000,
                total_lines_deleted=500,
            )

            result = self.formatter.format_range_stats(range_stats)
            clean_result = self._strip_ansi_codes(result)

            # Check that file lifecycle section is included
            assert "File Lifecycle Activity:" in clean_result
            assert "Files Added: 15 new files" in clean_result
            assert "Files Modified: 245 existing files" in clean_result
            assert "Files Deleted: 12 files removed" in clean_result
            assert "Files Renamed: 3 files moved" in clean_result

    def test_format_file_lifecycle_stats_empty(self):
        """Test formatting when there's no file lifecycle activity."""
        # Mock the _get_file_lifecycle_stats method to return zeros
        with patch.object(self.formatter, "_get_file_lifecycle_stats") as mock_get_stats:
            mock_get_stats.return_value = {
                "added": 0,
                "modified": 0,
                "deleted": 0,
                "renamed": 0,
            }

            # Create a range stats object with date information
            start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
            end_date = datetime(2023, 1, 31, tzinfo=timezone.utc)
            range_stats = RangeStats(
                start_date=start_date,
                end_date=end_date,
                total_commits=100,
                total_files_changed=200,
                total_lines_added=1000,
                total_lines_deleted=500,
            )

            result = self.formatter.format_range_stats(range_stats)
            clean_result = self._strip_ansi_codes(result)

            # Check that file lifecycle section is not included when all counts are zero
            assert "File Lifecycle Activity:" not in clean_result

    def test_get_file_lifecycle_stats(self):
        """Test the _get_file_lifecycle_stats method with mocked git output."""
        # Mock the git.Repo and its log method
        with patch("beaconled.formatters.extended.git.Repo") as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.git.log.return_value = (
                "A\tsrc/new_file.py\n"
                "M\tsrc/existing_file.py\n"
                "D\tsrc/deleted_file.py\n"
                "R100\told_name.py\tnew_name.py\n"
                "A\tsrc/another_new_file.py\n"
                "M\tsrc/existing_file.py\n"  # Duplicate should be counted only once
            )

            result = self.formatter._get_file_lifecycle_stats("2023-01-01", "2023-01-31")

            # Check that we get the expected counts
            assert result["added"] == 2  # Two unique files added
            assert result["modified"] == 1  # One unique file modified
            assert result["deleted"] == 1  # One file deleted
            assert result["renamed"] == 1  # One file renamed

    def _strip_ansi_codes(self, text):
        """Helper method to strip ANSI color codes from text."""
        import re

        return re.sub(r"\x1b\[[0-9;]*m", "", text)
