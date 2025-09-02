"""Tests for heatmap formatter."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from beaconled.core.models import CommitStats, RangeStats, FileStats
from beaconled.formatters.heatmap import HeatmapFormatter


class TestHeatmapFormatter:
    """Test cases for HeatmapFormatter."""

    def test_format_commit_stats_returns_message(self):
        """Test that format_commit_stats returns appropriate message for single commits."""
        formatter = HeatmapFormatter()
        commit_stats = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime.now(),
            message="Test commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=5,
        )

        result = formatter.format_commit_stats(commit_stats)
        assert "Heatmap visualization is only available for date range analysis" in result

    def test_format_range_stats_without_matplotlib_raises_error(self):
        """Test that formatter raises ImportError when matplotlib is not available."""
        with patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", False):
            with pytest.raises(ImportError, match="matplotlib and numpy are required"):
                HeatmapFormatter()

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    def test_format_range_stats_no_commits(self):
        """Test formatting range stats with no commits."""
        formatter = HeatmapFormatter()
        range_stats = RangeStats(
            start_date=datetime(2025, 1, 1), end_date=datetime(2025, 1, 31), total_commits=0
        )

        result = formatter.format_range_stats(range_stats)
        assert "No commits found" in result

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    @patch("beaconled.formatters.heatmap.plt")
    @patch("os.path.join")
    @patch("tempfile.gettempdir")
    def test_format_range_stats_with_commits(self, mock_temp_dir, mock_path_join, mock_plt):
        """Test formatting range stats with commits."""
        # Setup mocks
        mock_temp_dir.return_value = "/tmp"
        mock_path_join.return_value = "/tmp/test_heatmap.png"
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, (mock_ax1, mock_ax2))
        mock_plt.get_fignums.return_value = [1, 2]

        # Create test data
        commit = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime(2025, 1, 15, 10, 0),
            message="Test commit",
            files_changed=2,
            lines_added=20,
            lines_deleted=10,
        )

        range_stats = RangeStats(
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31),
            total_commits=1,
            commits=[commit],
        )
        range_stats.commits_by_day = {"2025-01-15": 1}
        range_stats.author_activity_by_day = {"Test Author": {"Friday": 1}}

        formatter = HeatmapFormatter()
        result = formatter.format_range_stats(range_stats)

        assert "Heatmap visualization saved" in result
        assert "/tmp/test_heatmap.png" in result

        # Verify matplotlib calls were made
        mock_plt.subplots.assert_called()
        mock_plt.savefig.assert_called()

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    @patch("beaconled.formatters.heatmap.plt")
    def test_create_activity_heatmap(self, mock_plt):
        """Test creating activity heatmap."""
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, (mock_ax1, mock_ax2))

        range_stats = RangeStats(start_date=datetime(2025, 1, 1), end_date=datetime(2025, 1, 31))
        range_stats.commits_by_day = {"2025-01-15": 5, "2025-01-16": 3}

        formatter = HeatmapFormatter()
        formatter._create_activity_heatmap(range_stats)

        # Verify plot calls
        mock_plt.subplots.assert_called_with(2, 1, figsize=(12, 8))
        mock_ax1.plot.assert_called()
        mock_ax1.set_title.assert_called_with("Daily Commit Activity", fontsize=14)

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    @patch("beaconled.formatters.heatmap.plt")
    @patch("beaconled.formatters.heatmap.np")
    def test_create_author_heatmap(self, mock_np, mock_plt):
        """Test creating author activity heatmap."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_array = MagicMock()
        mock_array.size = 3
        mock_np.array.return_value = mock_array
        mock_np.max.return_value = 3

        range_stats = RangeStats(start_date=datetime(2025, 1, 1), end_date=datetime(2025, 1, 31))
        range_stats.author_activity_by_day = {
            "Author 1": {"Monday": 1, "Tuesday": 2, "Wednesday": 3}
        }

        formatter = HeatmapFormatter()
        formatter._create_author_heatmap(range_stats)

        # Verify plot calls
        mock_plt.subplots.assert_called()
        mock_ax.set_title.assert_called_with(
            "Author Activity by Day of Week", fontsize=14, fontweight="bold"
        )

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    @patch("beaconled.formatters.heatmap.plt")
    def test_save_plots(self, mock_plt):
        """Test saving plots to files."""
        mock_plt.get_fignums.return_value = [1, 2]

        formatter = HeatmapFormatter()
        formatter._save_plots("/tmp/test.png")

        # Verify savefig was called for each figure
        assert mock_plt.savefig.call_count == 2
        # Note: close is called at the end, so we check it was called
        assert mock_plt.close.called
