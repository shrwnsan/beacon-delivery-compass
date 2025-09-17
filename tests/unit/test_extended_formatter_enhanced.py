"""Tests for the enhanced features in ExtendedFormatter."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from beaconled.analytics.models import (
    ActivityHeatmap,
    BusFactor,
    CoAuthorshipMetrics,
    CollaborationMetrics,
    CollaborationPatterns,
    KnowledgeDistribution,
    ReviewMetrics,
    TimeAnalytics,
    VelocityTrends,
)
from beaconled.core.models import RangeStats
from beaconled.formatters.extended import ExtendedFormatter

"""Unit tests for the ExtendedFormatter with enhanced analytics."""


@pytest.fixture
def sample_range_with_enhanced_analytics():
    """Provides a sample RangeStats object with enhanced analytics data."""

    # Create analytics data
    time_analytics = TimeAnalytics(
        velocity_trends=VelocityTrends(
            daily_velocity={"2023-01-15": 5, "2023-01-16": 3},
            weekly_average=12.3,
            trend_direction="increasing",
            peak_velocity=("2023-01-15", 5.0),
        ),
        activity_heatmap=ActivityHeatmap(
            by_day_of_week={"Monday": 10, "Tuesday": 5},
            by_hour={10: 5, 15: 8},
            peak_day="Monday",
            peak_hour=15,
        ),
        peak_periods=[("2023-01-15", 5), ("2023-01-16", 3)],
        bus_factor=BusFactor(
            factor=2,
            key_contributors=[("alice", 0.5), ("bob", 0.3), ("charlie", 0.2)],
            risk_level="medium",
        ),
    )

    collaboration_metrics = CollaborationMetrics(
        co_authorship=type(
            "CoAuthorshipMetrics",
            (),
            {"author_pairs": {}, "collaboration_strength": {}, "top_collaborators": []},
        )(),
        knowledge_distribution=type(
            "KnowledgeDistribution",
            (),
            {"author_expertise": {}, "knowledge_silos": [], "ownership_patterns": {}},
        )(),
        review_metrics=type(
            "ReviewMetrics",
            (),
            {"review_participation": {}, "review_coverage": {}, "review_quality_indicators": {}},
        )(),
        collaboration_patterns=CollaborationPatterns(
            team_connectivity=0.85, collaboration_balance=0.75, knowledge_risk="medium"
        ),
    )

    # Create range stats with analytics
    range_stats = RangeStats(
        start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
        total_commits=42,
        total_files_changed=123,
        total_lines_added=456,
        total_lines_deleted=234,
        authors={"alice": 20, "bob": 15, "charlie": 7},
        commits_by_day={"2023-01-15": 5, "2023-01-16": 3},
    )

    # Add analytics as attributes
    range_stats.time = time_analytics
    range_stats.collaboration = collaboration_metrics
    range_stats.quality = type(
        "QualityMetrics", (), {"maintainability_index": 82.5, "test_coverage": 78.5}
    )()
    range_stats.risk = type(
        "RiskMetrics",
        (),
        {"risk_score": 3.0, "hotspots": ["src/core/utils.py", "src/api/endpoints.py"]},
    )()

    return range_stats


class TestEnhancedExtendedFormatter:
    """Tests for the enhanced features in ExtendedFormatter."""

    def setup_method(self):
        """Set up the test case."""
        self.formatter = ExtendedFormatter()

    def test_format_range_stats_with_enhanced_analytics(self, sample_range_with_enhanced_analytics):
        """Test that enhanced analytics are included in the formatted output."""
        # Act
        result = self.formatter.format_range_stats(sample_range_with_enhanced_analytics)

        # Debug output
        print("\n=== Formatted Output ===")
        print(result)
        print("======================\n")

        # Check basic info is present
        assert "Range Analysis:" in result
        assert "2023-01-01 to 2023-01-31" in result
        assert "Total commits: 42" in result or "Total commits:\x1b[0m 42" in result
        assert "Total files changed: 123" in result or "Total files changed:\x1b[0m 123" in result
        assert "Total lines added: 456" in result or "Total lines added:\x1b[0m 456" in result
        assert "Total lines deleted: 234" in result or "Total lines deleted:\x1b[0m 234" in result

        # Check contributors
        assert "alice: 20 commits" in result
        assert "bob: 15 commits" in result
        assert "charlie: 7 commits" in result

        # Check daily activity
        assert "2023-01-15: 5 commits" in result
        assert "2023-01-16: 3 commits" in result

    def test_format_range_stats_with_missing_analytics(self):
        """Test that the formatter handles missing analytics gracefully."""
        # Arrange
        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            total_commits=10,
            total_files_changed=20,
            total_lines_added=100,
            total_lines_deleted=50,
            authors={"alice": 10},
            commits_by_day={"2023-01-15": 5, "2023-01-16": 5},
        )

        # Act
        result = self.formatter.format_range_stats(range_stats)

        # Assert - Basic info should still be present
        assert "Range Analysis:" in result
        assert "Total commits: 10" in result or "Total commits:\x1b[0m 10" in result

    @patch("beaconled.analytics.engine.AnalyticsEngine.analyze")
    def test_analytics_engine_integration(self, mock_analyze):
        """Test that the analytics engine is properly integrated."""
        # Arrange

        # Create mock analytics data
        time_analytics = TimeAnalytics(
            velocity_trends=VelocityTrends(
                daily_velocity={"2023-01-15": 5, "2023-01-16": 3},
                weekly_average=15.0,
                trend_direction="increasing",
                peak_velocity=("2023-01-15", 5.0),
            ),
            activity_heatmap=ActivityHeatmap(
                by_day_of_week={"Monday": 10, "Tuesday": 5},
                by_hour={9: 5, 10: 10},
                peak_day="Monday",
                peak_hour=10,
            ),
            peak_periods=[("2023-01-15", 5)],
            bus_factor=BusFactor(
                factor=2, key_contributors=[("alice", 0.6), ("bob", 0.4)], risk_level="low"
            ),
        )

        # Create mock collaboration metrics with all required fields
        collaboration_metrics = CollaborationMetrics(
            co_authorship=CoAuthorshipMetrics(
                author_pairs={}, collaboration_strength={}, top_collaborators=[]
            ),
            knowledge_distribution=KnowledgeDistribution(
                author_expertise={}, knowledge_silos=[], ownership_patterns={}
            ),
            review_metrics=ReviewMetrics(
                review_participation={}, review_coverage={}, review_quality_indicators={}
            ),
            collaboration_patterns=CollaborationPatterns(
                team_connectivity=0.8, collaboration_balance=0.7, knowledge_risk="low"
            ),
        )

        # Create a mock analytics result with the required structure as a dict
        mock_analytics_result = {
            "time": time_analytics,
            "collaboration": collaboration_metrics,
            "quality": type(
                "Quality", (), {"maintainability_index": 85.5, "test_coverage": 78.2}
            )(),
            "risk": type("Risk", (), {"risk_score": 2.5, "hotspots": ["src/core/"]})(),
        }

        mock_analyze.return_value = mock_analytics_result

        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 31, tzinfo=timezone.utc),
            total_commits=30,
            total_files_changed=15,
            total_lines_added=300,
            total_lines_deleted=150,
            authors={"alice": 18, "bob": 12},
            commits_by_day={"2023-01-15": 5, "2023-01-16": 3},
        )

        # Act
        result = self.formatter.format_range_stats(range_stats)

        # Assert - Check that the analytics data appears in the output
        assert "15.0 commits/week" in result
        assert "Team connectivity: 80.0%" in result
        assert "Knowledge risk: low" in result
        assert "Maintainability: 85.5" in result
        assert "Test coverage: 78.2%" in result
        assert "Overall risk: 2.5/10" in result

        # Verify the analytics engine was called with the range stats
        mock_analyze.assert_called_once_with(range_stats)
