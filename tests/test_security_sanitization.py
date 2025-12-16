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

"""Tests for security sanitization utilities and exception handling."""

from pathlib import Path

from beaconled.core.date_errors import DateParseError
from beaconled.exceptions import InvalidRepositoryError, CommitNotFoundError
from beaconled.utils.security import sanitize_path, sanitize_error_message, safe_repr


class TestPathSanitization:
    """Test path sanitization functionality."""

    def test_sanitizes_long_unix_paths(self):
        """Test that long Unix paths are properly truncated."""
        path = "/home/user/projects/myapp/config/settings.py"
        result = sanitize_path(path)
        # Should return only the last 2 components
        assert result == "config/settings.py"

    def test_sanitizes_long_windows_paths(self):
        """Test that long Windows paths are properly truncated."""
        path = "C:\\Users\\John\\Documents\\secret\\file.txt"
        result = sanitize_path(path)
        # Windows paths use os.path.join, so should preserve backslashes
        assert "secret/file.txt" in result or "secret\\file.txt" in result

    def test_preserves_short_paths(self):
        """Test that short paths are returned as-is."""
        path = "file.txt"
        result = sanitize_path(path)
        assert result == "file.txt"

    def test_preserves_relative_paths(self):
        """Test that relative paths are handled correctly."""
        path = "relative/path/to/file.txt"
        result = sanitize_path(path)
        assert result == "to/file.txt"

    def test_handles_path_objects(self):
        """Test that Path objects are handled correctly."""
        path = Path("/home/user/projects/myapp/config/settings.py")
        result = sanitize_path(path)
        # Should return only the last 2 components
        assert result == "config/settings.py"

    def test_handles_none_and_empty(self):
        """Test that None and empty values are handled gracefully."""
        assert sanitize_path(None) == "<no path>"
        assert sanitize_path("") == "<no path>"

    def test_custom_max_components(self):
        """Test custom max_components parameter."""
        path = "/a/b/c/d/e/f/g"
        result = sanitize_path(path, max_components=3)
        assert result == "e/f/g"

    def test_handles_invalid_paths_gracefully(self):
        """Test that invalid paths don't cause exceptions."""
        # This should not raise an exception
        result = sanitize_path(None)
        assert result == "<no path>"


class TestErrorSanitization:
    """Test error message sanitization."""

    def test_sanitizes_home_paths(self):
        """Test that home directory paths are sanitized."""
        message = "Error reading file at /home/alice/config/secrets.conf"
        result = sanitize_error_message(message)
        assert "/home/alice" not in result
        assert "/home/****" in result

    def test_sanitizes_windows_paths(self):
        """Test that Windows user paths are sanitized."""
        message = "Failed to access C:\\Users\\John\\Documents\\secret.txt"
        result = sanitize_error_message(message)
        assert "C:\\Users\\John" not in result
        # Should normalize to forward slashes in the sanitized output
        assert "C:/Users/****" in result

    def test_sanitizes_mac_paths(self):
        """Test that macOS user paths are sanitized."""
        message = "Cannot read /Users/charlie/.ssh/id_rsa"
        result = sanitize_error_message(message)
        assert "/Users/charlie" not in result
        assert "/Users/****" in result

    def test_limits_message_length(self):
        """Test that message length is properly limited."""
        message = "A" * 300
        result = sanitize_error_message(message, max_length=50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_handles_non_string_input(self):
        """Test that non-string inputs are handled gracefully."""
        result = sanitize_error_message(12345)
        assert result == "12345"


class TestSafeRepresentation:
    """Test safe object representation."""

    def test_handles_none(self):
        """Test None handling."""
        assert safe_repr(None) == "None"

    def test_limits_string_length(self):
        """Test string length limiting."""
        long_str = "A" * 200
        result = safe_repr(long_str, max_length=50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_handles_path_objects(self):
        """Test Path object handling."""
        path = Path("/home/user/secret/config")
        result = safe_repr(path)
        assert "user" not in result  # Should be sanitized

    def test_handles_objects_gracefully(self):
        """Test that objects are handled safely."""

        class TestObject:
            def __repr__(self):
                return "TestObject()"

        result = safe_repr(TestObject())
        assert result == "TestObject()"

    def test_handles_repr_exceptions(self):
        """Test that exceptions in __repr__ are handled gracefully."""

        class BadObject:
            def __repr__(self):
                raise Exception("Cannot represent")

        result = safe_repr(BadObject())
        assert "BadObject" in result


class TestExceptionSanitization:
    """Test that exceptions properly sanitize sensitive information."""

    def test_invalid_repository_error_sanitization(self):
        """Test that InvalidRepositoryError sanitizes paths."""
        sensitive_path = "/home/alice/sensitive/project/.git"
        error = InvalidRepositoryError(sensitive_path, "Not a git repository")

        # The displayed message should be sanitized
        message = str(error)
        assert "alice" not in message
        assert "sensitive" not in message

        # But the full path should be in details for logging
        assert error.repo_path == sensitive_path
        assert error.details["repo_path"] == sensitive_path
        assert "sanitized_path" in error.details

    def test_commit_not_found_error_sanitization(self):
        """Test that CommitNotFoundError sanitizes repository paths."""
        sensitive_path = "/Users/charlie/top-secret/repo"
        error = CommitNotFoundError("abc123", sensitive_path)

        # The displayed message should be sanitized to last 2 components
        message = str(error)
        assert "charlie" not in message
        # Should show only "top-secret/repo" which is acceptable for last 2 components
        assert "top-secret/repo" in message

        # But the full path should be in details
        assert error.details["repo_path"] == sensitive_path

    def test_date_parse_error_sanitization(self):
        """Test that DateParseError sanitizes input strings."""
        sensitive_date = "../../../etc/passwd"
        error = DateParseError(sensitive_date)

        # The message should not contain the full sensitive input
        message = str(error)
        assert sensitive_date not in message

        # But the full input should be in details
        assert error.date_str == sensitive_date
        assert error.details["date_string"] == sensitive_date

    def test_long_date_input_truncation(self):
        """Test that long date inputs are truncated."""
        long_date = "2025-01-15T14:30:45.123456789+00:00" * 10  # Very long
        error = DateParseError(long_date)

        message = str(error)
        assert "..." in message  # Should be truncated
        assert len(message) < len(long_date) + 50  # Reasonable length limit

    def test_get_safe_message_method(self):
        """Test the get_safe_message method on base exception."""
        from beaconled.exceptions import BeaconError

        sensitive_path = "/home/alice/secret/project"
        error = BeaconError(f"Error in {sensitive_path}")

        # Safe message should be sanitized to last 2 components
        safe_msg = error.get_safe_message()
        assert "alice" not in safe_msg
        # Should show only "secret/project" which is acceptable for last 2 components
        assert "secret/project" in safe_msg
