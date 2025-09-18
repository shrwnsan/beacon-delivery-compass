"""Analytics engine for integrating all analytics components.

This module provides the AnalyticsEngine class that integrates all the
analytics components (time, team, quality, risk) into a unified system
for the extended format.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from beaconled.core.models import RangeStats

from .collaboration_analyzer import CollaborationAnalyzer, CollaborationConfig
from .quality_analyzer import QualityAnalyzer, QualityConfig
from .risk_analyzer import RiskAnalyzer, RiskConfig
from .time_analyzer import TimeAnalyzer, TimeAnalyzerConfig

if TYPE_CHECKING:
    from beaconled.formatters.base_formatter import BaseFormatter
    from beaconled.formatters.chart import ChartFormatter as ChartRenderer
    from beaconled.formatters.heatmap import HeatmapFormatter as HeatmapRenderer


@dataclass
class RangeStatsWithAnalytics(RangeStats):
    """Wrapper for RangeStats that includes analytics data."""

    analytics: dict[str, Any] | None = None


class AnalyticsEngine:
    """Integrated analytics engine for all analysis components.

    This engine coordinates the various analytics components to provide
    a comprehensive analysis of repository data.
    """

    def __init__(self) -> None:
        """Initialize the analytics engine with all component analyzers."""
        self.logger = logging.getLogger(__name__)

        # Time-based analytics
        self.time_analyzer = TimeAnalyzer(TimeAnalyzerConfig())

        # Team collaboration analytics
        self.collaboration_analyzer = CollaborationAnalyzer(CollaborationConfig())

        # Code quality analytics
        self.quality_analyzer = QualityAnalyzer(QualityConfig())

        # Risk assessment analytics
        self.risk_analyzer = RiskAnalyzer(RiskConfig())

        # Caching for performance optimization
        self._cache: dict[Any, Any] = {}
        self._max_cache_size = 100  # Maximum number of results to cache

    def analyze(self, range_stats: RangeStats) -> dict[str, Any]:
        """Perform comprehensive analysis on range statistics.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary containing all analytics results with the following structure:
            {
                'time': {...},  # Time-based analytics
                'collaboration': {...},  # Team collaboration analytics
                'quality': {...},  # Code quality metrics
                'risk': {...}  # Risk assessment
            }
        """
        # Check cache first
        cache_key = self._get_cache_key(range_stats)
        if cache_key in self._cache:
            return cast("dict[str, Any]", self._cache[cache_key])

        # Perform parallel analysis
        results = self._run_parallel_analysis(range_stats)

        # Format and cache results
        result = self._format_analysis_results(results)
        self._cache_result(cache_key, result)

        return result

    def _run_parallel_analysis(self, range_stats: RangeStats) -> dict[str, Any]:
        """Run all analysis tasks in parallel.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary with results from all analyzers
        """
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all analysis tasks
            future_time = executor.submit(self.time_analyzer.analyze, range_stats)
            future_collaboration = executor.submit(self.collaboration_analyzer.analyze, range_stats)
            future_quality = executor.submit(self.quality_analyzer.analyze, range_stats)
            future_risk = executor.submit(self.risk_analyzer.analyze, range_stats)

            # Collect results as they complete
            return self._collect_analysis_results([
                (future_time, "time"),
                (future_collaboration, "collaboration"),
                (future_quality, "quality"),
                (future_risk, "risk"),
            ])

    def _collect_analysis_results(self, futures: list[tuple[Any, str]]) -> dict[str, Any]:
        """Collect results from analysis futures.

        Args:
            futures: List of (future, analyzer_name) tuples

        Returns:
            Dictionary with results from each analyzer
        """
        results = {}
        for future, analyzer_name in futures:
            try:
                result = future.result()
                results[analyzer_name] = result
            except Exception as e:
                self.logger.error("Analyzer %s failed: %s", analyzer_name, e)
                results[analyzer_name] = {}
        return results

    def _format_analysis_results(self, results: dict[str, Any]) -> dict[str, Any]:
        """Format analysis results in consistent order.

        Args:
            results: Raw results from analyzers

        Returns:
            Formatted results dictionary
        """
        return {
            "time": results.get("time", {}),
            "collaboration": results.get("collaboration", {}),
            "quality": results.get("quality", {}),
            "risk": results.get("risk", {}),
        }

    def _get_cache_key(self, range_stats: RangeStats) -> tuple[Any, ...]:
        """Generate a cache key for the given range stats.

        Optimized: Focus on core metrics rather than full author mapping
        to reduce cache misses when author details change but core stats remain same.
        """
        return (
            range_stats.total_commits,
            range_stats.start_date.isoformat(),
            range_stats.end_date.isoformat(),
            # Use author count instead of full author mapping for better cache hit rate
            len(range_stats.authors) if range_stats.authors else 0,
            # Include commit hash range for more precise caching
            getattr(range_stats, "first_commit_hash", ""),
            getattr(range_stats, "last_commit_hash", ""),
        )

    def _cache_result(self, key: Any, result: dict[str, Any]) -> None:
        """Cache the result and ensure cache doesn't exceed max size."""
        self._cache[key] = result

        # Remove oldest entries if cache is too large
        while len(self._cache) > self._max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]


class ExtendedFormatSystem:
    """Integrated system for the extended format.

    This system integrates all analytics, visualization, and formatting
    components into a cohesive pipeline for the extended format.
    """

    def __init__(self) -> None:
        """Initialize the extended format system."""
        # Analytics pipeline
        self.analytics_engine = AnalyticsEngine()

        # Visualization pipeline
        self.chart_renderer: ChartRenderer | None = None
        self.heatmap_renderer: HeatmapRenderer | None = None

        # Formatter for the output
        self.formatter: BaseFormatter | None = None

    def analyze(self, range_stats: RangeStats) -> dict[str, Any]:
        """Perform analysis on the given range stats.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary containing all analytics results
        """
        return self.analytics_engine.analyze(range_stats)

    def format_analysis(self, range_stats: RangeStats) -> str:
        """Format the analysis results as a string.

        Args:
            range_stats: The range statistics to analyze and format

        Returns:
            Formatted analysis as a string
        """
        if not self.formatter:
            error_msg = "No formatter configured for ExtendedFormatSystem"
            raise ValueError(error_msg)

        # Perform analysis
        analytics = self.analyze(range_stats)

        # Create a wrapper with analytics
        stats_with_analytics = RangeStatsWithAnalytics(
            **{k: v for k, v in vars(range_stats).items() if not k.startswith("_")},
            analytics=analytics,
        )

        # Format the results
        return self.formatter.format_range_stats(stats_with_analytics)

    def set_formatter(self, formatter: "BaseFormatter") -> None:
        """Set the formatter for the system.

        Args:
            formatter: The formatter to use for output
        """
        self.formatter = formatter

    def set_chart_renderer(self, renderer: "ChartRenderer") -> None:
        """Set the chart renderer for the system.

        Args:
            renderer: The chart renderer to use
        """
        self.chart_renderer = renderer

    def set_heatmap_renderer(self, renderer: "HeatmapRenderer") -> None:
        """Set the heatmap renderer for the system.

        Args:
            renderer: The heatmap renderer to use
        """
        self.heatmap_renderer = renderer
