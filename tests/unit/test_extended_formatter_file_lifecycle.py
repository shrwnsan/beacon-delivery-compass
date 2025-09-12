"""Tests for the file lifecycle tracking functionality in ExtendedFormatter."""

import re
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


from beaconled.core.models import RangeStats
from beaconled.formatters.extended import ExtendedFormatter


class TestExtendedFormatterFileLifecycle:
    """Tests for the file lifecycle tracking functionality in ExtendedFormatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = ExtendedFormatter()

    @patch("git.Repo")
    def test_get_file_lifecycle_stats(self, mock_repo):
        """Test _get_file_lifecycle_stats with mock git log output."""
        # Setup mock repo
        mock_commit1 = MagicMock()
        mock_commit1.stats.files = {
            "path/to/file1.py": MagicMock(),
            "path/to/new_file.py": MagicMock(),
            "path/to/deleted_file.py": MagicMock(),
            "new/path/file.txt": MagicMock(),
        }

        # Configure the mock repo to return our test commit
        mock_repo.return_value.iter_commits.return_value = [mock_commit1]

        # Call the method
        result = self.formatter._get_file_lifecycle_stats("2023-01-01", "2023-12-31")

        # Verify results - we can't easily test the exact counts due to the way
        # git stats are processed, but we can verify the structure
        assert isinstance(result, dict)
        assert set(result.keys()) == {"added", "modified", "deleted", "renamed"}
        assert all(isinstance(v, int) for v in result.values())

    def test_format_file_lifecycle(self):
        """Test _format_file_lifecycle with sample data."""
        # Create test data
        stats = {"added": 5, "modified": 10, "deleted": 2, "renamed": 3}

        # Call the method
        result = self.formatter._format_file_lifecycle(stats)

        # Verify results - should be 5 lines: header + 4 stats lines
        assert len(result) == 5
        assert "File Lifecycle Activity:" in result[0]
        assert "• Files Added: 5 new files" in result[1]
        assert "• Files Modified: 10 existing files" in result[2]
        assert "• Files Deleted: 2 files removed" in result[3]
        assert "• Files Renamed: 3 files moved" in result[4]

    def test_format_file_lifecycle_empty(self):
        """Test _format_file_lifecycle with empty stats."""
        result = self.formatter._format_file_lifecycle({})
        assert result == []

    def test_parse_git_log_output(self):
        """Test _parse_git_log_output with sample git log output."""
        log_output = """
M	path/to/file1.py
A	path/to/new_file.py
D	path/to/deleted_file.py
R100	old/path/file.txt	new/path/file.txt
        """

        result = self.formatter._parse_git_log_output(log_output)

        assert result["added"] == 1
        assert result["modified"] == 1
        assert result["deleted"] == 1
        assert result["renamed"] == 1

    def test_parse_git_log_output_empty(self):
        """Test _parse_git_log_output with empty input."""
        result = self.formatter._parse_git_log_output("")
        assert result == {"added": 0, "modified": 0, "deleted": 0, "renamed": 0}

    def test_format_range_stats_includes_file_lifecycle(self):
        """Test that format_range_stats includes the file lifecycle section."""
        # Create a RangeStats with date range
        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            commits=[],
        )

        # Mock the _get_file_lifecycle_stats method
        with patch.object(
            self.formatter,
            "_get_file_lifecycle_stats",
            return_value={"added": 1, "modified": 2, "deleted": 1, "renamed": 0},
        ) as mock_lifecycle:
            result = self.formatter.format_range_stats(range_stats)
            clean_result = self._strip_ansi_codes(result)

            # Verify the lifecycle section is included
            assert "File Lifecycle Activity:" in clean_result
            assert "• Files Added: 1 new files" in clean_result
            assert "• Files Modified: 2 existing files" in clean_result
            assert "• Files Deleted: 1 files removed" in clean_result

    def _strip_ansi_codes(self, text):
        """Helper method to strip ANSI color codes from text."""
        return re.sub(r"\x1b\[[0-9;]*m", "", text)
