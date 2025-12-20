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

"""Security validation tests for GitAnalyzer."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from beaconled.core.analyzer import GitAnalyzer
from beaconled.exceptions import InvalidRepositoryError


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
            patch("git.Repo", side_effect=Exception("Not a git repo")),
        ):
            with self.assertRaises(InvalidRepositoryError) as cm:
                analyzer._validate_repo_path("/etc")

            self.assertIn("boundaries", str(cm.exception))

    def test_safe_boundary_check(self):
        """Test that boundary checking works correctly."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)

        # Test with Python 3.8 (no is_relative_to)
        with patch.object(Path, "is_relative_to", side_effect=AttributeError):
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


if __name__ == "__main__":
    unittest.main()
