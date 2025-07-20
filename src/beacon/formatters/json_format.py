"""JSON output formatter."""

import json
from datetime import datetime
from ..core.models import CommitStats, RangeStats


class JSONFormatter:
    """JSON formatter for Beacon delivery analytics output."""

    def _serialize_datetime(self, obj):
        """JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as JSON."""
        data = {
            "hash": stats.hash,
            "author": stats.author,
            "date": stats.date,
            "message": stats.message,
            "files_changed": stats.files_changed,
            "lines_added": stats.lines_added,
            "lines_deleted": stats.lines_deleted,
            "net_change": stats.lines_added - stats.lines_deleted,
            "files": [
                {
                    "path": f.path,
                    "lines_added": f.lines_added,
                    "lines_deleted": f.lines_deleted,
                    "lines_changed": f.lines_changed,
                }
                for f in stats.files
            ],
        }
        return json.dumps(data, indent=2, default=self._serialize_datetime)

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as JSON."""
        data = {
            "start_date": stats.start_date,
            "end_date": stats.end_date,
            "total_commits": stats.total_commits,
            "total_files_changed": stats.total_files_changed,
            "total_lines_added": stats.total_lines_added,
            "total_lines_deleted": stats.total_lines_deleted,
            "net_change": stats.total_lines_added - stats.total_lines_deleted,
            "authors": stats.authors,
            "commits": [
                {
                    "hash": c.hash,
                    "author": c.author,
                    "date": c.date,
                    "message": c.message,
                    "files_changed": c.files_changed,
                    "lines_added": c.lines_added,
                    "lines_deleted": c.lines_deleted,
                }
                for c in stats.commits
            ],
        }
        return json.dumps(data, indent=2, default=self._serialize_datetime)
