"""Tests for heatmap formatter."""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from beaconled.core.models import CommitStats, RangeStats
from beaconled.formatters.heatmap import HeatmapFormatter


class TestHeatmapFormatter:
    """Test cases for HeatmapFormatter."""

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    def test_format_commit_stats_returns_message(self):
        """Test that format_commit_stats returns appropriate message for single commits."""
        formatter = HeatmapFormatter()
        commit_stats = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime.now(timezone.utc),
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
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
            total_commits=0,
        )

        result = formatter.format_range_stats(range_stats)
        assert "No commits found" in result

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    @patch("beaconled.formatters.heatmap.plt")
    @patch("beaconled.formatters.heatmap.np")
    @patch("os.path.join")
    @patch("tempfile.gettempdir")
    def test_format_range_stats_with_commits(
        self, mock_temp_dir, mock_path_join, mock_np, mock_plt
    ):
        """Test formatting range stats with commits."""
        # Setup mocks
        mock_temp_dir.return_value = "/tmp"  # noqa: S108
        mock_path_join.return_value = "/tmp/test_heatmap.png"  # noqa: S108

        # Mock matplotlib functions to handle multiple calls
        mock_fig1 = MagicMock()
        mock_fig2 = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_ax3 = MagicMock()

        # Configure subplots to return different values based on call arguments
        def subplots_side_effect(*args, **kwargs):
            if args == (2, 1) and kwargs.get("figsize") == (12, 8):
                # First call for activity heatmap
                return (mock_fig1, (mock_ax1, mock_ax2))
            elif "figsize" in kwargs and len(kwargs) == 1:
                # Second call for author heatmap
                return (mock_fig2, mock_ax3)
            else:
                # Default case
                return (MagicMock(), MagicMock())

        mock_plt.subplots.side_effect = subplots_side_effect
        mock_plt.get_fignums.return_value = [1, 2]

        # Mock numpy functions
        mock_array = MagicMock()
        mock_array.size = 1
        # Mock the array indexing to return actual integers
        mock_array.__getitem__ = lambda self, key: (
            1 if isinstance(key, tuple) and len(key) == 2 else 0
        )
        mock_np.array.return_value = mock_array
        mock_np.max.return_value = 1
        # Mock zeros to return our mock array
        mock_np.zeros.return_value = mock_array

        # Create test data
        commit = CommitStats(
            hash="abc123",
            author="Test Author",
            date=datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc),
            message="Test commit",
            files_changed=2,
            lines_added=20,
            lines_deleted=10,
        )

        range_stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
            total_commits=1,
            commits=[commit],
        )
        range_stats.commits_by_day = {"2025-01-15": 1}
        range_stats.author_activity_by_day = {"Test Author": {"Friday": 1}}

        formatter = HeatmapFormatter()
        result = formatter.format_range_stats(range_stats)

        assert "Heatmap visualization saved" in result
        assert "/tmp/test_heatmap.png" in result  # noqa: S108

        # Verify matplotlib calls were made
        mock_plt.subplots.assert_called()
        mock_plt.savefig.assert_called()

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    @patch("beaconled.formatters.heatmap.LinearSegmentedColormap")
    @patch("beaconled.formatters.heatmap.plt")
    @patch("beaconled.formatters.heatmap.np")
    def test_create_activity_heatmap(self, mock_np, mock_plt, mock_colormap):
        """Test creating activity heatmap."""
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, (mock_ax1, mock_ax2))
        mock_colormap.from_list.return_value = MagicMock()

        # Mock numpy for the calendar heatmap
        mock_array = MagicMock()
        # Mock array indexing to return integers
        mock_array.__getitem__ = lambda self, key: 5 if isinstance(key, tuple) else 0
        mock_np.zeros.return_value = mock_array
        mock_np.array.return_value = mock_array
        mock_np.max.return_value = 5

        range_stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )
        range_stats.commits_by_day = {"2025-01-15": 5, "2025-01-16": 3}

        formatter = HeatmapFormatter()
        formatter._create_activity_heatmap(range_stats)

        # Verify plot calls
        mock_plt.subplots.assert_called_with(2, 1, figsize=(12, 8))
        mock_ax1.plot.assert_called()
        mock_ax1.set_title.assert_called_with("Daily Commit Activity", fontsize=14)

    @patch("beaconled.formatters.heatmap.MATPLOTLIB_AVAILABLE", True)
    @patch("beaconled.formatters.heatmap.LinearSegmentedColormap")
    @patch("beaconled.formatters.heatmap.plt")
    @patch("beaconled.formatters.heatmap.np")
    def test_create_author_heatmap(self, mock_np, mock_plt, mock_colormap):
        """Test creating author activity heatmap."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_colormap.from_list.return_value = MagicMock()

        # Mock numpy array with proper indexing behavior
        mock_array = MagicMock()
        mock_array.size = 3
        # Mock the array indexing to return actual integers
        # Handle different index patterns that might be accessed
        mock_array.__getitem__ = lambda self, key: (
            [1, 2, 3, 4, 5, 6, 7][key[1]]
            if isinstance(key, tuple) and len(key) == 2 and key[0] == 0 and key[1] < 7
            else 0
        )
        mock_np.array.return_value = mock_array
        mock_np.max.return_value = 3

        range_stats = RangeStats(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        )
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
        mock_plt.figure.return_value = None
        # Mock the savefig method to be called
        mock_plt.savefig.return_value = None

        formatter = HeatmapFormatter()
        formatter.show_plot = False  # Ensure close is called instead of show
        formatter._save_plots("/tmp/test.png")  # noqa: S108

        # Verify savefig was called for each figure
        assert mock_plt.savefig.call_count == 2
        # Note: close("all") is called at the end, so we check it was called
        mock_plt.close.assert_called_once_with("all")
