"""Git repository analyzer."""

import os
from datetime import datetime, timezone, timedelta
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

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date from relative or absolute format.
        
        Supports:
        - Relative: 1d, 2w, 3m, 1y (days, weeks, months, years)
        - Absolute: YYYY-MM-DD or YYYY-MM-DD HH:MM
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime: Parsed datetime in local timezone
            
        Raises:
            ValueError: If date string format is invalid
        """
        # Handle relative dates
        if len(date_str) > 1 and date_str[-1] in {'d', 'w', 'm', 'y'}:
            now = datetime.now()
            try:
                num = int(date_str[:-1])
                unit = date_str[-1].lower()
                
                if unit == 'd':
                    return now - timedelta(days=num)
                elif unit == 'w':
                    return now - timedelta(weeks=num)
                elif unit == 'm':
                    return now - timedelta(weeks=num*4)  # Approximate
                elif unit == 'y':
                    return now - timedelta(weeks=num*52)  # Approximate
            except (ValueError, IndexError):
                pass  # Fall through to absolute date parsing
        
        # Handle absolute dates
        try:
            # Try with time
            try:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            except ValueError:
                # Try date only
                return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(
                f"Invalid date format: {date_str}. "
                "Use YYYY-MM-DD, YYYY-MM-DD HH:MM, or relative (1d, 2w, 3m, 1y)"
            ) from e
            
    def _parse_git_date(self, date_str: str) -> datetime:
        """Parse a date string from git log into a datetime.
        
        Args:
            date_str: Date string from git log
            
        Returns:
            datetime: Parsed datetime
            
        Note:
            If parsing fails, falls back to the current time.
        """
        try:
            # Handle git's default format: "YYYY-MM-DD HH:MM:SS +ZZZZ"
            if ' ' in date_str and '+' in date_str:
                date_part, tz_part = date_str.rsplit('+', 1)
                return datetime.strptime(date_part.strip(), '%Y-%m-%d %H:%M:%S')
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"Warning: Failed to parse git date '{date_str}': {e}")
            return datetime.now()

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
            
            # Initialize file stats
            files: List[FileStats] = []
            total_additions = 0
            total_deletions = 0
            
            # Get diff stats for this commit
            if commit.parents:
                # Compare with first parent (most common case)
                diff_index = commit.parents[0].diff(commit, create_patch=True)
            else:
                # For initial commit, compare with empty tree
                diff_index = commit.diff(git.NULL_TREE, create_patch=True)
            
            # Process each changed file in the diff
            for diff in diff_index:
                # Skip binary files
                if diff.diff is None:
                    continue
                
                # Parse the diff to count added/removed lines
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
                
                # Get the path (use b_path for new files, a_path for deleted files)
                path = diff.b_path if diff.b_path else diff.a_path
                if path:  # Only add if path is not None
                    files.append(FileStats(
                        path=str(path),  # Ensure path is a string
                        lines_added=added,
                        lines_deleted=deleted,
                        lines_changed=added + deleted
                    ))
                    total_additions += added
                    total_deletions += deleted

            # Get commit message and author info
            message = commit.message.strip() if commit.message else ""
            if isinstance(message, bytes):
                message = message.decode('utf-8', errors='replace')
            # Only take the first line of the commit message
            message_str = str(message).split('\n', 1)[0].strip()

            # Ensure we have a valid date
            commit_date = commit.authored_datetime
            if commit_date is None:
                commit_date = datetime.now(timezone.utc)

            return CommitStats(
                hash=commit.hexsha,
                author=f"{commit.author.name} <{commit.author.email}>" if hasattr(commit.author, 'name') and hasattr(commit.author, 'email') else str(commit.author),
                date=commit_date,
                message=message_str,
                files_changed=len(files),
                lines_added=total_additions,
                lines_deleted=total_deletions,
                files=files
            )
            
        except git.GitCommandError as e:
            raise RuntimeError(f"Failed to analyze commit {commit_hash}: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error analyzing commit {commit_hash}: {str(e)}") from e

    def get_range_analytics(
        self, start_date: Optional[Union[datetime, str]] = None, end_date: Optional[Union[datetime, str]] = None
    ) -> RangeStats:
        """Get analytics for a date range.

        Args:
            start_date: Start date for the range (inclusive) as datetime or string
            end_date: End date for the range (inclusive) as datetime or string

        Returns:
            RangeStats: Statistics for the date range
            
        Raises:
            RuntimeError: If there's an error analyzing the date range
            ValueError: If date strings cannot be parsed
        """
        try:
            repo = git.Repo(self.repo_path)
            
            # Parse string dates using our unified parser
            if isinstance(start_date, str):
                start_date = self._parse_date(start_date)
            
            if isinstance(end_date, str):
                if end_date.lower() in ['now', 'today', '']:
                    end_date = datetime.now()
                else:
                    end_date = self._parse_date(end_date)
            
            # Set default dates if not provided
            if start_date is None:
                # Get date of first commit
                first_commit = next(repo.iter_commits(rev='--all', reverse=True, max_count=1))
                start_date = first_commit.authored_datetime or datetime.min.replace(tzinfo=timezone.utc)
                
            if end_date is None:
                end_date = datetime.now(timezone.utc)
                
            # Initialize stats
            commits: List[CommitStats] = []
            total_files_changed = 0
            total_lines_added = 0
            total_lines_deleted = 0
            authors: Dict[str, int] = {}
            
            # Convert dates to git's format (without timezone)
            git_start_date = start_date.strftime('%Y-%m-%d %H:%M')
            git_end_date = end_date.strftime('%Y-%m-%d %H:%M')
            
            # Get commits in the date range using GitPython's native filtering
            # Convert dates to timezone-aware datetimes for comparison
            start_dt = start_date if start_date.tzinfo else start_date.replace(tzinfo=timezone.utc)
            end_dt = (end_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_dt.tzinfo:
                end_dt = end_dt.replace(tzinfo=timezone.utc)
                
            # Get all commits and filter by date in Python
            for commit in repo.iter_commits(rev='--all', reverse=True):
                commit_dt = commit.authored_datetime
                if commit_dt is None:
                    commit_dt = commit.committed_datetime or datetime.now(timezone.utc)
                    
                # Skip commits outside our date range
                if commit_dt < start_dt or commit_dt >= end_dt:
                    continue
                try:
                    # Get commit stats
                    commit_stats = self.get_commit_stats(commit.hexsha)
                    commits.append(commit_stats)
                    
                    # Update totals
                    total_files_changed += commit_stats.files_changed
                    total_lines_added += commit_stats.lines_added
                    total_lines_deleted += commit_stats.lines_deleted
                    
                    # Update author stats
                    author = commit.author.email if hasattr(commit.author, 'email') else str(commit.author)
                    if author:  # Only add if author is not None or empty
                        authors[author] = authors.get(author, 0) + 1
                except Exception as e:
                    # Log the error but continue with other commits
                    print(f"Warning: Could not process commit {commit.hexsha}: {e}")
                    continue
            
            return RangeStats(
                start_date=start_date,
                end_date=end_date,
                total_commits=len(commits),
                total_files_changed=total_files_changed,
                total_lines_added=total_lines_added,
                total_lines_deleted=total_lines_deleted,
                commits=commits,
                authors=authors
            )
            
        except git.GitCommandError as e:
            raise RuntimeError(f"Failed to analyze date range: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error analyzing date range: {str(e)}") from e

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
