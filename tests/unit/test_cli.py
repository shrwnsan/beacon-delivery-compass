"""Tests for the CLI module."""

import sys
import unittest
from io import StringIO, TextIOWrapper, BytesIO
from unittest.mock import MagicMock, patch, mock_open

from beaconled.cli import main
from beaconled.core.date_errors import DateParseError, DateRangeError


class TestCLI(unittest.TestCase):
    """Test cases for CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        """Clean up after tests."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--help"])
    def test_help_output(self, mock_analyzer):
        """Test that help output is displayed."""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("usage:", sys.stdout.getvalue())

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--version"])
    def test_version_output(self, mock_analyzer):
        """Test that version output is displayed."""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("beaconled 0.2.0", sys.stdout.getvalue())

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--format", "json"])
    def test_json_output_format(self, mock_analyzer):
        """Test JSON output format."""
        # Mock the analyzer to return test data
        mock_analyzer.return_value.get_commit_stats.return_value = MagicMock(
            hash="abc123",
            author="Test User",
            date="2025-01-01T12:00:00+00:00",
            message="Test commit",
            files_changed=2,
            lines_added=5,
            lines_deleted=1,
            files=[],
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            self.assertIn('"hash": "abc123"', output)
            self.assertIn('"author": "Test User"', output)

    @patch("beaconled.cli.StandardFormatter")
    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--range", "v1.0.0..HEAD"])
    def test_range_analysis(self, mock_analyzer, mock_formatter):
        """Test range analysis."""
        # Mock the analyzer to return test data for range analysis
        mock_stats = MagicMock()
        mock_stats.total_commits = 3
        mock_stats.authors = {"User1": 2, "User2": 1}
        mock_analyzer.return_value.get_range_analytics.return_value = mock_stats

        # Mock the formatter to return a simple string
        mock_formatter.return_value.format_range_stats.return_value = (
            "Mocked range stats output"
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            self.assertEqual(output, "Mocked range stats output\n")

    @patch("beaconled.cli.ExtendedFormatter")
    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--format", "extended"])
    def test_extended_output_format(self, mock_analyzer, mock_formatter):
        """Test extended output format."""
        # Mock the analyzer to return test data
        mock_commit = MagicMock(
            hash="abc123",
            author="Test User",
            date="2025-01-01T12:00:00+00:00",
            message="Test commit",
            files_changed=2,
            lines_added=5,
            lines_deleted=1,
            files=[],
        )
        mock_analyzer.return_value.get_commit_stats.return_value = mock_commit

        # Mock the formatter to return a simple string
        mock_formatter.return_value.format_commit_stats.return_value = (
            "Mocked extended output"
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            self.assertEqual(output, "Mocked extended output\n")

    @patch("sys.argv", ["beaconled", "--format", "invalid"])
    def test_invalid_output_format(self):
        """Test handling of invalid output format."""
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2)  # ArgumentParser error code
            self.assertIn("invalid choice", mock_stderr.getvalue())

    @patch("beaconled.cli.GitAnalyzer")
    def test_analyze_single_commit(self, mock_analyzer_class):
        """Test analyzing a single commit."""
        # Mock the analyzer and its methods
        mock_analyzer = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer

        # Mock commit stats
        from beaconled.core.models import CommitStats, FileStats
        from datetime import datetime

        mock_stats = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime.fromisoformat("2025-07-20T10:00:00+08:00"),
            message="Test commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=5,
            files=[FileStats("test.py", 10, 5, 15)],
        )
        mock_analyzer.get_commit_stats.return_value = mock_stats

        # Capture stdout
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            with patch("sys.argv", ["beaconled", "abc123"]):
                main()

        output = captured_output.getvalue()
        self.assertIn("abc123", output)
        self.assertIn("Test Author", output)
        self.assertIn("Test commit", output)

    @patch("beaconled.cli.GitAnalyzer")
    @patch("beaconled.cli.StandardFormatter")
    @patch("sys.argv", ["beaconled", "--repo", "/custom/repo/path"])
    def test_custom_repo_path(self, mock_formatter, mock_analyzer):
        """Test custom repository path."""
        # Create a more complete mock commit stats object
        from beaconled.core.models import CommitStats, FileStats
        from datetime import datetime, timezone

        mock_commit = CommitStats(
            hash="abc123",
            author="Test User",
            date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            message="Test commit",
            files_changed=1,
            lines_added=5,
            lines_deleted=1,
            files=[FileStats("test.txt", 5, 1, 10)],
        )

        # Mock the analyzer to return our test data
        mock_analyzer.return_value.get_commit_stats.return_value = mock_commit
        mock_formatter.return_value.format_commit_stats.return_value = (
            "Formatted output"
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            # Verify the analyzer was called with the custom repo path
            mock_analyzer.assert_called_once_with("/custom/repo/path")
            # Verify the formatter was called with our mock commit
            mock_formatter.return_value.format_commit_stats.assert_called_once_with(
                mock_commit
            )

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--range", "--since", "1w", "--until", "now"])
    @patch("beaconled.cli.StandardFormatter")
    def test_range_with_relative_dates(self, mock_formatter, mock_analyzer):
        """Test range analysis with relative dates."""
        # Mock the analyzer to return test data for range analysis
        mock_stats = MagicMock()
        mock_stats.total_commits = 3
        mock_analyzer.return_value.get_range_analytics.return_value = mock_stats
        mock_formatter.return_value.format_range_stats.return_value = "Mocked output"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            # Verify get_range_analytics was called with the correct arguments
            mock_analyzer.return_value.get_range_analytics.assert_called_once()
            args, kwargs = mock_analyzer.return_value.get_range_analytics.call_args
            self.assertEqual(args[0], "1w")  # since
            self.assertEqual(args[1], "now")  # until
            # Verify the formatter was called with the stats
            mock_formatter.return_value.format_range_stats.assert_called_once_with(
                mock_stats
            )

    @patch("beaconled.cli.GitAnalyzer")
    @patch("beaconled.cli.StandardFormatter")
    @patch(
        "sys.argv",
        ["beaconled", "--range", "--since", "2025-01-01", "--until", "2025-01-31"],
    )
    def test_range_with_absolute_dates(self, mock_formatter, mock_analyzer):
        """Test range analysis with absolute dates."""
        from beaconled.core.models import RangeStats, CommitStats
        from datetime import datetime, timezone

        # Create a mock range stats object
        mock_stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
            total_commits=5,
            total_files_changed=10,
            total_lines_added=50,
            total_lines_deleted=10,
            commits=[],  # Empty list of commits for this test
            authors={"Test User": 5},  # Author stats as a dict
        )

        # Set up mocks
        mock_analyzer.return_value.get_range_analytics.return_value = mock_stats
        mock_formatter.return_value.format_range_stats.return_value = (
            "Range stats output"
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()

            # Verify get_range_analytics was called with the correct arguments
            mock_analyzer.return_value.get_range_analytics.assert_called_once()
            args, kwargs = mock_analyzer.return_value.get_range_analytics.call_args
            self.assertEqual(args[0], "2025-01-01")  # since
            self.assertEqual(args[1], "2025-01-31")  # until

            # Verify the formatter was called with our mock stats
            mock_formatter.return_value.format_range_stats.assert_called_once_with(
                mock_stats
            )

            # Verify the output contains our formatted result
            self.assertEqual(mock_stdout.getvalue().strip(), "Range stats output")

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--range", "--since", "invalid-date"])
    def test_invalid_date_format(self, mock_analyzer):
        """Test handling of invalid date format."""
        # Mock the analyzer to raise DateParseError
        mock_analyzer.return_value.get_range_analytics.side_effect = DateParseError(
            "Invalid date format"
        )

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2)
            self.assertIn("Invalid date format", mock_stderr.getvalue())

    @patch("beaconled.cli.GitAnalyzer")
    @patch(
        "sys.argv",
        ["beaconled", "--range", "--since", "2025-01-31", "--until", "2025-01-01"],
    )
    def test_invalid_date_range(self, mock_analyzer):
        """Test handling of invalid date range (end before start)."""
        from datetime import datetime, timezone

        # Mock the analyzer to raise DateRangeError with required parameters
        start_date = datetime(2025, 1, 31, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_analyzer.return_value.get_range_analytics.side_effect = DateRangeError(
            start_date=start_date,
            end_date=end_date,
            message="End date must be after start date",
        )

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2)
            stderr_output = mock_stderr.getvalue()
            self.assertIn("Error: End date must be after start date", stderr_output)

    @patch("beaconled.cli.GitAnalyzer")
    @patch("beaconled.cli.StandardFormatter")
    @patch("sys.argv", ["beaconled"])  # No arguments, should use defaults
    def test_default_arguments(self, mock_formatter, mock_analyzer):
        """Test CLI with default arguments."""
        from beaconled.core.models import CommitStats, FileStats
        from datetime import datetime, timezone

        # Create a more complete mock commit stats object
        mock_commit = CommitStats(
            hash="abc123",
            author="Test User",
            date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            message="Test commit",
            files_changed=1,
            lines_added=5,
            lines_deleted=1,
            files=[FileStats("test.txt", 5, 1, 10)],
        )

        # Set up mocks
        mock_analyzer.return_value.get_commit_stats.return_value = mock_commit
        mock_formatter.return_value.format_commit_stats.return_value = (
            "Formatted output"
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()

            # Verify the analyzer was called with the default repo path and commit
            mock_analyzer.assert_called_once_with(".")
            mock_analyzer.return_value.get_commit_stats.assert_called_once_with("HEAD")

            # Verify the formatter was called with our mock commit
            mock_formatter.return_value.format_commit_stats.assert_called_once_with(
                mock_commit
            )

            # Verify the output contains our formatted result
            self.assertEqual(mock_stdout.getvalue().strip(), "Formatted output")

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--format", "standard"])
    def test_standard_output_format(self, mock_analyzer):
        """Test standard output format."""
        # Mock the analyzer to return test data
        mock_analyzer.return_value.get_commit_stats.return_value = MagicMock(
            hash="abc123",
            author="Test User",
            date="2025-01-01T12:00:00+00:00",
            message="Test commit",
            files_changed=1,
            lines_added=5,
            lines_deleted=1,
            files=[],
        )

        # Mock the StandardFormatter
        with patch("beaconled.cli.StandardFormatter") as mock_formatter:
            mock_formatter.return_value.format_commit_stats.return_value = (
                "Formatted output"
            )
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                self.assertEqual(mock_stdout.getvalue().strip(), "Formatted output")

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--format", "json"])
    def test_json_output_encoding(self, mock_analyzer):
        """Test JSON output with special characters that might cause encoding issues."""
        # Mock the analyzer to return test data with special characters
        mock_analyzer.return_value.get_commit_stats.return_value = MagicMock(
            hash="abc123",
            author="Tést Usér",  # Special characters
            date="2025-01-01T12:00:00+00:00",
            message="Tést commit with spéciál chàracters",
            files_changed=1,
            lines_added=5,
            lines_deleted=1,
            files=[],
        )

        # Create a mock stdout that simulates a non-Unicode terminal
        class MockStdOut(StringIO):
            def write(self, text):
                # Just pass through the text - the JSON formatter should handle encoding
                return super().write(text)

        with patch("sys.stdout", new_callable=MockStdOut) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

            # Verify it's valid JSON
            import json

            parsed = json.loads(output)

            # The JSON should contain the original Unicode characters
            self.assertEqual(parsed["author"], "Tést Usér")
            self.assertEqual(parsed["message"], "Tést commit with spéciál chàracters")

            # The raw output should contain the properly escaped Unicode sequences
            self.assertIn("T\\u00e9st Us\\u00e9r", output)  # Escaped Unicode in JSON
            self.assertIn(
                "sp\\u00e9ci\\u00e1l ch\\u00e0racters", output
            )  # Escaped Unicode in JSON

    @patch("beaconled.cli.GitAnalyzer")
    @patch("sys.argv", ["beaconled", "--range", "--since", "2025-01-01"])
    def test_error_message_handling(self, mock_analyzer):
        """Test proper error message handling and formatting."""
        # Mock the analyzer to raise an exception
        error_msg = "Failed to analyze repository: Permission denied"
        mock_analyzer.return_value.get_range_analytics.side_effect = Exception(
            error_msg
        )

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)
            self.assertIn(error_msg, mock_stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
