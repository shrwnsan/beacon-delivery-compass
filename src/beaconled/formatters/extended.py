"""Extended output formatter with additional analytics."""

from collections import defaultdict

from colorama import Fore, Style

from beaconled.core.models import CommitStats, RangeStats
from beaconled.formatters.base_formatter import BaseFormatter


class ExtendedFormatter(BaseFormatter):
    """Extended text formatter with additional analytics.

    Extends the base formatter with additional statistics including:
    - File type breakdown
    - Author contribution details
    - Daily activity patterns
    """

    def __init__(self, *, no_emoji: bool = False):
        """Initializes the formatter."""
        # Disable emojis in environments that don't support them
        self.no_emoji = no_emoji or not self._supports_emoji()

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
        output.extend(
            [
                "",
                f"{Fore.MAGENTA}File type breakdown:{Style.RESET_ALL}",
            ]
        )
        if file_types:
            output.extend(
                [
                    self._format_file_type_line(ext, counts)
                    for ext, counts in sorted(file_types.items())
                ]
            )
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
        if stats.commits:
            file_types = self._get_file_type_breakdown_from_commits(stats.commits)
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
