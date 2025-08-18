"""Date parsing and manipulation utilities for Beacon.

This module provides comprehensive date handling functionality, including parsing
various date formats, relative date calculations, and timezone management.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union, Tuple
import re

from ..exceptions import ValidationError
from ..core.date_errors import DateParseError


class DateParser:
    """Handles parsing and manipulation of dates for various use cases.
    
    This class provides methods for parsing dates from strings, handling relative
    dates, and validating date ranges. All dates are handled in UTC.
    """
    
    # Pre-compile regex patterns for better performance
    RELATIVE_DATE_PATTERN = re.compile(r'^\d+[dwmMy]$')  # e.g., 1d, 2w, 3m, 1y
    ISO_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    ISO_DATETIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')
    GIT_DATE_PATTERN = re.compile(
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}( [+-]\d{4})?$'
    )
    COMMIT_HASH_PATTERN = re.compile(r'^[0-9a-fA-F]{7,40}$')
    
    @classmethod
    def parse_date(cls, date_str: str) -> datetime:
        """Parse a date string into a timezone-aware datetime in UTC.
        
        All dates are interpreted as UTC. Timezone information in the input
        is not supported - please convert to UTC before passing to this function.
        
        Supported formats:
        - Relative: 1d (days), 2w (weeks), 3m (months), 1y (years)
        - Absolute: YYYY-MM-DD or YYYY-MM-DD HH:MM (both in UTC)
        - Special: 'now' for current time in UTC
        
        Args:
            date_str: The date string to parse, must be in UTC
            
        Returns:
            A timezone-aware datetime in UTC.
            
        Raises:
            DateParseError: If the date string cannot be parsed or contains timezone info.
        """
        if not date_str or not isinstance(date_str, str) or not date_str.strip():
            raise DateParseError(
                date_str or "",
                "Date string cannot be empty. Please provide a valid date in one of these formats (all times must be in UTC):\n"
                "  - Relative: 1d (days), 2w (weeks), 3m (months), 1y (years)\n"
                "  - Absolute: YYYY-MM-DD or YYYY-MM-DD HH:MM (interpreted as UTC)\n"
                "  - Special: 'now' for current time in UTC"
            )
            
        date_str = date_str.strip()
        
        # Handle special 'now' value
        if date_str.lower() == 'now':
            return datetime.now(timezone.utc)
        
        dt = None
        # Handle relative dates (e.g., 1d, 2w, 3m, 1y)
        if cls.RELATIVE_DATE_PATTERN.match(date_str):
            dt = cls._parse_relative_date(date_str)
        # Handle absolute dates
        elif cls.ISO_DATE_PATTERN.match(date_str):
            dt = cls._parse_iso_date(date_str)
        elif cls.ISO_DATETIME_PATTERN.match(date_str):
            dt = cls._parse_iso_datetime(date_str)
        else:
            raise DateParseError(
                date_str,
                "Could not parse date. Please use one of (all times must be in UTC):\n"
                "  - Relative: <number><unit> (e.g., '1d', '2w', '3m', '1y')\n"
                "  - Absolute: YYYY-MM-DD or YYYY-MM-DD HH:MM (interpreted as UTC)\n"
                "  - 'now' for current time in UTC"
            )

        # Ensure the final datetime is in UTC
        if dt:
            if dt.tzinfo is not None and dt.tzinfo != timezone.utc:
                raise DateParseError(
                    date_str,
                    "Timezone information is not supported. Please convert to UTC before passing to this function."
                )
            return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)

        # This path should not be reached if parsing is successful.
        raise DateParseError(date_str, "Failed to produce a valid datetime object.")
    
    @classmethod
    def parse_git_date(cls, date_str: str) -> datetime:
        """Parse a git date string into a UTC datetime.

        Supports formats like:
        - '<unix_timestamp> <+/-HHMM>' (e.g., '1690200000 +0000')
        - '<unix_timestamp>' (assumed UTC)

        Args:
            date_str: Date string from git log.
            
        Returns:
            A timezone-aware datetime in UTC.
            
        Raises:
            DateParseError: If the date string cannot be parsed.
        """
        if not date_str or not isinstance(date_str, str):
            raise DateParseError(
                str(date_str) if date_str is not None else "None",
                "Date string cannot be None or empty"
            )
            
        date_str = date_str.strip()
        try:
            parts = date_str.split()
            if len(parts) == 2:
                # <unix_timestamp> <+/-HHMM>
                ts, offset = parts
                dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
                # Parse offset: e.g. +0900, -0500
                sign = 1 if offset[0] == '+' else -1
                hours = int(offset[1:3])
                minutes = int(offset[3:5])
                delta = timedelta(hours=sign * hours, minutes=sign * minutes)
                # The offset is from UTC, so subtract it to get UTC time
                dt = dt - delta
                return dt.replace(tzinfo=timezone.utc)
            elif len(parts) == 1:
                # <unix_timestamp> only, assume UTC
                ts = parts[0]
                dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
                return dt
            else:
                raise DateParseError(date_str, "Unexpected git date format")
        except Exception as e:
            raise DateParseError(date_str, f"Failed to parse git date: {str(e)}") from e
    
    @classmethod
    def validate_date_range(
        cls, 
        start_date: Optional[Union[datetime, str]] = None, 
        end_date: Optional[Union[datetime, str]] = None
    ) -> Tuple[datetime, datetime]:
        """Validate and normalize a date range, returning UTC datetimes.
        
        Args:
            start_date: Start date as string or datetime.
            end_date: End date as string or datetime.
            
        Returns:
            (start_date, end_date) as UTC datetimes.
            
        Raises:
            ValueError: If the range is invalid.
        """
        # Parse string dates
        if start_date is not None and isinstance(start_date, str):
            start_date = cls.parse_date(start_date)
        if end_date is not None and isinstance(end_date, str):
            if end_date.lower() in ['now', 'today', '']:
                end_date = datetime.now(timezone.utc)
            else:
                end_date = cls.parse_date(end_date)
                
        # Set defaults
        if start_date is None:
            start_date = datetime.min.replace(tzinfo=timezone.utc)
        if end_date is None:
            end_date = datetime.now(timezone.utc)
            
        # Ensure timezone-aware and UTC
        if not start_date.tzinfo:
            start_date = start_date.replace(tzinfo=timezone.utc)
        else:
            start_date = start_date.astimezone(timezone.utc)
            
        if not end_date.tzinfo:
            end_date = end_date.replace(tzinfo=timezone.utc)
        else:
            end_date = end_date.astimezone(timezone.utc)
            
        # Validate BEFORE normalizing end_date to end of day so error message matches expected timestamp
        if end_date < start_date:
            raise ValueError(
                f"Invalid date range: end date ({end_date}) is before start date ({start_date})"
            )
        
        # Always normalize end_date to end of day after validation
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
        return start_date, end_date
    
    @classmethod
    def _parse_relative_date(cls, date_str: str) -> datetime:
        """Parse a relative date string (e.g., '1d', '2w', '3m', '1y')."""
        try:
            num = int(date_str[:-1])
            if num <= 0:
                raise ValueError("Relative date value must be positive")
                
            unit = date_str[-1].lower()
            now = datetime.now(timezone.utc)
            
            # Map units to timedelta
            unit_map = {
                'd': ('day', 'days', timedelta(days=1)),
                'w': ('week', 'weeks', timedelta(weeks=1)),
                'm': ('month', 'months', timedelta(weeks=4)),  # Approximate
                'y': ('year', 'years', timedelta(weeks=52))    # Approximate
            }
            
            if unit not in unit_map:
                valid_units = ", ".join(f"'{u}'" for u in unit_map.keys())
                raise ValueError(f"Invalid time unit '{unit}'. Valid units are: {valid_units}")
            
            _, _, delta = unit_map[unit]
            return now - (delta * num)
            
        except (ValueError, IndexError) as e:
            raise DateParseError(
                date_str,
                f"Could not parse date: Invalid relative date format: {str(e)}. "
                "Expected format: <number><unit> where <unit> is one of: "
                "d (days), w (weeks), m (months), y (years)"
            ) from e

    @classmethod
    def _parse_iso_date(cls, date_str: str) -> datetime:
        """Parse an ISO date string (YYYY-MM-DD).
        
        Returns a naive datetime object that will be treated as UTC.
        The date is interpreted as midnight in UTC.
        
        Args:
            date_str: The date string to parse (YYYY-MM-DD)
            
        Returns:
            A naive datetime object representing the date at midnight UTC.
            
        Raises:
            DateParseError: If the date string is invalid.
        """
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            if not (2000 <= dt.year <= 2100):
                raise ValidationError(
                    f"Year {dt.year} is outside the supported range (2000-2100)",
                    field="date",
                    value=date_str
                )
            return dt
        except ValueError as e:
            raise DateParseError(
                date_str,
                f"Could not parse date: Invalid date format. Expected YYYY-MM-DD: {str(e)}"
            ) from e
    
    @classmethod
    def _parse_iso_datetime(cls, datetime_str: str) -> datetime:
        """Parse an ISO datetime string (YYYY-MM-DD HH:MM).
        
        Returns a naive datetime object that will be treated as UTC.
        
        Args:
            datetime_str: The datetime string to parse (YYYY-MM-DD HH:MM)
            
        Returns:
            A naive datetime object representing the datetime in UTC.
            
        Raises:
            DateParseError: If the datetime string is invalid.
        """
        try:
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            if not (2000 <= dt.year <= 2100):
                raise ValidationError(
                    f"Year {dt.year} is outside the supported range (2000-2100)",
                    field="datetime",
                    value=datetime_str
                )
            return dt
        except ValueError as e:
            raise DateParseError(
                datetime_str,
                f"Could not parse datetime: Invalid format. Expected YYYY-MM-DD HH:MM: {str(e)}"
            ) from e

    @classmethod
    def is_valid_commit_hash(cls, commit_hash: str) -> bool:
        """Validate a git commit hash or reference.

        Accepts 7-40 hex chars which matches short/full SHA-1 forms.
        """
        if not isinstance(commit_hash, str):
            return False
        commit_hash = commit_hash.strip()
        if not commit_hash:
            return False
        return bool(cls.COMMIT_HASH_PATTERN.match(commit_hash))
