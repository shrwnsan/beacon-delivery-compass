"""Tests for the CLI module."""
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from beacon.cli import main


class TestCLI(unittest.TestCase):
    """Test cases for CLI functionality."""

    @patch('beacon.cli.GitAnalyzer')
    @patch('sys.argv', ['beacon', '--help'])
    def test_help_output(self, mock_analyzer):
        """Test that help output is displayed."""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)

    @patch('beacon.cli.GitAnalyzer')
    def test_analyze_single_commit(self, mock_analyzer_class):
        """Test analyzing a single commit."""
        # Mock the analyzer and its methods
        mock_analyzer = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer

        # Mock commit stats
        from beacon.core.models import CommitStats, FileStats
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
            with patch('sys.argv', ['beacon', 'abc123']):
                main()

        output = captured_output.getvalue()
        self.assertIn("abc123", output)
        self.assertIn("Test Author", output)
        self.assertIn("Test commit", output)


if __name__ == '__main__':
    unittest.main()
