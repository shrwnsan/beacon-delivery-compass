"""Custom exceptions for the Beacon Delivery Compass application.

This module defines custom exceptions with error codes for better programmatic handling.
Each exception includes a unique error code and a human-readable message.
"""
from typing import Any, Optional, Dict
from enum import Enum

# Re-export date-related errors for backward compatibility.
# Prefer importing from beaconled.core.date_errors in new code.
from .core.date_errors import DateParseError, DateRangeError

__all__ = [
    "DateParseError",
    "DateRangeError",
]

class ErrorCode(Enum):
    """Error codes for different types of exceptions."""
    # Generic errors (1000-1999)
    UNKNOWN_ERROR = 1000
    CONFIGURATION_ERROR = 1001
    VALIDATION_ERROR = 1002
    
    # Date-related errors (2000-2999)
    DATE_ERROR = 2000
    DATE_PARSE_ERROR = 2001
    DATE_RANGE_ERROR = 2002
    
    # Repository errors (3000-3999)
    REPOSITORY_ERROR = 3000
    INVALID_REPOSITORY = 3001
    COMMIT_ERROR = 3002
    COMMIT_NOT_FOUND = 3003
    COMMIT_PARSE_ERROR = 3004

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
    ) -> None:
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
        field: Optional[str] = None,
        value: Any = None,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.field = field
        self.value = value
        details = details or {}
        if field is not None:
            details['field'] = field
        if value is not None:
            details['value'] = value
            
        super().__init__(
            message=message,
            error_code=error_code or self.DEFAULT_ERROR_CODE,
            details=details
        )

class RepositoryError(BeaconError):
    """Base class for repository-related errors."""
    DEFAULT_ERROR_CODE = ErrorCode.REPOSITORY_ERROR

class InvalidRepositoryError(RepositoryError):
    """Raised when the repository path is invalid or not a git repository."""
    DEFAULT_ERROR_CODE = ErrorCode.INVALID_REPOSITORY
    
    def __init__(
        self, 
        repo_path: str, 
        reason: Optional[str] = None, 
        **kwargs: Any
    ) -> None:
        self.repo_path = repo_path
        self.reason = reason
        message = f"Invalid repository: {repo_path}"
        if reason:
            message += f" ({reason})"
            
        details = kwargs.pop('details', {})
        details['repo_path'] = repo_path
        if reason:
            details['reason'] = reason
            
        # Do not pass error_code twice; allow base to use DEFAULT_ERROR_CODE via its own logic
        super().__init__(
            message=message,
            details=details,
            **kwargs
        )

class CommitError(RepositoryError):
    """Base class for commit-related errors.
    
    Attributes:
        commit_ref: The commit reference (hash, branch, tag, etc.)
        message: Human-readable error message
        details: Additional error context
    """
    DEFAULT_ERROR_CODE = ErrorCode.COMMIT_ERROR
    
    def __init__(
        self, 
        commit_ref: str, 
        message: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        self.commit_ref = commit_ref
        message = message or f"Error processing commit: {commit_ref}"
        
        details = details or {}
        details['commit_ref'] = commit_ref
        
        # Avoid passing error_code explicitly to prevent duplicate keyword issues
        super().__init__(
            message=message,
            details=details,
            **kwargs
        )
        
    @classmethod
    def from_commit(
        cls, 
        commit_ref: str, 
        reason: Optional[str] = None,
        **kwargs: Any
    ) -> 'CommitError':
        """Create a CommitError with a reason.
        
        Args:
            commit_ref: The commit reference that caused the error
            reason: Optional reason for the error
            **kwargs: Additional arguments to pass to the exception
            
        Returns:
            A configured CommitError instance
        """
        message = f"Error processing commit {commit_ref}"
        if reason:
            message += f": {reason}"
            
        return cls(commit_ref=commit_ref, message=message, **kwargs)


class CommitNotFoundError(CommitError):
    """Raised when a commit cannot be found in the repository."""
    DEFAULT_ERROR_CODE = ErrorCode.COMMIT_NOT_FOUND
    
    def __init__(
        self, 
        commit_ref: str, 
        repo_path: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        message = f"Commit not found: {commit_ref}"
        details = kwargs.pop('details', {})
        details['commit_ref'] = commit_ref
        if repo_path:
            details['repo_path'] = repo_path
            message += f" in repository {repo_path}"
            
        # CommitError parent will handle DEFAULT_ERROR_CODE; avoid duplicating error_code
        super().__init__(
            commit_ref=commit_ref,
            message=message,
            details=details,
            **kwargs
        )


class CommitParseError(CommitError):
    """Raised when there's an error parsing commit data."""
    DEFAULT_ERROR_CODE = ErrorCode.COMMIT_PARSE_ERROR
    
    def __init__(
        self, 
        commit_ref: str, 
        parse_error: Optional[Exception] = None,
        **kwargs: Any
    ) -> None:
        message = f"Failed to parse commit: {commit_ref}"
        details = kwargs.pop('details', {})
        details['commit_ref'] = commit_ref
        
        if parse_error:
            details['parse_error'] = str(parse_error)
            message += f" - {str(parse_error)}"
            
        # CommitError parent provides error_code behavior; do not pass error_code again
        super().__init__(
            commit_ref=commit_ref,
            message=message,
            details=details,
            **kwargs
        )

# DateRangeError has been moved to core.date_errors module
