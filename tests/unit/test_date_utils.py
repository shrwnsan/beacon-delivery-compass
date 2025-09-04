"""Tests for the date_utils module."""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from beaconled.utils.date_utils import DateUtils as DateParser


class TestDateParser(unittest.TestCase):
    """Test cases for DateParser class."""

    def test_parse_absolute_dates(self) -> None:
        """Test parsing of absolute date strings."""
        test_cases: list[tuple[str, datetime]] = [
            # (input_string, expected_datetime)
            ("2023-10-05", datetime(2023, 10, 5, 0, 0, tzinfo=timezone.utc)),
            (
                "2023-10-05T14:30:00",
                datetime(2023, 10, 5, 14, 30, 0, tzinfo=timezone.utc),
            ),
            ("2024-01-01", datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)),
            ("20250820", datetime(2025, 8, 20, 0, 0, tzinfo=timezone.utc)),
        ]

        for date_str, expected_dt in test_cases:
            with self.subTest(date_str=date_str):
                parsed_dt = DateParser.parse_date(date_str)
                if expected_dt.tzinfo is None:
                    self.assertEqual(parsed_dt.date(), expected_dt.date())
                else:
                    self.assertEqual(parsed_dt, expected_dt)

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Use a fixed timestamp for consistent test results
        self.now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_parse_relative_dates(self) -> None:
        """Test parsing of valid relative dates."""
        # Fixed test date for consistent results
        fixed_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        test_cases: list[tuple[str, timedelta]] = [
            # (input_string, expected_timedelta)
            ("1d", timedelta(days=1)),
            ("2w", timedelta(weeks=2)),
            ("3m", timedelta(weeks=12)),  # 3 months ≈ 12 weeks in the implementation
            ("1y", timedelta(weeks=52)),  # 1 year ≈ 52 weeks in the implementation
            ("10d", timedelta(days=10)),
            ("1w", timedelta(weeks=1)),
        ]

        for date_str, expected_delta in test_cases:
            with self.subTest(date_str=date_str):
                # Mock datetime.now() in the module where it's actually used
                with patch("beaconled.utils.date_utils.datetime") as mock_datetime:
                    # Configure the mock
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args,
                        **kw,
                        tzinfo=timezone.utc,
                    )
                    mock_datetime.fromtimestamp.side_effect = lambda ts, tz: datetime.fromtimestamp(
                        ts,
                        tz,
                    )

                    # Call the method under test
                    result = DateParser.parse_date(date_str)

                    # Calculate expected result
                    # The implementation subtracts the delta from now
                    expected = fixed_now - expected_delta

                    # Verify the result is timezone-aware
                    self.assertEqual(result.tzinfo, timezone.utc)

                    # Compare the dates directly (ignoring microseconds)
                    result_no_us = result.replace(microsecond=0)
                    expected_no_us = expected.replace(microsecond=0)
                    self.assertEqual(
                        result_no_us,
                        expected_no_us,
                        f"Failed for {date_str}: expected {expected_no_us}, got {result_no_us}",
                    )

    def test_parse_git_date(self) -> None:
        """Test parsing of git date strings."""
        test_cases: list[tuple[str, datetime]] = [
            # (git_date_string, expected_datetime)
            ("1690200000 +0000", datetime(2023, 7, 24, 12, 0, tzinfo=timezone.utc)),
            ("1690200000 -0500", datetime(2023, 7, 24, 17, 0, tzinfo=timezone.utc)),
            ("1690200000 +0900", datetime(2023, 7, 24, 3, 0, tzinfo=timezone.utc)),
        ]

        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = DateParser.parse_git_date(date_str)
                self.assertEqual(result, expected)
                self.assertEqual(result.tzinfo, timezone.utc)

    def test_validate_date_range(self) -> None:
        """Test validation of date ranges."""
        test_cases: list[tuple[str, str, datetime, datetime]] = [
            # (start_str, end_str, expected_start, expected_end)
            (
                "2025-01-01",
                "2025-12-31",
                datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc),
                datetime(2025, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc),
            ),
            (
                "2025-07-20",
                "2025-07-20",  # Single day range
                datetime(2025, 7, 20, 0, 0, tzinfo=timezone.utc),
                datetime(2025, 7, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
            ),
        ]

        for start_str, end_str, expected_start, expected_end in test_cases:
            with self.subTest(f"{start_str} to {end_str}"):
                start, end = DateParser.validate_date_range(start_str, end_str)
                self.assertEqual(start, expected_start)
                self.assertEqual(end, expected_end)

    def test_validate_date_range_invalid(self) -> None:
        """Test validation of invalid date ranges."""
        with self.assertRaises(ValueError):
            DateParser.validate_date_range("2025-12-31", "2025-01-01")  # End before start

    def test_is_valid_commit_hash(self) -> None:
        """Test validation of commit hashes."""
        valid_hashes = [
            "a1b2c3d",  # Short hash
            "abc123" * 6,  # Full hash (40 chars)
            "a" * 7,  # Minimum length
            "0123456",  # All digits
            "abcdef0",  # All hex chars
        ]

        invalid_hashes = [
            ("", "empty string"),
            ("a" * 6, "too short"),
            ("a!b@c#", "invalid chars"),
            ("a b c", "contains spaces"),
            ("ghijklm", "contains non-hex chars"),
            ("-" * 7, "all invalid chars"),
        ]

        for commit_hash in valid_hashes:
            with self.subTest(f"Valid hash: {commit_hash}"):
                self.assertTrue(
                    DateParser.is_valid_commit_hash(commit_hash),
                    f"Expected '{commit_hash}' to be a valid commit hash",
                )

        for commit_hash, reason in invalid_hashes:
            with self.subTest(f"Invalid hash: {commit_hash} ({reason})"):
                self.assertFalse(
                    DateParser.is_valid_commit_hash(commit_hash),
                    f"Expected '{commit_hash}' to be invalid ({reason})",
                )


if __name__ == "__main__":
    unittest.main()
