"""Tests for the date_utils module."""
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from beaconled.utils.date_utils import DateParser
from beaconled.core.date_errors import DateParseError
from beaconled.exceptions import ValidationError


class TestDateParser(unittest.TestCase):
    """Test cases for DateParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.now = datetime.now(timezone.utc)
    
    def test_parse_relative_dates(self):
        """Test parsing of valid relative dates."""
        test_cases = [
            ('1d', timedelta(days=1)),
            ('2w', timedelta(weeks=2)),
            ('3m', timedelta(weeks=12)),  # 3 months ≈ 12 weeks
            ('1y', timedelta(weeks=52)),  # 1 year ≈ 52 weeks
            ('10d', timedelta(days=10)),
            ('1w', timedelta(weeks=1)),
            ('12m', timedelta(weeks=48)),  # 12 months
            ('52w', timedelta(weeks=52)),  # 52 weeks
        ]
        
        for date_str, expected_delta in test_cases:
            with self.subTest(date_str=date_str):
                with patch('beaconled.core.date_utils.datetime') as mock_datetime:
                    mock_datetime.now.return_value = self.now
                    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                    
                    result = DateParser.parse_date(date_str)
                    expected = self.now - expected_delta
                    
                    self.assertEqual(result.tzinfo, timezone.utc)
                    self.assertAlmostEqual(
                        result.timestamp(),
                        expected.timestamp(),
                        delta=1.0  # 1 second tolerance
                    )
    
    def test_parse_absolute_dates(self):
        """Test parsing of valid absolute dates."""
        test_cases = [
            ('2025-07-20', datetime(2025, 7, 20, 0, 0, tzinfo=timezone.utc)),
            ('2025-07-20 14:30', datetime(2025, 7, 20, 14, 30, tzinfo=timezone.utc)),
            ('2025-07-20T14:30', datetime(2025, 7, 20, 14, 30, tzinfo=timezone.utc)),
            ('2025-07-20 14:30:45', datetime(2025, 7, 20, 14, 30, 45, tzinfo=timezone.utc)),
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = GitDateParser.parse_date(date_str)
                self.assertEqual(result, expected)
                self.assertEqual(result.tzinfo, timezone.utc)
    
    def test_parse_git_date(self):
        """Test parsing of git date strings."""
        test_cases = [
            ('1690200000 +0000', datetime(2023, 7, 24, 12, 0, tzinfo=timezone.utc)),
            ('1690200000 -0500', datetime(2023, 7, 24, 17, 0, tzinfo=timezone.utc)),
            ('1690200000 +0900', datetime(2023, 7, 24, 3, 0, tzinfo=timezone.utc)),
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = DateParser.parse_git_date(date_str)
                self.assertEqual(result, expected)
                self.assertEqual(result.tzinfo, timezone.utc)
    
    def test_validate_date_range(self):
        """Test validation of date ranges."""
        # Valid range
        start, end = DateParser.validate_date_range("2025-01-01", "2025-12-31")
        self.assertEqual(start, datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2025, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc))
        
        # Single day range
        start, end = DateParser.validate_date_range("2025-07-20", "2025-07-20")
        self.assertEqual(start, datetime(2025, 7, 20, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2025, 7, 20, 23, 59, 59, 999999, tzinfo=timezone.utc))
        
        # Invalid range (end before start)
        with self.assertRaises(ValueError):
            DateParser.validate_date_range("2025-12-31", "2025-01-01")
    
    def test_is_valid_commit_hash(self):
        """Test validation of commit hashes."""
        self.assertTrue(DateParser.is_valid_commit_hash("a1b2c3d"))
        self.assertTrue(DateParser.is_valid_commit_hash("abc123" * 6))  # Full hash
        self.assertTrue(DateParser.is_valid_commit_hash("a" * 4))  # Minimum length
        
        # Invalid hashes
        self.assertFalse(DateParser.is_valid_commit_hash(""))
        self.assertFalse(DateParser.is_valid_commit_hash("a" * 3))  # Too short
        self.assertFalse(DateParser.is_valid_commit_hash("a!b@c#"))  # Invalid chars
        self.assertFalse(DateParser.is_valid_commit_hash("a b c"))  # Spaces not allowed


if __name__ == '__main__':
    unittest.main()
