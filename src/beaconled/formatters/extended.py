"""Extended output formatter with additional analytics."""

from collections import defaultdict

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

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with extended details."""
        range_net_change = self._format_net_change(
            stats.total_lines_added,
            stats.total_lines_deleted,
        )
        output = [
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

        # Get analytics data - either from a single 'analytics' attribute, individual attributes,
        # or by calling our own analytics engine
        analytics = getattr(stats, "analytics", None)
        if analytics is None:
            # Check for individual analytics attributes
            analytics = {}
            if hasattr(stats, "time"):
                analytics["time"] = stats.time
            if hasattr(stats, "collaboration"):
                analytics["collaboration"] = stats.collaboration
            if hasattr(stats, "quality"):
                analytics["quality"] = stats.quality
            if hasattr(stats, "risk"):
                analytics["risk"] = stats.risk

            # If we still don't have analytics data, call our own analytics engine
            if not analytics:
                analytics_result = self.analytics_engine.analyze(stats)
                # Handle case where analytics_result might be an object instead of dict
                if hasattr(analytics_result, "__dict__"):
                    # Convert object to dictionary
                    analytics = {}
                    for key in ["time", "collaboration", "quality", "risk"]:
                        if hasattr(analytics_result, key):
                            analytics[key] = getattr(analytics_result, key)
                else:
                    analytics = analytics_result

        # Add Time-Based Analytics
        if isinstance(analytics, dict) and "time" in analytics and analytics["time"] is not None:
            time_analytics = analytics["time"]
            output.extend([
                "",
                f"{self._get_emoji('time')} {Fore.MAGENTA}Time-Based Analytics:{Style.RESET_ALL}",
                f"  • Velocity: {time_analytics.velocity_trends.weekly_average:.1f} commits/week",
                f"  • Peak day: {time_analytics.activity_heatmap.peak_day}",
                f"  • Bus factor: {time_analytics.bus_factor.factor}",
            ])

        # Add Team Collaboration Analysis
        if (
            isinstance(analytics, dict)
            and "collaboration" in analytics
            and analytics["collaboration"] is not None
        ):
            collab = analytics["collaboration"]
            collab_patterns = getattr(collab, "collaboration_patterns", None)
            knowledge_risk = (
                collab_patterns.knowledge_risk
                if collab_patterns and hasattr(collab_patterns, "knowledge_risk")
                else "N/A"
            )

            output.extend([
                "",
                f"{self._get_emoji('team')} {Fore.MAGENTA}Team Collaboration:{Style.RESET_ALL}",
                f"  • Team connectivity: {getattr(collab_patterns, 'team_connectivity', 'N/A'):.1%}",
                f"  • Knowledge risk: {knowledge_risk}",
            ])

        # Add Code Quality Insights
        if isinstance(analytics, dict):
            quality = None
            if "quality" in analytics:
                quality = analytics["quality"]
            elif hasattr(analytics, "quality"):
                quality = getattr(analytics, "quality", None)

            if quality is not None:
                output.extend([
                    "",
                    f"{self._get_emoji('quality')} {Fore.MAGENTA}Code Quality:{Style.RESET_ALL}",
                    f"  • Maintainability: {getattr(quality, 'maintainability_index', 'N/A')}",
                    f"  • Test coverage: {getattr(quality, 'test_coverage', 'N/A')}%",
                ])

        # Add Risk Assessment
        if isinstance(analytics, dict):
            risk = None
            if "risk" in analytics:
                risk = analytics["risk"]
            elif hasattr(analytics, "risk"):
                risk = getattr(analytics, "risk", None)

            if risk is not None:
                risk_score = getattr(risk, "risk_score", "N/A")
                output.extend([
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
                ])

        # Add authors section
        if stats.authors:
            output.extend(
                [
                    "",
                    f"{self._get_emoji('contributors')} "
                    f"{Fore.MAGENTA}Contributors:{Style.RESET_ALL}",
                    *[
                        self._format_author_stats(a, c)
                        for a, c in sorted(
                            stats.authors.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                    ],
                ],
            )

        # Add daily activity if available
        if hasattr(stats, "commits_by_day"):
            output.extend(
                [
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
                ],
            )

        # Add file type breakdown if available
        file_types = {}
        if stats.commits:
            file_types = self._get_file_type_breakdown_from_commits(stats.commits)
        elif hasattr(stats, "file_types") and stats.file_types:
            file_types = stats.file_types

        if file_types:
            output.extend(
                [
                    "",
                    f"{self._get_emoji('breakdown')} "
                    f"{Fore.MAGENTA}File type breakdown:{Style.RESET_ALL}",
                    *[
                        self._format_file_type_line(ext, counts)
                        for ext, counts in sorted(file_types.items())
                    ],
                ],
            )
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
