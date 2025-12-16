# Copyright 2025 Beacon, shrwnsan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Date-related exceptions for the Beacon Delivery Compass application.

This module contains exceptions specific to date parsing and validation.
"""

from datetime import datetime
from typing import Any

from beaconled.exceptions import ErrorCode, ValidationError


class DateError(ValidationError):
    """Base class for date-related errors."""

    DEFAULT_ERROR_CODE = ErrorCode.DATE_ERROR

    def __init__(
        self,
        message: str,
        error_code: ErrorCode | None = None,
        details: dict[str, Any] | None = None,
        field: str = "date",
    ) -> None:
        # Ensure details is a proper dictionary
        safe_details: dict[str, Any] = {}
        if details is not None:
            safe_details.update(details)
        safe_details["field"] = field

        super().__init__(
            message=message,
            field=field,
            error_code=error_code or self.DEFAULT_ERROR_CODE,
            details=safe_details,
        )


class DateParseError(DateError):
    """Raised when a date string cannot be parsed."""

    DEFAULT_ERROR_CODE = ErrorCode.DATE_PARSE_ERROR

    def __init__(
        self,
        date_str: str,
        message: str | None = None,
        format_hint: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.date_str = date_str
        self.format_hint = format_hint

        # Store original date string in details for internal logging
        details: dict[str, Any] = {
            "date_string": date_str,
        }

        # Format the error message - sanitize user input for display
        if message is None:
            # Only show limited information about the input to prevent information disclosure
            # For potentially sensitive inputs like "../../../etc/passwd", show even less
            if any(
                pattern in date_str.lower()
                for pattern in ["../", "..\\", "/etc/", "\\windows\\", "passwd", "shadow"]
            ):
                # For obviously suspicious inputs, show minimal info
                safe_date_preview = "<sensitive_input>"
            elif len(date_str) > 20:
                safe_date_preview = date_str[:17] + "..."
            else:
                safe_date_preview = date_str
            message = f"Could not parse date: '{safe_date_preview}'"
            if format_hint:
                message += f"\nExpected format: {format_hint}"

        # Add format hint if provided
        if format_hint is not None:
            details["format_hint"] = format_hint

        # Add any additional details from kwargs (except 'details')
        for key, value in kwargs.items():
            if key != "details":
                details[key] = value

        # Try to sanitize the message for user display
        try:
            from beaconled.utils.security import sanitize_error_message

            safe_message = sanitize_error_message(message)
        except ImportError:
            # Fallback to original message if sanitization fails
            safe_message = message

        super().__init__(
            message=safe_message,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
        )


class DateRangeError(DateError):
    """Raised when there's an error with a date range.

    Attributes:
        start_date: The start date of the invalid range
        end_date: The end date of the invalid range
    """

    DEFAULT_ERROR_CODE = ErrorCode.DATE_RANGE_ERROR

    def __init__(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        message: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date

        # Generate default message if not provided
        if message is None:
            if start_date and end_date:
                message = f"Invalid date range: {start_date} to {end_date}"
            else:
                message = "Invalid date range"

        # Initialize details dictionary
        details: dict[str, Any] = {}

        # Add start and end dates to details if provided using space format
        if start_date is not None:
            details["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S%z")
        if end_date is not None:
            details["end_date"] = end_date.strftime("%Y-%m-%d %H:%M:%S%z")

        # Get any existing details from kwargs
        if "details" in kwargs and isinstance(kwargs["details"], dict):
            details.update(kwargs["details"])
            del kwargs["details"]

        # Extract error_code if provided
        error_code = kwargs.pop("error_code", self.DEFAULT_ERROR_CODE)

        # Add any additional kwargs to details (excluding special parameters)
        for key, value in kwargs.items():
            details[key] = value

        # Call the parent class (DateError) with the correct parameters
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )

    @classmethod
    def from_dates(
        cls,
        start_date: datetime,
        end_date: datetime,
        reason: str | None = None,
        **kwargs: object,
    ) -> "DateRangeError":
        """Create a DateRangeError from datetime objects with an optional reason."""
        message = f"Invalid date range: {start_date} to {end_date}"
        if reason:
            message += f" ({reason})"

        return cls(start_date=start_date, end_date=end_date, message=message, **kwargs)
