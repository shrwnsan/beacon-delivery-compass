"""Tests for date-related exceptions."""

from datetime import datetime, timezone

from beaconled.core.date_errors import DateError, DateParseError, DateRangeError
from beaconled.exceptions import ErrorCode, ValidationError


def test_date_error_initialization():
    """Test basic DateError initialization."""
    error = DateError("Test error")

    assert isinstance(error, ValidationError)
    assert str(error) == "Test error"
    assert error.field == "date"
    assert error.error_code == ErrorCode.DATE_ERROR
    assert error.details == {"field": "date"}


def test_date_error_with_details():
    """Test DateError with custom details."""
    details = {"custom": "detail"}
    error = DateError("Test error", details=details)

    assert error.details == {"custom": "detail", "field": "date"}


def test_date_parse_error_initialization():
    """Test DateParseError initialization."""
    error = DateParseError("2023-01-01")

    assert str(error) == "Could not parse date: '2023-01-01'"
    assert error.date_str == "2023-01-01"
    assert error.format_hint is None
    assert error.error_code == ErrorCode.DATE_PARSE_ERROR
    assert error.details == {"date_string": "2023-01-01", "field": "date"}


def test_date_parse_error_with_format_hint():
    """Test DateParseError with format hint."""
    error = DateParseError("01/01/2023", format_hint="YYYY-MM-DD")

    assert "Expected format: YYYY-MM-DD" in str(error)
    assert error.format_hint == "YYYY-MM-DD"
    assert error.details["format_hint"] == "YYYY-MM-DD"


def test_date_parse_error_custom_message():
    """Test DateParseError with custom message."""
    error = DateParseError("invalid", message="Custom message")
    assert str(error) == "Custom message"


def test_date_range_error_initialization():
    """Test DateRangeError initialization."""
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end = datetime(2023, 1, 2, tzinfo=timezone.utc)
    error = DateRangeError(start, end)

    error_str = str(error)
    assert "2023-01-01" in error_str
    assert "2023-01-02" in error_str
    assert error.start_date == start
    assert error.end_date == end
    assert error.error_code == ErrorCode.DATE_RANGE_ERROR
    assert error.details["start_date"] == "2023-01-01 00:00:00+00:00"
    assert error.details["end_date"] == "2023-01-02 00:00:00+00:00"


def test_date_range_error_custom_message():
    """Test DateRangeError with custom message."""
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end = datetime(2023, 1, 2, tzinfo=timezone.utc)
    error = DateRangeError(start, end, message="Custom range error")

    assert str(error) == "Custom range error"


def test_date_range_error_from_dates():
    """Test DateRangeError.from_dates factory method."""
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end = datetime(2023, 1, 2, tzinfo=timezone.utc)

    # Test with just dates
    error = DateRangeError.from_dates(start, end)
    error_str = str(error)
    assert "2023-01-01" in error_str
    assert "2023-01-02" in error_str

    # Test with reason
    error = DateRangeError.from_dates(start, end, reason="end before start")
    assert "(end before start)" in str(error)

    # Test with additional details
    error = DateRangeError.from_dates(start, end, details={"custom": "detail"})
    assert error.details == {
        "custom": "detail",
        "start_date": "2023-01-01 00:00:00+00:00",
        "end_date": "2023-01-02 00:00:00+00:00",
        "field": "date",
    }


def test_date_range_error_with_details():
    """Test DateRangeError with custom details."""
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end = datetime(2023, 1, 2, tzinfo=timezone.utc)

    error = DateRangeError(start, end, details={"custom": "detail"})

    assert error.details == {
        "custom": "detail",
        "start_date": "2023-01-01 00:00:00+00:00",
        "end_date": "2023-01-02 00:00:00+00:00",
        "field": "date",
    }
