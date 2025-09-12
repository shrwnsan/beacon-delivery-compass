"""Extended output formatter with additional analytics."""

import subprocess
from collections import defaultdict
from typing import Any

import git
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
    - File lifecycle tracking
    """

    def __init__(self, *, no_emoji: bool = False, repo_path: str = "."):
        """Initializes the formatter."""
        super().__init__()
        # Disable emojis in environments that don't support them
        self.no_emoji = no_emoji or not self._supports_emoji()
        self.analytics_engine = AnalyticsEngine()
        self.repo_path = repo_path

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
            "lifecycle": "🔄",
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

        # Add file lifecycle section if we have date range information
        if hasattr(stats, "start_date") and hasattr(stats, "end_date"):
            # Add frequently changed files section
            try:
                # Get frequently changed files in the last 30 days
                since = "30 days ago"
                frequent_files = self._get_frequently_changed_files(since)
                if frequent_files:
                    output.append("\n" + self._format_frequent_files(frequent_files))
            except Exception as e:
                output.append(f"\n{Fore.RED}Error analyzing file change frequency: {e}{Style.RESET_ALL}")

            # Convert dates to format expected by git
            since = stats.start_date.isoformat()
            until = stats.end_date.isoformat()
            lifecycle_stats = self._get_file_lifecycle_stats(since, until)
            output.extend(self._format_file_lifecycle(lifecycle_stats))

        # Add other sections
        output.extend(self._format_authors_section(stats))
        output.extend(self._format_daily_activity_section(stats))
        output.extend(self._format_file_types_section(stats))
        output.extend(self._format_largest_file_changes_section(stats))

        return "\n".join(output)

    def _get_file_lifecycle_stats(self, since: str, until: str) -> dict[str, int]:
        """Get file lifecycle statistics from git log.

        Args:
            since: Start date for analysis
            until: End date for analysis

        Returns:
            Dictionary with file lifecycle counts (added, modified, deleted, renamed)
        """
        # Initialize counts
        stats = {
            "added": 0,
            "modified": 0,
            "deleted": 0,
            "renamed": 0,
        }

        try:
            # Run git log with name-status to get file operations
            repo = git.Repo(self.repo_path)
            log_output = repo.git.log(
                "--name-status",
                "--pretty=format:",
                f"--since={since}",
                f"--until={until}",
            )

            # Parse the output to count file operations
            stats = self._parse_git_log_output(log_output)
        except Exception:
            # If we can't get git info, return zeros
            pass

        return stats

    def _parse_git_log_output(self, log_output: str) -> dict[str, int]:
        """Parse git log output to count file operations.

        Args:
            log_output: Raw output from git log command

        Returns:
            Dictionary with file lifecycle counts
        """
        stats = {"added": 0, "modified": 0, "deleted": 0, "renamed": 0}
        files_seen: set[str] = set()
        lines = log_output.splitlines()

        for line in lines:
            if not line.strip():
                continue

            parts = line.split("\t")
            if not parts:
                continue

            status = parts[0]
            file_path = parts[1] if len(parts) > 1 else None

            if not file_path:
                continue

            # Handle different status codes
            if status == "A":  # Added
                self._handle_added_file(stats, files_seen, file_path)
            elif status == "M":  # Modified
                self._handle_modified_file(stats, files_seen, file_path)
            elif status == "D":  # Deleted
                self._handle_deleted_file(stats, files_seen, file_path)
            elif status.startswith("R"):  # Renamed
                new_path = parts[2] if len(parts) > 2 else file_path
                self._handle_renamed_file(stats, files_seen, new_path)

        return stats

    def _handle_added_file(
        self, stats: dict[str, int], files_seen: set[str], file_path: str
    ) -> None:
        """Handle added file in git log."""
        if file_path not in files_seen:
            stats["added"] += 1
            files_seen.add(file_path)

    def _handle_modified_file(
        self, stats: dict[str, int], files_seen: set[str], file_path: str
    ) -> None:
        """Handle modified file in git log."""
        if file_path not in files_seen:
            stats["modified"] += 1
            files_seen.add(file_path)

    def _handle_deleted_file(
        self, stats: dict[str, int], files_seen: set[str], file_path: str
    ) -> None:
        """Handle deleted file in git log."""
        if file_path not in files_seen:
            stats["deleted"] += 1
            files_seen.add(file_path)

    def _handle_renamed_file(
        self, stats: dict[str, int], files_seen: set[str], new_path: str
    ) -> None:
        """Handle renamed file in git log."""
        if new_path not in files_seen:
            stats["renamed"] += 1
            files_seen.add(new_path)

    def _format_file_lifecycle(self, stats: dict[str, int]) -> list[str]:
        """Format file lifecycle statistics for display.

        Args:
            stats: Dictionary with file lifecycle counts

        Returns:
            List of formatted strings for display
        """
        output = []

        # Only show the section if we have any activity
        if any(count > 0 for count in stats.values()):
            lifecycle_header = (
                f"{self._get_emoji('lifecycle')} "
                f"{Fore.MAGENTA}File Lifecycle Activity:{Style.RESET_ALL}"
            )
            output.append(lifecycle_header)

            # Only show non-zero categories
            if stats["added"] > 0:
                output.append(f"  • Files Added: {stats['added']} new files")
            if stats["modified"] > 0:
                output.append(f"  • Files Modified: {stats['modified']} existing files")
            if stats["deleted"] > 0:
                output.append(f"  • Files Deleted: {stats['deleted']} files removed")
            if stats["renamed"] > 0:
                output.append(f"  • Files Renamed: {stats['renamed']} files moved")

        return output

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
        file_changes: dict[str, int] = {}
        for commit in commits:
            if commit.files:
                for file in commit.files:
                    total = file.added + file.deleted
                    if file.filename in file_changes:
                        file_changes[file.filename] += total
                    else:
                        file_changes[file.filename] = total

        # Sort by total changes in descending order
        return sorted(file_changes.items(), key=lambda x: x[1], reverse=True)

    def _format_largest_file_changes_section(self, stats: RangeStats) -> list[str]:
        """Format the largest file changes section."""
        output = [
            f"\n{self._get_emoji('breakdown')} {Fore.MAGENTA}Largest File Changes:{Style.RESET_ALL}"
        ]

        if not hasattr(stats, 'commits') or not stats.commits:
            output.append("  No commit data available")
            return output

        largest_changes = self._get_largest_file_changes(stats.commits)
        if not largest_changes:
            output.append("  No file changes detected")
            return output

        for i, (filename, changes) in enumerate(largest_changes[:5], 1):
            output.append(f"  {i}. {filename}: {changes:,} lines changed")

        return output

    def _get_frequently_changed_files(self, since: str) -> dict[str, int]:
        """Get files ordered by change frequency.

        Args:
            since: Time period to analyze (e.g., "30 days ago")

        Returns:
            Dictionary mapping file paths to change frequency
        """
        from collections import defaultdict

        file_changes: dict[str, int] = defaultdict(int)

        try:
            # Use GitPython to get file change counts
            repo = git.Repo()

            # Get commits since the specified time
            commits = list(repo.iter_commits(since=since))

            # Count file changes across all commits
            for commit in commits:
                # Get the files changed in this commit
                for file_obj in commit.stats.files:
                    file_path = str(file_obj)
                    file_changes[file_path] += 1

            # Sort by frequency (descending) and return top 5
            sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_files[:5])

        except Exception:
            # Handle any errors gracefully
=======
        import os
        from collections import defaultdict

        file_changes: dict[str, int] = defaultdict(int)
        
        try:
            # Use git log to get file change counts
            # Format: --name-only shows only file names, one per line
            # --since limits to commits in the specified time range
            cmd = [
                "git",
                "log",
                "--name-only",
                f"--since={since}",
                "--pretty=format:"
            ]
            
            # Execute git command in the repository directory
            result = subprocess.run(
                cmd,
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Count occurrences of each file
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():  # Skip empty lines
                    file_changes[line.strip()] += 1
            
            # Sort by frequency (descending) and return top 5
            sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_files[:5])
            
        except subprocess.CalledProcessError:
            # Handle git errors gracefully
            return {}
        except Exception:
            # Handle any other errors gracefully
>>>>>>> 7e46844 (feat: Implement frequently changed files highlighting in extended format)
            return {}

    def _format_frequent_files(self, frequent_files: dict[str, int]) -> list[str]:
        """Format frequently changed files section.

        Args:
            frequent_files: Dictionary mapping file paths to change frequency

        Returns:
            List of formatted strings for the output
        """
        if not frequent_files:
            return []

        output = [
            "",
            f"{self._get_emoji('activity')} {Fore.MAGENTA}Most Frequently Changed "
            f"(last 30 days):{Style.RESET_ALL}",
        ]
        for file_path, count in frequent_files.items():
            output.append(f"  • {file_path}: {count} changes")

<<<<<<< HEAD
        return output
=======
        return output
>>>>>>> 7e46844 (feat: Implement frequently changed files highlighting in extended format)
