"""Tests for the analytics engine."""

from datetime import datetime, timezone

from beaconled.analytics.engine import AnalyticsEngine, ExtendedFormatSystem
from beaconled.core.models import RangeStats


class TestAnalyticsEngine:
    """Test cases for AnalyticsEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AnalyticsEngine()
        self.sample_range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            total_commits=10,
            total_files_changed=15,
            total_lines_added=100,
            total_lines_deleted=50,
            commits=[],  # Empty for basic tests
            authors={"user1": 5, "user2": 3, "user3": 2},
        )

    def test_engine_initialization(self):
        """Test that the analytics engine initializes correctly."""
        engine = AnalyticsEngine()

        assert engine.time_analyzer is not None
        assert engine.collaboration_analyzer is not None
        assert engine._cache == {}

    def test_analyze_basic_functionality(self):
        """Test basic analysis functionality."""
        result = self.engine.analyze(self.sample_range_stats)

        assert isinstance(result, dict)
        assert "time" in result
        assert "collaboration" in result

    def test_analyze_caching(self):
        """Test that results are properly cached."""
        # First analysis
        result1 = self.engine.analyze(self.sample_range_stats)

        # Cache should have one entry
        assert len(self.engine._cache) == 1

        # Second analysis with same data should use cache
        result2 = self.engine.analyze(self.sample_range_stats)

        # Results should be identical (same object due to caching)
        assert result1 is result2
        assert len(self.engine._cache) == 1

    def test_analyze_cache_limit(self):
        """Test that cache is limited to prevent memory issues."""
        # Create multiple different range stats to fill cache
        for i in range(105):  # More than the 100 cache limit
            range_stats = RangeStats(
                start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2023, 1, 2, tzinfo=timezone.utc),
                total_commits=i,  # Vary commits to create different cache keys
                total_files_changed=1,
                total_lines_added=1,
                total_lines_deleted=0,
                commits=[],
                authors={"user": 1},
            )
            self.engine.analyze(range_stats)

        # Cache should not exceed 100 entries
        assert len(self.engine._cache) <= 100

    def test_analyze_different_stats(self):
        """Test analysis with different statistics."""
        different_stats = RangeStats(
            start_date=datetime(2023, 2, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 2, 28, tzinfo=timezone.utc),
            total_commits=20,
            total_files_changed=25,
            total_lines_added=200,
            total_lines_deleted=75,
            commits=[],
            authors={"user1": 8, "user2": 7, "user3": 3, "user4": 1, "user5": 1},
        )

        result = self.engine.analyze(different_stats)

        assert isinstance(result, dict)
        assert "time" in result
        assert "collaboration" in result


class TestExtendedFormatSystem:
    """Test cases for EnhancedExtendedSystem."""

    def setup_method(self):
        """Set up test fixtures."""
        self.system = ExtendedFormatSystem()
        self.sample_range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            total_commits=5,
            total_files_changed=10,
            total_lines_added=50,
            total_lines_deleted=25,
            commits=[],
            authors={"user1": 3, "user2": 2},
        )

    def test_system_initialization(self):
        """Test that the enhanced extended system initializes correctly."""
        system = ExtendedFormatSystem()

        assert system.analytics_engine is not None
        assert system.chart_renderer is None
        assert system.heatmap_renderer is None
        assert system.formatter is None

    def test_format_analysis_fallback(self):
        """Test format_analysis with standard formatter."""
        from beaconled.formatters.standard import StandardFormatter

        self.system.set_formatter(StandardFormatter())

        result = self.system.format_analysis(self.sample_range_stats)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_analysis_with_formatter(self):
        """Test format_analysis with a custom formatter."""
        from beaconled.formatters.standard import StandardFormatter

        # Set a formatter
        self.system.set_formatter(StandardFormatter())

        result = self.system.format_analysis(self.sample_range_stats)

        # Should use the formatter instead of fallback
        assert isinstance(result, str)
        # Should not contain fallback text
        assert "Enhanced analysis complete" not in result
