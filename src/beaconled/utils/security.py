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

"""Security utilities for input sanitization and safe error reporting."""

import logging
import os
import re
from pathlib import Path
from typing import Any

# Logger
logger = logging.getLogger(__name__)


def sanitize_path(path: str | Path | None, max_components: int = 2) -> str:
    """Sanitize file paths to prevent information disclosure in error messages.

    This function returns only the last N components of a path to prevent
    exposing sensitive directory structures while maintaining useful context
    for debugging.

    Args:
        path: The file path to sanitize
        max_components: Maximum number of path components to show (default: 2)

    Returns:
        Sanitized path string with only the last N components

    Examples:
        >>> sanitize_path("/home/user/projects/myapp/config/settings.py")
        "myapp/config/settings.py"
        >>> sanitize_path("C:\\Users\\John\\Documents\\secret\\file.txt")
        "secret/file.txt"
        >>> sanitize_path("relative/path/to/file.txt")
        "to/file.txt"
    """
    if not path:
        return "<no path>"

    try:
        # Convert to Path object for consistent handling
        path_obj = Path(path)

        # Get all parts of the path
        parts = path_obj.parts

        # If path has fewer components than max, return as-is
        if len(parts) <= max_components:
            return str(path_obj)

        # Return only the last N components
        sanitized_parts = parts[-max_components:]
        return os.path.join(*sanitized_parts)

    except Exception as e:
        # If sanitization fails, log and return safe fallback
        logger.debug("Path sanitization failed for %s: %s", path, e)
        return "<sanitized path>"


def sanitize_error_message(message: str, max_length: int = 200) -> str:
    """Sanitize error messages to prevent information disclosure.

    This function limits message length and removes potentially sensitive
    information while preserving the core error details.

    Args:
        message: The error message to sanitize
        max_length: Maximum length of the sanitized message

    Returns:
        Sanitized error message
    """
    if not message:
        return "<no message>"

    # Convert to string if needed
    if not isinstance(message, str):
        message = str(message)

    # Remove common sensitive patterns
    sanitized = re.sub(r"/home/[^/\s]+", "/home/****", message)
    # Handle Windows paths more carefully to avoid \U escape sequence issues
    sanitized = re.sub(r"C:[\\/][Uu]sers[\\/][^\\/]+", "C:/Users/****", sanitized)
    sanitized = re.sub(r"/Users/[^/\s]+", "/Users/****", sanitized)

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[: max_length - 3] + "..."

    return sanitized


def safe_repr(obj: Any, max_length: int = 100) -> str:
    """Get a safe representation of an object for error messages.

    This function creates a string representation of an object while
    limiting length and avoiding potential exposure of sensitive data.

    Args:
        obj: Object to represent
        max_length: Maximum length of the representation

    Returns:
        Safe string representation
    """
    try:
        # Handle None
        if obj is None:
            return "None"

        # Handle strings
        if isinstance(obj, str):
            if len(obj) > max_length:
                return obj[: max_length - 3] + "..."
            return obj

        # Handle paths
        if isinstance(obj, Path):
            return sanitize_path(obj)

        # For other objects, use repr but limit length
        repr_str = repr(obj)
        if len(repr_str) > max_length:
            return repr_str[: max_length - 3] + "..."
        return repr_str

    except Exception:
        return f"<object of type {type(obj).__name__}>"


def log_sensitive_error(
    logger_obj: logging.Logger, message: str, details: dict[str, Any] | None = None
) -> None:
    """Log full error details internally while providing safe external messages.

    This function logs complete error information at debug level for internal
    troubleshooting while ensuring that only sanitized information is exposed
    at higher log levels.

    Args:
        logger_obj: Logger instance to use
        message: Safe error message for higher log levels
        details: Sensitive details to log at debug level only
    """
    # Log safe message at warning level
    logger_obj.warning(message)

    # Log full details at debug level only
    if details:
        logger_obj.debug("Full error details: %s", details)
