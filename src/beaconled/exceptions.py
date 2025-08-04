"""Custom exceptions for the Beacon Delivery Compass application.

This module defines custom exceptions with error codes for better programmatic handling.
Each exception includes a unique error code and a human-readable message.
"""
from typing import Any, Optional, Dict, Type, Union
from enum import Enum, auto

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

# Date-related errors have been moved to core.date_errors module

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
        message: str = None, 
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self.commit_ref = commit_ref
        message = message or f"Error processing commit: {commit_ref}"
        
        details = details or {}
        details['commit_ref'] = commit_ref
        
        super().__init__(
            message=message,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
            **kwargs
        )
        
    @classmethod
    def from_commit(
        cls, 
        commit_ref: str, 
        reason: str = None,
        **kwargs
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
        repo_path: str = None,
        **kwargs
    ):
        message = f"Commit not found: {commit_ref}"
        details = kwargs.pop('details', {})
        details['commit_ref'] = commit_ref
        if repo_path:
            details['repo_path'] = repo_path
            message += f" in repository {repo_path}"
            
        super().__init__(
            commit_ref=commit_ref,
            message=message,
            details=details,
            error_code=self.DEFAULT_ERROR_CODE,
            **kwargs
        )


class CommitParseError(CommitError):
    """Raised when there's an error parsing commit data."""
    DEFAULT_ERROR_CODE = ErrorCode.COMMIT_PARSE_ERROR
    
    def __init__(
        self, 
        commit_ref: str, 
        parse_error: Exception = None,
        **kwargs
    ):
        message = f"Failed to parse commit: {commit_ref}"
        details = kwargs.pop('details', {})
        details['commit_ref'] = commit_ref
        
        if parse_error:
            details['parse_error'] = str(parse_error)
            message += f" - {str(parse_error)}"
            
        super().__init__(
            commit_ref=commit_ref,
            message=message,
            details=details,
            error_code=self.DEFAULT_ERROR_CODE,
            **kwargs
        )

# DateRangeError has been moved to core.date_errors module
