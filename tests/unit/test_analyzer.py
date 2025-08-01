"""Tests for the analyzer module."""
import unittest
import re
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, ANY

from beaconled.exceptions import DateParseError, ValidationError

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
        
        # Create a mock commit with a datetime
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.hexsha = "abc123"
        mock_commit.author.email = "test@example.com"
        
        # Set up the mock to return our test commit
        mock_repo_instance.iter_commits.return_value = [mock_commit]
        
        # Mock get_commit_stats to return a dummy CommitStats object
        self.analyzer.get_commit_stats = MagicMock(return_value=MagicMock(
            spec=CommitStats,
            files_changed=1,
            lines_added=5,
            lines_deleted=2,
            files=[FileStats(path="test.txt", lines_added=5, lines_deleted=2, lines_changed=7)]
        ))
        
        # Test with string dates
        result = self.analyzer.get_range_analytics("2025-01-01", "2025-12-31")
        self.assertEqual(result.start_date, datetime(2025, 1, 1))
        self.assertEqual(result.end_date, datetime(2025, 12, 31))
        
        # Test with datetime objects
        start = datetime(2025, 1, 1)
        end = datetime(2025, 12, 31)
        result = self.analyzer.get_range_analytics(start, end)
        self.assertEqual(result.start_date, start)
        self.assertEqual(result.end_date, end)
    
    @patch('git.Repo')
    def test_get_range_analytics_single_day_range(self, mock_repo):
        """Test that single-day ranges are valid."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Create a mock commit with a datetime
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.hexsha = "abc123"
        mock_commit.author.email = "test@example.com"
        
        # Set up the mock to return our test commit
        mock_repo_instance.iter_commits.return_value = [mock_commit]
        
        # Mock get_commit_stats to return a dummy CommitStats object
        self.analyzer.get_commit_stats = MagicMock(return_value=MagicMock(
            spec=CommitStats,
            files_changed=1,
            lines_added=5,
            lines_deleted=2,
            files=[FileStats(path="test.txt", lines_added=5, lines_deleted=2, lines_changed=7)]
        ))
        
        # Test with same start and end date
        result = self.analyzer.get_range_analytics("2025-07-20", "2025-07-20")
        self.assertEqual(result.start_date, datetime(2025, 7, 20))
        self.assertEqual(result.end_date, datetime(2025, 7, 20))
    
    @patch('git.Repo')
    def test_get_range_analytics_invalid_range(self, mock_repo):
        """Test that invalid date ranges raise an error."""
        # Setup mock repo to avoid git operations
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Test with string dates - should raise RuntimeError with our validation message
        with self.assertRaises(RuntimeError) as cm:
            self.analyzer.get_range_analytics("2025-12-31", "2025-01-01")
        self.assertIn("Invalid date range: end date (2025-01-01 00:00:00) is before start date (2025-12-31 00:00:00)", str(cm.exception))
        
        # Test with datetime objects - should raise RuntimeError with our validation message
        with self.assertRaises(RuntimeError) as cm:
            start = datetime(2025, 12, 31)
            end = datetime(2025, 1, 1)
            self.analyzer.get_range_analytics(start, end)
        self.assertIn("Invalid date range: end date (2025-01-01 00:00:00) is before start date (2025-12-31 00:00:00)", str(cm.exception))
    
    @patch('git.Repo')
    def test_get_range_analytics_missing_dates(self, mock_repo):
        """Test that missing dates are handled correctly."""
        # Setup mock repo and commits
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Create a mock commit with a datetime
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.hexsha = "abc123"
        mock_commit.author.email = "test@example.com"
        
        # Set up the mock to return our test commit
        mock_repo_instance.iter_commits.return_value = [mock_commit]
        
        # Mock get_commit_stats to return a dummy CommitStats object
        self.analyzer.get_commit_stats = MagicMock(return_value=MagicMock(
            spec=CommitStats,
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
        first_commit.author.email = "first@example.com"
        
        # Create a mock for the commit iteration
        mock_commit = MagicMock()
        mock_commit.authored_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.committed_datetime = datetime(2025, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
        mock_commit.hexsha = "abc123"
        mock_commit.author.email = "test@example.com"
        
        # Set up side_effect to return different values based on the call
        def iter_commits_side_effect(*args, **kwargs):
            if 'max_count' in kwargs and kwargs['max_count'] == 1:
                return iter([first_commit])
            return iter([mock_commit])
            
        mock_repo_instance.iter_commits.side_effect = iter_commits_side_effect
        
        # Test with only start date
        result = self.analyzer.get_range_analytics("2025-01-01", None)
        self.assertIsNotNone(result)
        self.assertEqual(result.start_date, datetime(2025, 1, 1))
        
        # Test with only end date
        result = self.analyzer.get_range_analytics(None, "2025-12-31")
        self.assertIsNotNone(result)
        self.assertEqual(result.end_date, datetime(2025, 12, 31))
        
        # Test with no dates (should use repository's full history)
        result = self.analyzer.get_range_analytics(None, None)
        self.assertIsNotNone(result)


class TestDateParsing(unittest.TestCase):
    """Test cases for date parsing functionality in GitAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures with a mocked Git repository."""
        # Create a mock repository to avoid filesystem operations
        self.mock_repo = MagicMock()
        
        # Patch the git.Repo class to return our mock
        self.repo_patcher = patch('git.Repo', return_value=self.mock_repo)
        self.repo_patcher.start()
        
        # Initialize the analyzer with a dummy path
        self.analyzer = GitAnalyzer(".")
        self.now = datetime.now()
    
    def tearDown(self):
        """Clean up after tests."""
        self.repo_patcher.stop()
    
    def test_parse_relative_dates(self):
        """Test parsing of valid relative dates."""
        test_cases = [
            ('1d', timedelta(days=1)),
            ('2w', timedelta(weeks=2)),
            ('3m', timedelta(weeks=12)),  # 3 months ≈ 12 weeks
            ('1y', timedelta(weeks=52)),  # 1 year ≈ 52 weeks
            ('10d', timedelta(days=10)),
            ('1w', timedelta(weeks=1)),   # Single week
            ('12m', timedelta(weeks=48)), # Exactly one year in months
            ('52w', timedelta(weeks=52)), # Exactly one year in weeks
        ]
        
        for date_str, expected_delta in test_cases:
            with self.subTest(date_str=date_str):
                result = self.analyzer._parse_date(date_str)
                expected = self.now - expected_delta
                # Allow for small time differences due to test execution time
                self.assertAlmostEqual(
                    result.timestamp(),
                    expected.timestamp(),
                    delta=1.0,  # 1 second tolerance
                    msg=f"Failed for {date_str}"
                )
    
    def test_parse_relative_date_edge_cases(self):
        """Test edge cases for relative date parsing."""
        # Test case sensitivity (function is case-sensitive, so 'D' should fail)
        with self.assertRaises((ValueError, DateParseError)) as context:
            self.analyzer._parse_date('1D')
        self.assertIn('Could not parse date', str(context.exception))
        
        # Test valid lowercase unit
        result_lower = self.analyzer._parse_date('1d')
        self.assertIsInstance(result_lower, datetime)
        
        # Test very large numbers (should not raise)
        try:
            large_result = self.analyzer._parse_date('9999d')
            self.assertIsInstance(large_result, datetime)
        except Exception as e:
            self.fail(f"Unexpected exception for large number: {e}")
            
        # Test with leading/trailing whitespace
        ws_result = self.analyzer._parse_date(' 1d ')
        expected = self.now - timedelta(days=1)
        self.assertAlmostEqual(
            ws_result.timestamp(),
            expected.timestamp(),
            delta=1.0
        )
    
    def test_parse_absolute_dates(self):
        """Test parsing of valid absolute dates."""
        test_cases = [
            # Date only
            ('2025-01-15', datetime(2025, 1, 15)),
            # Date with time
            ('2025-01-15 14:30', datetime(2025, 1, 15, 14, 30)),
            # Edge of supported range
            ('2100-12-31 23:59', datetime(2100, 12, 31, 23, 59)),
            # Start of supported range
            ('2000-01-01 00:00', datetime(2000, 1, 1, 0, 0)),
            # Leap year
            ('2024-02-29 12:00', datetime(2024, 2, 29, 12, 0)),
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = self.analyzer._parse_date(date_str)
                self.assertEqual(result, expected, f"Failed for {date_str}")
                
    def test_parse_absolute_date_edge_cases(self):
        """Test edge cases for absolute date parsing."""
        # Test with single-digit month/day
        result = self.analyzer._parse_date('2025-1-1 1:05')
        self.assertEqual(result, datetime(2025, 1, 1, 1, 5))
        
        # Test with leading zeros in time
        result = self.analyzer._parse_date('2025-01-01 01:05')
        self.assertEqual(result, datetime(2025, 1, 1, 1, 5))
        
        # Test with leading/trailing whitespace
        result = self.analyzer._parse_date(' 2025-01-15 14:30 ')
        self.assertEqual(result, datetime(2025, 1, 15, 14, 30))
    
    def test_invalid_relative_dates(self):
        """Test handling of invalid relative dates."""
        # Test cases that should raise DateParseError
        test_cases = [
            # Invalid formats that should raise DateParseError
            ('0d', 'Could not parse date'),
            ('-1d', 'Could not parse date'),
            ('1x', 'Could not parse date'),
            ('abc', 'Could not parse date'),
            ('d', 'Could not parse date'),
            ('1.5d', 'Could not parse date'),  # Decimal not supported
            ('1D', 'Could not parse date'),    # Uppercase unit not supported
            ('', 'Date string cannot be empty'),  # Empty string
            ('   ', 'Date string cannot be empty'),  # Whitespace only
        ]
        
        for date_str, error_msg in test_cases:
            with self.subTest(date_str=date_str):
                with self.assertRaises((ValueError, DateParseError, ValidationError)) as context:
                    self.analyzer._parse_date(date_str)
                self.assertIn(error_msg, str(context.exception))
        
        # Test cases that should not raise an exception but might return a default value
        # or be handled differently
        other_cases = [
            '1d2h',    # Multiple units not supported but might be parsed as '1d'
            '1d ',     # Trailing space after unit
            ' 1 d',    # Space between number and unit
            '1dd',     # Double unit
            '1',       # Just a number (might be parsed as a date)
        ]
        
        for date_str in other_cases:
            with self.subTest(date_str=date_str):
                try:
                    result = self.analyzer._parse_date(date_str)
                    self.assertIsInstance(result, datetime)
                except (ValueError, DateParseError, ValidationError) as e:
                    # It's okay if these raise an exception, but they might not
                    pass
        
        # Test very large number separately as it causes OverflowError
        with self.subTest(date_str='very_large_number'):
            with self.assertRaises(OverflowError):
                self.analyzer._parse_date('10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000d')
    
    def test_invalid_absolute_dates(self):
        """Test handling of invalid absolute dates."""
        test_cases = [
            # Invalid months
            ('2025-13-01', 'Could not parse date'),
            ('2025-00-01', 'Could not parse date'),
            ('2025-99-01', 'Could not parse date'),
            # Invalid days
            ('2025-01-32', 'Could not parse date'),
            ('2025-02-30', 'Could not parse date'),  # Not a leap year
            ('2025-04-31', 'Could not parse date'),  # April has 30 days
            # Invalid separators
            ('2025/01/15', 'Could not parse date'),
            ('2025.01.15', 'Could not parse date'),
            ('2025_01_15', 'Could not parse date'),
            # Invalid year format
            ('25-01-15', 'Could not parse date'),
            ('20251-01-15', 'Could not parse date'),
            # Invalid time
            ('2025-01-15 25:00', 'Could not parse date'),  # Invalid hour
            ('2025-01-15 14:60', 'Could not parse date'),  # Invalid minute
            ('2025-01-15 14:30:45', 'Could not parse date'),  # Seconds not supported
            # Out of range years
            ('1999-01-01', 'outside the supported range'),  # Before 2000
            ('2101-01-01', 'outside the supported range'),  # After 2100
            # Edge cases
            ('2025-01-15 14:30:00', 'Could not parse date'),  # With seconds
            ('2025-01-15T14:30', 'Could not parse date'),  # ISO format with T
            ('2025-01-15 14:30:45.123', 'Could not parse date'),  # With milliseconds
            ('2025-01-15 14:30:45 +08:00', 'Could not parse date'),  # With timezone
            ('2025-01-15 14:30:45Z', 'Could not parse date'),  # With Zulu time
            # Malformed strings
            ('2025-01-15 14', 'Could not parse date'),  # Incomplete time
            ('2025-01-15 14:', 'Could not parse date'),  # Incomplete time
            ('2025-01', 'Could not parse date'),  # Incomplete date
            ('2025-01-', 'Could not parse date'),  # Incomplete date
            ('2025-', 'Could not parse date'),  # Incomplete date
            ('2025', 'Could not parse date'),  # Just year
            ('not-a-date', 'Could not parse date'),  # Completely invalid
            ('2025-01-15 14:30:00.000000', 'Could not parse date'),  # Microseconds
        ]
        
        for date_str, error_msg in test_cases:
            with self.subTest(date_str=date_str):
                with self.assertRaises((ValueError, DateParseError, ValidationError)) as context:
                    self.analyzer._parse_date(date_str)
                self.assertIn(error_msg, str(context.exception))
    
    @patch('beaconled.core.analyzer.datetime')
    def test_parse_git_date(self, mock_datetime):
        """Test parsing of git log date strings."""
        # Mock the current time for consistent testing
        mock_now = datetime(2025, 7, 30, 13, 10, 0)  # Fixed time for testing
        mock_datetime.now.return_value = mock_now
        
        # Mock strptime to return a fixed datetime
        def mock_strptime(date_str, format_str):
            if '+0800' in date_str:
                return datetime(2025, 1, 15, 14, 30, 45)
            elif '-0200' in date_str:
                return datetime(2025, 1, 15, 6, 30, 45)
            else:
                return datetime(2025, 1, 15, 14, 30, 45)
        
        mock_datetime.strptime.side_effect = mock_strptime
        
        test_cases = [
            ('2025-01-15 14:30:45 +0800', datetime(2025, 1, 15, 14, 30, 45)),
            ('2025-01-15 06:30:45 -0200', datetime(2025, 1, 15, 6, 30, 45)),
            ('2025-01-15 14:30:45', datetime(2025, 1, 15, 14, 30, 45)),
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = self.analyzer._parse_git_date(date_str)
                self.assertEqual(result, expected, f"Failed for {date_str}")
    
    @patch('beaconled.core.analyzer.datetime')
    def test_parse_git_date_invalid(self, mock_datetime):
        """Test handling of invalid git date strings."""
        # Mock the current time for consistent testing
        mock_now = datetime(2025, 7, 30, 13, 10, 0)
        mock_datetime.now.return_value = mock_now
        
        # Mock strptime to raise ValueError
        mock_datetime.strptime.side_effect = ValueError("time data 'invalid-date' does not match format")
        
        # Call the method - it should handle the error gracefully
        with self.assertWarns(RuntimeWarning) as cm:
            result = self.analyzer._parse_git_date('invalid-date')
            
            # Verify it returns the current time as a fallback
            self.assertIsInstance(result, datetime)
            self.assertEqual(result, mock_now)
        
        # Verify the warning was issued
        self.assertIn("Failed to parse git date 'invalid-date'", str(cm.warning))


if __name__ == '__main__':
    unittest.main()
