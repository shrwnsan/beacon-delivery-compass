"""Tests for UTC-only date handling in the analyzer.

All dates are now treated as UTC. Timezone conversion is the responsibility
of the caller.
"""

from datetime import datetime, timezone

import pytest

from beaconled.core.date_errors import DateParseError
from beaconled.utils.date_utils import DateUtils as DateParser


class TestUTCOnlyHandling:
    """Test UTC-only date handling in the application.

    All dates are now treated as UTC. The caller is responsible for any
    timezone conversion.
    """

    # Test constants
    TEST_YEAR = 2023
    TEST_MONTH = 1
    START_DAY = 1
    START_HOUR = 10
    END_DAY = 10
    END_HOUR = 18
    END_OF_DAY_HOUR = 23
    END_OF_DAY_MINUTE = 59
    END_OF_DAY_SECOND = 59

    def test_naive_datetime_handling(self) -> None:
        """Tests that naive datetimes are interpreted as UTC."""
        # Create naive datetime objects (will be treated as UTC)
        naive_start = datetime(
            self.TEST_YEAR,
            self.TEST_MONTH,
            self.START_DAY,
            self.TEST_HOUR,
            0,
            0,
            tzinfo=timezone.utc,
        )
        naive_end = datetime(
            self.TEST_YEAR,
            self.TEST_MONTH,
            self.END_DAY,
            self.END_HOUR,
            0,
            0,
            tzinfo=timezone.utc,
        )

        # Validate the range
        aware_start, aware_end = DateParser.validate_date_range(naive_start, naive_end)
        self._verify_datetime_awareness(aware_start, is_start=True)
        self._verify_datetime_awareness(aware_end, is_start=False)

    def _verify_datetime_awareness(
        self,
        dt: datetime,
        *,  # Force keyword arguments after this point
        is_start: bool = True,
    ) -> None:
        """Verify that a datetime is timezone-aware and has expected values.

        Args:
            dt: The datetime to check
            is_start: If True, verifies start datetime values; otherwise,
                     verifies end datetime values
        """
        if dt.tzinfo != timezone.utc:
            pytest.fail("Datetime should be timezone-aware")

        if is_start:
            if dt.hour != self.START_HOUR:
                pytest.fail("Start hour should be preserved")
            if dt.minute != 0:
                pytest.fail("Start minute should be 0")
            if dt.day != self.START_DAY:
                pytest.fail("Start day should be 1")
        else:
            if dt.hour != self.END_OF_DAY_HOUR:
                pytest.fail("End hour should be end of day")
            if dt.minute != self.END_OF_DAY_MINUTE:
                pytest.fail("End minute should be 59")
            if dt.second != self.END_OF_DAY_SECOND:
                pytest.fail("End second should be 59")
            if dt.day != self.END_DAY:
                pytest.fail("End day should be 10")

        if dt.month != self.TEST_MONTH:
            pytest.fail(f"Month should be {self.TEST_MONTH}")
        if dt.year != self.TEST_YEAR:
            pytest.fail(f"Year should be {self.TEST_YEAR}")

    def test_parse_date_with_timezone_info(self) -> None:
        """Test that timezone information in date strings is rejected."""
        # These should all raise DateParseError because they contain timezone info
        test_cases = [
            "2025-01-15T14:30:00+00:00",
            "2025-01-15 14:30:00+05:30",
            "2025-01-15 14:30:00-08:00",
            "2025-01-15 14:30:00Z",
            "2025-01-15 14:30:00 UTC",
        ]
        expected_terms = ["timezone", "utc", "format"]

        for date_str in test_cases:
            with pytest.raises(
                DateParseError,
                match=r"(?i)timezone|utc|format",
            ) as exc_info:
                DateParser.parse_date(date_str)

            error_msg = str(exc_info.value).lower()
            if not any(term in error_msg for term in expected_terms):
                pytest.fail(
                    f"Expected timezone-related error for '{date_str}', " f"got: {error_msg}",
                )

    def _verify_parsed_date(
        self,
        date_str: str,
        expected: datetime | None = None,
    ) -> None:
        """Verify that a date string is parsed correctly.

        Args:
            date_str: The date string to parse
            expected: The expected datetime object, or None for relative dates
        """
        try:
            result = DateParser.parse_date(date_str)

            if expected is not None and result != expected:
                pytest.fail(
                    f"Expected {expected}, got {result} for '{date_str}'",
                )

            # For relative dates, just verify we got a datetime
            if not isinstance(result, datetime):
                pytest.fail(
                    f"Expected datetime, got {type(result)} for '{date_str}'",
                )

            if result.tzinfo != timezone.utc:
                pytest.fail(
                    f"Expected UTC timezone, got {result.tzinfo} for '{date_str}'",
                )

        except Exception as e:
            pytest.fail(f"Failed to parse date '{date_str}': {e}")

    def test_parse_date_formats(self) -> None:
        """Test that valid UTC date formats are parsed correctly."""
        test_cases: list[tuple[str, datetime | None]] = [
            # Date only (interpreted as midnight UTC)
            ("2025-01-15", datetime(2025, 1, 15, 0, 0, tzinfo=timezone.utc)),
            # Date and time (interpreted as UTC)
            ("2025-01-15 14:30", datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc)),
            # Relative dates
            ("now", None),  # Can't test exact value, but should not raise
            ("1d", None),  # Can't test exact value, but should not raise
            ("2w", None),  # Can't test exact value, but should not raise
        ]

        for date_str, expected in test_cases:
            self._verify_parsed_date(date_str, expected)

    def test_parse_date_invalid_formats(self) -> None:
        """Test that invalid date formats raise appropriate errors."""
        test_cases: list[tuple[str, str]] = [
            ("", "date string cannot be empty"),
            ("not-a-date", "parse date"),
            ("2025-13-01", "invalid date"),
            ("2025-01-32", "invalid date"),
            ("2025-01-15 25:00", "could not parse datetime"),
            ("2025-01-15 14:60", "could not parse datetime"),
            # Timezone offsets not allowed
            ("2025-01-15 14:30 +0000", "utc"),
            ("2025-01-15 14:30 -0500", "utc"),
        ]

        for date_str, error_keyword in test_cases:
            with pytest.raises(
                DateParseError,
                match=rf"(?i){error_keyword}",
            ) as exc_info:
                DateParser.parse_date(date_str)

            # Verify the error message contains the expected keyword
            error_msg = str(exc_info.value).lower()
            if error_keyword not in error_msg:
                pytest.fail(
                    f"Expected error message to contain '{error_keyword}' "
                    f"for input '{date_str}', got: {error_msg}",
                )
