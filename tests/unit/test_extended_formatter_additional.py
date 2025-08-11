"""Additional tests for ExtendedFormatter to improve coverage."""

from datetime import datetime, timedelta

from beaconled.core.models import CommitStats, RangeStats
from beaconled.formatters.extended import ExtendedFormatter


class TestExtendedFormatterAdditional:
    """Additional tests for ExtendedFormatter to improve coverage."""

    def setup_method(self):
        self.formatter = ExtendedFormatter()

    def test_get_author_contribution_stats(self):
        """Test the _get_author_contribution_stats method."""
        authors = {
            "Alice <alice@example.com>": 5,
            "Bob <bob@example.com>": 3,
            "Charlie <charlie@example.com>": 2,
        }
        total_commits = 10

        result = self.formatter._get_author_contribution_stats(authors, total_commits)

        assert len(result) == 3
        assert "  Alice <alice@example.com>: 5 commits (50.0%)" in result
        assert "  Bob <bob@example.com>: 3 commits (30.0%)" in result
        assert "  Charlie <charlie@example.com>: 2 commits (20.0%)" in result

    def test_get_daily_activity_stats(self):
        """Test the _get_daily_activity_stats method."""
        # Create test commits with different dates
        commits = [
            CommitStats(
                hash=f"hash{i}",
                author="Test Author",
                date=datetime(2023, 1, 1) + timedelta(days=i % 3),  # 3 different days
                message=f"Commit {i}",
                files_changed=1,
                lines_added=i + 1,
                lines_deleted=0,
                files=[],
            )
            for i in range(5)  # 5 commits total
        ]

        result = self.formatter._get_daily_activity_stats(commits)

        # Should have 3 days with commits
        assert len(result) == 3
        assert any("2023-01-01:" in line for line in result)
        assert any("2023-01-02:" in line for line in result)
        assert any("2023-01-03:" in line for line in result)

    def test_format_range_stats_with_daily_activity(self):
        """Test format_range_stats with commits_by_day attribute."""
        # Create a RangeStats with commits_by_day attribute
        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
            total_commits=10,
            total_files_changed=25,
            total_lines_added=100,
            total_lines_deleted=20,
            commits=[],
            authors={"Author": 10},
        )

        # Add commits_by_day attribute dynamically
        range_stats.commits_by_day = {"2023-01-01": 3, "2023-01-02": 5, "2023-01-03": 2}

        result = self.formatter.format_range_stats(range_stats)
        clean_result = self._strip_ansi_codes(result)

        # Check that daily activity is included
        assert "Temporal Analysis - Daily Activity Timeline:" in clean_result
        assert "2023-01-01: 3 commits" in clean_result
        assert "2023-01-02: 5 commits" in clean_result
        assert "2023-01-03: 2 commits" in clean_result

    def test_format_range_stats_with_file_types(self):
        """Test format_range_stats with file_types attribute."""
        # Create a RangeStats with file_types attribute
        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
            total_commits=10,
            total_files_changed=25,
            total_lines_added=100,
            total_lines_deleted=20,
            commits=[],
            authors={"Author": 10},
        )

        # Add file_types attribute dynamically
        range_stats.file_types = {
            ".py": {"count": 10, "added": 70, "deleted": 10},
            ".md": {"count": 5, "added": 20, "deleted": 5},
            ".txt": {"count": 10, "added": 10, "deleted": 5},
        }

        result = self.formatter.format_range_stats(range_stats)
        clean_result = self._strip_ansi_codes(result)

        # Check that file type breakdown is included
        assert "File type breakdown:" in clean_result
        assert ".py: 10 files, +70/-10" in clean_result
        assert ".md: 5 files, +20/-5" in clean_result
        assert ".txt: 10 files, +10/-5" in clean_result

    def _strip_ansi_codes(self, text):
        """Helper method to strip ANSI color codes from text."""
        import re

        return re.sub(r"\x1b\[[0-9;]*m", "", text)
