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

"""Security validation tests for GitAnalyzer and security utilities."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from beaconled.core.analyzer import GitAnalyzer
from beaconled.exceptions import InvalidRepositoryError
from beaconled.utils.security import (
    is_hard_link,
    secure_path_exists,
    secure_file_operation,
    atomic_write,
    verify_file_integrity,
)


class TestSecurityValidation(unittest.TestCase):
    """Test security features of GitAnalyzer."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_directory_traversal_blocked(self):
        """Test that directory traversal is blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        with self.assertRaises(InvalidRepositoryError) as cm:
            analyzer._validate_repo_path("../../../etc")

        error_msg = str(cm.exception)
        self.assertTrue("Directory traversal" in error_msg or "not allowed" in error_msg)

    def test_system_directory_blocked(self):
        """Test that access to system directories is blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_dir", return_value=True),
            patch("pathlib.Path.is_symlink", return_value=False),
            patch("pathlib.Path.resolve") as mock_resolve,
            patch("git.Repo", side_effect=Exception("Not a git repo")),
        ):
            # Mock resolve to return /etc without /private prefix
            mock_resolve.side_effect = lambda: Path("/etc")

            with self.assertRaises(InvalidRepositoryError) as cm:
                analyzer._validate_repo_path("/etc")

            # The actual error is "Access to system directories is not allowed"
            # because /etc is in the restricted_paths list (checked before boundaries)
            self.assertIn("not allowed", str(cm.exception))

    def test_safe_boundary_check(self):
        """Test that boundary checking works correctly."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        # Test the fallback logic (simulating Python < 3.9)
        # Patch hasattr to return False for is_relative_to
        with patch("builtins.hasattr") as mock_hasattr:
            mock_hasattr.side_effect = (
                lambda obj, attr: False if attr == "is_relative_to" else hasattr(obj, attr)
            )

            # These should NOT be considered within boundary
            self.assertFalse(
                analyzer._is_path_within_boundary(Path("/home/user2/repo"), Path("/home/user"))
            )

            # These SHOULD be considered within boundary
            self.assertTrue(
                analyzer._is_path_within_boundary(Path("/home/user/repo"), Path("/home/user"))
            )

    def test_suspicious_patterns_detected(self):
        """Test that suspicious patterns are detected."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        # Should detect encoded traversal
        self.assertTrue(analyzer._has_suspicious_patterns("..%2f..%2fetc"))
        self.assertTrue(analyzer._has_suspicious_patterns("%2e%2e%2fetc"))

        # Should detect null bytes
        self.assertTrue(analyzer._has_suspicious_patterns("path\x00with\x00null"))

        # Should not flag normal paths
        self.assertFalse(analyzer._has_suspicious_patterns("/normal/path/to/repo"))

    def test_symlink_validation(self):
        """Test symlink validation."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        with (
            patch("pathlib.Path.is_symlink", return_value=True),
            patch("pathlib.Path.readlink") as mock_readlink,
        ):
            # Mock symlink pointing to restricted directory
            mock_readlink.return_value = Path("/etc")

            with self.assertRaises(InvalidRepositoryError) as cm:
                analyzer._validate_symlink_chain(Path("/tmp/link/etc"))

            self.assertIn("restricted directory", str(cm.exception))

    def test_toctou_mitigation(self):
        """Test TOCTOU mitigation."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        test_path = Path("/some/path")

        # Test with non-existent path
        with patch("pathlib.Path.exists", return_value=False):
            self.assertFalse(analyzer._secure_path_exists(test_path))

        # Test with symlink replacement
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_dir", return_value=True),
            patch("pathlib.Path.is_symlink", return_value=True),
        ):
            self.assertFalse(analyzer._secure_path_exists(test_path))

    def test_security_logging(self):
        """Test that security violations are logged."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        with patch("beaconled.core.analyzer.logger") as mock_logger:
            # Test traversal logging
            try:
                analyzer._validate_repo_path("../../../etc")
            except InvalidRepositoryError:
                pass

            # Should have logged a warning
            mock_logger.warning.assert_called()


class TestSecurityUtilities(unittest.TestCase):
    """Test security utility functions."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.txt"
        self.test_file.write_text("test content")

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_is_hard_link_normal_file(self):
        """Test hard link detection on normal files."""
        # Regular file should not be a hard link
        self.assertFalse(is_hard_link(self.test_file))

    def test_is_hard_link_with_hard_link(self):
        """Test hard link detection when hard link exists."""
        # Create a hard link
        hard_link_path = self.temp_dir / "hardlink.txt"
        os.link(str(self.test_file), str(hard_link_path))

        # Both files should now be detected as hard links
        self.assertTrue(is_hard_link(self.test_file))
        self.assertTrue(is_hard_link(hard_link_path))

    def test_is_hard_link_nonexistent_file(self):
        """Test hard link detection on nonexistent file."""
        nonexistent = self.temp_dir / "nonexistent.txt"
        # Should return True (assume unsafe) for nonexistent files
        self.assertTrue(is_hard_link(nonexistent))

    @patch("beaconled.utils.security._validate_file_security")
    @patch("beaconled.utils.security._validate_directory_security")
    def test_secure_path_exists_file(self, mock_dir_validate, mock_file_validate):
        """Test secure path validation for files."""
        mock_file_validate.return_value = True

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch("pathlib.Path.is_dir", return_value=False),
        ):
            self.assertTrue(secure_path_exists(Path("/some/file.txt")))
            mock_file_validate.assert_called_once()

    @patch("beaconled.utils.security._validate_directory_security")
    def test_secure_path_exists_directory(self, mock_dir_validate):
        """Test secure path validation for directories."""
        mock_dir_validate.return_value = True

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=False),
            patch("pathlib.Path.is_dir", return_value=True),
        ):
            self.assertTrue(secure_path_exists(Path("/some/dir")))
            mock_dir_validate.assert_called_once()

    def test_secure_path_exists_nonexistent(self):
        """Test secure path validation on nonexistent path."""
        with patch("pathlib.Path.exists", return_value=False):
            self.assertFalse(secure_path_exists(Path("/nonexistent")))

    def test_secure_file_operation_success(self):
        """Test secure file operation wrapper on success."""

        def dummy_operation(path):
            return "success"

        with patch("beaconled.utils.security.secure_path_exists", return_value=True):
            result = secure_file_operation(dummy_operation, self.test_file)
            self.assertEqual(result, "success")

    def test_secure_file_operation_validation_failure(self):
        """Test secure file operation wrapper on validation failure."""

        def dummy_operation(path):
            return "success"

        with patch("beaconled.utils.security.secure_path_exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                secure_file_operation(dummy_operation, self.test_file)

    def test_secure_file_operation_retry_success(self):
        """Test secure file operation wrapper with retry success."""
        call_count = 0

        def failing_operation(path):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error_msg = "Temporary failure"
                raise PermissionError(error_msg)
            return "success"

        with patch("beaconled.utils.security.secure_path_exists", return_value=True):
            result = secure_file_operation(failing_operation, self.test_file, max_retries=3)
            self.assertEqual(result, "success")
            self.assertEqual(call_count, 2)

    def test_atomic_write(self):
        """Test atomic write functionality."""
        with atomic_write(self.temp_dir) as tmp_file:
            tmp_file.write("atomic content")
            tmp_path = Path(tmp_file.name)

        # File should exist after context manager
        self.assertTrue(tmp_path.exists())
        self.assertEqual(tmp_path.read_text(), "atomic content")

    def test_verify_file_integrity_exists(self):
        """Test file integrity verification for existing file."""
        self.assertTrue(verify_file_integrity(self.test_file))

    def test_verify_file_integrity_nonexistent(self):
        """Test file integrity verification for nonexistent file."""
        nonexistent = self.temp_dir / "nonexistent.txt"
        self.assertFalse(verify_file_integrity(nonexistent))

    def test_verify_file_integrity_with_hash(self):
        """Test file integrity verification with hash."""
        import hashlib

        # Calculate expected hash
        with open(self.test_file, "rb") as f:
            expected_hash = hashlib.sha256(f.read()).hexdigest()

        self.assertTrue(verify_file_integrity(self.test_file, expected_hash))

        # Wrong hash should fail
        self.assertFalse(verify_file_integrity(self.test_file, "wrong_hash"))

    def test_file_security_validation_symlink_block(self):
        """Test that symlinks are blocked in file validation."""
        from beaconled.utils.security import _validate_file_security

        symlink_path = self.temp_dir / "symlink.txt"

        with patch("pathlib.Path.is_symlink", return_value=True):
            self.assertFalse(_validate_file_security(symlink_path))

    def test_directory_security_validation_world_writable(self):
        """Test that world-writable directories are blocked."""
        from beaconled.utils.security import _validate_directory_security

        # Mock stat with world-writable permissions
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o40777  # World-writable

        with (
            patch("pathlib.Path.is_symlink", return_value=False),
            patch("pathlib.Path.is_dir", return_value=True),
            patch("pathlib.Path.stat", return_value=mock_stat),
        ):
            self.assertFalse(_validate_directory_security(self.temp_dir))


if __name__ == "__main__":
    unittest.main()
