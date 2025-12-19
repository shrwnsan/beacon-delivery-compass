"""Tests for error paths in the GitAnalyzer class."""

import os
from unittest.mock import MagicMock, patch

import pytest

from beaconled.core.analyzer import GitAnalyzer
from beaconled.exceptions import InvalidRepositoryError


def test_validate_repo_path_nonexistent(tmp_path):
    """Test validation with a non-existent path."""
    non_existent_path = os.path.join(str(tmp_path), "nonexistent")
    # Bypass __init__ so we can call _validate_repo_path directly
    analyzer = GitAnalyzer.__new__(GitAnalyzer)

    with pytest.raises(InvalidRepositoryError) as exc_info:
        analyzer._validate_repo_path(non_existent_path)

    assert "Path does not exist" in str(exc_info.value)


def test_validate_repo_path_not_a_directory(tmp_path):
    """Test validation with a path that is not a directory."""
    temp_file = tmp_path / "temp_file.txt"
    temp_file.write_text("test content")
    # Bypass __init__ so we can call _validate_repo_path directly
    analyzer = GitAnalyzer.__new__(GitAnalyzer)

    with pytest.raises(InvalidRepositoryError) as exc_info:
        analyzer._validate_repo_path(str(temp_file))

    assert "Path is not a directory" in str(exc_info.value)


def test_validate_repo_path_not_a_git_repo(tmp_path):
    """Test validation with a directory that is not a git repository."""
    # Bypass __init__ so we can call _validate_repo_path directly
    analyzer = GitAnalyzer.__new__(GitAnalyzer)

    with patch("git.Repo") as mock_repo:
        mock_repo.side_effect = Exception("Not a git repository")

        with pytest.raises(InvalidRepositoryError) as exc_info:
            analyzer._validate_repo_path(str(tmp_path))

            assert "Not a git repository" in str(exc_info.value)


def test_validate_repo_path_unexpected_error(tmp_path):
    """Test validation with an unexpected error during validation."""
    # Bypass __init__ so we can call _validate_repo_path directly
    analyzer = GitAnalyzer.__new__(GitAnalyzer)

    with patch("pathlib.Path.resolve") as mock_resolve:
        mock_resolve.side_effect = Exception("Unexpected error")

        with pytest.raises(InvalidRepositoryError) as exc_info:
            analyzer._validate_repo_path(str(tmp_path))

        assert "Unexpected error" in str(exc_info.value)


def test_validate_repo_path_valid(tmp_path):
    """Test validation with a valid git repository path."""
    import tempfile
    from pathlib import Path

    # Use /tmp instead of pytest's tmp_path to ensure path is in allowed boundaries
    with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
        # Create a mock .git directory
        git_dir = Path(temp_dir) / ".git"
        git_dir.mkdir()

        # Bypass __init__ so we can call _validate_repo_path directly
        # This avoids validating the current directory
        analyzer = GitAnalyzer.__new__(GitAnalyzer)
        result = analyzer._validate_repo_path(temp_dir)

        # Should return the absolute path to the temp directory
        assert os.path.isabs(result)
        assert os.path.samefile(result, temp_dir)


@patch("git.Repo")
def test_validate_repo_path_with_git_python(mock_repo, tmp_path):
    """Test validation when .git doesn't exist but git.Repo can open it."""
    import tempfile
    from pathlib import Path

    # Use /tmp instead of pytest's tmp_path to ensure path is in allowed boundaries
    with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
        # Get the resolved path to handle symlinks and /private/ prefix on macOS
        resolved_temp_dir = str(Path(temp_dir).resolve())

        # Configure the mock to return a mock repo object
        mock_repo.return_value = MagicMock()

        # Bypass __init__ so we can call _validate_repo_path directly
        analyzer = GitAnalyzer.__new__(GitAnalyzer)
        result = analyzer._validate_repo_path(temp_dir)

        assert os.path.isabs(result)
        assert os.path.samefile(result, resolved_temp_dir)

        # Verify the mock was called with the resolved path
        mock_repo.assert_called_once()
        assert len(mock_repo.call_args[0]) > 0  # Make sure there's at least one positional arg
        called_path = mock_repo.call_args[0][0]
        assert os.path.samefile(called_path, resolved_temp_dir)
