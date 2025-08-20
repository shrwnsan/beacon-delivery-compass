"""Additional test cases to improve coverage for analyzer.py."""

import unittest
from datetime import datetime, timezone
from pathlib import Path
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
        with (
            patch("pathlib.Path.exists", return_value=False),
            patch("pathlib.Path.resolve", return_value=Path("/nonexistent/path")),
        ):
            # Bypass __init__ so we can call _validate_repo_path directly
            analyzer = GitAnalyzer.__new__(GitAnalyzer)
            with self.assertRaises(InvalidRepositoryError) as cm:
                analyzer._validate_repo_path("/nonexistent/path")
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

    @patch("beaconled.core.analyzer.Path")
    @patch("beaconled.core.analyzer.git.Repo")
    def test_validate_repo_path_not_git_repo(self, mock_repo, mock_path_class):
        """Test _validate_repo_path with directory that is not a git repo."""
        from git.exc import InvalidGitRepositoryError

        # Configure the mock Path instance
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True
        mock_path.resolve.return_value = mock_path

        # Configure the .git path mock
        mock_git_path = MagicMock()
        mock_git_path.exists.return_value = False

        # Make __truediv__ return the mock_git_path for '.git' and mock_path for others
        def truediv_side_effect(other):
            if other == ".git":
                return mock_git_path
            return mock_path

        mock_path.__truediv__.side_effect = truediv_side_effect
        mock_path_class.return_value = mock_path

        # Configure the mock Repo to raise InvalidGitRepositoryError
        mock_repo.side_effect = InvalidGitRepositoryError("Not a git repository")

        # The error should be raised during initialization
        with self.assertRaises(InvalidRepositoryError) as cm:
            GitAnalyzer("/fake/repo")

        # Verify the error message
        self.assertIn("Not a git repository", str(cm.exception))

    def test_get_commit_stats_invalid_hash(self):
        """Test get_commit_stats with invalid commit hash."""
        from git.exc import BadName

        # Create a mock repository
        mock_repo = MagicMock()
        mock_repo.commit.side_effect = BadName("bad object")

        # Patch Path so constructor validation passes, and patch Repo
        with (
            patch("beaconled.core.analyzer.Path") as mock_path_class,
            patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo),
        ):
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = True
            mock_path.resolve.return_value = mock_path
            mock_git_dir = MagicMock()
            mock_git_dir.exists.return_value = True

            def _truediv(other):
                return mock_git_dir if other == ".git" else mock_path

            mock_path.__truediv__.side_effect = _truediv
            mock_path_class.return_value = mock_path

            analyzer = GitAnalyzer("/fake/repo")
            # git.GitCommandError should bubble to the outer handler and be mapped to RuntimeError
            with self.assertRaises(RuntimeError) as cm:
                analyzer.get_commit_stats("invalid-hash")
            self.assertIn("bad object", str(cm.exception))

    def test_get_commit_stats_git_command_error(self):
        """Test get_commit_stats with GitCommandError."""
        from git.exc import GitCommandError

        # Create a mock repository
        mock_repo = MagicMock()
        # GitCommandError(command, status, stderr=None, stdout=None)
        mock_repo.commit.side_effect = GitCommandError(
            ["log"],
            128,
            stderr="fatal: bad object HEAD",
        )

        # Patch Path so constructor validation passes, and patch Repo
        with (
            patch("beaconled.core.analyzer.Path") as mock_path_class,
            patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo),
        ):
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = True
            mock_path.resolve.return_value = mock_path
            # Simulate .git exists to skip opening Repo during validation
            mock_git_dir = MagicMock()
            mock_git_dir.exists.return_value = True

            def _truediv(other):
                return mock_git_dir if other == ".git" else mock_path

            mock_path.__truediv__.side_effect = _truediv
            mock_path_class.return_value = mock_path

            analyzer = GitAnalyzer("/fake/repo")
            # In current implementation, this ends as a RuntimeError
            with self.assertRaises(RuntimeError) as cm:
                analyzer.get_commit_stats("invalid-hash")
            self.assertIn("bad object", str(cm.exception))

    def test_get_range_analytics_empty_repo(self):
        """Test get_range_analytics with an empty repository."""
        from unittest.mock import MagicMock, patch

        # Create a mock repository with no commits
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = []

        # Patch the GitAnalyzer to use our mock repository and mock datetime
        with (
            patch("beaconled.core.analyzer.Path") as mock_path_class,
            patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo),
            patch("beaconled.core.analyzer.datetime") as mock_datetime,
        ):
            # Set up the mock datetime
            mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kw: (
                datetime(*args, **kw, tzinfo=timezone.utc)
                if "tzinfo" in kw or (len(args) > 6 and args[6] is not None)
                else datetime(
                    *args,
                    tzinfo=timezone.utc,
                    **{k: v for k, v in kw.items() if k != "tzinfo"},
                )
            )

            # Create an analyzer with our mocked repository
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = True
            mock_path.resolve.return_value = mock_path
            mock_git_dir = MagicMock()
            mock_git_dir.exists.return_value = True

            def _truediv(other):
                return mock_git_dir if other == ".git" else mock_path

            mock_path.__truediv__.side_effect = _truediv
            mock_path_class.return_value = mock_path

            analyzer = GitAnalyzer("/fake/repo")

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

        # Create a mock repository
        mock_repo = MagicMock()
        # Simulate git failing to iterate commits due to bad revision
        mock_repo.iter_commits.side_effect = GitCommandError(
            ["log"],
            128,
            stderr="fatal: bad revision",
        )

        # Patch the GitAnalyzer to use our mock repository and mock datetime
        with (
            patch("beaconled.core.analyzer.Path") as mock_path_class,
            patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo),
            patch("beaconled.core.analyzer.datetime") as mock_datetime,
        ):
            # Set up the mock datetime
            mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kw: (
                datetime(*args, **kw, tzinfo=timezone.utc)
                if "tzinfo" in kw or (len(args) > 6 and args[6] is not None)
                else datetime(
                    *args,
                    tzinfo=timezone.utc,
                    **{k: v for k, v in kw.items() if k != "tzinfo"},
                )
            )

            # Create an analyzer with our mocked repository
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = True
            mock_path.resolve.return_value = mock_path
            mock_git_dir = MagicMock()
            mock_git_dir.exists.return_value = True

            def _truediv(other):
                return mock_git_dir if other == ".git" else mock_path

            mock_path.__truediv__.side_effect = _truediv
            mock_path_class.return_value = mock_path

            analyzer = GitAnalyzer("/fake/repo")

            # Call the method with a date range
            rs = analyzer.get_range_analytics("2023-01-01", "2023-12-31")

            # Verify the result
            self.assertEqual(rs.total_commits, 0)
            self.assertEqual(rs.total_files_changed, 0)
            self.assertEqual(rs.total_lines_added, 0)
            self.assertEqual(rs.total_lines_deleted, 0)

    def test_get_range_analytics_invalid_date_range(self):
        """Test get_range_analytics with invalid date range."""

        # Create a mock repository
        mock_repo = MagicMock()

        # Patch the GitAnalyzer to use our mock repository and mock datetime
        with (
            patch("beaconled.core.analyzer.Path") as mock_path_class,
            patch("beaconled.core.analyzer.git.Repo", return_value=mock_repo),
            patch("beaconled.core.analyzer.datetime") as mock_datetime,
        ):
            # Set up the mock datetime to return fixed times
            mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kw: (
                datetime(*args, **kw, tzinfo=timezone.utc)
                if "tzinfo" in kw or (len(args) > 6 and args[6] is not None)
                else datetime(
                    *args,
                    tzinfo=timezone.utc,
                    **{k: v for k, v in kw.items() if k != "tzinfo"},
                )
            )

            # Create an analyzer with our mocked repository
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = True
            mock_path.resolve.return_value = mock_path
            mock_git_dir = MagicMock()
            mock_git_dir.exists.return_value = True

            def _truediv(other):
                return mock_git_dir if other == ".git" else mock_path

            mock_path.__truediv__.side_effect = _truediv
            mock_path_class.return_value = mock_path

            analyzer = GitAnalyzer("/fake/repo")

            # Test with start date after end date
            with self.assertRaises(ValueError) as cm:
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
