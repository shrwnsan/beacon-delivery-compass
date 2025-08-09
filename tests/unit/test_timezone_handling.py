"""Tests for UTC-only date handling in the analyzer.

All dates are now treated as UTC. Timezone conversion is the responsibility of the caller.
"""
import pytest
from datetime import datetime, timezone

from beaconled.core.date_errors import DateParseError
from beaconled.utils.date_utils import DateParser

class TestUTCOnlyHandling:
    """Test UTC-only date handling in the application.
    
    All dates are now treated as UTC. The caller is responsible for any timezone conversion.
    """
    def test_naive_datetime_handling(self):
        """Tests that naive datetimes are interpreted as UTC."""
        # Create naive datetime objects (will be treated as UTC)
        naive_start = datetime(2023, 1, 1, 10, 0, 0)
        naive_end = datetime(2023, 1, 10, 18, 0, 0)

        # Validate the range
        aware_start, aware_end = DateParser.validate_date_range(naive_start, naive_end)

        # Check that the start date is now timezone-aware and in UTC
        assert aware_start.tzinfo == timezone.utc
        assert aware_start.hour == 10  # Hour should be preserved
        assert aware_start.minute == 0
        assert aware_start.day == 1
        assert aware_start.month == 1
        assert aware_start.year == 2023

        # Check that the end date is now timezone-aware and in UTC
        assert aware_end.tzinfo == timezone.utc
        assert aware_end.hour == 23  # End of day
        assert aware_end.minute == 59
        assert aware_end.second == 59
        assert aware_end.day == 10
        assert aware_end.month == 1
        assert aware_end.year == 2023
    
    def test_parse_date_with_timezone_info(self):
        """Test that timezone information in date strings is rejected."""
        # These should all raise DateParseError because they contain timezone info
        test_cases = [
            '2025-01-15T14:30:00+00:00',
            '2025-01-15 14:30:00+05:30',
            '2025-01-15 14:30:00-08:00',
            '2025-01-15 14:30:00Z',
            '2025-01-15 14:30:00 UTC'
        ]
        
        for date_str in test_cases:
            with pytest.raises(DateParseError) as excinfo:
                DateParser.parse_date(date_str)
            error_msg = str(excinfo.value).lower()
            assert any(term in error_msg for term in ['timezone', 'utc', 'format']), \
                f"Expected timezone-related error for '{date_str}', got: {error_msg}"
    
    def test_parse_date_formats(self):
        """Test that valid UTC date formats are parsed correctly."""
        test_cases = [
            # Date only (interpreted as midnight UTC)
            ('2025-01-15', datetime(2025, 1, 15, 0, 0, tzinfo=timezone.utc)),
            # Date and time (interpreted as UTC)
            ('2025-01-15 14:30', datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc)),
            # Relative dates
            ('now', None),  # Can't test exact value, but should not raise
            ('1d', None),   # Can't test exact value, but should not raise
            ('2w', None),   # Can't test exact value, but should not raise
        ]
        
        for date_str, expected in test_cases:
            try:
                result = DateParser.parse_date(date_str)
                if expected is not None:
                    assert result == expected
                # For relative dates, just verify we got a datetime
                assert isinstance(result, datetime)
                assert result.tzinfo == timezone.utc
            except Exception as e:
                pytest.fail(f"Failed to parse date '{date_str}': {e}")
    

    
    def test_parse_date_invalid_formats(self):
        """Test that invalid date formats raise appropriate errors."""
        test_cases = [
            # (input, expected_error_contains)
            ('', 'date string cannot be empty'),
            ('not-a-date', 'parse date'),
            ('2025-13-01', 'invalid date'),
            ('2025-01-32', 'invalid date'),
            ('2025-01-15 25:00', 'could not parse datetime'),
            ('2025-01-15 14:60', 'could not parse datetime'),
            # Timezone offsets not allowed
            ('2025-01-15 14:30 +0000', 'utc'),
            ('2025-01-15 14:30 -0500', 'utc'),
        ]
        
        for date_str, error_keyword in test_cases:
            with pytest.raises(DateParseError) as excinfo:
                DateParser.parse_date(date_str)
            error_msg = str(excinfo.value).lower()
            assert error_keyword in error_msg, \
                f"Expected error message to contain '{error_keyword}' for input '{date_str}', got: {error_msg}"
