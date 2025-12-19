"""Additional test cases to improve coverage for analyzer.py."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Import the actual git module for exception classes
try:
    from git.exc import BadName, GitCommandError, InvalidGitRepositoryError

    GIT_AVAILABLE = True
except ImportError:
    # Define mock exception classes if git is not available
    class GitCommandError(Exception):
        def __init__(self, cmd, status, stderr=None, stdout=None):
            self.cmd = cmd
            self.status = status
            self.stderr = stderr
            self.stdout = stdout
            super().__init__(f"Command '{cmd}' returned non-zero exit status {status}")

    class BadName(Exception):
        pass

    class InvalidGitRepositoryError(Exception):
        pass

    GIT_AVAILABLE = False

from beaconled.core.analyzer import GitAnalyzer, InvalidRepositoryError
from beaconled.exceptions import InternalError
from beaconled.core.date_errors import DateRangeError


class TestGitAnalyzerCoverage(unittest.TestCase):
    """Test GitAnalyzer class with a focus on covering untested code paths."""

    def setUp(self):
        """Set up test fixtures before each test method (kept minimal)."""
        # Intentionally avoid patching the entire git module here to keep
        # git.exc exception classes intact for exception handling tests.
        # Each test will patch Path/git.Repo as needed and construct analyzers locally.

    def tearDown(self):
        """Clean up after each test method."""
        # No global patchers started in setUp; nothing to stop here.

    def test_validate_repo_path_nonexistent(self):
        """Test _validate_repo_path with nonexistent path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = os.path.join(temp_dir, "nonexistent")
            # Bypass __init__ so we can call _validate_repo_path directly
            analyzer = GitAnalyzer.__new__(GitAnalyzer)
            with self.assertRaises(InvalidRepositoryError) as cm:
                analyzer._validate_repo_path(nonexistent_path)
            self.assertIn("does not exist", str(cm.exception))

    def test_validate_repo_path_not_directory(self):
        """Test _validate_repo_path with path that is not a directory."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_dir", return_value=False),
            patch("pathlib.Path.is_file", return_value=True),
        ):
            # The error should be raised during initialization
            with self.assertRaises(InvalidRepositoryError) as cm:
                GitAnalyzer("/fake/file.txt")
            # Verify the error message contains both reason and path
            error_msg = str(cm.exception)
            self.assertIn("is not a directory", error_msg)
            # Check for path component (cross-platform compatible)
            self.assertIn("file.txt", error_msg)

    @patch("git.Repo")
    def test_validate_repo_path_not_git_repo(self, mock_repo):
        """Test validation with a directory that is not a git repository."""
        from git.exc import InvalidGitRepositoryError

        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure git.Repo to raise an error when trying to open the directory
            mock_repo.side_effect = InvalidGitRepositoryError("Not a git repository")

            # Expect InvalidRepositoryError during initialization
            with self.assertRaises(InvalidRepositoryError) as cm:
                GitAnalyzer(temp_dir)

            # Verify the error message contains information about not being a git repo
            self.assertIn("Not a git repository", str(cm.exception))

    def test_get_commit_stats_invalid_hash(self):
        """Test get_commit_stats with invalid commit hash."""
        from git.exc import BadName

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real git-like directory structure
            git_dir = os.path.join(temp_dir, ".git")
            os.makedirs(git_dir)

            # Create a mock repository
            mock_repo = MagicMock()
            mock_repo.commit.side_effect = BadName("bad object")

            # Patch git.Repo to return our mock
            with patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo):
                analyzer = GitAnalyzer(temp_dir)
                # git.BadName should be caught and converted to InternalError
                with self.assertRaises(InternalError) as cm:
                    analyzer.get_commit_stats("invalid-hash")
                self.assertIn("bad object", str(cm.exception))

    def test_get_commit_stats_git_command_error(self):
        """Test get_commit_stats with GitCommandError."""
        from git.exc import GitCommandError

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real git-like directory structure
            git_dir = os.path.join(temp_dir, ".git")
            os.makedirs(git_dir)

            # Create a mock repository
            mock_repo = MagicMock()
            # GitCommandError(command, status, stderr=None, stdout=None)
            mock_repo.commit.side_effect = GitCommandError(
                ["log"],
                128,
                stderr="fatal: bad object HEAD",
            )

            # Patch git.Repo to return our mock
            with patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo):
                analyzer = GitAnalyzer(temp_dir)
                # In current implementation, this ends as an InternalError
                with self.assertRaises(InternalError) as cm:
                    analyzer.get_commit_stats("invalid-hash")
                self.assertIn("bad object", str(cm.exception))

    def test_get_range_analytics_empty_repo(self):
        """Test get_range_analytics with an empty repository."""
        from unittest.mock import MagicMock, patch

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real git-like directory structure
            git_dir = os.path.join(temp_dir, ".git")
            os.makedirs(git_dir)

            # Create a mock repository with no commits
            mock_repo = MagicMock()
            mock_repo.iter_commits.return_value = []

            # Patch git.Repo to return our mock
            with patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo):
                analyzer = GitAnalyzer(temp_dir)

                # Call the method with a date range
                result = analyzer.get_range_analytics("2023-01-01", "2023-12-31")

                # Verify the result
                self.assertEqual(result.total_commits, 0)
                self.assertEqual(result.total_files_changed, 0)
                self.assertEqual(result.total_lines_added, 0)
                self.assertEqual(result.total_lines_deleted, 0)

    def test_get_range_analytics_git_command_error(self):
        """Test get_range_analytics with GitCommandError."""
        from git.exc import GitCommandError

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real git-like directory structure
            git_dir = os.path.join(temp_dir, ".git")
            os.makedirs(git_dir)

            # Create a mock repository
            mock_repo = MagicMock()
            # Simulate git failing to iterate commits due to bad revision
            mock_repo.iter_commits.side_effect = GitCommandError(
                ["log"],
                128,
                stderr="fatal: bad revision",
            )

            # Patch git.Repo to return our mock
            with patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo):
                analyzer = GitAnalyzer(temp_dir)

                # Call the method with a date range
                rs = analyzer.get_range_analytics("2023-01-01", "2023-12-31")

                # Verify the result
                self.assertEqual(rs.total_commits, 0)
                self.assertEqual(rs.total_files_changed, 0)
                self.assertEqual(rs.total_lines_added, 0)
                self.assertEqual(rs.total_lines_deleted, 0)

    def test_get_range_analytics_invalid_date_range(self):
        """Test get_range_analytics with invalid date range."""

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real git-like directory structure
            git_dir = os.path.join(temp_dir, ".git")
            os.makedirs(git_dir)

            # Create a mock repository
            mock_repo = MagicMock()

            # Patch git.Repo to return our mock
            with patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo):
                analyzer = GitAnalyzer(temp_dir)

                # Test with start date after end date
                with self.assertRaises(DateRangeError) as cm:
                    analyzer.get_range_analytics("2025-01-31", "2025-01-01")
                msg = str(cm.exception)
                self.assertIn("Invalid date range", msg)
                self.assertIn("before start date", msg)

    def test_is_valid_date_string_edge_cases(self):
        """Test _is_valid_date_string with edge cases."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)
        # Test empty string
        self.assertFalse(analyzer._is_valid_date_string(""))

        # Test very long string
        self.assertFalse(analyzer._is_valid_date_string("a" * 100))

        # Test invalid date format
        self.assertFalse(analyzer._is_valid_date_string("2025/01/01"))

        # Test valid HEAD
        self.assertTrue(analyzer._is_valid_date_string("HEAD"))


if __name__ == "__main__":
    unittest.main()
