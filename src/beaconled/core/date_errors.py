"""Date-related exceptions for the Beacon Delivery Compass application.

This module contains exceptions specific to date parsing and validation.
"""

from datetime import datetime

from beaconled.exceptions import ErrorCode, ValidationError


class DateError(ValidationError):
    """Base class for date-related validation errors.

    This serves as a common base for all date-related exceptions.
    """

    DEFAULT_ERROR_CODE = ErrorCode.DATE_ERROR

    def __init__(
        self,
        message: str,
        error_code: ErrorCode | None = None,
        details: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            message=message,
            field="date",
            error_code=error_code or self.DEFAULT_ERROR_CODE,
            details=details or {},
            **kwargs,
        )


class DateParseError(DateError):
    """Raised when date parsing fails.

    Attributes:
        date_str: The date string that could not be parsed
        format_hint: Suggestion for the expected format (optional)
    """

    DEFAULT_ERROR_CODE = ErrorCode.DATE_PARSE_ERROR

    def __init__(
        self,
        date_str: str,
        message: str | None = None,
        format_hint: str | None = None,
        **kwargs: object,
    ) -> None:
        self.date_str = date_str
        self.format_hint = format_hint

        if not message:
            message = f"Could not parse date: '{date_str}'"
            if format_hint:
                message += f"\nExpected format: {format_hint}"

        details = kwargs.pop("details", {})
        details["date_string"] = date_str
        if format_hint:
            details["format_hint"] = format_hint

        super().__init__(
            message=message,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
            **kwargs,
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
        start_date: datetime,
        end_date: datetime,
        message: str | None = None,
        **kwargs: object,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date

        if not message:
            message = f"Invalid date range: {start_date} to {end_date}"

        # Get any existing details or create a new dict
        details = kwargs.pop("details", {})
        details["start_date"] = str(start_date)
        details["end_date"] = str(end_date)

        # Remove field from kwargs to prevent duplicate field parameter
        kwargs.pop("field", None)

        # Call the parent class (DateError) with the correct parameters
        # Note: We don't pass field here to prevent the duplicate field issue
        super().__init__(
            message=message,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
            **kwargs,
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
