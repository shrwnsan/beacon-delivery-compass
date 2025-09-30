"""Tests for coverage analyzer functionality."""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from beaconled.analytics.coverage_analyzer import CoverageAnalyzer
from beaconled.core.models import CoverageStats, CoverageTrend


class TestCoverageAnalyzer(unittest.TestCase):
    """Test cases for CoverageAnalyzer."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = CoverageAnalyzer(self.temp_dir)

    def test_init(self) -> None:
        """Test CoverageAnalyzer initialization."""
        analyzer = CoverageAnalyzer("/test/path")
        self.assertEqual(str(analyzer.repo_path), str(Path("/test/path").resolve()))

    def test_find_coverage_files_none(self) -> None:
        """Test find_coverage_files when no coverage files exist."""
        files = self.analyzer.find_coverage_files()
        self.assertEqual(files, [])

    def test_find_coverage_files_xml(self) -> None:
        """Test find_coverage_files with XML coverage file."""
        coverage_xml = Path(self.temp_dir) / "coverage.xml"
        coverage_xml.write_text(
            """<?xml version="1.0" ?>
<coverage version="7.9.2" timestamp="1757606795036" lines-valid="100" lines-covered="85" line-rate="0.85" branches-valid="50" branches-covered="40" branch-rate="0.8">
</coverage>"""
        )

        files = self.analyzer.find_coverage_files()
        self.assertEqual(len(files), 1)
        # Use resolve() to handle macOS /private/var vs /var path differences
        self.assertEqual(files[0].resolve(), coverage_xml.resolve())

    def test_find_coverage_files_db(self) -> None:
        """Test find_coverage_files with .coverage database file."""
        coverage_db = Path(self.temp_dir) / ".coverage"
        coverage_db.write_text("dummy coverage data")

        files = self.analyzer.find_coverage_files()
        self.assertEqual(len(files), 1)
        # Use resolve() to compare absolute paths
        self.assertEqual(files[0].resolve(), coverage_db.resolve())

    def test_parse_coverage_xml_valid(self) -> None:
        """Test parsing valid coverage XML file."""
        coverage_xml = Path(self.temp_dir) / "coverage.xml"
        coverage_xml.write_text(
            """<?xml version="1.0" ?>
<coverage version="7.9.2" timestamp="1757606795036" lines-valid="100" lines-covered="85" line-rate="0.85" branches-valid="50" branches-covered="40" branch-rate="0.8">
    <sources>
        <source>/test/path</source>
    </sources>
    <packages>
        <package name="test" line-rate="0.85" branch-rate="0.8">
            <classes>
                <class name="test_file.py" filename="test_file.py" line-rate="0.9">
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="0"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""
        )

        coverage = self.analyzer.parse_coverage_xml(coverage_xml)

        self.assertEqual(coverage.total_lines, 100)
        self.assertEqual(coverage.covered_lines, 85)
        self.assertEqual(coverage.line_rate, 0.85)
        self.assertEqual(coverage.total_branches, 50)
        self.assertEqual(coverage.covered_branches, 40)
        self.assertEqual(coverage.branch_rate, 0.8)
        self.assertEqual(coverage.line_percentage, 85.0)
        self.assertEqual(coverage.branch_percentage, 80.0)
        self.assertEqual(coverage.overall_percentage, 82.5)
        self.assertIn("test_file.py", coverage.file_coverage)
        self.assertEqual(coverage.file_coverage["test_file.py"], 90.0)

    def test_parse_coverage_xml_nonexistent(self) -> None:
        """Test parsing non-existent coverage XML file."""
        with self.assertRaises(FileNotFoundError):
            self.analyzer.parse_coverage_xml("nonexistent.xml")

    def test_parse_coverage_xml_invalid(self) -> None:
        """Test parsing invalid coverage XML file."""
        coverage_xml = Path(self.temp_dir) / "invalid.xml"
        coverage_xml.write_text("invalid xml content")

        with self.assertRaises(ValueError):
            self.analyzer.parse_coverage_xml(coverage_xml)

    @patch("coverage.Coverage")
    def test_parse_coverage_db_valid(self, mock_coverage_class) -> None:
        """Test parsing valid .coverage database file."""
        # Mock coverage module and its behavior
        mock_cov = MagicMock()
        mock_analysis = MagicMock()
        mock_analysis.numbers.n_statements = 100
        mock_analysis.numbers.pc_covered = 0.85
        # Mock file-level analysis to return same percentage
        mock_file_analysis = MagicMock()
        mock_file_analysis.numbers.n_statements = 50
        mock_file_analysis.numbers.pc_covered = 0.9

        def mock_analyze_side_effect(filename):
            if filename == "":
                return mock_analysis
            else:
                return mock_file_analysis

        mock_cov._analyze.side_effect = mock_analyze_side_effect
        mock_cov.get_data.return_value.measured_files.return_value = ["test_file.py"]
        mock_coverage_class.return_value = mock_cov

        coverage_db = Path(self.temp_dir) / ".coverage"
        coverage_db.write_text("dummy data")

        coverage = self.analyzer.parse_coverage_db(coverage_db)

        self.assertEqual(coverage.total_lines, 100)
        self.assertEqual(coverage.covered_lines, 85)
        self.assertEqual(coverage.line_rate, 0.85)

    def test_parse_coverage_db_nonexistent(self) -> None:
        """Test parsing non-existent .coverage database file."""
        with self.assertRaises(FileNotFoundError):
            self.analyzer.parse_coverage_db("nonexistent.coverage")

    @patch.dict("sys.modules", {"coverage": None})
    def test_parse_coverage_db_no_coverage_module(self) -> None:
        """Test parsing .coverage database when coverage module is not available."""
        coverage_db = Path(self.temp_dir) / ".coverage"
        coverage_db.write_text("dummy data")

        with self.assertRaises(ImportError) as cm:
            self.analyzer.parse_coverage_db(coverage_db)

        self.assertIn("coverage module is required", str(cm.exception))

    def test_get_latest_coverage_none(self) -> None:
        """Test get_latest_coverage when no coverage files exist."""
        coverage = self.analyzer.get_latest_coverage()
        self.assertIsNone(coverage)

    def test_get_latest_coverage_with_files(self) -> None:
        """Test get_latest_coverage with coverage files."""
        # Create coverage XML file
        coverage_xml = Path(self.temp_dir) / "coverage.xml"
        coverage_xml.write_text(
            """<?xml version="1.0" ?>
<coverage version="7.9.2" timestamp="1757606795036" lines-valid="100" lines-covered="85" line-rate="0.85">
</coverage>"""
        )

        coverage = self.analyzer.get_latest_coverage()
        self.assertIsNotNone(coverage)
        self.assertEqual(coverage.total_lines, 100)
        self.assertEqual(coverage.covered_lines, 85)

    def test_get_coverage_history_empty(self) -> None:
        """Test get_coverage_history when no coverage files exist."""
        history = self.analyzer.get_coverage_history()
        self.assertEqual(history, [])

    def test_get_coverage_history_with_files(self) -> None:
        """Test get_coverage_history with multiple coverage files."""
        # Create multiple coverage files with names that will be found
        coverage_xml1 = Path(self.temp_dir) / "coverage.xml"
        coverage_xml1.write_text(
            """<?xml version="1.0" ?>
<coverage version="7.9.2" timestamp="1757606795036" lines-valid="100" lines-covered="80" line-rate="0.8">
</coverage>"""
        )

        coverage_xml2 = Path(self.temp_dir) / "reports" / "coverage.xml"
        coverage_xml2.parent.mkdir(exist_ok=True)
        coverage_xml2.write_text(
            """<?xml version="1.0" ?>
<coverage version="7.9.2" timestamp="1757606795037" lines-valid="100" lines-covered="85" line-rate="0.85">
</coverage>"""
        )

        history = self.analyzer.get_coverage_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].line_percentage, 80.0)  # Sorted chronologically
        self.assertEqual(history[1].line_percentage, 85.0)

    def test_analyze_coverage_trends_empty(self) -> None:
        """Test analyze_coverage_trends with empty history."""
        trend = self.analyzer.analyze_coverage_trends([])
        self.assertEqual(trend.trend_direction, "stable")
        self.assertEqual(trend.trend_magnitude, 0.0)

    def test_analyze_coverage_trends_single(self) -> None:
        """Test analyze_coverage_trends with single coverage point."""
        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=100,
            covered_lines=85,
            line_rate=0.85,
        )
        trend = self.analyzer.analyze_coverage_trends([coverage])
        self.assertEqual(trend.trend_direction, "stable")
        self.assertEqual(trend.trend_magnitude, 0.0)

    def test_analyze_coverage_trends_improving(self) -> None:
        """Test analyze_coverage_trends with improving coverage."""
        start_coverage = CoverageStats(
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            total_lines=100,
            covered_lines=80,
            line_rate=0.8,
        )
        end_coverage = CoverageStats(
            timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
            total_lines=100,
            covered_lines=90,
            line_rate=0.9,
        )

        trend = self.analyzer.analyze_coverage_trends([start_coverage, end_coverage])
        self.assertEqual(trend.trend_direction, "increasing")
        self.assertEqual(trend.trend_magnitude, 10.0)
        self.assertTrue(trend.has_improved)
        self.assertAlmostEqual(trend.improvement_percentage, 12.5, places=1)

    def test_analyze_coverage_trends_declining(self) -> None:
        """Test analyze_coverage_trends with declining coverage."""
        start_coverage = CoverageStats(
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            total_lines=100,
            covered_lines=90,
            line_rate=0.9,
        )
        end_coverage = CoverageStats(
            timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
            total_lines=100,
            covered_lines=80,
            line_rate=0.8,
        )

        trend = self.analyzer.analyze_coverage_trends([start_coverage, end_coverage])
        self.assertEqual(trend.trend_direction, "decreasing")
        self.assertEqual(trend.trend_magnitude, 10.0)
        self.assertFalse(trend.has_improved)
        self.assertAlmostEqual(trend.improvement_percentage, -11.1, places=1)

    def test_analyze_coverage_trends_change_points(self) -> None:
        """Test analyze_coverage_trends detects significant changes."""
        coverages = [
            CoverageStats(
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                total_lines=100,
                covered_lines=80,
                line_rate=0.8,
            ),
            CoverageStats(
                timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
                total_lines=100,
                covered_lines=95,  # +15% change - significant
                line_rate=0.95,
            ),
            CoverageStats(
                timestamp=datetime(2025, 1, 3, tzinfo=timezone.utc),
                total_lines=100,
                covered_lines=96,
                line_rate=0.96,
            ),
        ]

        trend = self.analyzer.analyze_coverage_trends(coverages)
        self.assertEqual(len(trend.change_points), 1)
        self.assertEqual(trend.change_points[0]["change"], 15.0)

    def test_analyze_coverage_trends_file_trends(self) -> None:
        """Test analyze_coverage_trends includes file-level trends."""
        start_coverage = CoverageStats(
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            total_lines=100,
            covered_lines=80,
            line_rate=0.8,
            file_coverage={"file1.py": 80.0, "file2.py": 70.0},
        )
        end_coverage = CoverageStats(
            timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
            total_lines=100,
            covered_lines=90,
            line_rate=0.9,
            file_coverage={"file1.py": 90.0, "file2.py": 75.0},
        )

        trend = self.analyzer.analyze_coverage_trends([start_coverage, end_coverage])
        self.assertIn("file1.py", trend.file_trends)
        self.assertIn("file2.py", trend.file_trends)
        self.assertEqual(trend.file_trends["file1.py"]["change"], 10.0)
        self.assertEqual(trend.file_trends["file2.py"]["change"], 5.0)

    def test_coverage_stats_properties(self) -> None:
        """Test CoverageStats property calculations."""
        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=100,
            covered_lines=85,
            line_rate=0.85,
            total_branches=50,
            covered_branches=40,
            branch_rate=0.8,
        )

        self.assertEqual(coverage.line_percentage, 85.0)
        self.assertEqual(coverage.branch_percentage, 80.0)
        self.assertEqual(coverage.overall_percentage, 82.5)

    def test_coverage_stats_properties_line_only(self) -> None:
        """Test CoverageStats properties with line coverage only."""
        coverage = CoverageStats(
            timestamp=datetime.now(timezone.utc),
            total_lines=100,
            covered_lines=85,
            line_rate=0.85,
        )

        self.assertEqual(coverage.line_percentage, 85.0)
        self.assertEqual(coverage.branch_percentage, 0.0)
        self.assertEqual(coverage.overall_percentage, 85.0)

    def test_coverage_trend_properties_no_data(self) -> None:
        """Test CoverageTrend properties with no data."""
        trend = CoverageTrend()
        self.assertFalse(trend.has_improved)
        self.assertEqual(trend.improvement_percentage, 0.0)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
