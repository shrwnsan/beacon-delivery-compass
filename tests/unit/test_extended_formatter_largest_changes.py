"""Tests for the largest file changes functionality in ExtendedFormatter."""

from datetime import datetime, timezone

from beaconled.core.models import CommitStats, FileStats, RangeStats
from beaconled.formatters.extended import ExtendedFormatter


class TestExtendedFormatterLargestChanges:
    """Tests for the largest file changes functionality in ExtendedFormatter."""

    def setup_method(self):
        self.formatter = ExtendedFormatter()

    def test_get_largest_file_changes(self):
        """Test the _get_largest_file_changes method."""
        # Create test commits with different file changes
        commits = [
            CommitStats(
                hash="hash1",
                author="Author 1",
                date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                message="Commit 1",
                files=[
                    FileStats(
                        path="src/main.py",
                        lines_added=100,
                        lines_deleted=50,
                    ),
                    FileStats(
                        path="tests/test_main.py",
                        lines_added=30,
                        lines_deleted=10,
                    ),
                ],
            ),
            CommitStats(
                hash="hash2",
                author="Author 2",
                date=datetime(2023, 1, 2, tzinfo=timezone.utc),
                message="Commit 2",
                files=[
                    FileStats(
                        path="src/main.py",
                        lines_added=200,
                        lines_deleted=100,
                    ),
                    FileStats(
                        path="docs/README.md",
                        lines_added=50,
                        lines_deleted=20,
                    ),
                ],
            ),
            CommitStats(
                hash="hash3",
                author="Author 1",
                date=datetime(2023, 1, 3, tzinfo=timezone.utc),
                message="Commit 3",
                files=[
                    FileStats(
                        path="src/utils.py",
                        lines_added=75,
                        lines_deleted=25,
                    ),
                    FileStats(
                        path="tests/test_utils.py",
                        lines_added=40,
                        lines_deleted=15,
                    ),
                ],
            ),
        ]

        # Test the method
        result = self.formatter._get_largest_file_changes(commits)

        # Verify results
        assert len(result) == 5  # Should return top 5
        # src/main.py has 150 + 300 = 450 total changes
        assert result[0][0] == "src/main.py"
        assert result[0][1] == 450
        # src/utils.py has 100 changes
        assert result[1][0] == "src/utils.py"
        assert result[1][1] == 100
        # docs/README.md has 70 changes
        assert result[2][0] == "docs/README.md"
        assert result[2][1] == 70
        # tests/test_utils.py has 55 changes
        assert result[3][0] == "tests/test_utils.py"
        assert result[3][1] == 55
        # tests/test_main.py has 40 changes
        assert result[4][0] == "tests/test_main.py"
        assert result[4][1] == 40

    def test_get_largest_file_changes_empty_commits(self):
        """Test _get_largest_file_changes with empty commits list."""
        result = self.formatter._get_largest_file_changes([])
        assert result == []

    def test_format_largest_file_changes_section(self):
        """Test the _format_largest_file_changes_section method."""
        # Create a RangeStats with commits
        commits = [
            CommitStats(
                hash="hash1",
                author="Author 1",
                date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                message="Commit 1",
                files=[
                    FileStats(
                        path="src/main.py",
                        lines_added=100,
                        lines_deleted=50,
                    ),
                    FileStats(
                        path="tests/test_main.py",
                        lines_added=30,
                        lines_deleted=10,
                    ),
                ],
            ),
            CommitStats(
                hash="hash2",
                author="Author 2",
                date=datetime(2023, 1, 2, tzinfo=timezone.utc),
                message="Commit 2",
                files=[
                    FileStats(
                        path="src/main.py",
                        lines_added=200,
                        lines_deleted=100,
                    ),
                ],
            ),
        ]

        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            commits=commits,
        )

        result = self.formatter._format_largest_file_changes_section(range_stats)

        # Should have section header and file entries
        assert len(result) == 4  # Empty line + header + 2 file entries
        assert "Largest File Changes:" in result[1]
        assert "src/main.py: 450 lines changed" in result[2]
        assert "tests/test_main.py: 40 lines changed" in result[3]

    def test_format_largest_file_changes_section_empty(self):
        """Test _format_largest_file_changes_section with empty commits."""
        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            commits=[],
        )

        result = self.formatter._format_largest_file_changes_section(range_stats)
        assert result == []

    def test_format_range_stats_includes_largest_changes(self):
        """Test that format_range_stats includes the largest file changes section."""
        # Create a RangeStats with commits
        commits = [
            CommitStats(
                hash="hash1",
                author="Author 1",
                date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                message="Commit 1",
                files=[
                    FileStats(
                        path="src/main.py",
                        lines_added=100,
                        lines_deleted=50,
                    ),
                ],
            ),
        ]

        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            commits=commits,
        )

        result = self.formatter.format_range_stats(range_stats)
        clean_result = self._strip_ansi_codes(result)

        # Check that the largest file changes section is included
        assert "Largest File Changes:" in clean_result
        assert "src/main.py: 150 lines changed" in clean_result

    def _strip_ansi_codes(self, text):
        """Helper method to strip ANSI color codes from text."""
        import re

        return re.sub(r"\x1b\[[0-9;]*m", "", text)
