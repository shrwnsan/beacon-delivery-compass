# Copyright 2025 Beacon, shrwnsan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Heatmap formatter for visualizing git repository analytics."""

from __future__ import annotations

import os
import tempfile
from datetime import date as date_type
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from beaconled.config import display_config

from .base_formatter import BaseFormatter

if TYPE_CHECKING:
    from beaconled.core.models import CommitStats, RangeStats

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]
    LinearSegmentedColormap = None  # type: ignore[assignment,misc]
    MATPLOTLIB_AVAILABLE = False


class HeatmapFormatter(BaseFormatter):
    """Heatmap formatter for visualizing git repository analytics.

    Generates visual heatmaps showing commit activity patterns over time
    and author activity by day of week.
    """

    def __init__(self, output_file: str | None = None, *, show_plot: bool = True):
        """Initialize the heatmap formatter.

        Args:
            output_file: Path to save the heatmap image. If None, saves to temp file.
            show_plot: Whether to display the plot interactively.
        """
        if not MATPLOTLIB_AVAILABLE:
            msg = (
                "matplotlib and numpy are required for heatmap visualization. "
                "Install with: pip install matplotlib numpy"
            )
            raise ImportError(msg)

        self.output_file = output_file
        self.show_plot = show_plot

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as heatmap (not applicable for single commits)."""
        return "Heatmap visualization is only available for date range analysis (--since/--until)"

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as visual heatmaps."""
        if not stats.commits:
            return "No commits found in the specified date range"

        # Ensure extended stats are calculated
        if not hasattr(stats, "commits_by_day") or not stats.commits_by_day:
            stats.calculate_extended_stats()

        # Create the heatmaps
        self._create_activity_heatmap(stats)
        self._create_author_heatmap(stats)

        # Determine output file path
        if self.output_file:
            output_path = self.output_file
        else:
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(temp_dir, f"beacon_heatmap_{timestamp}.png")

        # Save plots to files
        self._save_plots(output_path)

        message = f"📊 Heatmap visualization saved to: {output_path}"

        if self.show_plot:
            message += "\n💡 The heatmap shows commit activity patterns over time"

        return message

    def _create_activity_heatmap(self, stats: RangeStats) -> None:
        """Create a calendar-style heatmap of daily commit activity."""
        if not self._is_matplotlib_available() or not self._has_commit_data(stats):
            return

        # Parse and prepare data
        dates, commits = self._parse_commit_data(stats)
        if not dates:
            return

        # Create visualization
        self._render_heatmap(dates, commits)

    def _is_matplotlib_available(self) -> bool:
        """Check if matplotlib dependencies are available."""
        return MATPLOTLIB_AVAILABLE and plt is not None and np is not None

    def _has_commit_data(self, stats: RangeStats) -> bool:
        """Check if stats has commit data for heatmap."""
        return hasattr(stats, "commits_by_day") and bool(stats.commits_by_day)

    def _parse_commit_data(self, stats: RangeStats) -> tuple[list[date_type], list[int]]:
        """Parse and sort commit data from stats."""
        dates = []
        commits = []
        date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]

        for date_str, count in stats.commits_by_day.items():
            if isinstance(date_str, str):
                date_obj = self._try_parse_date(date_str, date_formats)
                if date_obj:
                    dates.append(date_obj)
                    commits.append(count)

        if not dates:
            return [], []

        # Sort by date and optimize size
        date_commit_pairs = sorted(zip(dates, commits, strict=False))
        sorted_dates, sorted_commits = zip(*date_commit_pairs, strict=False)

        # Sample data if too large
        dates_list = list(sorted_dates)
        commits_list = list(sorted_commits)

        if len(dates_list) > 200:
            step = len(dates_list) // 200
            return dates_list[::step], commits_list[::step]

        return dates_list, commits_list

    def _try_parse_date(self, date_str: str, date_formats: list[str]) -> date_type | None:
        """Try parsing a date string with multiple formats."""
        for fmt in date_formats:
            try:
                parsed_dt = datetime.strptime(date_str, fmt)  # noqa: DTZ007
                return parsed_dt.replace(tzinfo=timezone.utc).date()
            except ValueError:
                continue
        return None

    def _render_heatmap(self, dates: list[date_type], commits: list[int]) -> None:
        """Render the heatmap visualization."""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
            fig.suptitle("Git Repository Activity Heatmap", fontsize=14, fontweight="bold")
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.warning("Failed to create figure: %s", e)
            return

        try:
            # Plot daily activity
            ax1.plot(dates, commits, marker="o", linewidth=1, markersize=3, color="#2E86AB")
            ax1.set_title("Daily Commit Activity", fontsize=12)
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Commits")
            ax1.grid(visible=True, alpha=0.3)
            ax1.tick_params(axis="x", rotation=45)

            # Create calendar heatmap
            self._create_calendar_heatmap(ax2, dates, commits)

            plt.tight_layout()
            plt.draw()
        finally:
            plt.close(fig)

    def _create_calendar_heatmap(
        self,
        ax: Any,
        dates: list[date_type],
        commits: list[int],
    ) -> None:
        """Create a simplified calendar heatmap."""
        if not self._is_matplotlib_available():
            return

        # Process data for heatmap
        month_data, max_commits = self._process_heatmap_data(dates, commits)
        if not month_data:
            return

        # Create visualization
        self._render_calendar_heatmap(ax, month_data, max_commits)

    def _process_heatmap_data(
        self, dates: list[date_type], commits: list[int]
    ) -> tuple[dict[str, dict[int, int]], int]:
        """Process dates and commits for heatmap visualization.

        Args:
            dates: List of dates
            commits: List of commit counts

        Returns:
            Tuple of (month_data, max_commits) where month_data maps month->day->commits
        """
        month_data: dict[str, dict[int, int]] = {}
        max_commits = max(commits) if commits else 1

        # Limit to last {display_config.last_n_months_heatmap} months for memory efficiency
        if dates:
            cutoff_date = dates[-1] - timedelta(days=365)
            filtered_pairs = [
                (d, c) for d, c in zip(dates, commits, strict=False) if d >= cutoff_date
            ]
        else:
            filtered_pairs = []

        # Group by month and day
        for commit_date, commit_count in filtered_pairs:
            month_key = commit_date.strftime("%Y-%m")
            if month_key not in month_data:
                month_data[month_key] = {}
            month_data[month_key][commit_date.day] = commit_count

        return month_data, max_commits

    def _render_calendar_heatmap(
        self, ax: Any, month_data: dict[str, dict[int, int]], max_commits: int
    ) -> None:
        """Render the calendar heatmap visualization.

        Args:
            ax: Matplotlib axis
            month_data: Processed month data
            max_commits: Maximum commit count for color scaling
        """
        months = sorted(month_data.keys())
        if not months:
            return

        # Use most recent month
        current_month = months[-1]
        days_in_month = month_data[current_month]

        # Create grid data
        heatmap_data = self._create_heatmap_grid(days_in_month)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Create and apply colormap
        cmap = self._create_colormap()
        im = ax.imshow(heatmap_data, cmap=cmap, aspect="auto")

        # Add colorbar and labels
        self._add_heatmap_styling(ax, im, current_month, day_names, heatmap_data, max_commits)

    def _create_heatmap_grid(self, days_in_month: dict[int, int]) -> Any:
        """Create the heatmap grid data.

        Args:
            days_in_month: Dictionary mapping day->commit_count

        Returns:
            NumPy array with heatmap data
        """
        heatmap_data = np.zeros((5, 7))

        for day, commit_count in days_in_month.items():
            week_row = (day - 1) // 7
            day_col = (day - 1) % 7

            if week_row < 5:  # Stay within 5-week grid
                heatmap_data[week_row, day_col] = commit_count

        return heatmap_data

    def _create_colormap(self) -> Any:
        """Create custom colormap for heatmap."""
        colors = ["#f7fbff", "#08306b"]  # Light blue to dark blue
        return LinearSegmentedColormap.from_list("custom_blue", colors)

    def _add_heatmap_styling(
        self,
        ax: Any,
        im: Any,
        current_month: str,
        day_names: list[str],
        heatmap_data: Any,
        max_commits: int,
    ) -> None:
        """Add styling elements to the heatmap.

        Args:
            ax: Matplotlib axis
            im: Image object
            current_month: Current month string
            day_names: List of day names
            heatmap_data: Heatmap data array
            max_commits: Maximum commit count
        """
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Commits")

        # Set labels and title
        ax.set_title(f"Commit Activity - {current_month}", fontsize=14)
        ax.set_xticks(range(7))
        ax.set_yticks(range(5))
        ax.set_xticklabels(day_names)
        ax.set_yticklabels([f"Week {i + 1}" for i in range(5)])

        # Add commit count text
        self._add_commit_count_text(ax, heatmap_data, max_commits)

    def _add_commit_count_text(self, ax: Any, heatmap_data: Any, max_commits: int) -> None:
        """Add commit count text to heatmap cells.

        Args:
            ax: Matplotlib axis
            heatmap_data: Heatmap data array
            max_commits: Maximum commit count for color threshold
        """
        for i in range(5):
            for j in range(7):
                if heatmap_data[i, j] > 0:
                    color = "white" if heatmap_data[i, j] > max_commits * 0.6 else "black"
                    ax.text(
                        j,
                        i,
                        int(heatmap_data[i, j]),
                        ha="center",
                        va="center",
                        color=color,
                        fontweight="bold",
                    )

    def _create_author_heatmap(self, stats: RangeStats) -> None:
        """Create a heatmap showing author activity by day of week."""
        if not MATPLOTLIB_AVAILABLE or plt is None or np is None or LinearSegmentedColormap is None:
            return

        if not hasattr(stats, "author_activity_by_day") or not stats.author_activity_by_day:
            return

        # Extract data
        authors = list(stats.author_activity_by_day.keys())
        if not authors:
            return

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        author_data = []

        for author in authors:
            day_activity = stats.author_activity_by_day[author]
            week_data = [day_activity.get(day, 0) for day in day_names]
            author_data.append(week_data)

        if not author_data:
            return

        # Create heatmap data
        heatmap_data = np.array(author_data)
        max_activity = np.max(heatmap_data) if heatmap_data.size > 0 else 1

        # Create new figure for author heatmap
        _fig, ax = plt.subplots(figsize=(10, max(4, len(authors) * 0.5)))

        # Create custom colormap (green to red for activity levels)
        colors = ["#f7fcf5", "#00441b"]  # Light green to dark green
        cmap = LinearSegmentedColormap.from_list("custom_green", colors)

        # Plot heatmap
        im = ax.imshow(heatmap_data, cmap=cmap, aspect="auto")

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Commits")

        # Set labels
        ax.set_title("Author Activity by Day of Week", fontsize=14, fontweight="bold")
        ax.set_xticks(range(len(day_names)))
        ax.set_yticks(range(len(authors)))
        ax.set_xticklabels([day[:3] for day in day_names])  # Abbreviated day names
        ax.set_yticklabels(authors)

        # Add activity counts as text
        for i in range(len(authors)):
            for j in range(len(day_names)):
                count = heatmap_data[i, j]
                if count > 0:
                    ax.text(
                        j,
                        i,
                        count,
                        ha="center",
                        va="center",
                        color="white" if count > max_activity * 0.6 else "black",
                        fontweight="bold",
                    )

        plt.tight_layout()

    def _save_plots(self, output_path: str) -> None:
        """Save all current plots to the specified path."""
        if not MATPLOTLIB_AVAILABLE or not plt:
            return

        # Save all open figures
        for i, fig in enumerate(plt.get_fignums()):
            plt.figure(fig)
            if i == 0:
                # First figure (activity heatmap)
                filename = f"{output_path.rsplit('.', 1)[0]}_activity.png"
            else:
                # Second figure (author heatmap)
                filename = f"{output_path.rsplit('.', 1)[0]}_authors.png"
            plt.savefig(filename, dpi=150, bbox_inches="tight")

        if self.show_plot:
            plt.show()
        else:
            plt.close("all")  # Close all figures to free memory</content>
