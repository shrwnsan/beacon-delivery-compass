"""Extended output formatter with additional analytics."""

from collections import defaultdict
from typing import Any

from colorama import Fore, Style

from beaconled.analytics.engine import AnalyticsEngine
from beaconled.core.models import CommitStats, RangeStats
from beaconled.formatters.base_formatter import BaseFormatter


class ExtendedFormatter(BaseFormatter):
    """Extended text formatter with additional analytics.

    Extends the base formatter with additional statistics including:
    - File type breakdown
    - Author contribution details
    - Daily activity patterns
    - Time-based analytics
    - Team collaboration analysis
    - Code quality insights
    - Risk assessment
    """

    def __init__(self, *, no_emoji: bool = False):
        """Initializes the formatter."""
        super().__init__()
        # Disable emojis in environments that don't support them
        self.no_emoji = no_emoji or not self._supports_emoji()
        self.analytics_engine = AnalyticsEngine()

        self.EMOJIS = {
            "commit": "📊",
            "author": "👤",
            "date": "📅",
            "message": "💬",
            "files": "📂",
            "added": "📈",
            "deleted": "📉",
            "net": "🔀",
            "range": "📊",
            "contributors": "👥",
            "activity": "🔥",
            "breakdown": "🔍",
            "time": "⏱️",
            "team": "👥",
            "quality": "🛠️",
            "risk": "⚠️",
        }

    def _supports_emoji(self) -> bool:
        """Check if the environment supports emoji."""
        import sys

        # A simple check for UTF-8 encoding is usually sufficient.
        # Also, handle environments where stdout might be redirected or missing (like in tests).
        encoding = getattr(sys.stdout, "encoding", "")
        if encoding:
            return encoding.lower() == "utf-8"
        return False

    def _get_emoji(self, name: str) -> str:
        """Return emoji if supported, else empty string."""
        return self.EMOJIS.get(name, "") if not self.no_emoji else ""

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics with extended details."""
        net_change_str = self._format_net_change(
            stats.lines_added,
            stats.lines_deleted,
        )
        output = [
            f"{self._get_emoji('commit')} {Fore.CYAN}Commit:{Style.RESET_ALL} {stats.hash[:8]}",
            f"{self._get_emoji('author')} {Fore.CYAN}Author:{Style.RESET_ALL} {stats.author}",
            f"{self._get_emoji('date')} {Fore.CYAN}Date:{Style.RESET_ALL} "
            f"{self._format_date(stats.date)}",
            f"{self._get_emoji('message')} {Fore.CYAN}Message:{Style.RESET_ALL} {stats.message}",
            "",
            f"{self._get_emoji('files')} {Fore.YELLOW}Files changed:{Style.RESET_ALL} "
            f"{stats.files_changed:,}",
            f"{self._get_emoji('added')} {Fore.GREEN}Lines added:{Style.RESET_ALL} "
            f"{stats.lines_added:,}",
            f"{self._get_emoji('deleted')} {Fore.RED}Lines deleted:{Style.RESET_ALL} "
            f"{stats.lines_deleted:,}",
            f"{self._get_emoji('net')} {Fore.YELLOW}Net change:{Style.RESET_ALL} {net_change_str}",
        ]

        if stats.files:
            # Add file changes
            output.extend(
                [
                    "",
                    f"{Fore.MAGENTA}File changes:{Style.RESET_ALL}",
                    *[self._format_file_stats(f) for f in stats.files],
                ],
            )

        # Add file type breakdown (match test expectation wording)
        # Always include this section for consistency in extended format
        file_types = self._get_file_type_breakdown(stats.files) if stats.files else {}
        output.extend([
            "",
            f"{Fore.MAGENTA}File type breakdown:{Style.RESET_ALL}",
        ])
        if file_types:
            output.extend([
                self._format_file_type_line(ext, counts)
                for ext, counts in sorted(file_types.items())
            ])
        else:
            output.append("  No files changed")

        return "\n".join(output)

    def _format_file_type_line(self, ext: str, counts: dict[str, int]) -> str:
        added = counts["added"]
        deleted = counts["deleted"]
        count = counts["count"]
        return f"  {ext}: {count} files, +{added:,}/-{deleted:,}"

    def _convert_analytics_object_to_dict(self, analytics: Any) -> dict[str, Any]:
        """Convert an analytics object to a dictionary."""
        # Ensure we return a dict, not just any object
        if isinstance(analytics, dict):
            return analytics
        # If it's an object, convert to dict
        elif hasattr(analytics, "__dict__"):
            analytics_dict = analytics.__dict__
            if isinstance(analytics_dict, dict):
                return analytics_dict
            else:
                return {}
        # Try to convert arbitrary objects to dict by accessing their attributes
        elif hasattr(analytics, "__class__"):
            result: dict[str, Any] = {}
            for attr in ["time", "collaboration", "quality", "risk"]:
                if hasattr(analytics, attr):
                    result[attr] = getattr(analytics, attr)
            return result
        else:
            # Fallback to empty dict
            return {}

    def _extract_stats_analytics(self, stats: RangeStats) -> dict[str, Any]:
        """Extract analytics data from stats object attributes."""
        stats_analytics: dict[str, Any] = {}
        if hasattr(stats, "time"):
            stats_analytics["time"] = stats.time
        if hasattr(stats, "collaboration"):
            stats_analytics["collaboration"] = stats.collaboration
        if hasattr(stats, "quality"):
            stats_analytics["quality"] = stats.quality
        if hasattr(stats, "risk"):
            stats_analytics["risk"] = stats.risk
        return stats_analytics

    def _get_analytics_data(self, stats: RangeStats) -> dict[str, Any]:
        """Get analytics data from stats or by calling analytics engine."""
        result: dict[str, Any] = {}

        # First check if analytics is already attached to stats
        analytics = getattr(stats, "analytics", None)
        if analytics is not None:
            result = self._convert_analytics_object_to_dict(analytics)
        else:
            # Check for individual analytics attributes on stats object
            stats_analytics = self._extract_stats_analytics(stats)

            # If we have analytics data from attributes, use it
            if stats_analytics:
                result = stats_analytics
            else:
                # Otherwise, call our own analytics engine
                analytics_result = self.analytics_engine.analyze(stats)
                # analytics_result is guaranteed to be a dict from the engine
                result = analytics_result

        return result

    def _format_basic_stats(self, stats: RangeStats) -> list[str]:
        """Format basic statistics section."""
        range_net_change = self._format_net_change(
            stats.total_lines_added,
            stats.total_lines_deleted,
        )
        return [
            f"{self._get_emoji('range')} {Fore.CYAN}Range Analysis:{Style.RESET_ALL} "
            f"{self._format_date(stats.start_date).split()[0]} to "
            f"{self._format_date(stats.end_date).split()[0]}",
            "",
            f"{Fore.YELLOW}Total commits:{Style.RESET_ALL} {stats.total_commits:,}",
            f"{Fore.YELLOW}Total files changed:{Style.RESET_ALL} {stats.total_files_changed:,}",
            f"{self._get_emoji('added')} {Fore.GREEN}Total lines added:{Style.RESET_ALL} "
            f"{stats.total_lines_added:,}",
            f"{self._get_emoji('deleted')} {Fore.RED}Total lines deleted:{Style.RESET_ALL} "
            f"{stats.total_lines_deleted:,}",
            f"{self._get_emoji('net')} {Fore.YELLOW}Net change:{Style.RESET_ALL} "
            f"{range_net_change}",
        ]

    def _format_authors_section(self, stats: RangeStats) -> list[str]:
        """Format authors section."""
        if not stats.authors:
            return []

        return [
            "",
            f"{self._get_emoji('contributors')} {Fore.MAGENTA}Contributors:{Style.RESET_ALL}",
            *[
                self._format_author_stats(a, c)
                for a, c in sorted(
                    stats.authors.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ],
        ]

    def _format_daily_activity_section(self, stats: RangeStats) -> list[str]:
        """Format daily activity section."""
        if not hasattr(stats, "commits_by_day"):
            return []

        return [
            "",
            (
                f"{self._get_emoji('activity')} "
                f"{Fore.MAGENTA}Temporal Analysis - Daily Activity "
                f"Timeline:{Style.RESET_ALL}"
            ),
            *[
                f"  {day}: {count} commit{'s' if count != 1 else ''}"
                for day, count in sorted(stats.commits_by_day.items())
            ],
        ]

    def _format_file_types_section(self, stats: RangeStats) -> list[str]:
        """Format file types section."""
        file_types = {}
        if stats.commits:
            file_types = self._get_file_type_breakdown_from_commits(stats.commits)
        elif hasattr(stats, "file_types") and stats.file_types:
            file_types = stats.file_types

        if not file_types:
            return []

        return [
            "",
            f"{self._get_emoji('breakdown')} {Fore.MAGENTA}File type breakdown:{Style.RESET_ALL}",
            *[
                self._format_file_type_line(ext, counts)
                for ext, counts in sorted(file_types.items())
            ],
        ]

    def _format_time_analytics_section(self, analytics: dict[str, Any]) -> list[str]:
        """Format the time-based analytics section."""
        has_time_analytics = (
            isinstance(analytics, dict) and "time" in analytics and analytics["time"] is not None
        )
        if not has_time_analytics:
            return []

        time_analytics = analytics["time"]
        return [
            "",
            f"{self._get_emoji('time')} {Fore.MAGENTA}Time-Based Analytics:{Style.RESET_ALL}",
            f"  • Velocity: {time_analytics.velocity_trends.weekly_average:.1f} commits/week",
            f"  • Peak day: {time_analytics.activity_heatmap.peak_day}",
            f"  • Bus factor: {time_analytics.bus_factor.factor}",
        ]

    def _format_team_collaboration_section(self, analytics: dict[str, Any]) -> list[str]:
        """Format the team collaboration analytics section."""
        has_collab_analytics = (
            isinstance(analytics, dict)
            and "collaboration" in analytics
            and analytics["collaboration"] is not None
        )
        if not has_collab_analytics:
            return []

        collab = analytics["collaboration"]
        collab_patterns = getattr(collab, "collaboration_patterns", None)
        knowledge_risk = (
            collab_patterns.knowledge_risk
            if collab_patterns and hasattr(collab_patterns, "knowledge_risk")
            else "N/A"
        )

        return [
            "",
            f"{self._get_emoji('team')} {Fore.MAGENTA}Team Collaboration:{Style.RESET_ALL}",
            f"  • Team connectivity: {getattr(collab_patterns, 'team_connectivity', 'N/A'):.1%}",
            f"  • Knowledge risk: {knowledge_risk}",
        ]

    def _format_code_quality_section(self, analytics: dict[str, Any]) -> list[str]:
        """Format the code quality analytics section."""

        quality = None
        if "quality" in analytics:
            quality = analytics["quality"]
        elif hasattr(analytics, "quality"):
            quality = getattr(analytics, "quality", None)

        if quality is not None:
            return [
                "",
                f"{self._get_emoji('quality')} {Fore.MAGENTA}Code Quality:{Style.RESET_ALL}",
                f"  • Maintainability: {getattr(quality, 'maintainability_index', 'N/A')}",
                f"  • Test coverage: {getattr(quality, 'test_coverage', 'N/A')}%",
            ]
        return []

    def _format_risk_assessment_section(self, analytics: dict[str, Any]) -> list[str]:
        """Format the risk assessment analytics section."""

        risk = None
        if "risk" in analytics:
            risk = analytics["risk"]
        elif hasattr(analytics, "risk"):
            risk = getattr(analytics, "risk", None)

        if risk is not None:
            risk_score = getattr(risk, "risk_score", "N/A")
            return [
                "",
                f"{self._get_emoji('risk')} {Fore.MAGENTA}Risk Assessment:{Style.RESET_ALL}",
                (
                    f"  • Overall risk: {risk_score}/10"
                    if risk_score != "N/A"
                    else "  • Overall risk: N/A"
                ),
                (
                    f"  • Hotspots: {len(getattr(risk, 'hotspots', []))} files"
                    if isinstance(getattr(risk, "hotspots", []), list)
                    else "  • Hotspots: N/A"
                ),
            ]
        return []

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with extended details."""
        output = self._format_basic_stats(stats)

        # Get analytics data
        analytics = self._get_analytics_data(stats)

        # Add analytics sections
        output.extend(self._format_time_analytics_section(analytics))
        output.extend(self._format_team_collaboration_section(analytics))
        output.extend(self._format_code_quality_section(analytics))
        output.extend(self._format_risk_assessment_section(analytics))

        # Add other sections
        output.extend(self._format_authors_section(stats))
        output.extend(self._format_daily_activity_section(stats))
        output.extend(self._format_file_types_section(stats))
        output.extend(self._format_largest_file_changes_section(stats))

        return "\n".join(output)

    def _get_author_contribution_stats(
        self,
        authors: dict[str, int],
        total_commits: int,
    ) -> list[str]:
        """Format author contribution statistics."""
        return [
            f"  {author}: {count} commits ({count / total_commits:.1%})"
            for author, count in sorted(
                authors.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        ]

    def _get_file_type_breakdown_from_commits(
        self, commits: list[CommitStats]
    ) -> dict[str, dict[str, int]]:
        """Calculate file type breakdown from commits.

        Args:
            commits: List of CommitStats objects to analyze

        Returns:
            Dictionary mapping file extensions to their statistics
        """
        file_types: dict[str, dict[str, int]] = defaultdict(
            lambda: {"count": 0, "added": 0, "deleted": 0}
        )

        for commit in commits:
            for file_stat in commit.files:
                # Extract file extension
                path_parts = file_stat.path.split(".")
                if len(path_parts) > 1:
                    ext = "." + path_parts[-1]
                else:
                    ext = "no extension"

                file_types[ext]["count"] += 1
                file_types[ext]["added"] += file_stat.lines_added
                file_types[ext]["deleted"] += file_stat.lines_deleted

        return dict(file_types)

    def _get_daily_activity_stats(self, commits: list[CommitStats]) -> list[str]:
        """Format daily activity statistics.

        Args:
            commits: List of CommitStats objects to analyze

        Returns:
            List of formatted strings showing daily commit activity
        """
        if not commits:
            return ["  No commits in the specified range"]

        daily_activity: dict[str, int] = defaultdict(int)
        for commit in commits:
            day = commit.date.strftime("%Y-%m-%d")
            daily_activity[day] += 1

        return [
            f"  {day}: {count} commit{'s' if count != 1 else ''}"
            for day, count in sorted(daily_activity.items())
        ]

    def _get_largest_file_changes(self, commits: list[CommitStats]) -> list[tuple[str, int]]:
        """Calculate the largest file changes by summing additions + deletions per file.

        Args:
            commits: List of CommitStats objects to analyze

        Returns:
            List of tuples (file_path, total_changes) sorted by total_changes descending
        """
        file_changes: dict[str, int] = defaultdict(int)

        for commit in commits:
            for file_stat in commit.files:
                file_changes[file_stat.path] += file_stat.lines_added + file_stat.lines_deleted

        # Sort by total changes descending and return top 5
        sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
        return sorted_files[:5]

    def _format_largest_file_changes_section(self, stats: RangeStats) -> list[str]:
        """Format the largest file changes section."""
        if not stats.commits:
            return []

        largest_changes = self._get_largest_file_changes(stats.commits)

        if not largest_changes:
            return []

        output = [
            "",
            f"{self._get_emoji('added')} {Fore.MAGENTA}Largest File Changes:{Style.RESET_ALL}",
        ]

        for file_path, changes in largest_changes:
            output.append(f"  • {file_path}: {changes:,} lines changed")

        return output
