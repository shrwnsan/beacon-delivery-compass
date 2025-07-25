"""Tests for the analyzer module."""
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, ANY

import git
from beaconled.core.analyzer import GitAnalyzer
from beaconled.core.models import CommitStats, FileStats, RangeStats


class TestGitAnalyzer(unittest.TestCase):
    """Test cases for GitAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = GitAnalyzer(".")

    @patch('git.Repo')
    def test_get_commit_stats_success(self, mock_repo):
        """Test successful commit analysis."""
        # Create mock commit
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc123"
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.message = "Test commit\n\nMore details here"
        
        # Create mock diff
        mock_diff = MagicMock()
        mock_diff.a_path = None
        mock_diff.b_path = "file.txt"
        mock_diff.diff = b"""diff --git a/file.txt b/file.txt
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/file.txt
@@ -0,0 +1 @@
+test
"""
        
        # Set up parent commit for diff
        mock_parent = MagicMock()
        mock_commit.parents = [mock_parent]
        mock_parent.diff.return_value = [mock_diff]
        
        # Set up repo mock
        mock_repo.return_value.commit.return_value = mock_commit
        
        # Call the method under test
        result = self.analyzer.get_commit_stats("abc123")
        
        # Verify results
        self.assertEqual(result.hash, "abc123")
        self.assertEqual(result.author, "Test User <test@example.com>")
        self.assertEqual(result.message, "Test commit")
        self.assertEqual(result.files_changed, 1)
        self.assertEqual(result.lines_added, 1)
        self.assertEqual(result.lines_deleted, 0)  # Only one line added, none deleted
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].path, "file.txt")

    @patch('git.Repo')
    def test_get_commit_stats_failure(self, mock_repo):
        """Test commit analysis with git command failure."""
        # Set up the mock to raise an exception
        mock_repo.return_value.commit.side_effect = git.exc.BadName("Ref 'nonexistent' did not resolve to an object")

        with self.assertRaises(RuntimeError) as context:
            self.analyzer.get_commit_stats("nonexistent")
            
        self.assertIn("Error getting commit stats", str(context.exception))

    @patch('git.Repo')
    def test_date_parsing_variations(self, mock_repo):
        """Test handling of datetime objects from GitPython."""
        test_cases = [
            (datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)),
            (datetime(2025, 7, 20, 10, 0, 0)),
            (datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc).replace(tzinfo=None)),
        ]

        for test_date in test_cases:
            with self.subTest(date=test_date):
                # Create mock commit
                mock_commit = MagicMock()
                mock_commit.hexsha = "abc123"
                mock_commit.author.name = "Test User"
                mock_commit.author.email = "test@example.com"
                mock_commit.authored_datetime = test_date
                mock_commit.message = "Test commit"
                mock_commit.parents = []
                
                # Set up repo mock
                mock_repo.return_value.commit.return_value = mock_commit
                
                # Call the method under test
                result = self.analyzer.get_commit_stats("abc123")
                
                # Verify the date was handled correctly
                self.assertEqual(result.date.year, 2025)
                self.assertEqual(result.date.month, 7)
                self.assertEqual(result.date.day, 20)
                self.assertEqual(result.date.hour, 10)
                self.assertEqual(result.date.minute, 0)
                self.assertEqual(result.date.second, 0)

    @patch('git.Repo')
    def test_invalid_date_fallback(self, mock_repo):
        """Test that invalid dates are handled gracefully."""
        # Create mock commit with invalid date
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc123"
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        
        # Set up the authored_datetime to be invalid
        mock_commit.authored_datetime = None
        
        # Set up parent commit for diff
        mock_parent = MagicMock()
        mock_commit.parents = [mock_parent]
        mock_parent.diff.return_value = []
        
        # Set up repo mock
        mock_repo.return_value.commit.return_value = mock_commit
        
        # Call the method under test
        result = self.analyzer.get_commit_stats("abc123")
        
        # Verify the result is a datetime (fallback to now)
        self.assertIsInstance(result.date, datetime, 
                           "Expected a datetime object as fallback")

    @patch('git.Repo')
    def test_get_range_analytics_success(self, mock_repo):
        """Test successful range analysis."""
        # Create mock commits
        mock_commits = []
        for i in range(3):
            mock_commit = MagicMock()
            mock_commit.hexsha = f"commit_{i}"
            mock_commit.author.name = f"Author {i % 2}"  # Two different authors
            mock_commit.author.email = f"author{i%2}@example.com"
            mock_commit.authored_datetime = datetime(2025, 7, 20 - i, 10, 0, 0, tzinfo=timezone.utc)
            mock_commit.message = f"Commit {i}"
            mock_commits.append(mock_commit)
        
        # Set up repo mock
        mock_repo.return_value.iter_commits.return_value = mock_commits
        
        # Mock get_commit_stats to return consistent stats
        mock_commit_stats = CommitStats(
            hash="abc123",
            author="Test Author <test@example.com>",
            date=datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc),
            message="Test commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=5,
            files=[FileStats("test.py", 10, 5, 15)]
        )
        self.analyzer.get_commit_stats = MagicMock(return_value=mock_commit_stats)

        # Call the method under test
        result = self.analyzer.get_range_analytics("1 week ago")

        # Verify results
        self.assertIsInstance(result, RangeStats)
        self.assertEqual(result.total_commits, 3)
        self.assertEqual(result.total_files_changed, 3)
        self.assertEqual(result.total_lines_added, 30)
        self.assertEqual(result.total_lines_deleted, 15)
        self.assertEqual(len(result.commits), 3)
        self.assertEqual(len(result.authors), 2)  # Two different authors

    @patch('git.Repo')
    def test_get_range_analytics_failure(self, mock_repo):
        """Test range analysis with git command failure."""
        # Set up the mock to raise an exception
        mock_repo.return_value.iter_commits.side_effect = git.GitCommandError("git log", 1)

        with self.assertRaises(RuntimeError) as context:
            self.analyzer.get_range_analytics("1 week ago")
            
        self.assertIn("Git command failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()
