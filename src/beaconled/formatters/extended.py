"""Extended output formatter with additional analytics."""

from collections import defaultdict
from colorama import Fore, Style
from typing import Dict, List

from .base_formatter import BaseFormatter
from ..core.models import CommitStats, RangeStats

class ExtendedFormatter(BaseFormatter):
    """Extended text formatter with additional analytics.
    
    Extends the base formatter with additional statistics including:
    - File type breakdown
    - Author contribution details
    - Daily activity patterns
    """

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics with extended details."""
        output = [
            f"{Fore.CYAN}Commit:{Style.RESET_ALL} {stats.hash[:8]}",
            f"{Fore.CYAN}Author:{Style.RESET_ALL} {stats.author}",
            f"{Fore.CYAN}Date:{Style.RESET_ALL} {self._format_date(stats.date)}",
            f"{Fore.CYAN}Message:{Style.RESET_ALL} {stats.message}",
            "",
            f"{Fore.YELLOW}Files changed:{Style.RESET_ALL} {stats.files_changed}",
            f"{Fore.GREEN}Lines added:{Style.RESET_ALL} {stats.lines_added}",
            f"{Fore.RED}Lines deleted:{Style.RESET_ALL} {stats.lines_deleted}",
            f"{Fore.YELLOW}Net change:{Style.RESET_ALL} {self._format_net_change(stats.lines_added, stats.lines_deleted)}"
        ]

        if stats.files:
            # Add file changes
            output.extend([
                "",
                f"{Fore.MAGENTA}File changes:{Style.RESET_ALL}",
                *[self._format_file_stats(f) for f in stats.files]
            ])
            
            # Add file type breakdown (match test expectation wording)
            file_types = self._get_file_type_breakdown(stats.files)
            output.extend([
                "",
                f"{Fore.MAGENTA}File type breakdown:{Style.RESET_ALL}",
                *[f"  {ext}: {counts['count']} files, +{counts['added']}/-{counts['deleted']}"
                  for ext, counts in sorted(file_types.items())]
            ])

        return "\n".join(output)

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with extended details."""
        output = [
            f"{Fore.CYAN}Range Analysis:{Style.RESET_ALL} "
            f"{self._format_date(stats.start_date).split()[0]} to "
            f"{self._format_date(stats.end_date).split()[0]}",
            "",
            f"{Fore.YELLOW}Total commits:{Style.RESET_ALL} {stats.total_commits}",
            f"{Fore.YELLOW}Total files changed:{Style.RESET_ALL} {stats.total_files_changed}",
            f"{Fore.GREEN}Total lines added:{Style.RESET_ALL} {stats.total_lines_added}",
            f"{Fore.RED}Total lines deleted:{Style.RESET_ALL} {stats.total_lines_deleted}",
            f"{Fore.YELLOW}Net change:{Style.RESET_ALL} "
            f"{self._format_net_change(stats.total_lines_added, stats.total_lines_deleted)}"
        ]

        # Add authors section
        if stats.authors:
            output.extend([
                "",
                f"{Fore.MAGENTA}Contributors:{Style.RESET_ALL}",
                *[self._format_author_stats(a, c) for a, c in 
                  sorted(stats.authors.items(), key=lambda x: x[1], reverse=True)]
            ])

        # Add daily activity if available
        if hasattr(stats, 'commits_by_day'):
            output.extend([
                "",
                f"{Fore.MAGENTA}Temporal Analysis - Daily Activity Timeline:{Style.RESET_ALL}",
                *[f"  {day}: {count} commit{'s' if count != 1 else ''}"
                  for day, count in sorted(stats.commits_by_day.items())]
            ])
        
        # Add file type breakdown if available
        if hasattr(stats, 'file_types'):
            output.extend([
                "",
                f"{Fore.MAGENTA}File type breakdown:{Style.RESET_ALL}",
                *[f"  {ext}: {counts['count']} files, +{counts['added']}/-{counts['deleted']}"
                  for ext, counts in sorted(stats.file_types.items())]
            ])

        return "\n".join(output)
    def _get_author_contribution_stats(self, authors: Dict[str, int], total_commits: int) -> List[str]:
        """Format author contribution statistics."""
        return [
            f"  {author}: {count} commits ({count/total_commits:.1%})"
            for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)
        ]
        
    def _get_daily_activity_stats(self, commits: List[CommitStats]) -> List[str]:
        """Format daily activity statistics.
        
        Args:
            commits: List of CommitStats objects to analyze
            
        Returns:
            List of formatted strings showing daily commit activity
        """
        if not commits:
            return ["  No commits in the specified range"]
            
        daily_activity: Dict[str, int] = defaultdict(int)
        for commit in commits:
            day = commit.date.strftime("%Y-%m-%d")
            daily_activity[day] += 1
            
        return [
            f"  {day}: {count} commit{'s' if count != 1 else ''}"
            for day, count in sorted(daily_activity.items())
        ]
