# Beacon Core API Reference

This document provides detailed documentation for the core modules of the Beacon Delivery Compass.

## Table of Contents
- [GitAnalyzer](#gitanalyzer)
- [Data Models](#data-models)
  - [FileStats](#filestats)
  - [CommitStats](#commitstats)
  - [RangeStats](#rangestats)

## GitAnalyzer

The `GitAnalyzer` class provides functionality to analyze git repositories and extract various metrics.

### Initialization
```python
from beaconled.core import GitAnalyzer

# Initialize with path to git repository
analyzer = GitAnalyzer(repo_path=".")
```

### Methods

#### `get_commit_stats(commit_hash: str = "HEAD") -> CommitStats`
Get detailed statistics for a specific commit.

**Parameters:**
- `commit_hash` (str): The commit hash to analyze (default: "HEAD")

**Returns:**
- `CommitStats`: Object containing commit statistics

**Example:**
```python
stats = analyzer.get_commit_stats("abc123")
print(f"Commit by {stats.author} on {stats.date}")
```

#### `get_range_analytics(start_date: Optional[Union[datetime, str]] = None, end_date: Optional[Union[datetime, str]] = None) -> RangeStats`
Get analytics for a range of commits.

**Parameters:**
- `start_date`: Start date for the range (inclusive)
  - Can be a datetime object or a string in formats:
    - `YYYY-MM-DD` (date only, assumes 00:00:00 UTC)
    - `YYYY-MM-DD HH:MM` (date with time, space separator, seconds default to 00)
    - `YYYY-MM-DDTHH:MM:SS` (ISO 8601 format with 'T' separator; seconds are accepted but truncated to minutes)
    - Relative format (e.g., "1d", "2w", "3m", "1y")
- `end_date`: End date for the range (inclusive)
  - Same format as start_date, or "now" for current time

**Returns:**
- `RangeStats`: Object containing statistics for the date range

**Example:**
```python
# Get stats for the last month
stats = analyzer.get_range_analytics("1m")
print(f"{stats.total_commits} commits in the last month")

# Get stats for a specific date range
from datetime import datetime, timedelta
today = datetime.now()
last_week = today - timedelta(days=7)
stats = analyzer.get_range_analytics(last_week, today)
```

## Data Models

### FileStats
Represents statistics for a single file in a commit.

**Attributes:**
- `path` (str): Path to the file
- `lines_added` (int): Number of lines added
- `lines_deleted` (int): Number of lines deleted
- `lines_changed` (int): Total number of lines changed (added + deleted)

### CommitStats
Represents statistics for a single commit.

**Attributes:**
- `hash` (str): Commit hash
- `author` (str): Author name and email
- `date` (datetime): Commit date and time
- `message` (str): Commit message (first line)
- `files_changed` (int): Number of files changed
- `lines_added` (int): Total lines added
- `lines_deleted` (int): Total lines deleted
- `files` (List[FileStats]): List of file statistics

### RangeStats
Represents statistics for a range of commits.

**Attributes:**
- `start_date` (datetime): Start of the date range
- `end_date` (datetime): End of the date range
- `total_commits` (int): Total number of commits
- `total_files_changed` (int): Total files changed
- `total_lines_added` (int): Total lines added
- `total_lines_deleted` (int): Total lines deleted
- `commits` (List[CommitStats]): List of commit statistics
- `authors` (Dict[str, int]): Dictionary of authors and their commit counts

## Example Usage

```python
from beaconled.core import GitAnalyzer

# Initialize with repository path
analyzer = GitAnalyzer("/path/to/your/repo")

# Get stats for a specific commit
commit = analyzer.get_commit_stats("abc123")
print(f"Commit {commit.hash[:7]} by {commit.author}")
print(f"Message: {commit.message}")
print(f"Files changed: {commit.files_changed}")
print(f"Lines added/deleted: +{commit.lines_added}/-{commit.lines_deleted}")

# Get stats for a date range
stats = analyzer.get_range_analytics("2w")
print(f"\nLast 2 weeks summary:")
print(f"Commits: {stats.total_commits}")
print(f"Files changed: {stats.total_files_changed}")
print(f"Lines: +{stats.total_lines_added}/-{stats.total_lines_deleted}")
print("\nTop contributors:")
for author, count in sorted(stats.authors.items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"- {author}: {count} commits")
```

## Error Handling

All methods may raise the following exceptions:
- `ValueError`: For invalid input parameters
- `git.GitCommandError`: For git-related errors
- `RuntimeError`: For other unexpected errors during analysis
