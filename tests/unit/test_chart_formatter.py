"""Tests for ChartFormatter."""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.beaconled.core.models import RangeStats, CommitStats, FileStats
from src.beaconled.formatters.chart import ChartFormatter


class TestChartFormatter:
    """Test cases for ChartFormatter."""

    def test_init_without_dependencies(self):
        """Test initialization when dependencies are not available."""
        with patch.dict("sys.modules", {"matplotlib.pyplot": None}):
            with pytest.raises(ImportError, match="Chart generation requires matplotlib"):
                ChartFormatter()

    def test_format_commit_stats(self):
        """Test formatting commit stats (should return message for single commits)."""
        formatter = ChartFormatter()
        mock_stats = MagicMock()

        result = formatter.format_commit_stats(mock_stats)

        assert "Chart generation is only supported for range analysis" in result
        assert "--since flag" in result

    def test_format_range_stats_success(self):
        """Test successful range stats formatting."""
        with (
            patch("matplotlib.pyplot.subplots") as mock_subplots,
            patch("matplotlib.pyplot.savefig") as mock_savefig,
            patch("matplotlib.pyplot.close") as mock_close,
        ):
            # Mock matplotlib
            mock_subplots.return_value = (MagicMock(), MagicMock())
            mock_savefig.return_value = None
            mock_close.return_value = None

            formatter = ChartFormatter()
            # Mock the dependencies
            formatter.plt = MagicMock()
            formatter.plt.subplots.return_value = (MagicMock(), MagicMock())
            formatter.plt.savefig.return_value = None
            formatter.plt.close.return_value = None
            formatter.plt.cm.Set3.colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

            mock_stats = self._create_mock_range_stats()

            result = formatter.format_range_stats(mock_stats)

            assert "Charts generated successfully" in result
            assert "beacon-charts.png" in result

    @patch("beaconled.formatters.chart.plt")
    def test_format_range_stats_custom_output(self, mock_plt):
        """Test range stats formatting with custom output path."""
        # Mock matplotlib
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())
        mock_plt.savefig.return_value = None
        mock_plt.close.return_value = None

        formatter = ChartFormatter(output_path="custom.png")
        mock_stats = self._create_mock_range_stats()

        result = formatter.format_range_stats(mock_stats)

        assert "custom.png" in result
        mock_plt.savefig.assert_called_once_with("custom.png", dpi=300, bbox_inches="tight")

    @patch("beaconled.formatters.chart.plt")
    def test_format_range_stats_error(self, mock_plt):
        """Test range stats formatting with error."""
        # Mock matplotlib to raise an error
        mock_plt.subplots.side_effect = Exception("Test error")

        formatter = ChartFormatter()
        mock_stats = self._create_mock_range_stats()

        result = formatter.format_range_stats(mock_stats)

        assert "Error generating charts" in result
        assert "Test error" in result

    def _create_mock_range_stats(self):
        """Create a mock RangeStats object for testing."""
        start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 7, tzinfo=timezone.utc)

        # Create mock commits
        commit1 = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime(2025, 1, 2, tzinfo=timezone.utc),
            message="Test commit",
            files_changed=2,
            lines_added=10,
            lines_deleted=5,
            files=[
                FileStats(path="test.py", lines_added=10, lines_deleted=5),
                FileStats(path="README.md", lines_added=0, lines_deleted=0),
            ],
        )

        commit2 = CommitStats(
            hash="def456",
            author="Test Author",
            date=datetime(2025, 1, 3, tzinfo=timezone.utc),
            message="Another commit",
            files_changed=1,
            lines_added=5,
            lines_deleted=2,
            files=[
                FileStats(path="main.py", lines_added=5, lines_deleted=2),
            ],
        )

        return RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=2,
            total_files_changed=3,
            total_lines_added=15,
            total_lines_deleted=7,
            commits=[commit1, commit2],
            authors={"Test Author": 2},
            commits_by_day={"2025-01-02": 1, "2025-01-03": 1},
        )
