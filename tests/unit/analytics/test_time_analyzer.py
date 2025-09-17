"""Unit tests for TimeAnalyzer."""

from datetime import datetime, timedelta, timezone

import pytest

from beaconled.analytics.time_analyzer import TimeAnalyzer, TimeAnalyzerConfig
from beaconled.core.models import CommitStats, RangeStats


class TestTimeAnalyzer:
    """Test cases for TimeAnalyzer class."""

    @pytest.fixture
    def config(self):
        """Default test configuration."""
        return TimeAnalyzerConfig(
            velocity_window_days=7, peak_threshold=1.5, bus_factor_threshold=0.5
        )

    @pytest.fixture
    def analyzer(self, config):
        """TimeAnalyzer instance for testing."""
        return TimeAnalyzer(config)

    @pytest.fixture
    def sample_commits(self):
        """Sample commit data for testing."""
        base_date = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        commits = []

        # Create commits over several days with varying activity
        for i in range(30):
            date = base_date + timedelta(days=i % 10, hours=i % 24)
            commits.append(
                CommitStats(
                    hash=f"commit_{i:03d}",
                    author=f"author_{(i % 3) + 1}",
                    date=date,
                    message=f"Commit {i}",
                    files_changed=i % 5 + 1,
                    lines_added=i * 10,
                    lines_deleted=i * 2,
                )
            )

        return commits

    @pytest.fixture
    def sample_range_stats(self, sample_commits):
        """Sample RangeStats for testing."""
        return RangeStats(
            start_date=min(c.date for c in sample_commits),
            end_date=max(c.date for c in sample_commits),
            commits=sample_commits,
        )

    def test_analyze_empty_commits(self, analyzer):
        """Test analysis with empty commit list."""
        empty_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 2, tzinfo=timezone.utc),
            commits=[],
        )

        result = analyzer.analyze(empty_stats)

        assert result.velocity_trends.daily_velocity == {}
        assert result.velocity_trends.weekly_average == 0.0
        assert result.activity_heatmap.by_day_of_week == {}
        assert result.peak_periods == []
        assert result.bus_factor.factor == 0

    def test_calculate_velocity_trends(self, analyzer, sample_commits):
        """Test velocity trends calculation."""
        velocity = analyzer._calculate_velocity_trends(sample_commits)

        assert isinstance(velocity.daily_velocity, dict)
        assert all(isinstance(v, float) for v in velocity.daily_velocity.values())
        assert isinstance(velocity.weekly_average, float)
        assert velocity.trend_direction in ["increasing", "decreasing", "stable"]
        assert isinstance(velocity.peak_velocity, tuple)
        assert len(velocity.peak_velocity) == 2

    def test_generate_activity_heatmap(self, analyzer, sample_commits):
        """Test activity heatmap generation."""
        heatmap = analyzer._generate_activity_heatmap(sample_commits)

        assert isinstance(heatmap.by_day_of_week, dict)
        assert isinstance(heatmap.by_hour, dict)
        assert all(isinstance(v, int) for v in heatmap.by_day_of_week.values())
        assert all(isinstance(v, int) for v in heatmap.by_hour.values())
        assert isinstance(heatmap.peak_day, str)
        assert isinstance(heatmap.peak_hour, int)
        assert 0 <= heatmap.peak_hour <= 23

    def test_identify_peak_periods(self, analyzer, sample_commits):
        """Test peak period identification."""
        peaks = analyzer._identify_peak_periods(sample_commits)

        assert isinstance(peaks, list)
        for peak in peaks:
            assert isinstance(peak, tuple)
            assert len(peak) == 2
            assert isinstance(peak[0], str)
            assert isinstance(peak[1], int)

        # Peaks should be sorted by commit count descending
        if len(peaks) > 1:
            assert peaks[0][1] >= peaks[1][1]

    def test_calculate_bus_factor(self, analyzer, sample_range_stats):
        """Test bus factor calculation."""
        bus_factor = analyzer._calculate_bus_factor(sample_range_stats.authors)

        assert isinstance(bus_factor.factor, int)
        assert bus_factor.factor >= 0
        assert isinstance(bus_factor.key_contributors, list)
        assert bus_factor.risk_level in ["low", "medium", "high"]

        for contributor in bus_factor.key_contributors:
            assert isinstance(contributor, tuple)
            assert len(contributor) == 2
            assert isinstance(contributor[0], str)
            assert isinstance(contributor[1], float)
            assert 0 <= contributor[1] <= 1

    def test_full_analysis(self, analyzer, sample_range_stats):
        """Test complete analysis pipeline."""
        result = analyzer.analyze(sample_range_stats)

        assert hasattr(result, "velocity_trends")
        assert hasattr(result, "activity_heatmap")
        assert hasattr(result, "peak_periods")
        assert hasattr(result, "bus_factor")

        # Verify all components are properly populated
        assert isinstance(result.velocity_trends.daily_velocity, dict)
        assert isinstance(result.activity_heatmap.by_day_of_week, dict)
        assert isinstance(result.peak_periods, list)
        assert isinstance(result.bus_factor.key_contributors, list)

    def test_single_author_bus_factor(self, analyzer):
        """Test bus factor with single author."""
        authors = {"single_author": 100}
        bus_factor = analyzer._calculate_bus_factor(authors)

        assert bus_factor.factor == 1
        assert len(bus_factor.key_contributors) == 1
        assert bus_factor.key_contributors[0][0] == "single_author"
        assert bus_factor.risk_level == "high"

    def test_multiple_authors_bus_factor(self, analyzer):
        """Test bus factor with multiple authors."""
        authors = {"author1": 60, "author2": 30, "author3": 10}
        bus_factor = analyzer._calculate_bus_factor(authors)

        assert bus_factor.factor == 1  # First author makes 60% (>= 50% threshold)
        assert len(bus_factor.key_contributors) == 1
        assert bus_factor.risk_level == "high"

    def test_config_parameters(self):
        """Test configuration parameter effects."""
        custom_config = TimeAnalyzerConfig(
            velocity_window_days=14, peak_threshold=2.0, bus_factor_threshold=0.7
        )
        analyzer = TimeAnalyzer(custom_config)

        assert analyzer.velocity_window_days == 14
        assert analyzer.peak_threshold == 2.0
        assert analyzer.bus_factor_threshold == 0.7
