"""Unit tests for enhanced standard formatter functionality."""

import re
import unittest
from datetime import datetime, timezone

from beaconled.core.models import CommitStats, FileStats, RangeStats
from beaconled.formatters.standard import StandardFormatter


class TestEnhancedStandardFormatter(unittest.TestCase):
    """Test enhanced standard formatter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = StandardFormatter()

        # Create test commits with different impact levels
        self.test_commits = [
            CommitStats(
                hash="abc123def456",
                author="John Doe <john@example.com>",
                date=datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
                message="High impact commit",
                files_changed=20,  # High impact
                lines_added=150,
                lines_deleted=50,
                files=[
                    FileStats("src/main.py", 100, 30, 130),
                    FileStats("src/utils.py", 50, 20, 70),
                ],
            ),
            CommitStats(
                hash="def456ghi789",
                author="Jane Smith <jane@example.com>",
                date=datetime(2025, 1, 16, 14, 30, 0, tzinfo=timezone.utc),
                message="Medium impact commit",
                files_changed=8,  # Medium impact
                lines_added=40,
                lines_deleted=10,
                files=[
                    FileStats("docs/readme.md", 30, 5, 35),
                    FileStats("tests/test_main.py", 10, 5, 15),
                ],
            ),
            CommitStats(
                hash="ghi789jkl012",
                author="John Doe <john@example.com>",
                date=datetime(2025, 1, 17, 9, 15, 0, tzinfo=timezone.utc),
                message="Low impact commit",
                files_changed=2,  # Low impact
                lines_added=5,
                lines_deleted=2,
                files=[
                    FileStats("config.json", 3, 1, 4),
                    FileStats("root.txt", 2, 1, 3),
                ],
            ),
        ]

    def strip_ansi_codes(self, text: str) -> str:
        """Strip ANSI color codes from text for easier testing."""
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text)

    def test_impact_categorization(self):
        """Test commit impact categorization logic."""
        high_impact_commit = self.test_commits[0]
        medium_impact_commit = self.test_commits[1]
        low_impact_commit = self.test_commits[2]

        self.assertEqual(
            RangeStats.categorize_commit_impact(high_impact_commit), "high"
        )
        self.assertEqual(
            RangeStats.categorize_commit_impact(medium_impact_commit), "medium"
        )
        self.assertEqual(RangeStats.categorize_commit_impact(low_impact_commit), "low")

    def test_component_name_extraction(self):
        """Test component name extraction from file paths."""
        self.assertEqual(RangeStats.get_component_name("src/main.py"), "src/")
        self.assertEqual(RangeStats.get_component_name("docs/readme.md"), "docs/")
        self.assertEqual(RangeStats.get_component_name("config.json"), "root")
        self.assertEqual(
            RangeStats.get_component_name("tests/unit/test_main.py"), "tests/"
        )

    def test_extended_stats_calculation(self):
        """Test extended statistics calculation."""
        start_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 17, tzinfo=timezone.utc)

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            commits=self.test_commits,
        )

        # Calculate extended stats
        range_stats.calculate_extended_stats()

        # Test author impact stats
        self.assertIn("John Doe <john@example.com>", range_stats.author_impact_stats)
        john_impact = range_stats.author_impact_stats["John Doe <john@example.com>"]
        self.assertEqual(john_impact["high"], 1)
        self.assertEqual(john_impact["low"], 1)

        # Test author activity by day
        self.assertIn("John Doe <john@example.com>", range_stats.author_activity_by_day)
        john_activity = range_stats.author_activity_by_day[
            "John Doe <john@example.com>"
        ]
        # 2025-01-15 was a Wednesday, 2025-01-17 was a Friday
        self.assertEqual(john_activity["Wednesday"], 1)
        self.assertEqual(john_activity["Friday"], 1)

        # Test component stats
        self.assertIn("src/", range_stats.component_stats)
        self.assertIn("docs/", range_stats.component_stats)
        self.assertIn("root", range_stats.component_stats)

        src_stats = range_stats.component_stats["src/"]
        self.assertEqual(src_stats["commits"], 1)
        self.assertEqual(src_stats["lines"], 200)  # 150 + 50 from first commit

    def test_enhanced_format_output(self):
        """Test enhanced standard format output."""
        start_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 17, tzinfo=timezone.utc)

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=3,
            total_files_changed=30,
            total_lines_added=195,
            total_lines_deleted=62,
            commits=self.test_commits,
            authors={
                "John Doe <john@example.com>": 2,
                "Jane Smith <jane@example.com>": 1,
            },
        )

        # Calculate extended stats
        range_stats.calculate_extended_stats()

        # Format the output
        output = self.formatter.format_range_stats(range_stats)
        clean_output = self.strip_ansi_codes(output)

        # Test header format
        self.assertIn(
            "Analysis Period: 2025-01-15 to 2025-01-17 (2 days)", clean_output
        )

        # Test total statistics section
        self.assertIn("Total commits: 3", clean_output)
        self.assertIn("Total files changed: 30", clean_output)
        self.assertIn("Total lines added: 195", clean_output)
        self.assertIn("Total lines deleted: 62", clean_output)
        self.assertIn("Net change:", clean_output)

        # Test team overview section
        self.assertIn("=== TEAM OVERVIEW ===", clean_output)
        self.assertIn("Total Contributors: 2", clean_output)
        self.assertIn("Total Commits: 3", clean_output)
        self.assertIn("Average Commits/Day: 1.5", clean_output)

        # Test contributor breakdown section
        self.assertIn("=== CONTRIBUTOR BREAKDOWN ===", clean_output)
        self.assertIn("John Doe <john@example.com>: 2 commits (67%)", clean_output)
        self.assertIn("Jane Smith <jane@example.com>: 1 commits (33%)", clean_output)
        self.assertIn("High Impact: 1 commits", clean_output)
        self.assertIn("Medium Impact:", clean_output)
        self.assertIn("Low Impact:", clean_output)
        self.assertIn("Most Active:", clean_output)

        # Test component activity section
        self.assertIn("=== COMPONENT ACTIVITY ===", clean_output)
        self.assertIn("Most Changed Components:", clean_output)
        self.assertIn("src/", clean_output)
        self.assertIn("docs/", clean_output)

    def test_no_commits_handling(self):
        """Test handling of range stats with no commits."""
        start_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 17, tzinfo=timezone.utc)

        range_stats = RangeStats(
            start_date=start_date, end_date=end_date, commits=[], authors={}
        )

        range_stats.calculate_extended_stats()
        output = self.formatter.format_range_stats(range_stats)
        clean_output = self.strip_ansi_codes(output)

        # Should still show header
        self.assertIn(
            "Analysis Period: 2025-01-15 to 2025-01-17 (2 days)", clean_output
        )

        # Should not show team overview or breakdown sections
        self.assertNotIn("=== TEAM OVERVIEW ===", output)
        self.assertNotIn("=== CONTRIBUTOR BREAKDOWN ===", output)
        self.assertNotIn("=== COMPONENT ACTIVITY ===", output)

    def test_single_day_range(self):
        """Test formatting for single-day range."""
        start_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 15, tzinfo=timezone.utc)

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            commits=self.test_commits[:1],
            authors={"John Doe <john@example.com>": 1},
        )

        range_stats.calculate_extended_stats()
        output = self.formatter.format_range_stats(range_stats)
        clean_output = self.strip_ansi_codes(output)

        self.assertIn(
            "Analysis Period: 2025-01-15 to 2025-01-15 (1 days)", clean_output
        )
        self.assertIn("Average Commits/Day: 1.0", clean_output)

    def test_component_sorting(self):
        """Test that components are sorted correctly by commits and lines."""
        # Create a range stats with known component data
        start_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 17, tzinfo=timezone.utc)

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            commits=self.test_commits,
            authors={
                "John Doe <john@example.com>": 2,
                "Jane Smith <jane@example.com>": 1,
            },
        )

        range_stats.calculate_extended_stats()

        # Check that src/ has highest impact (1 commit, 200 lines)
        # docs/ has medium impact (1 commit, 35 lines)
        # root has lower impact (1 commit, 7 lines)

        self.assertEqual(range_stats.component_stats["src/"]["commits"], 1)
        self.assertEqual(range_stats.component_stats["src/"]["lines"], 200)
        self.assertEqual(range_stats.component_stats["docs/"]["commits"], 1)
        self.assertEqual(range_stats.component_stats["docs/"]["lines"], 35)


if __name__ == "__main__":
    unittest.main()
