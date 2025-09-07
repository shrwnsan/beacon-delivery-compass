"""Integration tests for the AnalyticsEngine and EnhancedExtendedSystem.

These tests verify that all components integrate correctly and produce
expected output for the enhanced extended format.
"""

from datetime import datetime, timedelta, timezone

from beaconled.analytics import AnalyticsEngine, EnhancedExtendedSystem
from beaconled.core.models import CommitStats, RangeStats


class TestAnalyticsEngine:
    """Test suite for the AnalyticsEngine class."""

    def test_analytics_engine_initialization(self):
        """Test that AnalyticsEngine initializes correctly."""
        engine = AnalyticsEngine()
        assert engine.time_analyzer is not None
        assert engine.collaboration_analyzer is not None

    def test_analyze_with_simple_data(self):
        """Test analytics engine with simple test data."""
        # Create simple test data
        start_date = datetime.now(timezone.utc) - timedelta(days=7)
        end_date = datetime.now(timezone.utc)

        commit1 = CommitStats(
            hash="a" * 40,
            author="Alice <alice@example.com>",
            date=start_date + timedelta(days=1),
            message="Initial commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=0,
        )

        commit2 = CommitStats(
            hash="b" * 40,
            author="Bob <bob@example.com>",
            date=start_date + timedelta(days=2),
            message="Second commit",
            files_changed=2,
            lines_added=20,
            lines_deleted=5,
        )

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=2,
            total_files_changed=3,
            total_lines_added=30,
            total_lines_deleted=5,
            commits=[commit1, commit2],
            authors={"Alice": 1, "Bob": 1},
        )

        # Test the analytics engine
        engine = AnalyticsEngine()
        result = engine.analyze(range_stats)

        # Verify we get expected structure
        assert "time" in result
        assert "collaboration" in result
        assert result["time"] is not None
        assert result["collaboration"] is not None


class TestEnhancedExtendedSystem:
    """Test suite for the EnhancedExtendedSystem class."""

    def test_system_initialization(self):
        """Test that EnhancedExtendedSystem initializes correctly."""
        system = EnhancedExtendedSystem()
        assert system.analytics_engine is not None
        assert system.chart_renderer is None  # Not yet implemented
        assert system.heatmap_renderer is None  # Not yet implemented
        assert system.extended_formatter is None  # Not yet set

    def test_analyze_and_format_with_simple_data(self):
        """Test the complete analysis and formatting pipeline."""
        # Create simple test data
        start_date = datetime.now(timezone.utc) - timedelta(days=7)
        end_date = datetime.now(timezone.utc)

        commit1 = CommitStats(
            hash="a" * 40,
            author="Alice <alice@example.com>",
            date=start_date + timedelta(days=1),
            message="Initial commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=0,
        )

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=1,
            total_files_changed=1,
            total_lines_added=10,
            total_lines_deleted=0,
            commits=[commit1],
            authors={"Alice": 1},
        )

        # Test the system
        system = EnhancedExtendedSystem()
        result = system.analyze_and_format(range_stats)

        # Verify we get a string result
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain information about the analysis
        assert "Enhanced analysis complete" in result
