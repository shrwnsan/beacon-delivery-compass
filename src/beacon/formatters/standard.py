"""Standard output formatter."""

from ..core.models import CommitStats, RangeStats


class StandardFormatter:
    """Standard text formatter for git analytics output."""
    
    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as standard text."""
        output = []
        output.append(f"Commit: {stats.hash[:8]}")
        output.append(f"Author: {stats.author}")
        output.append(f"Date: {stats.date.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Message: {stats.message}")
        output.append("")
        output.append(f"Files changed: {stats.files_changed}")
        output.append(f"Lines added: {stats.lines_added}")
        output.append(f"Lines deleted: {stats.lines_deleted}")
        output.append(f"Net change: {stats.lines_added - stats.lines_deleted}")
        
        if stats.files:
            output.append("")
            output.append("File changes:")
            for file_stat in stats.files:
                output.append(f"  {file_stat.path}: +{file_stat.lines_added} -{file_stat.lines_deleted}")
        
        return "\n".join(output)
    
    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as standard text."""
        output = []
        output.append(f"Range Analysis: {stats.start_date.strftime('%Y-%m-%d')} to {stats.end_date.strftime('%Y-%m-%d')}")
        output.append("")
        output.append(f"Total commits: {stats.total_commits}")
        output.append(f"Total files changed: {stats.total_files_changed}")
        output.append(f"Total lines added: {stats.total_lines_added}")
        output.append(f"Total lines deleted: {stats.total_lines_deleted}")
        output.append(f"Net change: {stats.total_lines_added - stats.total_lines_deleted}")
        
        if stats.authors:
            output.append("")
            output.append("Contributors:")
            for author, count in sorted(stats.authors.items(), key=lambda x: x[1], reverse=True):
                output.append(f"  {author}: {count} commits")
        
        return "\n".join(output)