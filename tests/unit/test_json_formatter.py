"""Tests for the JSON formatter."""

import json
from datetime import datetime

import pytest

from beaconled.core.models import CommitStats, FileStats, RangeStats
from beaconled.formatters.json_format import JSONFormatter


class TestJSONFormatter:
    """Tests for the JSONFormatter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = JSONFormatter()

    def test_serialize_datetime(self):
        """Test the _serialize_datetime method."""
        # Test with a datetime object
        dt = datetime(2023, 1, 15, 10, 30, 0)
        result = self.formatter._serialize_datetime(dt)
        assert result == "2023-01-15T10:30:00"

        # Test with a non-datetime object
        with pytest.raises(TypeError):
            self.formatter._serialize_datetime("not a datetime")

    def test_format_commit_stats(self):
        """Test the format_commit_stats method."""
        # Create a sample commit with files
        commit = CommitStats(
            hash="abc123def456",
            author="John Doe <john@example.com>",
            date=datetime(2023, 1, 15, 10, 30, 0),
            message="Add new feature",
            files_changed=2,
            lines_added=10,
            lines_deleted=2,
            files=[
                FileStats("src/main.py", 8, 0, 8),
                FileStats("tests/test_main.py", 2, 2, 4),
            ],
        )

        # Format the commit stats
        result = self.formatter.format_commit_stats(commit)
        data = json.loads(result)

        # Check the output
        assert data["hash"] == "abc123def456"
        assert data["author"] == "John Doe <john@example.com>"
        assert data["date"] == "2023-01-15T10:30:00"
        assert data["message"] == "Add new feature"
        assert data["files_changed"] == 2
        assert data["lines_added"] == 10
        assert data["lines_deleted"] == 2
        assert data["net_change"] == 8
        assert len(data["files"]) == 2
        assert data["files"][0]["path"] == "src/main.py"
        assert data["files"][0]["lines_added"] == 8
        assert data["files"][1]["path"] == "tests/test_main.py"
        assert data["files"][1]["lines_deleted"] == 2

    def test_format_range_stats(self):
        """Test the format_range_stats method."""
        # Create a sample range with commits
        commit1 = CommitStats(
            hash="abc123def456",
            author="John Doe <john@example.com>",
            date=datetime(2023, 1, 15, 10, 30, 0),
            message="Add new feature",
            files_changed=2,
            lines_added=10,
            lines_deleted=2,
            files=[FileStats("src/main.py", 8, 0, 8)],
        )

        commit2 = CommitStats(
            hash="def456abc123",
            author="Jane Smith <jane@example.com>",
            date=datetime(2023, 1, 16, 14, 30, 0),
            message="Fix bug",
            files_changed=1,
            lines_added=2,
            lines_deleted=5,
            files=[FileStats("src/main.py", 2, 5, 7)],
        )

        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 2, 1),
            total_commits=2,
            total_files_changed=3,
            total_lines_added=12,
            total_lines_deleted=7,
            commits=[commit1, commit2],
            authors={
                "John Doe <john@example.com>": 1,
                "Jane Smith <jane@example.com>": 1,
            },
        )

        # Format the range stats
        result = self.formatter.format_range_stats(range_stats)
        data = json.loads(result)

        # Check the output
        assert data["start_date"] == "2023-01-01T00:00:00"
        assert data["end_date"] == "2023-02-01T00:00:00"
        assert data["total_commits"] == 2
        assert data["total_files_changed"] == 3
        assert data["total_lines_added"] == 12
        assert data["total_lines_deleted"] == 7
        assert data["net_change"] == 5

        # Check authors
        assert data["authors"] == {
            "John Doe <john@example.com>": 1,
            "Jane Smith <jane@example.com>": 1,
        }

        # Check commits
        assert len(data["commits"]) == 2
        assert data["commits"][0]["hash"] == "abc123def456"
        assert data["commits"][0]["author"] == "John Doe <john@example.com>"
        assert data["commits"][1]["hash"] == "def456abc123"
        assert data["commits"][1]["author"] == "Jane Smith <jane@example.com>"

    def test_format_empty_commit_stats(self):
        """Test formatting commit stats with no files."""
        commit = CommitStats(
            hash="abc123def456",
            author="John Doe <john@example.com>",
            date=datetime(2023, 1, 15, 10, 30, 0),
            message="Empty commit",
            files_changed=0,
            lines_added=0,
            lines_deleted=0,
            files=[],
        )

        result = self.formatter.format_commit_stats(commit)
        data = json.loads(result)

        assert data["files_changed"] == 0
        assert data["lines_added"] == 0
        assert data["lines_deleted"] == 0
        assert data["net_change"] == 0
        assert data["files"] == []

    def test_format_range_stats_no_commits(self):
        """Test formatting range stats with no commits."""
        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 2, 1),
            total_commits=0,
            total_files_changed=0,
            total_lines_added=0,
            total_lines_deleted=0,
            commits=[],
            authors={},
        )

        result = self.formatter.format_range_stats(range_stats)
        data = json.loads(result)

        assert data["total_commits"] == 0
        assert data["total_files_changed"] == 0
        assert data["total_lines_added"] == 0
        assert data["total_lines_deleted"] == 0
        assert data["net_change"] == 0
        assert data["authors"] == {}
        assert data["commits"] == []
