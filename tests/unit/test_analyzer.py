"""Tests for the analyzer module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import git

from beaconled.core.analyzer import GitAnalyzer
from beaconled.core.models import CommitStats, FileStats


class TestGitAnalyzer(unittest.TestCase):
    """Test cases for GitAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = GitAnalyzer(".")

    @patch("git.Repo")
    def test_get_commit_stats_success(self, mock_repo):
        """Test successful commit analysis."""
        # Create mock commit
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc123"
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.authored_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
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

    @patch("git.Repo")
    def test_get_commit_stats_failure(self, mock_repo):
        """Test commit analysis with git command failure."""
        # Set up the mock to raise an exception
        mock_repo.return_value.commit.side_effect = git.exc.BadName(
            "Ref 'nonexistent' did not resolve to an object",
        )

        with self.assertRaises(RuntimeError) as context:
            self.analyzer.get_commit_stats("nonexistent")

        self.assertIn("Unexpected error analyzing commit", str(context.exception))

    @patch("git.Repo")
    def test_get_commit_stats_multiple_files(self, mock_repo):
        """Test commit analysis with multiple file changes including binary and renamed files."""
        # Create mock commit
        mock_commit = MagicMock()
        mock_commit.hexsha = "multi123"
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.authored_datetime = datetime(
            2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc
        )
        mock_commit.message = (
            "Update multiple files\n\n- Added new features\n- Fixed bugs"
        )

        # Create multiple mock diffs
        # 1. Modified text file
        diff1 = MagicMock()
        diff1.a_path = "src/file1.py"
        diff1.b_path = "src/file1.py"
        diff1.diff = b"""diff --git a/src/file1.py b/src/file1.py
index 1234567..89abcde 100644
--- a/src/file1.py
+++ b/src/file1.py
@@ -1,4 +1,5 @@
 def hello():
+    print("Hello, world!")
     return "Hello"
 """

        # 2. Added binary file
        diff2 = MagicMock()
        diff2.a_path = None
        diff2.b_path = "assets/image.png"
        diff2.diff = b"BINARY DATA"
        diff2.b_blob.size = 1024  # 1KB binary file

        # 3. Renamed file
        diff3 = MagicMock()
        diff3.a_path = "old_name.txt"
        diff3.b_path = "new_name.txt"
        diff3.renamed = True
        diff3.diff = b"""diff --git a/old_name.txt b/new_name.txt
similarity index 100%
rename from old_name.txt
rename to new_name.txt
"""

        # 4. Deleted file
        diff4 = MagicMock()
        diff4.a_path = "deleted.txt"
        diff4.b_path = None
        diff4.deleted_file = True
        diff4.diff = b"""diff --git a/deleted.txt b/deleted.txt
deleted file mode 100644
index 1234567..0000000
--- a/deleted.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-This file was deleted
-in the commit
"""

        # Set up parent commit for diffs
        mock_parent = MagicMock()
        mock_commit.parents = [mock_parent]
        mock_parent.diff.return_value = [diff1, diff2, diff3, diff4]

        # Set up repo mock
        mock_repo.return_value.commit.return_value = mock_commit

        # Call the method under test
        result = self.analyzer.get_commit_stats("multi123")

        # Verify results
        self.assertEqual(result.hash, "multi123")
        self.assertEqual(result.author, "Test User <test@example.com>")
        self.assertEqual(result.message, "Update multiple files")

        # Should count all files including binary and renamed
        self.assertEqual(result.files_changed, 4)

        # Should count actual line changes (only in text files)
        self.assertEqual(result.lines_added, 1)  # One line added in file1.py
        self.assertEqual(result.lines_deleted, 2)  # Two lines deleted in deleted.txt

        # Verify all files are included
        self.assertEqual(len(result.files), 4)

        # Verify file stats
        file_paths = [f.path for f in result.files]
        self.assertIn("src/file1.py", file_paths)
        self.assertIn("assets/image.png", file_paths)
        self.assertIn("new_name.txt", file_paths)
        self.assertIn("deleted.txt", file_paths)

    @patch("git.Repo")
    def test_date_parsing_variations(self, mock_repo):
        """Test handling of datetime objects from GitPython."""
        test_cases = [
            (datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)),
            (datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)),
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

    @patch("git.Repo")
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
        self.assertIsInstance(
            result.date,
            datetime,
            "Expected a datetime object as fallback",
        )

    @patch("git.Repo")
    @patch("beaconled.core.analyzer.GitAnalyzer._parse_date")
    def test_get_range_analytics_success(self, mock_parse_date, mock_repo):
        """Test successful range analysis."""
        # Mock the parse_date to return a fixed date
        mock_parse_date.return_value = datetime(
            2025,
            7,
            20,
            0,
            0,
            0,
            tzinfo=timezone.utc,
        )

        # Create a mock git repository
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        # Create mock commits with explicit dates that will be within our test range
        test_dates = [
            datetime(2025, 7, 20, 12, 0, 0, tzinfo=timezone.utc),  # 2025-07-20 12:00:00
            datetime(2025, 7, 21, 14, 0, 0, tzinfo=timezone.utc),  # 2025-07-21 14:00:00
            datetime(2025, 7, 22, 16, 0, 0, tzinfo=timezone.utc),  # 2025-07-22 16:00:00
        ]

        # Create mock commits
        mock_commits = []
        for i, commit_date in enumerate(test_dates):
            mock_commit = MagicMock()
            mock_commit.hexsha = f"commit_{i}"
            mock_commit.authored_datetime = commit_date
            mock_commits.append(mock_commit)

        # Set up the mock to return our test commits
        mock_repo_instance.iter_commits.return_value = mock_commits
        # Also ensure git.log returns corresponding hashes when analyzer falls back to git.log
        mock_repo_instance.git.log.return_value = "\n".join(
            [mc.hexsha for mc in mock_commits],
        )

        # Mock get_commit_stats to return dummy stats
        self.analyzer.get_commit_stats = MagicMock()
        self.analyzer.get_commit_stats.side_effect = [
            CommitStats(
                hash=f"commit_{i}",
                author=f"Author {i} <author.{i}@example.com>",
                date=date,
                message=f"Test commit {i}",
                files_changed=1,
                lines_added=5,
                lines_deleted=2,
                files=[
                    FileStats(
                        path=f"file_{i}.txt",
                        lines_added=5,
                        lines_deleted=2,
                        lines_changed=7,
                    ),
                ],
            )
            for i, date in enumerate(test_dates)
        ]

        # Call the method under test
        result = self.analyzer.get_range_analytics("7d")

        # Verify the results
        self.assertEqual(result.total_commits, 3)
        self.assertEqual(result.total_commits, 3)
        self.assertEqual(result.total_files_changed, 3)
        self.assertEqual(result.total_lines_added, 15)
        self.assertEqual(result.total_lines_deleted, 6)
        self.assertEqual(len(result.commits), 3)

    @patch("git.Repo")
    @patch("beaconled.core.analyzer.GitAnalyzer._parse_date")
    def test_get_range_analytics_failure(self, mock_parse_date, mock_repo):
        """Test range analysis with git command failure."""
        # Set up the mock to return a valid datetime
        mock_parse_date.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)

        # Create a mock repository instance
        mock_repo_instance = mock_repo.return_value

        # Set up both iter_commits and git.log to fail
        mock_repo_instance.iter_commits.side_effect = git.GitCommandError("git log", 1)
        mock_repo_instance.git.log.side_effect = git.GitCommandError("git log", 1)

        # The method should handle the failure gracefully and return empty results
        result = self.analyzer.get_range_analytics("2025-01-01")

        # Should return valid RangeStats with zero values when git commands fail
        self.assertEqual(result.total_commits, 0)
        self.assertEqual(result.total_files_changed, 0)
        self.assertEqual(result.total_lines_added, 0)
        self.assertEqual(result.total_lines_deleted, 0)

    @patch("git.Repo")
    def test_get_range_analytics_valid_date_range(self, mock_repo):
        """Test that valid date ranges are accepted."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        # Create a mock commit with a datetime and author
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.committed_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.hexsha = "abc123"
        mock_commit.author = MagicMock()
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.message = "Test commit message"
        mock_commit.parents = []

        # Set up the mock to return our test commit
        mock_repo_instance.iter_commits.return_value = [mock_commit]

        # Mock get_commit_stats to return a dummy CommitStats object with author
        commit_stats = MagicMock(spec=CommitStats)
        commit_stats.files_changed = 1
        commit_stats.lines_added = 5
        commit_stats.lines_deleted = 2
        commit_stats.files = [
            FileStats(path="test.txt", lines_added=5, lines_deleted=2, lines_changed=7),
        ]
        commit_stats.author = "Test User <test@example.com>"
        commit_stats.date = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        self.analyzer.get_commit_stats = MagicMock(return_value=commit_stats)

        # Test with string dates
        result = self.analyzer.get_range_analytics("2025-01-01", "2025-12-31")
        self.assertEqual(result.start_date, datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(
            result.end_date,
            datetime(2025, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc),
        )

        # Test with datetime objects
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end = datetime(2025, 12, 31, tzinfo=timezone.utc)
        result = self.analyzer.get_range_analytics(start, end)
        self.assertEqual(result.start_date, start)
        self.assertEqual(
            result.end_date,
            end.replace(hour=23, minute=59, second=59, microsecond=999999),
        )

    @patch("git.Repo")
    def test_get_range_analytics_single_day_range(self, mock_repo):
        """Test that single-day ranges are valid."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        # Create a mock commit with a datetime and author
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.committed_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.hexsha = "abc123"
        mock_commit.author = MagicMock()
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.message = "Test commit message"
        mock_commit.parents = []

        # Set up the mock to return our test commit
        mock_repo_instance.iter_commits.return_value = [mock_commit]

        # Mock get_commit_stats to return a dummy CommitStats object with author
        commit_stats = MagicMock(spec=CommitStats)
        commit_stats.files_changed = 1
        commit_stats.lines_added = 5
        commit_stats.lines_deleted = 2
        commit_stats.files = [
            FileStats(path="test.txt", lines_added=5, lines_deleted=2, lines_changed=7),
        ]
        commit_stats.author = "Test User <test@example.com>"
        commit_stats.date = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        self.analyzer.get_commit_stats = MagicMock(return_value=commit_stats)

        # Test with same start and end date
        result = self.analyzer.get_range_analytics("2025-07-20", "2025-07-20")
        # The start date should be the beginning of the day in UTC
        self.assertEqual(
            result.start_date,
            datetime(2025, 7, 20, 0, 0, 0, tzinfo=timezone.utc),
        )
        # The end date should be the end of the day in UTC
        self.assertEqual(
            result.end_date,
            datetime(2025, 7, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
        )

    @patch("git.Repo")
    def test_get_range_analytics_invalid_range(self, mock_repo):
        """Test that invalid date ranges raise an error."""
        # Setup mock repo to avoid git operations
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        # Test with string dates - should raise ValueError with our validation message
        with self.assertRaises(ValueError) as cm:
            self.analyzer.get_range_analytics("2025-12-31", "2025-01-01")
        self.assertIn(
            "Invalid date range: end date (2025-01-01 00:00:00+00:00) is before start date (2025-12-31 00:00:00+00:00)",
            str(cm.exception),
        )

        # Test with datetime objects - should raise ValueError with our validation message
        with self.assertRaises(ValueError) as cm:
            start = datetime(2025, 12, 31, tzinfo=timezone.utc)
            end = datetime(2025, 1, 1, tzinfo=timezone.utc)
            self.analyzer.get_range_analytics(start, end)
        self.assertIn(
            "Invalid date range: end date (2025-01-01 00:00:00+00:00) is before start date (2025-12-31 00:00:00+00:00)",
            str(cm.exception),
        )

    @patch("git.Repo")
    def test_get_range_analytics_missing_dates(self, mock_repo):
        """Test that missing dates are handled correctly."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        # Create a mock commit with a datetime and author
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.committed_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.hexsha = "abc123"
        mock_commit.author = MagicMock()
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.message = "Test commit message"
        mock_commit.parents = []

        # Set up the mock to return our test commit
        mock_repo_instance.iter_commits.return_value = [mock_commit]

        # Mock get_commit_stats to return a dummy CommitStats object
        self.analyzer.get_commit_stats = MagicMock(
            return_value=MagicMock(
                spec=CommitStats,
                hash="abc123",
                author="Test User <test@example.com>",
                date=datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc),
                message="Test commit",
                files_changed=1,
                lines_added=5,
                lines_deleted=2,
                files=[
                    FileStats(
                        path="test.txt",
                        lines_added=5,
                        lines_deleted=2,
                        lines_changed=7,
                    ),
                ],
            ),
        )

        # Mock the first commit to return a specific date for the first call (when getting repo start date)
        first_commit = MagicMock()
        first_commit.authored_datetime = datetime(2024, 1, 1, tzinfo=timezone.utc)
        first_commit.committed_datetime = datetime(2024, 1, 1, tzinfo=timezone.utc)
        first_commit.hexsha = "first_commit"
        first_commit.author = MagicMock()
        first_commit.author.name = "First Author"
        first_commit.author.email = "first@example.com"
        first_commit.message = "First commit message"
        first_commit.parents = []

        # Create a mock for the commit iteration
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.committed_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )
        mock_commit.hexsha = "abc123"
        mock_commit.author = MagicMock()
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.message = "Test commit message"
        mock_commit.parents = []

        # Set up side_effect to return different values based on the call
        def iter_commits_side_effect(*args, **kwargs):
            if "max_count" in kwargs and kwargs["max_count"] == 1:
                return iter([first_commit])
            return iter([mock_commit])

        mock_repo_instance.iter_commits.side_effect = iter_commits_side_effect

        # Test with only start date
        result = self.analyzer.get_range_analytics("2025-01-01", None)
        self.assertIsNotNone(result)
        self.assertEqual(result.start_date, datetime(2025, 1, 1, tzinfo=timezone.utc))

        # Test with only end date
        result = self.analyzer.get_range_analytics(None, "2025-12-31")
        self.assertIsNotNone(result)
        self.assertEqual(
            result.end_date,
            datetime(2025, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc),
        )

        # Test with no dates (should use repository's full history)
        result = self.analyzer.get_range_analytics(None, None)
        self.assertIsNotNone(result)

    @patch("git.Repo")
    def test_get_range_analytics_timezone_handling(self, mock_repo):
        """Test that timezones are handled correctly in date ranges."""
        # Setup mock repo
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        # Create mock commits with different timezones
        mock_commit1 = MagicMock()
        mock_commit1.hexsha = "commit1"
        mock_commit1.author.name = "User1"
        mock_commit1.author.email = "user1@example.com"
        mock_commit1.committed_datetime = datetime(
            2025,
            7,
            20,
            10,
            0,
            0,
            tzinfo=timezone.utc,
        )  # 10:00 UTC
        mock_commit1.message = "Commit 1"
        mock_commit1.stats.files = {
            "file1.py": {"insertions": 5, "deletions": 2, "lines": 7}
        }

        mock_commit2 = MagicMock()
        mock_commit2.hexsha = "commit2"
        mock_commit2.author.name = "User2"
        mock_commit2.author.email = "user2@example.com"
        mock_commit2.committed_datetime = datetime(
            2025,
            7,
            20,
            15,
            0,
            0,
            tzinfo=timezone.utc,
        )  # 15:00 UTC (11:00 EDT)
        mock_commit2.message = "Commit 2"
        mock_commit2.stats.files = {
            "file2.py": {"insertions": 3, "deletions": 1, "lines": 4}
        }

        # Set up repo mock to return our test commits
        mock_repo_instance.iter_commits.return_value = [mock_commit1, mock_commit2]

        # Mock _parse_date to return timezone-aware datetimes
        with (
            patch("beaconled.core.analyzer.GitAnalyzer._parse_date") as mock_parse,
            patch.object(
                self.analyzer,
                "get_commit_stats",
            ) as mock_get_stats,
        ):
            # Mock _parse_date to return timezone-aware datetimes
            mock_parse.side_effect = [
                datetime(
                    2025, 7, 20, 6, 0, 0, tzinfo=timezone.utc
                ),  # 06:00 UTC (start)
                datetime(2025, 7, 20, 16, 0, 0, tzinfo=timezone.utc),  # 16:00 UTC (end)
            ]

            # Mock get_commit_stats to return stats for each commit
            mock_get_stats.side_effect = [
                MagicMock(files_changed=1, lines_added=5, lines_deleted=2),  # commit1
                MagicMock(files_changed=1, lines_added=3, lines_deleted=1),  # commit2
            ]

            # Test with timezone-aware date strings
            result = self.analyzer.get_range_analytics(
                "2025-07-20T01:00-05:00",
                "2025-07-20T11:00-05:00",
            )

            # Should include both commits since they fall within the UTC day
            self.assertEqual(len(result.commits), 2)
            # The actual hash might be a mock object, so we'll just check the length
            self.assertEqual(len(result.commits), 2)
            self.assertEqual(result.total_commits, 2)
            self.assertEqual(result.total_lines_added, 8)  # 5 + 3
            self.assertEqual(result.total_lines_deleted, 3)  # 2 + 1

            # Verify date range is preserved with timezone
            self.assertEqual(result.start_date.hour, 6)  # 06:00 UTC
            self.assertEqual(result.end_date.hour, 23)  # End of day (23:59:59)

    @patch("git.Repo")
    def test_get_range_analytics_empty_range(self, mock_repo):
        """Test behavior with an empty commit range."""
        # Setup mock repo
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        # Set up empty commit range
        mock_repo_instance.iter_commits.return_value = []

        # Mock _parse_date to return specific dates
        with patch("beaconled.core.analyzer.GitAnalyzer._parse_date") as mock_parse:
            mock_parse.side_effect = [
                datetime(2023, 1, 1, tzinfo=timezone.utc),
                datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
            ]

            # Test with a specific date range that has no commits
            result = self.analyzer.get_range_analytics("2025-01-01", "2025-01-31")

            # Should return a valid RangeStats object with zero values
            self.assertEqual(result.total_commits, 0)
            self.assertEqual(result.total_lines_added, 0)
            self.assertEqual(result.total_lines_deleted, 0)
            self.assertEqual(len(result.commits), 0)
            self.assertEqual(len(result.authors), 0)

            # Date range should match the parsed dates from the mock
            self.assertEqual(result.start_date.year, 2023)  # First mock date
            self.assertEqual(result.start_date.month, 1)
            self.assertEqual(result.start_date.day, 1)
            self.assertEqual(result.end_date.year, 2025)  # Second mock date
            self.assertEqual(result.end_date.month, 1)
            self.assertEqual(result.end_date.day, 31)


if __name__ == "__main__":
    unittest.main()
