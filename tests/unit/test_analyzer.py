"""Tests for the analyzer module."""
import subprocess
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from beaconled.core.analyzer import GitAnalyzer
from beaconled.core.models import CommitStats, FileStats, RangeStats


class TestGitAnalyzer(unittest.TestCase):
    """Test cases for GitAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = GitAnalyzer(".")

    @patch('subprocess.run')
    def test_get_commit_stats_success(self, mock_run):
        """Test successful commit analysis."""
        mock_output = (
            "abc123|John Doe|2025-07-20 10:00:00 +0800|Test commit\n"
            "\n"
            "5\t2\tfile1.py\n"
            "10\t0\tfile2.js\n"
        )
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            returncode=0
        )

        result = self.analyzer.get_commit_stats("abc123")

        self.assertIsInstance(result, CommitStats)
        self.assertEqual(result.hash, "abc123")
        self.assertEqual(result.author, "John Doe")
        self.assertEqual(result.message, "Test commit")
        self.assertEqual(result.files_changed, 2)
        self.assertEqual(result.lines_added, 15)
        self.assertEqual(result.lines_deleted, 2)
        self.assertEqual(len(result.files), 2)

    @patch('subprocess.run')
    def test_get_commit_stats_failure(self, mock_run):
        """Test commit analysis with git command failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')

        with self.assertRaises(subprocess.CalledProcessError):
            self.analyzer.get_commit_stats("nonexistent")

    @patch('subprocess.run')
    def test_get_range_analytics_success(self, mock_run):
        """Test successful range analysis."""
        mock_log_output = "abc123\ndef456\nghi789"
        mock_run.return_value = MagicMock(
            stdout=mock_log_output,
            returncode=0
        )

        mock_commit_stats = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime.fromisoformat("2025-07-20T10:00:00+08:00"),
            message="Test commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=5,
            files=[FileStats("test.py", 10, 5, 15)]
        )
        self.analyzer.get_commit_stats = MagicMock(
            return_value=mock_commit_stats
        )

        result = self.analyzer.get_range_analytics("1 week ago")

        self.assertIsInstance(result, RangeStats)
        self.assertEqual(result.total_commits, 3)
        self.assertEqual(result.total_files_changed, 3)
        self.assertEqual(result.total_lines_added, 30)
        self.assertEqual(result.total_lines_deleted, 15)
        self.assertEqual(len(result.commits), 3)
        self.assertEqual(len(result.authors), 1)

    @patch('subprocess.run')
    def test_get_range_analytics_failure(self, mock_run):
        """Test range analysis with git command failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')

        with self.assertRaises(subprocess.CalledProcessError):
            self.analyzer.get_range_analytics("1 week ago")


if __name__ == '__main__':
    unittest.main()
