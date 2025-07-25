"""Tests for the CLI module."""
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from beaconled.cli import main


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

    @patch('beaconled.cli.GitAnalyzer')
    @patch('sys.argv', ['beaconled', '--help'])
    def test_help_output(self, mock_analyzer):
        """Test that help output is displayed."""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn('usage:', sys.stdout.getvalue())

    @patch('beaconled.cli.GitAnalyzer')
    @patch('sys.argv', ['beaconled', '--version'])
    def test_version_output(self, mock_analyzer):
        """Test that version output is displayed."""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn('beaconled 0.2.0', sys.stdout.getvalue())

    @patch('beaconled.cli.GitAnalyzer')
    @patch('sys.argv', ['beaconled', '--format', 'json'])
    def test_json_output_format(self, mock_analyzer):
        """Test JSON output format."""
        # Mock the analyzer to return test data
        mock_analyzer.return_value.get_commit_stats.return_value = MagicMock(
            hash='abc123',
            author='Test User',
            date='2025-01-01T12:00:00+00:00',
            message='Test commit',
            files_changed=2,
            lines_added=5,
            lines_deleted=1,
            files=[]
        )
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            self.assertIn('"hash": "abc123"', output)
            self.assertIn('"author": "Test User"', output)

    @patch('beaconled.cli.StandardFormatter')
    @patch('beaconled.cli.GitAnalyzer')
    @patch('sys.argv', ['beaconled', '--range', 'v1.0.0..HEAD'])
    def test_range_analysis(self, mock_analyzer, mock_formatter):
        """Test range analysis."""
        # Mock the analyzer to return test data for range analysis
        mock_stats = MagicMock()
        mock_stats.total_commits = 3
        mock_stats.authors = {'User1': 2, 'User2': 1}
        mock_analyzer.return_value.get_range_analytics.return_value = mock_stats
        
        # Mock the formatter to return a simple string
        mock_formatter.return_value.format_range_stats.return_value = "Mocked range stats output"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            self.assertEqual(output, "Mocked range stats output\n")

    @patch('beaconled.cli.ExtendedFormatter')
    @patch('beaconled.cli.GitAnalyzer')
    @patch('sys.argv', ['beaconled', '--format', 'extended'])
    def test_extended_output_format(self, mock_analyzer, mock_formatter):
        """Test extended output format."""
        # Mock the analyzer to return test data
        mock_commit = MagicMock(
            hash='abc123',
            author='Test User',
            date='2025-01-01T12:00:00+00:00',
            message='Test commit',
            files_changed=2,
            lines_added=5,
            lines_deleted=1,
            files=[]
        )
        mock_analyzer.return_value.get_commit_stats.return_value = mock_commit
        
        # Mock the formatter to return a simple string
        mock_formatter.return_value.format_commit_stats.return_value = "Mocked extended output"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            self.assertEqual(output, "Mocked extended output\n")

    @patch('sys.argv', ['beaconled', '--format', 'invalid'])
    def test_invalid_output_format(self):
        """Test handling of invalid output format."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2)  # ArgumentParser error code
            self.assertIn('invalid choice', mock_stderr.getvalue())

    @patch('beaconled.cli.GitAnalyzer')
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
            files=[FileStats("test.py", 10, 5, 15)]
        )
        mock_analyzer.get_commit_stats.return_value = mock_stats

        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            with patch('sys.argv', ['beaconled', 'abc123']):
                main()

        output = captured_output.getvalue()
        self.assertIn("abc123", output)
        self.assertIn("Test Author", output)
        self.assertIn("Test commit", output)


if __name__ == '__main__':
    unittest.main()
