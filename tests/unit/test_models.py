"""Tests for the models module."""

import unittest
from datetime import datetime

from beaconled.core.models import CommitStats, FileStats, RangeStats


class TestFileStats(unittest.TestCase):
    """Test cases for FileStats."""

    def test_file_stats_creation(self):
        """Test FileStats creation."""
        file_stats = FileStats(
            path="test.py",
            lines_added=10,
            lines_deleted=5,
            lines_changed=15,
        )

        self.assertEqual(file_stats.path, "test.py")
        self.assertEqual(file_stats.lines_added, 10)
        self.assertEqual(file_stats.lines_deleted, 5)
        self.assertEqual(file_stats.lines_changed, 15)


class TestCommitStats(unittest.TestCase):
    """Test cases for CommitStats."""

    def test_commit_stats_creation(self):
        """Test CommitStats creation."""
        commit_stats = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime.fromisoformat("2025-07-20T10:00:00+08:00"),
            message="Test commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=5,
            files=[FileStats("test.py", 10, 5, 15)],
        )

        self.assertEqual(commit_stats.hash, "abc123")
        self.assertEqual(commit_stats.author, "Test Author")
        self.assertEqual(
            commit_stats.date,
            datetime.fromisoformat("2025-07-20T10:00:00+08:00"),
        )
        self.assertEqual(commit_stats.message, "Test commit")
        self.assertEqual(commit_stats.files_changed, 1)
        self.assertEqual(commit_stats.lines_added, 10)
        self.assertEqual(commit_stats.lines_deleted, 5)
        self.assertEqual(len(commit_stats.files), 1)
        self.assertEqual(commit_stats.files[0].path, "test.py")


class TestRangeStats(unittest.TestCase):
    """Test cases for RangeStats."""

    def test_range_stats_creation(self):
        """Test RangeStats creation."""
        range_stats = RangeStats(
            start_date=datetime.fromisoformat("2025-07-20T10:00:00+08:00"),
            end_date=datetime.fromisoformat("2025-07-21T10:00:00+08:00"),
            total_commits=1,
            total_files_changed=1,
            total_lines_added=10,
            total_lines_deleted=5,
            commits=[
                CommitStats(
                    hash="abc123",
                    author="Test Author",
                    date=datetime.fromisoformat("2025-07-20T10:00:00+08:00"),
                    message="Test commit",
                    files_changed=1,
                    lines_added=10,
                    lines_deleted=5,
                    files=[FileStats("test.py", 10, 5, 15)],
                ),
            ],
            authors={"Test Author": 1},
        )

        self.assertEqual(
            range_stats.start_date,
            datetime.fromisoformat("2025-07-20T10:00:00+08:00"),
        )
        self.assertEqual(
            range_stats.end_date,
            datetime.fromisoformat("2025-07-21T10:00:00+08:00"),
        )
        self.assertEqual(range_stats.total_commits, 1)
        self.assertEqual(range_stats.total_files_changed, 1)
        self.assertEqual(range_stats.total_lines_added, 10)
        self.assertEqual(range_stats.total_lines_deleted, 5)
        self.assertEqual(len(range_stats.commits), 1)
        self.assertEqual(len(range_stats.authors), 1)
        self.assertEqual(range_stats.authors["Test Author"], 1)
