"""Tests for error paths in the GitAnalyzer class."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from beaconled.core.analyzer import GitAnalyzer
from beaconled.exceptions import InvalidRepositoryError


def test_validate_repo_path_nonexistent():
    """Test validation with a non-existent path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_path = os.path.join(temp_dir, "nonexistent")
        analyzer = GitAnalyzer()

        with pytest.raises(InvalidRepositoryError) as exc_info:
            analyzer._validate_repo_path(non_existent_path)

        assert "Path does not exist" in str(exc_info.value)


def test_validate_repo_path_not_a_directory():
    """Test validation with a path that is not a directory."""
    with tempfile.NamedTemporaryFile() as temp_file:
        analyzer = GitAnalyzer()

        with pytest.raises(InvalidRepositoryError) as exc_info:
            analyzer._validate_repo_path(temp_file.name)

        assert "Path is not a directory" in str(exc_info.value)


def test_validate_repo_path_not_a_git_repo():
    """Test validation with a directory that is not a git repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = GitAnalyzer()

        with patch("git.Repo") as mock_repo:
            mock_repo.side_effect = Exception("Not a git repository")

            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_repo_path(temp_dir)

            assert "Not a git repository" in str(exc_info.value)


def test_validate_repo_path_unexpected_error():
    """Test validation with an unexpected error during validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = GitAnalyzer()

        with patch("pathlib.Path.resolve") as mock_resolve:
            mock_resolve.side_effect = Exception("Unexpected error")

            with pytest.raises(InvalidRepositoryError) as exc_info:
                analyzer._validate_repo_path(temp_dir)

            assert "Unexpected error" in str(exc_info.value)


def test_validate_repo_path_valid():
    """Test validation with a valid git repository path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock .git directory
        os.makedirs(os.path.join(temp_dir, ".git"))

        analyzer = GitAnalyzer()
        result = analyzer._validate_repo_path(temp_dir)

        # Should return the absolute path to the temp directory
        assert os.path.isabs(result)
        assert os.path.samefile(result, temp_dir)


@patch("os.path.exists", return_value=True)
@patch("os.path.isdir", return_value=True)
@patch("pathlib.Path.is_dir", return_value=True)
@patch("git.Repo")
def test_validate_repo_path_with_git_python(mock_repo, *args):
    """Test validation when .git doesn't exist but git.Repo can open it."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Get the resolved path to handle symlinks and /private/ prefix on macOS
        resolved_temp_dir = str(Path(temp_dir).resolve())

        # Configure the mock to return a mock repo object
        mock_repo.return_value = MagicMock()

        analyzer = GitAnalyzer()
        result = analyzer._validate_repo_path(temp_dir)

        assert os.path.isabs(result)
        assert os.path.samefile(result, temp_dir)

        # Verify the mock was called with the resolved path
        mock_repo.assert_called_once()
        assert len(mock_repo.call_args[0]) > 0  # Make sure there's at least one positional arg
        called_path = mock_repo.call_args[0][0]
        assert os.path.samefile(called_path, resolved_temp_dir)
