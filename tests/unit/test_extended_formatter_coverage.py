"""Tests for extended formatter coverage tracking functionality."""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from beaconled.core.models import CoverageStats, CoverageTrend, RangeStats
from beaconled.formatters.extended import ExtendedFormatter


class TestExtendedFormatterCoverage(unittest.TestCase):
    """Test cases for ExtendedFormatter coverage tracking."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.formatter = ExtendedFormatter(repo_path=self.temp_dir)

    def test_init_with_coverage_analyzer(self) -> None:
        """Test ExtendedFormatter initializes with coverage analyzer."""
        self.assertIsNotNone(self.formatter.coverage_analyzer)
        self.assertEqual(self.formatter.coverage_analyzer.repo_path, Path(self.temp_dir).resolve())

    def test_format_coverage_section_no_data(self) -> None:
        """Test _format_coverage_section when no coverage data is available."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        # Mock coverage analyzer to return no coverage
        with patch.object(
            self.formatter.coverage_analyzer, "get_latest_coverage", return_value=None
        ):
            lines = self.formatter._format_coverage_section(stats)

        self.assertEqual(len(lines), 1)
        self.assertIn("No coverage data found", lines[0])

    def test_format_coverage_section_with_data(self) -> None:
        """Test _format_coverage_section with coverage data."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=1000,
            covered_lines=850,
            line_rate=0.85,
            total_branches=500,
            covered_branches=400,
            branch_rate=0.8,
            file_coverage={
                "src/main.py": 95.0,
                "src/utils.py": 80.0,
                "tests/test_main.py": 98.0,
                "src/low_coverage.py": 45.0,
            },
        )

        # Mock the analyzer to return our test coverage
        with patch.object(
            self.formatter.coverage_analyzer,
            "get_latest_coverage",
            return_value=coverage,
        ):
            lines = self.formatter._format_coverage_section(stats)

        # Check basic coverage information is present
        self.assertTrue(any("Test Coverage:" in line for line in lines))
        self.assertTrue(any("Overall: 82.5%" in line for line in lines))
        self.assertTrue(any("Lines: 85.0%" in line for line in lines))
        self.assertTrue(any("Branches: 80.0%" in line for line in lines))

    def test_format_coverage_section_with_trends(self) -> None:
        """Test _format_coverage_section with trend analysis."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        # Add coverage data and trends
        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=1000,
            covered_lines=850,
            line_rate=0.85,
        )
        stats.coverage_history = [coverage]

        trend = CoverageTrend(
            start_coverage=CoverageStats(
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                total_lines=1000,
                covered_lines=800,
                line_rate=0.8,
            ),
            end_coverage=coverage,
            trend_direction="increasing",
            trend_magnitude=5.0,
            change_points=[
                {
                    "timestamp": datetime(2025, 1, 15, tzinfo=timezone.utc),
                    "change": 3.0,
                }
            ],
        )
        stats.coverage_trends = trend

        lines = self.formatter._format_coverage_section(stats)

        # Check trend information is present
        self.assertTrue(any("Coverage Trends:" in line for line in lines))
        self.assertTrue(any("Direction: increasing" in line for line in lines))
        self.assertTrue(any("Change: +5.0%" in line for line in lines))
        self.assertTrue(any("Improving" in line for line in lines))
        self.assertTrue(any("Significant changes:" in line for line in lines))

    def test_format_coverage_section_declining_trend(self) -> None:
        """Test _format_coverage_section with declining coverage trend."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        # Add declining trend
        trend = CoverageTrend(
            start_coverage=CoverageStats(
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                total_lines=1000,
                covered_lines=900,
                line_rate=0.9,
            ),
            end_coverage=CoverageStats(
                timestamp=datetime(2025, 1, 31, tzinfo=timezone.utc),
                total_lines=1000,
                covered_lines=850,
                line_rate=0.85,
            ),
            trend_direction="decreasing",
            trend_magnitude=5.0,
        )
        stats.coverage_trends = trend

        # Mock the analyzer to return our test coverage
        with patch.object(
            self.formatter.coverage_analyzer,
            "get_latest_coverage",
            return_value=trend.end_coverage,
        ):
            lines = self.formatter._format_coverage_section(stats)

        # Check declining trend is shown with red color
        self.assertTrue(any("Declining" in line for line in lines))

    def test_format_coverage_section_file_highlights(self) -> None:
        """Test _format_coverage_section highlights top and low coverage files."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=1000,
            covered_lines=850,
            line_rate=0.85,
            file_coverage={
                "src/excellent.py": 95.0,
                "src/good.py": 85.0,
                "src/okay.py": 75.0,
                "src/low.py": 45.0,
                "src/critical.py": 25.0,
            },
        )

        # Mock the analyzer to return our test coverage
        with patch.object(
            self.formatter.coverage_analyzer,
            "get_latest_coverage",
            return_value=coverage,
        ):
            lines = self.formatter._format_coverage_section(stats)

        # Check file coverage highlights
        self.assertTrue(any("Top covered files:" in line for line in lines))
        self.assertTrue(any("Files needing attention" in line for line in lines))
        self.assertTrue(any("src/excellent.py" in line for line in lines))
        self.assertTrue(any("src/low.py" in line for line in lines))

    def test_format_coverage_section_emoji_disabled(self) -> None:
        """Test _format_coverage_section with emojis disabled."""
        formatter = ExtendedFormatter(no_emoji=True, repo_path=self.temp_dir)

        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=1000,
            covered_lines=850,
            line_rate=0.85,
        )

        lines = formatter._format_coverage_section(stats)

        # Check emojis are not present
        for line in lines:
            self.assertNotIn("🧪", line)
            self.assertNotIn("📈", line)

    def test_format_coverage_section_from_analyzer(self) -> None:
        """Test _format_coverage_section gets coverage from analyzer when not in stats."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=1000,
            covered_lines=850,
            line_rate=0.85,
        )

        # Mock analyzer to return coverage
        with patch.object(
            self.formatter.coverage_analyzer,
            "get_latest_coverage",
            return_value=coverage,
        ):
            lines = self.formatter._format_coverage_section(stats)

        self.assertTrue(any("Overall: 85.0%" in line for line in lines))

    def test_format_coverage_section_analyzer_error(self) -> None:
        """Test _format_coverage_section handles analyzer errors gracefully."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )

        # Mock analyzer to raise an exception
        with patch.object(
            self.formatter.coverage_analyzer,
            "get_latest_coverage",
            side_effect=Exception("Test error"),
        ):
            lines = self.formatter._format_coverage_section(stats)

        self.assertEqual(len(lines), 1)
        self.assertIn("No coverage data found", lines[0])

    def test_format_range_stats_includes_coverage(self) -> None:
        """Test that format_range_stats includes coverage section."""
        stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
            total_commits=10,
            total_files_changed=20,
            total_lines_added=500,
            total_lines_deleted=300,
        )

        # Add some coverage data
        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=1000,
            covered_lines=850,
            line_rate=0.85,
        )
        stats.coverage_history = [coverage]

        # Mock the coverage section method directly
        with patch.object(
            self.formatter,
            "_format_coverage_section",
            return_value=["\n🧪 Test Coverage:", "  Overall: 85.0%"],
        ):
            output = self.formatter.format_range_stats(stats)

        # Check coverage section is included in the output
        self.assertIn("Test Coverage:", output)
        self.assertIn("85.0%", output)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
