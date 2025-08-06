"""Tests for timezone and DST handling in the analyzer."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from beaconled.core.analyzer import GitAnalyzer
from beaconled.utils.date_utils import DateParser
from beaconled.core.date_errors import DateParseError
from beaconled.exceptions import ValidationError

# Timezones to test - including ones with DST changes
TIMEZONES = [
    # UTC
    timezone.utc,
    # Timezones with DST
    timezone(timedelta(hours=1), 'CET'),  # Central European Time
    timezone(-timedelta(hours=5), 'EST'),  # Eastern Standard Time
    # Timezones without DST
    timezone(timedelta(hours=9), 'JST'),   # Japan Standard Time
    timezone(timedelta(hours=5, minutes=30), 'IST'),  # India Standard Time
]

# Known DST transition dates (approximate)
# Format: (timezone_name, transition_date, is_spring_forward)
DST_TRANSITIONS = [
    ('US/Eastern', '2025-03-09 02:00:00', True),   # Spring forward
    ('US/Eastern', '2025-11-02 02:00:00', False),  # Fall back
    ('Europe/London', '2025-03-30 01:00:00', True),
    ('Europe/London', '2025-10-26 01:00:00', False),
]

class TestTimezoneHandling:
    """Test timezone and DST handling in date parsing and analysis."""
    
    @pytest.mark.parametrize("tz", TIMEZONES)
    def test_parse_date_with_different_timezones(self, tz):
        """Test that dates without timezone info are assumed to be in UTC."""
        # Create a datetime in the target timezone
        local_dt = datetime(2025, 6, 15, 12, 0, tzinfo=tz)
        # Format without timezone info (as parse_date expects)
        local_date_str = local_dt.strftime('%Y-%m-%d %H:%M')
        
        # Parse the date string (which doesn't have timezone info)
        parsed_dt = DateParser.parse_date(local_date_str)
        
        # The parsed date should be in UTC
        assert parsed_dt.tzinfo == timezone.utc
        
        # The parsed date should match the input time exactly
        # because parse_date assumes no timezone means UTC
        assert parsed_dt.hour == local_dt.hour
        assert parsed_dt.minute == local_dt.minute
        assert parsed_dt.day == local_dt.day
        assert parsed_dt.month == local_dt.month
        assert parsed_dt.year == local_dt.year
    
    @pytest.mark.parametrize("tz_name,transition_time,is_spring_forward", DST_TRANSITIONS)
    def test_dst_transition_handling(self, tz_name, transition_time, is_spring_forward):
        """Test that DST transitions are handled correctly."""
        try:
            import pytz
            tz = pytz.timezone(tz_name)
        except ImportError:
            pytest.skip(f"pytz not available, skipping DST test for {tz_name}")
        
        transition_dt = tz.localize(datetime.strptime(transition_time, '%Y-%m-%d %H:%M'))
        
        # Test times around the DST transition
        if is_spring_forward:
            # Test just before and after spring forward
            before_dt = transition_dt - timedelta(minutes=30)
            after_dt = transition_dt + timedelta(hours=1)  # Skip the "missing" hour
        else:
            # Test just before and after fall back
            before_dt = transition_dt - timedelta(hours=1)
            after_dt = transition_dt + timedelta(minutes=30)
        
        # Test parsing times around the transition
        for dt in [before_dt, after_dt]:
            dt_str = dt.strftime('%Y-%m-%d %H:%M')
            parsed_dt = DateParser.parse_date(dt_str)
            
            # The parsed date should be in UTC
            assert parsed_dt.tzinfo == timezone.utc
            
            # The local time components should match (accounting for DST offset)
            offset = dt.utcoffset().total_seconds() / 3600
            expected_hour = (dt.hour - offset) % 24
            assert parsed_dt.hour == int(expected_hour)
            assert parsed_dt.day == dt.day
            assert parsed_dt.month == dt.month
            assert parsed_dt.year == dt.year
    
    def test_naive_datetime_handling(self):
        """Test that naive datetimes are assumed to be in UTC."""
        # Create a naive datetime (no timezone info)
        naive_dt = datetime(2025, 6, 15, 12, 0)
        dt_str = naive_dt.strftime('%Y-%m-%d %H:%M')
        
        # Parse the date string
        parsed_dt = GitDateParser.parse_date(dt_str)
        
        # The parsed date should be in UTC and match the input time exactly
        assert parsed_dt.tzinfo == timezone.utc
        assert parsed_dt.hour == naive_dt.hour
        assert parsed_dt.minute == naive_dt.minute
        assert parsed_dt.day == naive_dt.day
        assert parsed_dt.month == naive_dt.month
        assert parsed_dt.year == naive_dt.year
    
    @pytest.mark.parametrize("offset_hours", [-12, -6, 0, 6, 12])
    def test_utc_offset_handling(self, offset_hours):
        """Test that parse_date raises an error for timezone offsets (not supported)."""
        # Create a datetime with a specific UTC offset
        offset = timezone(timedelta(hours=offset_hours))
        dt = datetime(2025, 6, 15, 12, 0, tzinfo=offset)
        
        # Format with timezone offset (which parse_date doesn't support)
        if offset_hours >= 0:
            dt_str = dt.strftime(f'%Y-%m-%d %H:%M +{offset_hours:02d}00')
        else:
            dt_str = dt.strftime(f'%Y-%m-%d %H:%M -{abs(offset_hours):02d}00')
        
        # Should raise DateParseError because timezone offsets are not supported
        with pytest.raises(DateParseError):
            DateParser.parse_date(dt_str)
