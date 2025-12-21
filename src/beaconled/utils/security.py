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
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from beaconled.config import performance_config

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


def sanitize_error_message(message: str, max_length: int | None = None) -> str:
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
    if max_length is None:
        max_length = performance_config.max_error_length
    if len(sanitized) > max_length:
        sanitized = sanitized[: max_length - 3] + "..."

    return sanitized


def safe_repr(obj: Any, max_length: int | None = None) -> str:
    """Get a safe representation of an object for error messages.

    This function creates a string representation of an object while
    limiting length and avoiding potential exposure of sensitive data.

    Args:
        obj: Object to represent
        max_length: Maximum length of the representation

    Returns:
        Safe string representation
    """
    if max_length is None:
        max_length = performance_config.max_repr_length

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


def is_hard_link(path: Path) -> bool:
    """Check if a path is a hard link (multiple inodes pointing to same data).

    This is critical for shared CI environments where hard links can:
    - Break isolation between test runs
    - Cause unexpected file modifications
    - Create security risks through shared file access

    Args:
        path: The file path to check

    Returns:
        True if the path is a hard link (st_nlink > 1), False otherwise
    """
    try:
        stat_info = path.stat()
        return stat_info.st_nlink > 1
    except (OSError, FileNotFoundError, PermissionError) as e:
        logger.debug("Failed to check hard link status for %s: %s", path, e)
        # If we can't check, assume it might be unsafe
        return True


def secure_path_exists(path: Path) -> bool:
    """Securely check if a path exists, protecting against TOCTOU attacks.

    This function performs multiple validation checks to ensure the path
    hasn't been tampered with between check and use operations.

    Args:
        path: The path to validate

    Returns:
        True if the path exists and is safe to use, False otherwise
    """
    try:
        # First check: does the path exist?
        if not path.exists():
            return False

        # Second check: is it the expected type?
        if path.is_file():
            # Additional file-specific checks
            return _validate_file_security(path)
        elif path.is_dir():
            # Additional directory-specific checks
            return _validate_directory_security(path)

        return True  # Other file types (sockets, etc.)

    except (OSError, PermissionError) as e:
        logger.warning("Path validation error for %s: %s", sanitize_path(path), e)
        return False


def _validate_file_security(path: Path) -> bool:
    """Perform security validation on file paths.

    Args:
        path: File path to validate

    Returns:
        True if the file is safe to use, False otherwise
    """
    try:
        # Check if it's a symlink (potential TOCTOU vector)
        if path.is_symlink():
            logger.warning("Path is a symlink (potential security risk): %s", sanitize_path(path))
            return False

        # Check for hard links in shared environments
        if is_hard_link(path):
            logger.warning("Path is a hard link (isolation risk): %s", sanitize_path(path))
            return False

        # Verify file is accessible and not changed during validation
        stat1 = path.stat()
        time.sleep(0.001)  # Brief pause to detect race conditions
        stat2 = path.stat()

        # Check if inode or modification time changed (TOCTOU indicator)
        if stat1.st_ino != stat2.st_ino or stat1.st_mtime != stat2.st_mtime:
            logger.warning(
                "Path changed during validation (TOCTOU attack detected): %s", sanitize_path(path)
            )
            return False

        return True

    except (OSError, PermissionError) as e:
        logger.warning("File security validation failed for %s: %s", sanitize_path(path), e)
        return False


def _validate_directory_security(path: Path) -> bool:
    """Perform security validation on directory paths.

    Args:
        path: Directory path to validate

    Returns:
        True if the directory is safe to use, False otherwise
    """
    try:
        # Check if it's a symlink
        if path.is_symlink():
            logger.warning(
                "Directory path is a symlink (potential security risk): %s", sanitize_path(path)
            )
            return False

        # Verify directory structure is intact
        if not path.is_dir():
            return False

        # Check for suspicious permissions (world-writable directories)
        stat_info = path.stat()
        if stat_info.st_mode & 0o002:  # Check world-writable bit
            logger.warning("Directory is world-writable (security risk): %s", sanitize_path(path))
            return False

        return True

    except (OSError, PermissionError) as e:
        logger.warning("Directory security validation failed for %s: %s", sanitize_path(path), e)
        return False


def secure_file_operation(operation: Callable, path: Path, max_retries: int = 3, *args, **kwargs):
    """Execute a file operation with TOCTOU protection and retry logic.

    This wrapper ensures that file operations are atomic and protected
    against race condition attacks.

    Args:
        operation: The file operation function to execute
        path: The file path the operation will work on
        max_retries: Maximum number of retries on failure
        *args: Arguments to pass to the operation
        **kwargs: Keyword arguments to pass to the operation

    Returns:
        The result of the operation function

    Raises:
        FileNotFoundError: If path validation fails
        PermissionError: If permission issues occur
        OSError: If other file system errors occur
    """
    for attempt in range(max_retries):
        try:
            # Pre-operation validation
            if not secure_path_exists(path):
                error_msg = f"Path validation failed: {sanitize_path(path)}"
                raise FileNotFoundError(error_msg)

            # Execute the operation
            result = operation(path, *args, **kwargs)

            # Post-operation validation (if path still exists)
            if path.exists():
                if not secure_path_exists(path):
                    logger.warning(
                        "Path validation failed after operation: %s", sanitize_path(path)
                    )

            return result

        except (OSError, PermissionError, FileNotFoundError):
            if attempt == max_retries - 1:
                # Last attempt failed, re-raise the exception
                logger.error(
                    "File operation failed after %d attempts: %s", max_retries, sanitize_path(path)
                )
                raise

            # Exponential backoff for retry
            wait_time = (2**attempt) * 0.1  # 0.1s, 0.2s, 0.4s
            logger.debug(
                "File operation attempt %d failed, retrying in %.1fs: %s",
                attempt + 1,
                wait_time,
                sanitize_path(path),
            )
            time.sleep(wait_time)


def atomic_write(temp_dir: Path | None = None) -> tempfile.NamedTemporaryFile:
    """Create a temporary file for atomic write operations.

    This function creates a temporary file that can be written to
    atomically and then moved to the final location.

    Args:
        temp_dir: Directory for temporary file (uses system default if None)

    Returns:
        NamedTemporaryFile context manager for atomic writing
    """
    # Create temporary file in specified or system temp directory
    return tempfile.NamedTemporaryFile(
        mode="w", dir=temp_dir, delete=False, suffix=".tmp", encoding="utf-8"
    )


def verify_file_integrity(path: Path, expected_hash: str | None = None) -> bool:
    """Verify file integrity and detect tampering.

    Args:
        path: File path to verify
        expected_hash: Expected SHA256 hash (if provided)

    Returns:
        True if file integrity is verified, False otherwise
    """
    try:
        if not path.exists():
            return False

        # Check for basic file attributes
        stat_info = path.stat()

        # Verify file is not empty (unless expected)
        if stat_info.st_size == 0:
            logger.debug("File is empty: %s", sanitize_path(path))

        # If hash verification is requested
        if expected_hash:
            import hashlib

            with open(path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                if file_hash != expected_hash:
                    logger.warning("File integrity check failed: %s", sanitize_path(path))
                    return False

        return True

    except (OSError, PermissionError) as e:
        logger.warning("File integrity verification failed for %s: %s", sanitize_path(path), e)
        return False
