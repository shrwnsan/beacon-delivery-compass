"""Custom exceptions for the Beacon Delivery Compass application.

This module defines custom exceptions with error codes for better programmatic handling.
Each exception includes a unique error code and a human-readable message.
"""
from typing import Any, Optional, Dict, Type
from enum import Enum, auto

class ErrorCode(Enum):
    """Error codes for different types of exceptions."""
    # Generic errors (1000-1999)
    UNKNOWN_ERROR = 1000
    CONFIGURATION_ERROR = 1001
    VALIDATION_ERROR = 1002
    
    # Date-related errors (2000-2999)
    DATE_PARSE_ERROR = 2001
    DATE_RANGE_ERROR = 2002
    
    # Repository errors (3000-3999)
    REPOSITORY_ERROR = 3000
    INVALID_REPOSITORY = 3001
    COMMIT_ERROR = 3002

class BeaconError(Exception):
    """Base exception class for all application-specific exceptions.
    
    Attributes:
        error_code: A unique error code from the ErrorCode enum
        message: Human-readable error message
        details: Additional error details (optional)
    """
    DEFAULT_ERROR_CODE = ErrorCode.UNKNOWN_ERROR
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code or self.DEFAULT_ERROR_CODE
        self.details = details or {}
        super().__init__(message)

class ConfigurationError(BeaconError):
    """Raised when there is a configuration error."""
    DEFAULT_ERROR_CODE = ErrorCode.CONFIGURATION_ERROR

class ValidationError(BeaconError):
    """Raised when input validation fails.
    
    Attributes:
        message: Explanation of the validation error
        field: The field that failed validation (optional)
        value: The value that caused the validation to fail (optional)
        error_code: Specific error code (defaults to VALIDATION_ERROR)
    """
    DEFAULT_ERROR_CODE = ErrorCode.VALIDATION_ERROR
    
    def __init__(
        self,
        message: str,
        field: str = None,
        value: Any = None,
        error_code: ErrorCode = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.field = field
        self.value = value
        details = details or {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = value
            
        super().__init__(
            message=message,
            error_code=error_code or self.DEFAULT_ERROR_CODE,
            details=details
        )

class DateParseError(ValidationError):
    """Raised when date parsing fails.
    
    Attributes:
        date_str: The date string that could not be parsed
        format_hint: Suggestion for the expected format (optional)
    """
    DEFAULT_ERROR_CODE = ErrorCode.DATE_PARSE_ERROR
    
    def __init__(self, date_str: str, format_hint: str = None, **kwargs):
        self.date_str = date_str
        self.format_hint = format_hint
        message = f"Could not parse date: '{date_str}'"
        if format_hint:
            message += f"\nExpected format: {format_hint}"
            
        details = kwargs.pop('details', {})
        details['date_string'] = date_str
        if format_hint:
            details['format_hint'] = format_hint
            
        super().__init__(
            message=message,
            field="date",
            value=date_str,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
            **kwargs
        )

class RepositoryError(BeaconError):
    """Base class for repository-related errors."""
    DEFAULT_ERROR_CODE = ErrorCode.REPOSITORY_ERROR

class InvalidRepositoryError(RepositoryError):
    """Raised when the repository path is invalid or not a git repository."""
    DEFAULT_ERROR_CODE = ErrorCode.INVALID_REPOSITORY
    
    def __init__(self, repo_path: str, reason: str = None, **kwargs):
        self.repo_path = repo_path
        self.reason = reason
        message = f"Invalid repository: {repo_path}"
        if reason:
            message += f" ({reason})"
            
        details = kwargs.pop('details', {})
        details['repo_path'] = repo_path
        if reason:
            details['reason'] = reason
            
        super().__init__(
            message=message,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
            **kwargs
        )

class CommitError(RepositoryError):
    """Raised when there's an error processing a commit."""
    DEFAULT_ERROR_CODE = ErrorCode.COMMIT_ERROR
    
    def __init__(self, commit_ref: str, message: str = None, **kwargs):
        self.commit_ref = commit_ref
        message = message or f"Error processing commit: {commit_ref}"
        
        details = kwargs.pop('details', {})
        details['commit_ref'] = commit_ref
        
        super().__init__(
            message=message,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
            **kwargs
        )

class DateRangeError(ValidationError):
    """Raised when there's an error with a date range."""
    DEFAULT_ERROR_CODE = ErrorCode.DATE_RANGE_ERROR
    
    def __init__(self, start_date, end_date, message: str = None, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        if not message:
            message = f"Invalid date range: {start_date} to {end_date}"
            
        details = kwargs.pop('details', {})
        details['start_date'] = str(start_date)
        details['end_date'] = str(end_date)
        
        super().__init__(
            message=message,
            field="date_range",
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
            **kwargs
        )
