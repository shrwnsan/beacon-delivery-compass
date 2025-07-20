"""Extended output formatter."""

from ..core.models import CommitStats, RangeStats
from .standard import StandardFormatter


class ExtendedFormatter(StandardFormatter):
    """Extended formatter with additional details."""
    
    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics with extended details."""
        output = super().format_commit_stats(stats)
        
        if stats.files:
            # Add file type analysis
            file_types = {}
            for file_stat in stats.files:
                ext = file_stat.path.split('.')[-1] if '.' in file_stat.path else 'no-ext'
                if ext not in file_types:
                    file_types[ext] = {'count': 0, 'added': 0, 'deleted': 0}
                file_types[ext]['count'] += 1
                file_types[ext]['added'] += file_stat.lines_added
                file_types[ext]['deleted'] += file_stat.lines_deleted
            
            output += "\n\nFile type breakdown:"
            for ext, data in sorted(file_types.items()):
                output += f"\n  .{ext}: {data['count']} files, +{data['added']} -{data['deleted']}"
        
        return output
    
    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with extended details."""
        output = super().format_range_stats(stats)
        
        if stats.commits:
            # Add daily activity
            daily_activity = {}
            for commit in stats.commits:
                day = commit.date.strftime('%Y-%m-%d')
                if day not in daily_activity:
                    daily_activity[day] = 0
                daily_activity[day] += 1
            
            output += "\n\nDaily activity:"
            for day, count in sorted(daily_activity.items()):
                output += f"\n  {day}: {count} commits"
        
        return output