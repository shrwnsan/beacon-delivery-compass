"""Git repository analyzer."""

import subprocess
import json
from datetime import datetime
from typing import List, Dict
from .models import CommitStats, RangeStats, FileStats


class GitAnalyzer:
    """Analyzes git repository statistics."""

    def __init__(self, repo_path: str = "."):
        """Initialize analyzer with repository path."""
        self.repo_path = repo_path

    def get_commit_stats(self, commit_hash: str = "HEAD") -> CommitStats:
        """Get statistics for a single commit."""
        # Get commit info
        cmd = [
            "git",
            "-C",
            self.repo_path,
            "show",
            "--format=%H|%an|%ad|%s",
            "--date=iso",
            "--numstat",
            commit_hash,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        lines = result.stdout.strip().split("\n")
        header = lines[0].split("|")

        commit_hash = header[0]
        author = header[1]
        date = datetime.fromisoformat(header[2].replace(" ", "T"))
        message = header[3]

        files = []
        total_added = 0
        total_deleted = 0

        for line in lines[2:]:  # Skip header and empty line
            if line.strip():
                parts = line.split("\t")
                if len(parts) >= 3:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    deleted = int(parts[1]) if parts[1] != "-" else 0
                    path = parts[2]

                    files.append(
                        FileStats(
                            path=path,
                            lines_added=added,
                            lines_deleted=deleted,
                            lines_changed=added + deleted,
                        )
                    )

                    total_added += added
                    total_deleted += deleted

        return CommitStats(
            hash=commit_hash,
            author=author,
            date=date,
            message=message,
            files_changed=len(files),
            lines_added=total_added,
            lines_deleted=total_deleted,
            files=files,
        )

    def get_range_analytics(self, since: str, until: str = "HEAD") -> RangeStats:
        """Get analytics for a range of commits."""
        # Get commit list
        cmd = [
            "git",
            "-C",
            self.repo_path,
            "log",
            f"--since={since}",
            f"--until={until}",
            "--format=%H",
            "--reverse",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        commit_hashes = [
            line.strip() for line in result.stdout.strip().split("\n") if line.strip()
        ]

        commits = []
        authors = {}
        total_files = 0
        total_added = 0
        total_deleted = 0

        for commit_hash in commit_hashes:
            try:
                commit_stats = self.get_commit_stats(commit_hash)
                commits.append(commit_stats)

                # Update author stats
                authors[commit_stats.author] = authors.get(commit_stats.author, 0) + 1

                # Update totals
                total_files += commit_stats.files_changed
                total_added += commit_stats.lines_added
                total_deleted += commit_stats.lines_deleted

            except subprocess.CalledProcessError:
                continue  # Skip problematic commits

        start_date = commits[0].date if commits else datetime.now()
        end_date = commits[-1].date if commits else datetime.now()

        return RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=len(commits),
            total_files_changed=total_files,
            total_lines_added=total_added,
            total_lines_deleted=total_deleted,
            commits=commits,
            authors=authors,
        )
