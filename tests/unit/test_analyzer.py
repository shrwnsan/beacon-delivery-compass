"""Tests for the analyzer module."""
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from beaconled.core.date_errors import DateParseError

import git
from beaconled.core.analyzer import GitAnalyzer
from beaconled.core.models import CommitStats, FileStats


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
            
        self.assertIn("Unexpected error analyzing commit", str(context.exception))

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
    @patch('beaconled.core.analyzer.GitAnalyzer._parse_date')
    def test_get_range_analytics_success(self, mock_parse_date, mock_repo):
        """Test successful range analysis."""
        # Mock the parse_date to return a fixed date
        mock_parse_date.return_value = datetime(2025, 7, 20, 0, 0, 0, tzinfo=timezone.utc)
        
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
        mock_repo_instance.git.log.return_value = "\n".join([mc.hexsha for mc in mock_commits])
        
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
                files=[FileStats(path=f"file_{i}.txt", lines_added=5, lines_deleted=2, lines_changed=7)]
            ) for i, date in enumerate(test_dates)
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

    @patch('git.Repo')
    def test_get_range_analytics_failure(self, mock_repo):
        """Test range analysis with git command failure."""
        # Set up the mock to raise an exception during date parsing
        mock_repo.return_value.git.log.side_effect = git.GitCommandError("git log", 1)

        with self.assertRaises(RuntimeError) as context:
            self.analyzer.get_range_analytics("1 week ago")
            
        # The error should be about failing to analyze the date range
        self.assertIn("Unexpected error analyzing date range", str(context.exception))
    
    @patch('git.Repo')
    def test_get_range_analytics_valid_date_range(self, mock_repo):
        """Test that valid date ranges are accepted."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Create a mock commit with a datetime and author
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
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
        commit_stats.files = [FileStats(path="test.txt", lines_added=5, lines_deleted=2, lines_changed=7)]
        commit_stats.author = "Test User <test@example.com>"
        commit_stats.date = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        self.analyzer.get_commit_stats = MagicMock(return_value=commit_stats)
        
        # Test with string dates
        result = self.analyzer.get_range_analytics("2025-01-01", "2025-12-31")
        self.assertEqual(result.start_date, datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(result.end_date, datetime(2025, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc))
        
        # Test with datetime objects
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end = datetime(2025, 12, 31, tzinfo=timezone.utc)
        result = self.analyzer.get_range_analytics(start, end)
        self.assertEqual(result.start_date, start)
        self.assertEqual(result.end_date, end.replace(hour=23, minute=59, second=59, microsecond=999999))
    
    @patch('git.Repo')
    def test_get_range_analytics_single_day_range(self, mock_repo):
        """Test that single-day ranges are valid."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Create a mock commit with a datetime and author
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
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
        commit_stats.files = [FileStats(path="test.txt", lines_added=5, lines_deleted=2, lines_changed=7)]
        commit_stats.author = "Test User <test@example.com>"
        commit_stats.date = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        self.analyzer.get_commit_stats = MagicMock(return_value=commit_stats)
        
        # Test with same start and end date
        result = self.analyzer.get_range_analytics("2025-07-20", "2025-07-20")
        # The start date should be the beginning of the day in UTC
        self.assertEqual(result.start_date, datetime(2025, 7, 20, 0, 0, 0, tzinfo=timezone.utc))
        # The end date should be the end of the day in UTC
        self.assertEqual(result.end_date, datetime(2025, 7, 20, 23, 59, 59, 999999, tzinfo=timezone.utc))
    
    @patch('git.Repo')
    def test_get_range_analytics_invalid_range(self, mock_repo):
        """Test that invalid date ranges raise an error."""
        # Setup mock repo to avoid git operations
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Test with string dates - should raise ValueError with our validation message
        with self.assertRaises(ValueError) as cm:
            self.analyzer.get_range_analytics("2025-12-31", "2025-01-01")
        self.assertIn("Invalid date range: end date (2025-01-01 00:00:00+00:00) is before start date (2025-12-31 00:00:00+00:00)", 
                     str(cm.exception))
        
        # Test with datetime objects - should raise ValueError with our validation message
        with self.assertRaises(ValueError) as cm:
            start = datetime(2025, 12, 31, tzinfo=timezone.utc)
            end = datetime(2025, 1, 1, tzinfo=timezone.utc)
            self.analyzer.get_range_analytics(start, end)
        self.assertIn("Invalid date range: end date (2025-01-01 00:00:00+00:00) is before start date (2025-12-31 00:00:00+00:00)", 
                     str(cm.exception))
    
    @patch('git.Repo')
    def test_get_range_analytics_missing_dates(self, mock_repo):
        """Test that missing dates are handled correctly."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Create a mock commit with a datetime and author
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.hexsha = "abc123"
        mock_commit.author = MagicMock()
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.message = "Test commit message"
        mock_commit.parents = []
        
        # Set up the mock to return our test commit
        mock_repo_instance.iter_commits.return_value = [mock_commit]
        
        # Mock get_commit_stats to return a dummy CommitStats object
        self.analyzer.get_commit_stats = MagicMock(return_value=MagicMock(
            spec=CommitStats,
            hash="abc123",
            author="Test User <test@example.com>",
            date=datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc),
            message="Test commit",
            files_changed=1,
            lines_added=5,
            lines_deleted=2,
            files=[FileStats(path="test.txt", lines_added=5, lines_deleted=2, lines_changed=7)]
        ))
        
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
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.hexsha = "abc123"
        mock_commit.author = MagicMock()
        mock_commit.author.name = "Test User"
        mock_commit.author.email = "test@example.com"
        mock_commit.message = "Test commit message"
        mock_commit.parents = []
        
        # Set up side_effect to return different values based on the call
        def iter_commits_side_effect(*args, **kwargs):
            if 'max_count' in kwargs and kwargs['max_count'] == 1:
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
        self.assertEqual(result.end_date, datetime(2025, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc))
        
        # Test with no dates (should use repository's full history)
        result = self.analyzer.get_range_analytics(None, None)
        self.assertIsNotNone(result)


class TestDateParsing(unittest.TestCase):
    """Test cases for date parsing functionality in GitAnalyzer.
    
    Note: Most date parsing tests have been moved to test_date_utils.py.
    This class is kept for backward compatibility and will be removed in a future version.
    Now uses DateParser instead of GitDateParser.
    """
    
    def setUp(self):
        """Set up test fixtures with a mocked Git repository."""
        # Create a mock repository to avoid filesystem operations
        self.mock_repo = MagicMock()
        
        # Patch the git.Repo class to return our mock
        self.repo_patcher = patch('git.Repo', return_value=self.mock_repo)
        self.repo_patcher.start()
        
        # Initialize the analyzer with a dummy path
        self.analyzer = GitAnalyzer(".")
    
    def tearDown(self):
        """Clean up after tests."""
        self.repo_patcher.stop()
    
    def test_parse_relative_dates(self):
        """Test that _parse_date forwards to DateParser.parse_date."""
        test_cases = [
            '1d', '2w', '3m', '1y', '10d', '1w', '12m', '52w'
        ]
        
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                with patch('beaconled.utils.date_utils.DateParser.parse_date') as mock_parse:
                    mock_parse.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)
                    result = self.analyzer._parse_date(date_str)
                    mock_parse.assert_called_once_with(date_str)
                    self.assertEqual(result, mock_parse.return_value)
    
    def test_parse_git_date(self):
        """Test that _parse_git_date forwards to DateParser.parse_git_date."""
        test_cases = [
            '1690200000 +0000',
            '1690200000 -0500',
            '1690200000 +0900',
        ]
        
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                with patch('beaconled.utils.date_utils.DateParser.parse_git_date') as mock_parse:
                    mock_parse.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)
                    result = self.analyzer._parse_git_date(date_str)
                    mock_parse.assert_called_once_with(date_str)
                    self.assertEqual(result, mock_parse.return_value)
    
    def test_is_valid_commit_hash(self):
        """Test that _is_valid_commit_hash forwards to DateParser.is_valid_commit_hash."""
        test_cases = [
            ('a1b2c3d', True),
            ('invalid!', False),
            ('1234567', True),
        ]
        
        for commit_hash, expected in test_cases:
            with self.subTest(commit_hash=commit_hash):
                with patch('beaconled.utils.date_utils.DateParser.is_valid_commit_hash') as mock_validate:
                    mock_validate.return_value = expected
                    result = self.analyzer._is_valid_commit_hash(commit_hash)
                    mock_validate.assert_called_once_with(commit_hash)
                    self.assertEqual(result, expected)
    
    def test_parse_absolute_dates(self):
        """Test that _parse_date handles absolute dates by forwarding to DateParser."""
        test_cases = [
            '2025-07-20',
            '2025-07-20 14:30',
            '2025-07-20T14:30',
            '2025-07-20 14:30:45',
        ]
        
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                with patch('beaconled.utils.date_utils.DateParser.parse_date') as mock_parse:
                    mock_parse.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)
                    result = self.analyzer._parse_date(date_str)
                    mock_parse.assert_called_once_with(date_str)
                    self.assertEqual(result, mock_parse.return_value)
    
    def test_parse_absolute_date_edge_cases(self):
        """Test that _parse_date handles various date formats by forwarding to DateParser."""
        test_cases = [
            '2025/07/20',
            '2025-07-20 14:30',
            '2025/07/20 14:30:45',
            '2025-07-20T14:30:45',
        ]
        
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                with patch('beaconled.utils.date_utils.DateParser.parse_date') as mock_parse:
                    mock_parse.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)
                    result = self.analyzer._parse_date(date_str)
                    mock_parse.assert_called_once_with(date_str)
                    self.assertEqual(result, mock_parse.return_value)
    
    def test_parse_invalid_relative_dates(self):
        """Test that _parse_date raises errors for invalid relative dates."""
        invalid_cases = [
            '1x',  # Invalid unit
            'abc',  # Not a number
            '1d1h', # Mixed units not supported
            'd',    # Missing number
            '-1d',  # Negative numbers not supported
            '1.5d', # Decimal numbers not supported
        ]
        
        for date_str in invalid_cases:
            with self.subTest(date_str=date_str):
                with patch('beaconled.utils.date_utils.DateParser.parse_date') as mock_parse:
                    mock_parse.side_effect = DateParseError(f"Could not parse date: {date_str}")
                    with self.assertRaises(DateParseError):
                        self.analyzer._parse_date(date_str)
                    mock_parse.assert_called_once_with(date_str)
    
    def test_parse_invalid_absolute_dates(self):
        """Test that _parse_date raises errors for invalid absolute dates."""
        invalid_cases = [
            '2025-13-01',  # Invalid month
            '2025-07-32',  # Invalid day
            '2025-07-20 25:00',  # Invalid hour
            '2025-07-20 14:60',  # Invalid minute
            'not-a-date',  # Completely invalid
            '',             # Empty string
            ' ',            # Whitespace only
        ]
        
        for date_str in invalid_cases:
            with self.subTest(date_str=date_str):
                with patch('beaconled.utils.date_utils.DateParser.parse_date') as mock_parse:
                    mock_parse.side_effect = DateParseError(f"Could not parse date: {date_str}")
                    with self.assertRaises(DateParseError):
                        self.analyzer._parse_date(date_str)
                    mock_parse.assert_called_once_with(date_str)
    
    @patch('beaconled.core.analyzer.datetime')
    @patch('logging.Logger.warning')
    def test_parse_git_date_invalid(self, mock_warning, mock_datetime):
        """Test handling of invalid git date strings."""
        # Mock the current time for consistent testing with UTC timezone
        fixed_now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_now
        
        # Create a mock for the datetime.strptime().replace() chain
        mock_dt = MagicMock()
        mock_dt.replace.return_value = fixed_now
        mock_datetime.strptime.return_value = mock_dt
        
        # Test various invalid formats
        invalid_cases = [
            '',                      # Empty string
            ' ',                     # Whitespace
            '2025-01-01',            # Missing time
            '10:00:00',              # Missing date
            '2025-01-01 10:00:00 +', # Incomplete timezone
            '2025-01-01 10:00:00 +25:00', # Invalid timezone
            '2025-01-01 10:00:00 +9999', # Invalid timezone offset
            '2025-13-01 10:00:00 +0000', # Invalid month
            '2025-01-32 10:00:00 +0000', # Invalid day
            '2025-01-01 25:00:00 +0000', # Invalid hour
            '2025-01-01 10:60:00 +0000', # Invalid minute
            '2025-01-01 10:00:60 +0000', # Invalid second
        ]
        
        # Test all invalid cases
        for date_str in invalid_cases:
            with self.subTest(date_str=date_str):
                # Reset the mock for each test case
                mock_warning.reset_mock()
                
                # The actual call will raise an exception, which should be caught
                result = self.analyzer._parse_git_date(date_str)
                
                # Should return current time in UTC on error
                self.assertEqual(result, fixed_now)
                self.assertEqual(result.tzinfo, timezone.utc)
                
                # Should log a warning
                mock_warning.assert_called()
        
        # Test non-string inputs
        for invalid in [None, 123, {}, []]:
            with self.subTest(invalid=invalid):
                # Reset the mock for each test case
                mock_warning.reset_mock()
                
                result = self.analyzer._parse_git_date(invalid)
                
                # Should return current time in UTC on error
                self.assertEqual(result, fixed_now)
                self.assertEqual(result.tzinfo, timezone.utc)
                
                # Should log a warning
                mock_warning.assert_called()
        
        # Verify at least one warning was logged in total
        self.assertGreaterEqual(mock_warning.call_count, 1)


if __name__ == '__main__':
    unittest.main()
