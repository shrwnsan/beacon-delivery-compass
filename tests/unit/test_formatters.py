"""Test suite for output formatters."""

import json
from datetime import datetime
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from src.beaconled.core.models import CommitStats, FileStats, RangeStats
from src.beaconled.formatters.extended import ExtendedFormatter
from src.beaconled.formatters.json_format import JSONFormatter
from src.beaconled.formatters.standard import StandardFormatter


@pytest.fixture
def sample_commit_stats():
    """Create sample commit statistics for testing."""
    return CommitStats(
        hash="abc123def456",
        author="John Doe <john@example.com>",
        date=datetime(2023, 1, 15, 10, 30, 0),
        message="Add new feature implementation",
        files_changed=3,
        lines_added=45,
        lines_deleted=12,
        files=[
            FileStats(path="src/main.py", lines_added=30, lines_deleted=5, lines_changed=35),
            FileStats(path="tests/test_main.py", lines_added=10, lines_deleted=5, lines_changed=15),
            FileStats(path="docs/README.md", lines_added=5, lines_deleted=2, lines_changed=7),
        ],
    )


@pytest.fixture
def sample_range_stats():
    """Create sample range statistics for testing."""
    return RangeStats(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 1, 31),
        total_commits=5,
        total_files_changed=12,
        total_lines_added=156,
        total_lines_deleted=45,
        commits=[
            CommitStats(
                hash="abc123",
                author="John Doe",
                date=datetime(2023, 1, 10),
                message="Initial commit",
                files_changed=2,
                lines_added=25,
                lines_deleted=0,
                files=[],
            ),
            CommitStats(
                hash="def456",
                author="Jane Smith",
                date=datetime(2023, 1, 12),
                message="Add authentication",
                files_changed=3,
                lines_added=45,
                lines_deleted=10,
                files=[],
            ),
            CommitStats(
                hash="ghi789",
                author="John Doe",
                date=datetime(2023, 1, 15),
                message="Fix bug in login",
                files_changed=1,
                lines_added=8,
                lines_deleted=15,
                files=[],
            ),
            CommitStats(
                hash="jkl012",
                author="Bob Johnson",
                date=datetime(2023, 1, 20),
                message="Update documentation",
                files_changed=2,
                lines_added=50,
                lines_deleted=5,
                files=[],
            ),
            CommitStats(
                hash="mno345",
                author="Jane Smith",
                date=datetime(2023, 1, 25),
                message="Optimize database queries",
                files_changed=4,
                lines_added=28,
                lines_deleted=15,
                files=[],
            ),
        ],
        authors={"John Doe": 2, "Jane Smith": 2, "Bob Johnson": 1},
    )


class TestStandardFormatter:
    """Test the StandardFormatter class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.formatter = StandardFormatter()

    def test_format_commit_stats(self, sample_commit_stats):
        """Test formatting of commit statistics."""
        result = self.formatter.format_commit_stats(sample_commit_stats)
        
        # Remove ANSI color codes for testing
        import re
        clean_result = re.sub(r'\x1b\[[0-9;]*m', '', result)
        
        # Check basic content
        assert "Commit: abc123de" in clean_result
        assert "Author: John Doe <john@example.com>" in clean_result
        assert "Date: 2023-01-15 10:30:00" in clean_result
        assert "Message: Add new feature implementation" in clean_result
        assert "Files changed: 3" in clean_result
        assert "Lines added: 45" in clean_result
        assert "Lines deleted: 12" in clean_result
        assert "Net change: 33" in clean_result
        
        # Check file changes section
        assert "File changes:" in clean_result
        assert "src/main.py: +30 -5" in clean_result
        assert "tests/test_main.py: +10 -5" in clean_result
        assert "docs/README.md: +5 -2" in clean_result

    def test_format_range_stats(self, sample_range_stats):
        """Test formatting of range statistics."""
        result = self.formatter.format_range_stats(sample_range_stats)
        
        # Remove ANSI color codes for testing
        import re
        clean_result = re.sub(r'\x1b\[[0-9;]*m', '', result)
        
        # Check basic content
        assert "Range Analysis: 2023-01-01 to 2023-01-31" in clean_result
        assert "Total commits: 5" in clean_result
        assert "Total files changed: 12" in clean_result
        assert "Total lines added: 156" in clean_result
        assert "Total lines deleted: 45" in clean_result
        assert "Net change: 111" in clean_result
        
        # Check contributors section
        assert "Contributors:" in clean_result
        assert "John Doe: 2 commits" in clean_result
        assert "Jane Smith: 2 commits" in clean_result
        assert "Bob Johnson: 1 commits" in clean_result


class TestJSONFormatter:
    """Test the JSONFormatter class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.formatter = JSONFormatter()

    def test_format_commit_stats(self, sample_commit_stats):
        """Test JSON formatting of commit statistics."""
        result = self.formatter.format_commit_stats(sample_commit_stats)
        data = json.loads(result)
        
        # Check all fields are present and correct
        assert data["hash"] == "abc123def456"
        assert data["author"] == "John Doe <john@example.com>"
        assert data["date"] == "2023-01-15T10:30:00"
        assert data["message"] == "Add new feature implementation"
        assert data["files_changed"] == 3
        assert data["lines_added"] == 45
        assert data["lines_deleted"] == 12
        assert data["net_change"] == 33
        
        # Check files array
        assert len(data["files"]) == 3
        assert data["files"][0]["path"] == "src/main.py"
        assert data["files"][0]["lines_added"] == 30
        assert data["files"][0]["lines_deleted"] == 5
        assert data["files"][0]["lines_changed"] == 35

    def test_format_range_stats(self, sample_range_stats):
        """Test JSON formatting of range statistics."""
        result = self.formatter.format_range_stats(sample_range_stats)
        data = json.loads(result)
        
        # Check all fields are present and correct
        assert data["start_date"] == "2023-01-01T00:00:00"
        assert data["end_date"] == "2023-01-31T00:00:00"
        assert data["total_commits"] == 5
        assert data["total_files_changed"] == 12
        assert data["total_lines_added"] == 156
        assert data["total_lines_deleted"] == 45
        assert data["net_change"] == 111
        assert data["authors"] == {"John Doe": 2, "Jane Smith": 2, "Bob Johnson": 1}
        
        # Check commits array
        assert len(data["commits"]) == 5
        assert data["commits"][0]["hash"] == "abc123"
        assert data["commits"][0]["author"] == "John Doe"
        assert data["commits"][0]["date"] == "2023-01-10T00:00:00"


class TestExtendedFormatter:
    """Test the ExtendedFormatter class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.formatter = ExtendedFormatter()

    def test_format_commit_stats_with_file_types(self, sample_commit_stats):
        """Test extended formatting of commit statistics with file type analysis."""
        result = self.formatter.format_commit_stats(sample_commit_stats)
        
        # Remove ANSI color codes for testing
        import re
        clean_result = re.sub(r'\x1b\[[0-9;]*m', '', result)
        
        # Check standard output is included
        assert "Commit: abc123de" in clean_result
        assert "Files changed: 3" in clean_result
        
        # Check file type breakdown
        assert "File type breakdown:" in clean_result
        assert ".py: 2 files, +40 -10" in clean_result
        assert ".md: 1 files, +5 -2" in clean_result

    def test_format_range_stats_with_author_breakdown(self, sample_range_stats):
        """Test extended formatting of range statistics with author contribution breakdown."""
        result = self.formatter.format_range_stats(sample_range_stats)
        
        # Remove ANSI color codes for testing
        import re
        clean_result = re.sub(r'\x1b\[[0-9;]*m', '', result)
        
        # Check standard output is included
        assert "Range Analysis: 2023-01-01 to 2023-01-31" in clean_result
        assert "Total commits: 5" in clean_result
        
        # Check author contribution breakdown
        assert "Author Contribution Breakdown:" in clean_result
        assert "John Doe: 2 commits (40.0%)" in clean_result
        assert "Jane Smith: 2 commits (40.0%)" in clean_result
        assert "Bob Johnson: 1 commits (20.0%)" in clean_result

    @freeze_time("2023-01-31")
    def test_format_range_stats_with_temporal_analysis(self, sample_range_stats):
        """Test extended formatting of range statistics with temporal analysis visualization."""
        result = self.formatter.format_range_stats(sample_range_stats)
        
        # Remove ANSI color codes for testing
        import re
        clean_result = re.sub(r'\x1b\[[0-9;]*m', '', result)
        
        # Check temporal analysis section
        assert "Temporal Analysis - Daily Activity Timeline:" in clean_result
        
        # Check that all commit dates are represented
        assert "2023-01-10:  1 █" in clean_result
        assert "2023-01-12:  1 █" in clean_result
        assert "2023-01-15:  1 █" in clean_result
        assert "2023-01-20:  1 █" in clean_result
        assert "2023-01-25:  1 █" in clean_result
        
        # Check that dates without commits show zero activity (with proper spacing)
        assert "2023-01-11:  0" in clean_result
        assert "2023-01-13:  0" in clean_result
        assert "2023-01-14:  0" in clean_result
        assert "2023-01-16:  0" in clean_result
        assert "2023-01-17:  0" in clean_result
        assert "2023-01-18:  0" in clean_result
        assert "2023-01-19:  0" in clean_result
        assert "2023-01-21:  0" in clean_result
        assert "2023-01-22:  0" in clean_result
        assert "2023-01-23:  0" in clean_result
        assert "2023-01-24:  0" in clean_result
