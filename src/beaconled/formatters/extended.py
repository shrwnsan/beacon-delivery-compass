"""Extended output formatter with additional analytics."""

from collections import defaultdict

import git
from colorama import Fore, Style

from beaconled.analytics.engine import AnalyticsEngine
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

    def __init__(self, no_emoji=None, repo_path="."):
        """Initialize the formatter.

        Args:
            no_emoji: Whether to disable emoji output
            repo_path: Path to the git repository
        """
        super().__init__()
        # Disable emojis in environments that don't support them
        self.no_emoji = no_emoji if no_emoji is not None else not self._supports_emoji()
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
        }

    def _get_emoji(self, emoji_name):
        """Get emoji if enabled, otherwise return empty string."""
        if self.no_emoji:
            return ""
        return self.EMOJIS.get(emoji_name, "")

    def _get_largest_file_changes(self, commits):
        """Calculate the largest file changes by summing additions + deletions per file.

        Args:
            commits: List of CommitStats objects to analyze

        Returns:
            List of tuples (file_path, total_changes) sorted by total_changes descending
        """
        file_changes = {}
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

    def _format_largest_file_changes_section(self, stats):
        """Format the largest file changes section."""
        output = [
            f"\n{self._get_emoji('breakdown')} {Fore.MAGENTA}Largest File Changes:{Style.RESET_ALL}"
        ]

        if not hasattr(stats, "commits") or not stats.commits:
            output.append("  No commit data available")
            return output

        largest_changes = self._get_largest_file_changes(stats.commits)
        if not largest_changes:
            output.append("  No file changes detected")
            return output

        for i, (filename, changes) in enumerate(largest_changes[:5], 1):
            output.append(f"  {i}. {filename}: {changes:,} lines changed")

        return output

    def _get_frequently_changed_files(self, since):
        """Get files ordered by change frequency within the analysis period.

        Args:
            since: Start of the analysis period in ISO format (e.g., "2025-01-01")

        Returns:
            Dictionary mapping file paths to change frequency, sorted by frequency (descending)
            and limited to the top 5 most frequently changed files.
        """

        file_changes = defaultdict(int)

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
            # Log the error instead of printing
            return {}

    def _format_frequent_files(self, frequent_files):
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

        return output
