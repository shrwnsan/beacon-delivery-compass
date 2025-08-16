"""Property-based tests for date parsing functionality."""

import re
from datetime import datetime, timezone

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from beaconled.core.analyzer import GitAnalyzer
from beaconled.core.date_errors import DateParseError
from beaconled.exceptions import ValidationError


class TestPropertyBasedDateParsing:
    """Property-based tests for date parsing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = GitAnalyzer(".")

    # Strategy for generating valid relative date strings
    @st.composite
    def relative_date_strategy(draw, min_value: int = 1, max_value: int = 1000) -> str:
        """Generate valid relative date strings."""
        number = draw(st.integers(min_value=min_value, max_value=max_value))
        unit = draw(st.sampled_from(["d", "w", "m", "y"]))
        return f"{number}{unit}"

    # Strategy for generating valid absolute date strings
    @st.composite
    def absolute_date_strategy(draw, min_year: int = 2000, max_year: int = 2100) -> str:
        """Generate valid absolute date strings."""
        year = draw(st.integers(min_year, max_year))
        month = draw(st.integers(1, 12))
        day = draw(st.integers(1, 28))  # Safe upper bound for all months

        # Sometimes include time, sometimes not
        if draw(st.booleans()):
            hour = draw(st.integers(0, 23))
            minute = draw(st.integers(0, 59))
            return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
        return f"{year:04d}-{month:02d}-{day:02d}"

    @given(relative_date_strategy())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_parse_relative_dates_property(self, date_str: str):
        """Test that valid relative dates are parsed correctly."""
        try:
            result = self.analyzer._parse_date(date_str)
            # Verify the result is a datetime in UTC
            assert isinstance(result, datetime)
            assert result.tzinfo == timezone.utc

            # Verify the result is not in the future (since we're using 'now' as reference)
            assert result <= datetime.now(timezone.utc)

        except (DateParseError, ValidationError) as e:
            pytest.fail(f"Failed to parse valid relative date '{date_str}': {e}")

    @given(absolute_date_strategy())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_parse_absolute_dates_property(self, date_str: str):
        """Test that valid absolute dates are parsed correctly."""
        try:
            result = self.analyzer._parse_date(date_str)
            # Verify the result is a datetime in UTC
            assert isinstance(result, datetime)
            assert result.tzinfo == timezone.utc

            # Verify the parsed date matches the input (ignoring time for date-only strings)
            if " " in date_str:
                # Datetime with time
                expected = datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(
                    tzinfo=timezone.utc,
                )
                assert result == expected
            else:
                # Date only - should be at midnight UTC
                expected_date = (
                    datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
                )
                assert result.date() == expected_date
                assert result.hour == 0
                assert result.minute == 0
                assert result.second == 0
                assert result.microsecond == 0

        except (DateParseError, ValidationError) as e:
            pytest.fail(f"Failed to parse valid absolute date '{date_str}': {e}")

    @given(
        st.datetimes(
            min_value=datetime(2000, 1, 1, tzinfo=timezone.utc),
            max_value=datetime(2100, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            timezones=st.just(timezone.utc),
        ),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_roundtrip_datetime(self, dt: datetime, tzinfo=timezone.utc):
        """Test that datetimes can be formatted and parsed back to the same value."""
        # Format the datetime in a way that our parser can handle
        date_str = dt.strftime("%Y-%m-%d %H:%M")
        parsed = self.analyzer._parse_date(date_str)

        # The parsed datetime should be the same as the input (to the minute)
        assert parsed.replace(second=0, microsecond=0) == dt.replace(
            second=0,
            microsecond=0,
        )

    @given(st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_dates_raise_errors(self, text: str):
        """Test that invalid date strings raise appropriate exceptions."""
        # Skip empty strings and valid formats
        if not text.strip():
            return

        # Skip strings that happen to match our valid patterns
        if re.match(r"^\d+[dwmy]$", text):  # Relative dates
            return
        if re.match(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?$", text):  # Absolute dates
            return
        if text.lower() == "now":
            return

        # The actual test - invalid formats should raise an exception
        with pytest.raises((DateParseError, ValidationError)):
            self.analyzer._parse_date(text)

    @given(
        st.datetimes(
            min_value=datetime(1970, 1, 2, tzinfo=timezone.utc),
            max_value=datetime(2038, 1, 1, tzinfo=timezone.utc),
            timezones=st.just(timezone.utc),
        ),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_parse_git_date_property(self, dt: datetime):
        """Test that git date strings are parsed correctly."""
        # Create a git-style date string (timestamp +0000)
        git_date = f"{int(dt.timestamp())} +0000"
        result = self.analyzer._parse_git_date(git_date)

        # Verify the result is a datetime in UTC
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

        # The date part should match the input, ignoring minor precision differences
        assert result.date() == dt.date()
