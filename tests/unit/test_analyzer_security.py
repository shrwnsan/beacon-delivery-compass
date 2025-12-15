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

"""Comprehensive security tests for GitAnalyzer path validation."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from beaconled.core.analyzer import GitAnalyzer
from beaconled.exceptions import InvalidRepositoryError


class TestPathSecurity(unittest.TestCase):
    """Test suite for comprehensive path security validation."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()

        # Create a valid git repository in temp dir
        git_dir = self.temp_dir / ".git"
        git_dir.mkdir()

        # Create some basic git structure
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n")
        (git_dir / "refs").mkdir()
        (git_dir / "refs" / "heads").mkdir()
        (git_dir / "refs" / "heads" / "main").write_text("1234567890abcdef\n")
        (git_dir / "objects").mkdir()

        yield

        # Cleanup
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_directory_traversal_blocked(self):
        """Test that directory traversal attempts are blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Test various traversal attempts
        traversal_attempts = [
            "../../../etc",
            "..\\..\\..\\windows\\system32",
            "../../etc/passwd",
            "..%2f..%2fetc",
            "..%2F..%2Fetc",
            "%2e%2e%2f%2e%2e%2fetc",
            "%252e%252e%252f%252e%252e%252fetc",
            "/etc/../../../etc",  # Attempt to normalize after absolute path
        ]

        for attempt in traversal_attempts:
            with self.assertRaises(InvalidRepositoryError) as cm:
                analyzer._validate_repo_path(attempt)

            error_msg = str(cm.exception)
            self.assertTrue(
                "Directory traversal" in error_msg or "not allowed" in error_msg
            )

    def test_system_directories_blocked(self):
        """Test that access to system directories is blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Mock system directories as if they were git repos
        system_dirs = [
            "/etc",
            "/usr/bin",
            "/bin",
            "/sbin",
            "/usr/sbin",
            "/sys",
            "/proc",
            "/dev",
            "/var/log",
            "/var/spool",
            "/boot",
            "/root",
            str(Path.home() / ".ssh"),
            str(Path.home() / ".gnupg"),
            str(Path.home() / ".aws"),
            str(Path.home() / ".config"),
        ]

        for sys_dir in system_dirs:
            # Mock the directory as existing and being a git repo
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.is_dir', return_value=True), \
                 patch('git.Repo') as mock_repo:

                with pytest.raises(InvalidRepositoryError) as exc_info:
                    analyzer._validate_repo_path(sys_dir)

                assert "Access to system directories" in str(exc_info.value)

    def test_boundary_enforcement(self):
        """Test that paths outside allowed boundaries are blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Mock a path outside allowed boundaries
        outside_path = "/some/unknown/path/repo"

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=True), \
             patch('git.Repo', side_effect=Exception("Not a git repo")):

            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_repo_path(outside_path)

            assert "outside allowed boundaries" in str(exc_info.value)

    def test_symlink_chain_validation(self):
        """Test that symlink chains pointing to restricted directories are blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Create a symlink chain that points to /etc
        with patch('pathlib.Path.is_symlink', return_value=True), \
             patch('pathlib.Path.readlink') as mock_readlink:

            # Mock symlink pointing to /etc
            mock_readlink.return_value = Path("/etc")

            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_symlink_chain(Path("/tmp/link/etc/passwd"))

            assert "Symlink chain points to restricted directory" in str(exc_info.value)

    def test_safe_boundary_check(self):
        """Test that boundary checking is safe against similar path names."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Test with Python 3.8 (no is_relative_to)
        with patch.object(Path, 'is_relative_to', side_effect=AttributeError):
            # These should NOT be considered within boundary
            assert not analyzer._is_path_within_boundary(
                Path("/home/user2/repo"),
                Path("/home/user")
            )
            assert not analyzer._is_path_within_boundary(
                Path("/home/userdocs/repo"),
                Path("/home/user")
            )

            # These SHOULD be considered within boundary
            assert analyzer._is_path_within_boundary(
                Path("/home/user/repo"),
                Path("/home/user")
            )
            assert analyzer._is_path_within_boundary(
                Path("/home/user/projects/repo"),
                Path("/home/user")
            )

    def test_suspicious_pattern_detection(self):
        """Test detection of suspicious patterns in paths."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        suspicious_paths = [
            "..%2f..%2fetc",
            "..%2F..%2Fetc",
            "..%5c..%5cwindows",
            "%2e%2e%2fetc",
            "%2E%2E%2Fetc",
            "%252e%252e%252fetc",
            "/path%2fwith%2fencoded%2fslashes",
            "path\x00with\x00null\x00bytes",
            "path\nwith\nnewlines",
            "path\rwith\rcarriage\rreturns",
            "path\twith\ttabs",
        ]

        for path in suspicious_paths:
            assert analyzer._has_suspicious_patterns(path), f"Should detect suspicious pattern in: {path}"

        # These should not be detected as suspicious
        safe_paths = [
            "/normal/path/to/repo",
            "relative/path/to/repo",
            "~/projects/my-repo",
            "/tmp/repo",
        ]

        for path in safe_paths:
            assert not analyzer._has_suspicious_patterns(path), f"Should not detect suspicious pattern in: {path}"

    def test_toctou_mitigation(self):
        """Test TOCTOU (Time-of-Check-Time-of-Use) mitigation."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        test_path = Path("/some/path")

        # Test case where path doesn't exist
        with patch('pathlib.Path.exists', return_value=False):
            assert not analyzer._secure_path_exists(test_path)

        # Test case where path is not a directory
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=False):
            assert not analyzer._secure_path_exists(test_path)

        # Test case where path was replaced by symlink
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=True), \
             patch('pathlib.Path.is_symlink', return_value=True):
            assert not analyzer._secure_path_exists(test_path)

        # Test case where git directory doesn't exist
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=True), \
             patch('pathlib.Path.is_symlink', return_value=False):
            # Only .git doesn't exist
            def exists_side_effect(path_arg):
                return str(path_arg).endswith(".git") == False

            with patch.object(Path, 'exists', side_effect=exists_side_effect):
                assert not analyzer._secure_path_exists(test_path)

        # Test successful validation
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_dir', return_value=True), \
             patch('pathlib.Path.is_symlink', return_value=False):
            assert analyzer._secure_path_exists(test_path)

    def test_encoding_variations_blocked(self):
        """Test that various encoding variations of traversal are blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Various encodings of "../"
        encodings = [
            "..%2f",
            "..%2F",
            "..%5c",
            "..%5C",
            "%2e%2e%2f",
            "%2E%2E%2F",
            "%252e%252e%252f",
            "&#x2f;&#x2e;&#x2e;&#x2f;",
            "..&#47;",
            "..&#92;",
        ]

        for encoding in encodings:
            path = f"/tmp{encoding}etc"
            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_repo_path(path)

            # Should be caught either by traversal check or suspicious pattern check
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "traversal", "not allowed", "suspicious", "invalid"
            ])

    def test_null_byte_injection_blocked(self):
        """Test that null byte injection is blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        null_byte_paths = [
            "/etc/passwd\x00.git",
            "/tmp/repo\x00/etc/passwd",
            "safe/path\x00dangerous/path",
        ]

        for path in null_byte_paths:
            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_repo_path(path)

            error_msg = str(exc_info.value).lower()
            assert "suspicious" in error_msg or "invalid" in error_msg

    def test_valid_git_repo_outside_boundaries(self):
        """Test that valid git repos outside boundaries are allowed."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        outside_path = "/opt/external-repo"

        # Mock as a valid git repo outside standard boundaries
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_dir', return_value=True), \
             patch('pathlib.Path.resolve') as mock_resolve, \
             patch('git.Repo') as mock_git_repo:

            # Configure mocks
            def exists_side_effect(path_arg):
                path_str = str(path_arg)
                # .git exists, it's a directory
                return path_str.endswith(".git") or "external-repo" in path_str

            mock_exists.side_effect = exists_side_effect
            mock_resolve.return_value = Path(outside_path).resolve()
            mock_git_repo.return_value = MagicMock()  # Successful validation

            # This should succeed
            result = analyzer._validate_repo_path(outside_path)
            assert result == str(Path(outside_path).resolve())

    def test_security_logging(self):
        """Test that security violations are properly logged."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        with patch('beaconled.core.analyzer.logger') as mock_logger:
            # Test traversal attempt logging
            with pytest.raises(InvalidRepositoryError):
                analyzer._validate_repo_path("../../../etc")

            # Should log warning about traversal attempt
            mock_logger.warning.assert_called()
            warning_call_args = str(mock_logger.warning.call_args)
            assert "traversal" in warning_call_args.lower()

            # Reset mock
            mock_logger.reset_mock()

            # Test restricted directory access logging
            with patch('pathlib.Path.is_relative_to', return_value=True), \
                 patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.is_dir', return_value=True):

                with pytest.raises(InvalidRepositoryError):
                    analyzer._validate_repo_path("/etc")

                # Should log warning about restricted directory
                mock_logger.warning.assert_called()
                warning_call_args = str(mock_logger.warning.call_args)
                assert "restricted" in warning_call_args.lower()

    def test_control_characters_blocked(self):
        """Test that control characters in paths are blocked."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        control_char_paths = [
            "path\nwith\nnewlines",
            "path\rwith\rcarriage\rrreturns",
            "path\twith\ttabs",
            "path\x01with\x02control\x03chars",
        ]

        for path in control_char_paths:
            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_repo_path(path)

            error_msg = str(exc_info.value).lower()
            assert "suspicious" in error_msg or "invalid" in error_msg

    def test_extremely_long_paths_blocked(self):
        """Test that extremely long paths are handled properly."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Create a very long path
        long_path = "/tmp/" + "a" * 10000

        with pytest.raises(InvalidRepositoryError):
            analyzer._validate_repo_path(long_path)

    def test_python_version_compatibility(self):
        """Test that security measures work across Python versions."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        # Test with Python 3.8 (no is_relative_to)
        with patch.object(Path, 'is_relative_to', side_effect=AttributeError):
            # Should still work properly
            assert analyzer._is_path_within_boundary(
                Path("/home/user/repo"),
                Path("/home/user")
            )

            assert not analyzer._is_path_within_boundary(
                Path("/home/user2/repo"),
                Path("/home/user")
            )

    def test_comprehensive_attack_vectors(self):
        """Test comprehensive list of attack vectors."""
        analyzer = GitAnalyzer.__new__(GitAnalyzer)  # Bypass __init__

        attack_vectors = [
            # Directory traversal variants
            "../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc",
            "..%2f..%2f..%2fetc",
            "..%252f..%252f..%252fetc",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc",

            # Symlink attacks
            "/tmp/symlink-to-etc",
            "/var/tmp/malicious-symlink",

            # Encoding attacks
            "/etc%00passwd",
            "/tmp%2frepo%00%2e%2e%2fetc",

            # Unicode attacks
            "/etc\u202epasswd",  # Right-to-left override
            "/tmp\u202erepo.git",  # Hidden extension

            # Mixed attacks
            "/tmp/..%2fetc/passwd",
            "/var/tmp/..%5c..%5cwindows",
        ]

        for attack in attack_vectors:
            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_repo_path(attack)

            # All should be blocked
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "traversal", "not allowed", "suspicious", "invalid",
                "restricted", "boundaries", "race condition"
            ]), f"Attack vector not blocked: {attack}"