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
        # Use PureWindowsPath on non-Windows systems to properly handle Windows paths
        if isinstance(path, str) and ("\\" in path or (len(path) >= 2 and path[1] == ":")):
            # Looks like a Windows path
            if os.name != "nt":
                from pathlib import PureWindowsPath

                path_obj = PureWindowsPath(path)
            else:
                path_obj = Path(path)
        else:
            path_obj = Path(path)

        # Get all parts of the path
        parts = path_obj.parts

        # Check if first part is a Windows drive letter (e.g., 'C:\\')
        start_idx = 0
        if len(parts) > 0 and len(parts[0]) >= 2 and parts[0][1] == ":":
            # Skip the Windows drive letter for component counting
            start_idx = 1

        # Get effective parts (excluding Windows drive letter)
        effective_parts = parts[start_idx:]

        # If effective path has fewer components than max, return as-is
        if len(effective_parts) <= max_components:
            return str(path_obj)

        # Return only the last N components from effective parts
        sanitized_parts = effective_parts[-max_components:]

        # For PureWindowsPath, use forward slashes for consistency
        if hasattr(path_obj, "flavour") and hasattr(path_obj.flavour, "sep"):
            # It's a PurePath object
            separator = path_obj.flavour.sep
            return separator.join(sanitized_parts)
        else:
            # Regular Path object
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

    # Remove common sensitive patterns (case-insensitive to prevent bypass)
    # Unix/Linux home directories
    sanitized = re.sub(r"/home/[^/\s]+", "/home/****", message, flags=re.IGNORECASE)
    # macOS user directories
    sanitized = re.sub(r"/Users/[^/\s]+", "/Users/****", sanitized, flags=re.IGNORECASE)
    # Root home directory (privileged user)
    sanitized = re.sub(r"/root/?[^/\s]*", "/root/****", sanitized, flags=re.IGNORECASE)
    # System service directories
    sanitized = re.sub(r"/opt/[^/\s]+", "/opt/****", sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r"/srv/[^/\s]+", "/srv/****", sanitized, flags=re.IGNORECASE)
    # Some Linux distributions use /var/home
    sanitized = re.sub(r"/var/home/[^/\s]+", "/var/home/****", sanitized, flags=re.IGNORECASE)
    # Handle Windows paths more carefully to avoid \U escape sequence issues
    sanitized = re.sub(
        r"C:[\\/][Uu]sers[\\/][^\\/]+", "C:/Users/****", sanitized, flags=re.IGNORECASE
    )
    # Windows UNC paths (\\server\share\user) - simplified pattern
    sanitized = re.sub(r"\\\\\\\\[^\\\\]+\\\\\\\\[^\\\\]+", r"\\\\server\\share\\****", sanitized)
    # Handle tilde expansion (~username)
    sanitized = re.sub(r"~[^/\s]+", "~****", sanitized, flags=re.IGNORECASE)

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
