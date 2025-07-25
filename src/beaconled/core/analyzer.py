"""Git repository analyzer."""

import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
import git
from pathlib import Path
from pathlib import Path

from .models import CommitStats, FileStats, RangeStats


class GitAnalyzer:
    """Analyzes git repository statistics."""

    def __init__(self, repo_path: str = "."):
        """Initialize analyzer with repository path."""
        self.repo_path = self._validate_repo_path(repo_path)

    def _validate_repo_path(self, repo_path: str) -> str:
        """Validate and sanitize repository path.
        
        Args:
            repo_path: Path to the git repository
            
        Returns:
            str: Absolute path to the validated repository
            
        Raises:
            ValueError: If the path is invalid, not a directory, or not a git repository
        """
        try:
            path = Path(repo_path).resolve()
            
            # Ensure path exists and is a directory
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Repository path does not exist: {repo_path}")
            
            # Ensure it's within allowed boundaries (prevent directory traversal)
            cwd = Path.cwd().resolve()
            if not str(path).startswith(str(cwd)):
                raise ValueError("Repository path must be within current working directory")
            
            # Check if it's actually a git repository
            git_dir = path / '.git'
            if not git_dir.exists():
                raise ValueError(f"Not a git repository: {repo_path}")
                
            return str(path)
        except Exception as e:
            raise ValueError(f"Invalid repository path: {e}")

    def _parse_git_date(self, date_str: str) -> datetime:
        """Parse a date string from git log into a timezone-aware datetime.
        
        Handles git log's default date format: "YYYY-MM-DD HH:MM:SS +ZZZZ"
        and converts it to a timezone-aware datetime object.
        
        Args:
            date_str: Date string from git log
            
        Returns:
            datetime: Timezone-aware datetime object
            
        Note:
            If parsing fails, falls back to the current time in UTC and logs a warning.
        """
        try:
            # Try parsing with space separator (git log format)
            if ' ' in date_str:
                # Format: "YYYY-MM-DD HH:MM:SS +ZZZZ" -> "YYYY-MM-DDTHH:MM:SS+ZZ:ZZ"
                date_parts = date_str.split()
                if len(date_parts) >= 2:
                    # Reconstruct in ISO 8601 format with timezone
                    tz = date_parts[-1]
                    if len(tz) == 5:  # Handle +0800 -> +08:00
                        tz = f"{tz[:3]}:{tz[3:]}"
                    date_str = f"{date_parts[0]}T{date_parts[1]}{tz}"
            
            return datetime.fromisoformat(date_str)
        except ValueError as e:
            # Fallback to current time if parsing fails
            print(f"Warning: Failed to parse date '{date_str}': {e}")
            return datetime.now(timezone.utc)

    def get_commit_stats(self, commit_hash: str = "HEAD") -> CommitStats:
        """Get statistics for a single commit.
        
        This method retrieves commit information using GitPython, which provides
        a more Pythonic interface to git repositories compared to subprocess.
        
        Args:
            commit_hash: Commit hash to retrieve statistics for (default: "HEAD")
        
        Returns:
            CommitStats: Statistics for the specified commit
            
        Raises:
            git.GitCommandError: If there's an error executing git commands
            ValueError: If the commit hash is invalid
        """
        if not self._is_valid_commit_hash(commit_hash):
            raise ValueError(f"Invalid commit hash: {commit_hash}")
            
        try:
            # Initialize the git repository
            repo = git.Repo(self.repo_path)
            
            # Get the commit object
            commit = repo.commit(commit_hash)
            
            # Get commit details
            commit_hash = commit.hexsha
            author = f"{commit.author.name} <{commit.author.email}>"
            date = commit.authored_datetime or datetime.now(timezone.utc)
            message = commit.message.split('\n')[0]  # Get first line of commit message
            
            # Initialize file stats
            files = []
            total_added = 0
            total_deleted = 0
            
            # Get diff stats for this commit
            if commit.parents:
                # Compare with first parent (most common case)
                diff_index = commit.parents[0].diff(commit, create_patch=False)
            else:
                # For initial commit, compare with empty tree
                diff_index = commit.diff(git.NULL_TREE, create_patch=False)
            
            # Process each changed file in the diff
            for diff in diff_index:
                # Get the path (use b_path for new files, a_path for deleted files)
                path = diff.b_path if diff.b_path else diff.a_path
                
                # Get line statistics - handle both bytes and string diff outputs
                diff_content = diff.diff
                if isinstance(diff_content, bytes):
                    added = diff_content.count(b'\n+') - 1  # Subtract 1 for the header line
                    deleted = diff_content.count(b'\n-') - 1  # Subtract 1 for the header line
                else:
                    # Convert to bytes if it's a string
                    if isinstance(diff_content, str):
                        diff_content = diff_content.encode('utf-8')
                    added = diff_content.count(b'\n+') - 1
                    deleted = diff_content.count(b'\n-') - 1
                
                # Ensure non-negative values
                added = max(0, added)
                deleted = max(0, deleted)
                
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
            
        except git.GitCommandError as e:
            raise RuntimeError(f"Git command failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error getting commit stats: {e}")

    def get_range_analytics(
        self, since: str, until: str = "HEAD"
    ) -> RangeStats:
        """Get analytics for a range of commits.
        
        Args:
            since: Start date for the range (git date format)
            until: End date for the range (default: "HEAD")
            
        Returns:
            RangeStats: Statistics for the specified commit range
            
        Raises:
            git.GitCommandError: If there's an error executing git commands
            ValueError: If the date format is invalid
        """
        # Validate date parameters
        if not self._is_valid_date_string(since):
            raise ValueError("Invalid since date format")
        if not self._is_valid_date_string(until):
            raise ValueError("Invalid until date format")
            
        try:
            # Initialize the git repository
            repo = git.Repo(self.repo_path)
            
            # Get all commits since the specified date
            # We need to use git rev-list directly to handle date-based ranges
            commit_hashes = repo.git.rev_list(
                '--since', since,
                until,
                '--reverse'
            ).splitlines()
            
            # Get commit objects for each hash
            commits = [repo.commit(hash) for hash in commit_hashes if hash]
            
            commit_stats_list = []
            authors = {}
            total_files = 0
            total_added = 0
            total_deleted = 0
            
            for commit in commits:
                try:
                    # Get stats for this commit
                    commit_stats = self.get_commit_stats(commit.hexsha)
                    commit_stats_list.append(commit_stats)
                    
                    # Update author stats
                    author = f"{commit.author.name} <{commit.author.email}>"
                    authors[author] = authors.get(author, 0) + 1
                    
                    # Update totals
                    total_files += commit_stats.files_changed
                    total_added += commit_stats.lines_added
                    total_deleted += commit_stats.lines_deleted
                    
                except Exception as e:
                    # Log the error but continue with other commits
                    print(f"Warning: Could not process commit {commit.hexsha}: {e}")
                    continue

            # Get date range
            start_date = commit_stats_list[0].date if commit_stats_list else datetime.now(timezone.utc)
            end_date = commit_stats_list[-1].date if commit_stats_list else datetime.now(timezone.utc)
            
            return RangeStats(
                start_date=start_date,
                end_date=end_date,
                total_commits=len(commit_stats_list),
                total_files_changed=total_files,
                total_lines_added=total_added,
                total_lines_deleted=total_deleted,
                commits=commit_stats_list,
                authors=authors,
            )
            
        except git.GitCommandError as e:
            raise RuntimeError(f"Git command failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error getting range analytics: {e}")

    def _is_valid_commit_hash(self, commit_hash: str) -> bool:
        """Validate commit hash format to prevent injection."""
        import re
        
        # Reject empty or overly long inputs
        if not commit_hash or len(commit_hash) > 100:
            return False
            
        # Allow HEAD, branch names, and valid commit hashes
        if commit_hash in {"HEAD", "HEAD~", "HEAD^"}:
            return True
        # Allow branch names (alphanumeric, hyphens, underscores, slashes, dots)
        if re.match(r'^[a-zA-Z0-9\-_/.]+$', commit_hash):
            return True
        # Allow full commit hashes (40 hex chars)
        if re.match(r'^[a-fA-F0-9]{40}$', commit_hash):
            return True
        # Allow short commit hashes (7-40 hex chars)
        if re.match(r'^[a-fA-F0-9]{7,40}$', commit_hash):
            return True
        return False

    def _is_valid_date_string(self, date_str: str) -> bool:
        """Validate date string format to prevent injection."""
        import re
        
        # Reject empty or overly long inputs
        if not date_str or len(date_str) > 50:
            return False
            
        # Allow relative dates (e.g., "1 week ago", "2 days ago")
        if re.match(r'^\d+\s+(second|minute|hour|day|week|month|year)s?\s+ago$', date_str, re.IGNORECASE):
            return True
        # Allow ISO dates (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return True
        # Allow ISO datetime (YYYY-MM-DD HH:MM:SS)
        if re.match(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$', date_str):
            return True
        # Allow HEAD
        if date_str == "HEAD":
            return True
        return False
