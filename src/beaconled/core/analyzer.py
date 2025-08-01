"""Git repository analyzer."""

import os
import warnings
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Union, Type, TypeVar, cast
import git
from pathlib import Path

from ..exceptions import (
    InvalidRepositoryError,
    CommitError,
    DateParseError,
    DateRangeError,
    ValidationError
)
from .models import CommitStats, FileStats, RangeStats

# Type variable for generic type hints
T = TypeVar('T')


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
            InvalidRepositoryError: If the path is invalid, not a directory, or not a git repository
        """
        try:
            path = Path(repo_path).resolve()
            
            # Ensure path exists and is a directory
            if not path.exists():
                raise InvalidRepositoryError(
                    str(path), 
                    reason="Path does not exist"
                )
            if not path.is_dir():
                raise InvalidRepositoryError(
                    str(path),
                    reason="Path is not a directory"
                )
            
            # Ensure it's within allowed boundaries (prevent directory traversal)
            cwd = Path.cwd().resolve()
            if not str(path).startswith(str(cwd)):
                raise InvalidRepositoryError(
                    str(path),
                    reason="Path is outside the current working directory"
                )
            
            # Check if it's actually a git repository
            git_dir = path / '.git'
            if not git_dir.exists():
                raise InvalidRepositoryError(
                    str(path),
                    reason="No .git directory found"
                )
                
            return str(path)
        except InvalidRepositoryError:
            raise  # Re-raise our custom exceptions as-is
        except Exception as e:
            # Wrap any unexpected errors
            raise InvalidRepositoryError(
                str(repo_path),
                reason=str(e)
            ) from e

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date from relative or absolute format.
        
        This method supports flexible date input formats to make it easier to specify
        dates for analysis. It handles both relative and absolute date specifications.
        
        Supported Relative Formats:
            - 1d    - 1 day ago
            - 2w    - 2 weeks ago
            - 3m    - 3 months ago (approximate, using 4 weeks per month)
            - 1y    - 1 year ago (approximate, using 52 weeks per year)
        
        Supported Absolute Formats:
            - YYYY-MM-DD              - Date only (midnight in local timezone)
            - YYYY-MM-DD HH:MM        - Date and time (24-hour format)
        
        Examples:
            >>> analyzer._parse_date("1d")      # 1 day ago from now
            >>> analyzer._parse_date("2w")      # 2 weeks ago from now
            >>> analyzer._parse_date("2025-01-15")          # Jan 15, 2025 00:00
            >>> analyzer._parse_date("2025-01-15 14:30")    # Jan 15, 2025 14:30
        
        Note:
            - Relative dates are calculated from the current time when this method is called
            - Month and year calculations are approximate (4 weeks/month, 52 weeks/year)
            - All times are in the local timezone
        
        Args:
            date_str: Date string to parse. Can be a relative date (e.g., "1d", "2w") 
                     or an absolute date (e.g., "2025-01-15" or "2025-01-15 14:30").
            
        Returns:
            datetime: Parsed datetime in local timezone.
            
        Raises:
            ValueError: If the date string format is invalid, malformed, or out of range.
                      The error message will provide specific guidance on the issue.
        """
        if not date_str or not date_str.strip():
            raise ValueError(
                "Date string cannot be empty. Please provide a valid date in one of these formats:\n"
                "  - Relative: 1d (days), 2w (weeks), 3m (months), 1y (years)\n"
                "  - Absolute: YYYY-MM-DD or YYYY-MM-DD HH:MM\n"
                "  - Special: 'now' for current time\n"
                "Example: '1w' for one week ago, '2025-01-15' for January 15, 2025, or 'now' for current time"
            )
            
        date_str = date_str.strip()
        
        # Handle special 'now' value
        if date_str.lower() == 'now':
            return datetime.now()
        
        # Handle relative dates (e.g., 1d, 2w, 3m, 1y)
        if len(date_str) > 1 and date_str[-1] in {'d', 'w', 'm', 'y'}:
            try:
                # Extract number and unit
                num_part = date_str[:-1]
                if not num_part.isdigit():
                    raise ValueError("Relative dates must start with a number")
                    
                num = int(num_part)
                if num <= 0:
                    raise ValueError("Relative date value must be a positive number")
                    
                unit = date_str[-1].lower()
                now = datetime.now()
                
                # Map units to timedelta
                unit_map = {
                    'd': ('day', 'days', timedelta(days=1)),
                    'w': ('week', 'weeks', timedelta(weeks=1)),
                    'm': ('month', 'months', timedelta(weeks=4)),  # Approximate
                    'y': ('year', 'years', timedelta(weeks=52))    # Approximate
                }
                
                if unit not in unit_map:
                    valid_units = ", ".join(f"'{u}'" for u in unit_map.keys())
                    raise ValueError(
                        f"Invalid time unit '{unit}'. "
                        f"Valid units are: {valid_units}"
                    )
                
                unit_singular, unit_plural, delta = unit_map[unit]
                return now - (delta * num)
                
            except ValueError as e:
                    # Convert to our custom exception
                raise DateParseError(
                    date_str,
                    format_hint=(
                        "Expected format: <number><unit> where <unit> is one of: "
                        "d (days), w (weeks), m (months), y (years)\n"
                        "Examples: '1d' (1 day ago), '2w' (2 weeks ago), '3m' (3 months ago)"
                    )
                ) from e
        
        # Handle absolute dates
        try:
            # Try with date and time first
            try:
                parsed = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                # Validate reasonable year range
                if not (2000 <= parsed.year <= 2100):
                    raise ValidationError(
                        f"Year {parsed.year} is outside the supported range (2000-2100)",
                        field="date",
                        value=date_str
                    )
                return parsed
            except ValueError:
                # Try date only
                try:
                    parsed = datetime.strptime(date_str, '%Y-%m-%d')
                    if not (2000 <= parsed.year <= 2100):
                        raise ValidationError(
                            f"Year {parsed.year} is outside the supported range (2000-2100)",
                            field="date",
                            value=date_str
                        )
                    return parsed
                except ValueError as e:
                    # Check for common mistakes in date format
                    if len(date_str) == 10 and (date_str[4] != '-' or date_str[7] != '-'):
                        raise DateParseError(
                            date_str,
                            format_hint=(
                                "For absolute dates, please use YYYY-MM-DD or YYYY-MM-DD HH:MM\n"
                                "Example: '2025-01-15' or '2025-01-15 14:30'"
                            )
                        )
                    raise  # Re-raise the original exception
                    
        except (ValueError, ValidationError) as e:
            # Convert to our custom DateParseError
            if isinstance(e, ValidationError):
                raise DateParseError(date_str, str(e))
            
            # For other ValueErrors, provide a helpful message
            raise DateParseError(
                date_str,
                format_hint=(
                    "Please use one of these formats:\n"
                    "  - Relative: <number><unit> (e.g., '1d', '2w', '3m', '1y')\n"
                    "  - Absolute: YYYY-MM-DD or YYYY-MM-DD HH:MM (e.g., '2025-01-15' or '2025-01-15 14:30')\n\n"
                    f"Original error: {str(e)}"
                )
            ) from e
            
    def _parse_git_date(self, date_str: str) -> datetime:
        """Parse a date string from git log output into a datetime object.
        
        This internal method handles the specific date formats used by git log,
        particularly the default format that includes timezone information.
        
        Supported Formats:
            - "YYYY-MM-DD HH:MM:SS +ZZZZ" - Default git log format with timezone
            - "YYYY-MM-DD HH:MM:SS" - Just the timestamp without timezone
            
        Examples:
            >>> analyzer._parse_git_date("2025-01-15 14:30:45 +0800")
            datetime(2025, 1, 15, 14, 30, 45)
            
            >>> analyzer._parse_git_date("2025-01-15 14:30:45")
            datetime(2025, 1, 15, 14, 30, 45)
        
        Note:
            - Timezone information (if present) is currently discarded
            - If parsing fails, falls back to the current time and logs a warning
            - This is an internal method primarily used for processing git log output
        
        Args:
            date_str: Date string from git log, typically in the format 
                     "YYYY-MM-DD HH:MM:SS +ZZZZ" or "YYYY-MM-DD HH:MM:SS"
            
        Returns:
            datetime: Parsed datetime object in local timezone, or current time 
                     if parsing fails
            
        Raises:
            DateParseError: If the date string cannot be parsed and strict mode is enabled
        """
        try:
            # Handle git's default format: "YYYY-MM-DD HH:MM:SS +ZZZZ"
            if ' ' in date_str and '+' in date_str:
                date_part, tz_part = date_str.rsplit('+', 1)
                try:
                    return datetime.strptime(date_part.strip(), '%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    raise DateParseError(
                        date_str,
                        format_hint=(
                            "Expected format: 'YYYY-MM-DD HH:MM:SS +ZZZZ' or 'YYYY-MM-DD HH:MM:SS'\n"
                            "Example: '2025-01-15 14:30:45 +0800' or '2025-01-15 14:30:45'"
                        )
                    ) from e
            
            # Try parsing without timezone
            try:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                raise DateParseError(
                    date_str,
                    format_hint=(
                        "Expected format: 'YYYY-MM-DD HH:MM:SS +ZZZZ' or 'YYYY-MM-DD HH:MM:SS'\n"
                        "Example: '2025-01-15 14:30:45 +0800' or '2025-01-15 14:30:45'"
                    )
                ) from e
        except Exception as e:
            # For this internal method, we'll log a warning but still return the current time
            # to avoid breaking the calling code that expects a datetime
            import warnings
            warnings.warn(
                f"Failed to parse git date '{date_str}': {str(e)}. Using current time.",
                RuntimeWarning,
                stacklevel=2
            )
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
            CommitError: If there's an error processing the commit
            InvalidRepositoryError: If the repository path is invalid
            git.GitCommandError: If there's an error executing git commands
            
        Example:
            >>> analyzer = GitAnalyzer("./my-repo")
            >>> stats = analyzer.get_commit_stats("a1b2c3d")
            >>> print(f"Commit by {stats.author} on {stats.date}")
            
        Note:
            - The method will attempt to handle various error conditions gracefully
            - Debug logging is available by configuring the 'beaconled.core.analyzer' logger
        """
        import logging
        logger = logging.getLogger('beaconled.core.analyzer')
        logger.debug("Getting commit stats for hash: %s", commit_hash)
        if not commit_hash or not isinstance(commit_hash, str) or not commit_hash.strip():
            error_msg = f"Invalid commit hash: '{commit_hash}'. Must be a non-empty string."
            logger.error(error_msg)
            raise CommitError(
                "",  # Empty string for invalid commit hash
                error_msg
            )
            
        commit_hash = commit_hash.strip()
        
        if not self._is_valid_commit_hash(commit_hash):
            error_msg = f"Invalid commit hash format: '{commit_hash}'. Expected a 7-40 character hex string."
            logger.error(error_msg)
            raise CommitError(
                commit_hash,
                error_msg
            )
            
        try:
            # Initialize the git repository
            try:
                logger.debug("Initializing git repository at: %s", self.repo_path)
                repo = git.Repo(self.repo_path)
                logger.debug("Successfully initialized git repository")
            except git.InvalidGitRepositoryError as e:
                error_msg = f"Not a valid git repository: {e}"
                logger.error("%s: %s", error_msg, self.repo_path)
                raise InvalidRepositoryError(
                    self.repo_path,
                    error_msg
                ) from e
            except git.NoSuchPathError as e:
                error_msg = f"Repository path does not exist: {e}"
                logger.error("%s: %s", error_msg, self.repo_path)
                raise InvalidRepositoryError(
                    self.repo_path,
                    error_msg
                ) from e
            
            # Get the commit object
            try:
                logger.debug("Retrieving commit object for hash: %s", commit_hash)
                commit = repo.commit(commit_hash)
                logger.debug("Successfully retrieved commit: %s - %s", 
                            commit.hexsha[:7], commit.message.split('\n')[0])
            except (ValueError, TypeError, git.BadName) as e:
                error_msg = f"Commit not found: {commit_hash}"
                logger.error("%s: %s", error_msg, str(e))
                raise CommitError(commit_hash, error_msg) from e
            except Exception as e:
                error_msg = f"Error retrieving commit {commit_hash}"
                logger.exception("%s: %s", error_msg, str(e))
                raise CommitError(commit_hash, error_msg) from e
            
            # Initialize file stats
            files: List[FileStats] = []
            total_additions = 0
            total_deletions = 0
            
            try:
                # Get diff stats for this commit
                if commit.parents:
                    # Compare with first parent (most common case)
                    logger.debug("Generating diff with parent commit")
                    diff_index = commit.parents[0].diff(commit, create_patch=True)
                else:
                    # For initial commit, compare with empty tree
                    logger.debug("Generating diff for initial commit (no parent)")
                    diff_index = commit.diff(git.NULL_TREE, create_patch=True)
                
                logger.debug("Processing %d changed files", len(diff_index))
                
                # Process each changed file in the diff
                for i, diff in enumerate(diff_index, 1):
                    try:
                        # Skip binary files
                        if diff.diff is None:
                            logger.debug("Skipping binary file: %s", diff.b_path or diff.a_path)
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
                            file_stats = FileStats(
                                path=str(path),  # Ensure path is a string
                                lines_added=added,
                                lines_deleted=deleted,
                                lines_changed=added + deleted
                            )
                            files.append(file_stats)
                            total_additions += added
                            total_deletions += deleted
                            
                            logger.debug("Processed file %d/%d: %s (+%d/-%d lines)", 
                                       i, len(diff_index), path, added, deleted)
                        else:
                            logger.warning("Skipping file with no path in diff")
                            
                    except Exception as e:
                        logger.warning("Error processing file %d/%d: %s", 
                                     i, len(diff_index), str(e), exc_info=True)
                        continue  # Skip this file but continue with others
                        
            except Exception as e:
                error_msg = f"Error generating diff for commit {commit_hash}"
                logger.exception("%s: %s", error_msg, str(e))
                # We'll continue processing with the files we've collected so far
                # rather than failing the entire operation for a diff error

            try:
                # Get commit message and author info
                message = commit.message.strip() if commit.message else ""
                if isinstance(message, bytes):
                    message = message.decode('utf-8', errors='replace')
                # Only take the first line of the commit message
                message_str = str(message).split('\n', 1)[0].strip()
                
                logger.debug("Processed commit message: %s", message_str[:50] + (message_str[50:] and '...'))

                # Ensure we have a valid date
                commit_date = commit.authored_datetime
                if commit_date is None:
                    logger.warning("No authored_datetime for commit %s, using current time", commit_hash[:7])
                    commit_date = datetime.now(timezone.utc)
                else:
                    logger.debug("Commit date: %s", commit_date.isoformat())
                
                # Format author information
                author_info = ""
                try:
                    if hasattr(commit.author, 'name') and hasattr(commit.author, 'email'):
                        author_info = f"{commit.author.name} <{commit.author.email}>"
                        logger.debug("Commit author: %s", author_info)
                    else:
                        author_info = str(commit.author)
                        logger.debug("Using fallback author info: %s", author_info)
                except Exception as e:
                    logger.warning("Error getting author info: %s", str(e), exc_info=True)
                    author_info = "Unknown Author <unknown@example.com>"
                
                # Create and return the CommitStats object
                stats = CommitStats(
                    hash=commit.hexsha,
                    author=author_info,
                    date=commit_date,
                    message=message_str,
                    files_changed=len(files),
                    lines_added=total_additions,
                    lines_deleted=total_deletions,
                    files=files
                )
                
                logger.debug("Successfully processed commit %s: %d files, +%d -%d lines", 
                           commit_hash[:7], len(files), total_additions, total_deletions)
                
                return stats
                
            except Exception as e:
                error_msg = f"Error processing commit {commit_hash}"
                logger.exception("%s: %s", error_msg, str(e))
                raise CommitError(commit_hash, error_msg) from e
            
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
            ValueError: If date strings cannot be parsed or if date range is invalid
        """
        try:
            # Convert string dates to datetime objects if needed
            if start_date and isinstance(start_date, str):
                start_date = self._parse_date(start_date)
            if end_date and isinstance(end_date, str):
                end_date = self._parse_date(end_date)
                
            # Validate date range
            if start_date and end_date and end_date < start_date:
                raise ValueError(
                    f"Invalid date range: end date ({end_date}) is before start date ({start_date}).\n"
                    "Please ensure the end date is after the start date."
                )
                
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
