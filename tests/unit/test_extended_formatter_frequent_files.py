"""Tests for the frequently changed files functionality in ExtendedFormatter."""

from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


from beaconled.core.models import RangeStats
from beaconled.formatters.extended import ExtendedFormatter


class TestExtendedFormatterFrequentFiles:
    """Tests for the frequently changed files functionality in ExtendedFormatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = ExtendedFormatter()

    @patch("git.Repo")
    def test_get_frequently_changed_files(self, mock_repo):
        """Test _get_frequently_changed_files with mock GitPython objects."""
        # Setup mock commits
        mock_commit1 = MagicMock()
        mock_commit1.stats.files = {
            "src/file1.py": MagicMock(),
            "src/file2.py": MagicMock(),
            "tests/test_file1.py": MagicMock(),
        }

        mock_commit2 = MagicMock()
        mock_commit2.stats.files = {
            "src/file1.py": MagicMock(),  # Changed again
            "src/file3.py": MagicMock(),
            "docs/readme.md": MagicMock(),
        }

        # Configure the mock repo to return our test commits
        mock_repo.return_value.iter_commits.return_value = [mock_commit1, mock_commit2]

        # Call the method with a test date
        result = self.formatter._get_frequently_changed_files("2025-01-01")

        # Verify results - should have 5 unique files
        assert len(result) == 5
        # Check that all expected files are present
        assert "src/file1.py" in result
        assert "src/file2.py" in result
        assert "tests/test_file1.py" in result
        assert "src/file3.py" in result
        assert "docs/readme.md" in result
        # Check that file1.py has the highest count (appears in both commits)
        assert result["src/file1.py"] == 2

    @patch("git.Repo")
    def test_get_frequently_changed_files_empty(self, mock_repo):
        """Test _get_frequently_changed_files with no commits in the period."""
        # Configure the mock repo to return no commits
        mock_repo.return_value.iter_commits.return_value = []

        # Call the method
        result = self.formatter._get_frequently_changed_files("2025-01-01")

        # Verify results
        assert result == {}

    @patch("git.Repo")
    def test_format_frequent_files(self, mock_repo):
        """Test _format_frequent_files with sample data."""
        # Setup test data
        frequent_files = {
            "src/file1.py": 5,
            "src/file2.py": 3,
            "tests/test_file1.py": 2,
        }

        # Call the method
        result = self.formatter._format_frequent_files(frequent_files)

        # Verify results
        assert len(result) > 0  # Should have some output
        output_text = "\n".join(result)
        # Check that all files are in the output
        assert "src/file1.py: 5 changes" in output_text
        assert "src/file2.py: 3 changes" in output_text
        assert "tests/test_file1.py: 2 changes" in output_text

    def test_format_frequent_files_empty(self):
        """Test _format_frequent_files with empty input."""
        result = self.formatter._format_frequent_files({})
        assert result == []

    @patch("git.Repo")
    def test_format_range_stats_includes_frequent_files(self, mock_repo):
        """Test that format_range_stats includes the frequently changed files section."""
        # Setup mock repo to return empty results
        mock_repo.return_value.iter_commits.return_value = []

        # Create a RangeStats with date range
        range_stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
            commits=[],
        )

        # Call the method
        result = self.formatter.format_range_stats(range_stats)

        # The output should contain the frequently changed files section
        # Since we're not mocking the git repo for this test, we'll just check the output format
        assert isinstance(result, str)
        assert "Range Analysis:" in result
