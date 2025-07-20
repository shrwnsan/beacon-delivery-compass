"""Tests for the analyzer module."""
import unittest
import subprocess
from unittest.mock import patch, MagicMock
from beacon.core.analyzer import GitAnalyzer
from beacon.core.models import CommitStats, FileStats


class TestGitAnalyzer(unittest.TestCase):
    """Test cases for GitAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = GitAnalyzer(".")

    @patch('subprocess.run')
    def test_get_commit_stats_success(self, mock_run):
        """Test successful commit analysis."""
        # Mock git show output
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


if __name__ == '__main__':
    unittest.main()