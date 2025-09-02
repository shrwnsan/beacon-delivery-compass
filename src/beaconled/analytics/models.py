"""Data models for analytics components.

This module defines the data structures used by the analytics engine
for time-based analysis, code quality metrics, and team collaboration insights.
"""

from dataclasses import dataclass


@dataclass
class VelocityTrends:
    """Commit velocity trends over time.

    Attributes:
        daily_velocity: Dictionary mapping dates to commits per day
        weekly_average: Average commits per week
        trend_direction: Direction of velocity trend ('increasing', 'decreasing', 'stable')
        peak_velocity: Tuple of (date, velocity) for the peak day
    """

    daily_velocity: dict[str, float]
    weekly_average: float
    trend_direction: str
    peak_velocity: tuple[str, float]


@dataclass
class ActivityHeatmap:
    """Activity patterns by day of week and hour.

    Attributes:
        by_day_of_week: Dictionary mapping day names to commit counts
        by_hour: Dictionary mapping hour (0-23) to commit counts
        peak_day: Day of week with highest activity
        peak_hour: Hour of day with highest activity
    """

    by_day_of_week: dict[str, int]
    by_hour: dict[int, int]
    peak_day: str
    peak_hour: int


@dataclass
class BusFactor:
    """Team bus factor analysis.

    Attributes:
        factor: Number of people who do 50% of the work
        key_contributors: List of (author, percentage) tuples for top contributors
        risk_level: Risk level ('low', 'medium', 'high')
    """

    factor: int
    key_contributors: list[tuple[str, float]]
    risk_level: str


@dataclass
class TimeAnalytics:
    """Comprehensive time-based analytics results.

    Attributes:
        velocity_trends: Velocity trends analysis
        activity_heatmap: Activity heatmap data
        peak_periods: List of peak activity periods
        bus_factor: Bus factor analysis
    """

    velocity_trends: VelocityTrends
    activity_heatmap: ActivityHeatmap
    peak_periods: list[tuple[str, int]]  # List of (date, commit_count) for peak periods
    bus_factor: BusFactor
