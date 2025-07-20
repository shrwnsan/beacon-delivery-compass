# API Reference

## Command Line Interface

### beacon
The main command-line interface for Beacon.

```bash
beacon [OPTIONS] [COMMIT_HASH]
```

#### Arguments
- `COMMIT_HASH` (optional): Specific commit hash to analyze. If omitted, analyzes HEAD.

#### Options
- `--format FORMAT`: Output format (`standard`, `extended`, `json`)
- `--range`: Enable range analysis mode
- `--since DATE`: Start date for range analysis
- `--until DATE`: End date for range analysis
- `--repo PATH`: Path to git repository (default: current directory)
- `--help`: Show help message and exit
- `--version`: Show version information

#### Examples
```bash
# Basic usage
beacon

# Specific commit
beacon abc123

# JSON output
beacon --format json

# Weekly report
beacon --range --since "1 week ago"

# Custom repository
beacon --repo /path/to/repo --format extended
```

## Python API

### Core Classes

#### `CommitStats`
Represents statistics for a single commit.

```python
from beacon.core.models import CommitStats

stats = CommitStats(
    hash="abc123",
    author="John Doe",
    date="2025-07-20T10:30:00",
    message="Add new feature",
    files_changed=3,
    lines_added=45,
    lines_deleted=12,
    files=[...]
)
```

**Attributes:**
- `hash`: str - Commit hash
- `author`: str - Author name
- `date`: str - Commit date in ISO format
- `message`: str - Commit message
- `files_changed`: int - Number of files changed
- `lines_added`: int - Lines added
- `lines_deleted`: int - Lines deleted
- `files`: List[FileStats] - Detailed file changes

#### `FileStats`
Represents statistics for a single file change.

```python
from beacon.core.models import FileStats

file_stats = FileStats(
    path="src/main.py",
    lines_added=30,
    lines_deleted=5,
    lines_changed=35
)
```

**Attributes:**
- `path`: str - File path
- `lines_added`: int - Lines added
- `lines_deleted`: int - Lines deleted
- `lines_changed`: int - Total lines changed

#### `RangeStats`
Represents statistics for a range of commits.

```python
from beacon.core.models import RangeStats

range_stats = RangeStats(
    start_date="2025-07-13",
    end_date="2025-07-20",
    total_commits=15,
    total_files_changed=42,
    total_insertions=1234,
    total_deletions=567,
    authors={"John Doe": 8, "Jane Smith": 4}
)
```

**Attributes:**
- `start_date`: str - Range start date
- `end_date`: str - Range end date
- `total_commits`: int - Total commits in range
- `total_files_changed`: int - Total files changed
- `total_insertions`: int - Total lines added
- `total_deletions`: int - Total lines deleted
- `authors`: Dict[str, int] - Commit count per author

### Core Functions

#### `analyze_commit()`
Analyze a single commit.

```python
from beacon.core.analyzer import GitAnalyzer

analyzer = GitAnalyzer(repo_path="/path/to/repo")
stats = analyzer.analyze_commit("abc123")
```

**Parameters:**
- `commit_hash`: str - Commit hash to analyze

**Returns:** `CommitStats` object

#### `analyze_range()`
Analyze a range of commits.

```python
from beacon.core.analyzer import GitAnalyzer

analyzer = GitAnalyzer(repo_path="/path/to/repo")
stats = analyzer.analyze_range(since="1 week ago", until="now")
```

**Parameters:**
- `since`: str - Start date (relative or absolute)
- `until`: str - End date (relative or absolute)

**Returns:** `RangeStats` object

### Formatters

#### `StandardFormatter`
Formats output in standard text format.

```python
from beacon.formatters.standard import StandardFormatter

formatter = StandardFormatter()
output = formatter.format(stats)
```

#### `ExtendedFormatter`
Formats output in extended text format with additional details.

```python
from beacon.formatters.extended import ExtendedFormatter

formatter = ExtendedFormatter()
output = formatter.format(stats)
```

#### `JSONFormatter`
Formats output as JSON.

```python
from beacon.formatters.json_format import JSONFormatter

formatter = JSONFormatter()
output = formatter.format(stats)
```

## Environment Variables

### `BEACON_REPO_PATH`
Default repository path when `--repo` is not specified.

```bash
export BEACON_REPO_PATH=/path/to/default/repo
```

### `BEACON_FORMAT`
Default output format.

```bash
export BEACON_FORMAT=extended
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: Git repository not found
- `4`: Invalid commit hash

## Error Handling

### Common Error Messages

**Repository not found:**
```
Error: Not a git repository (or any of the parent directories)
```

**Invalid commit hash:**
```
Error: Commit 'abc123' not found
```

**Invalid date format:**
```
Error: Invalid date format: 'tomorrow'
```

### Exception Classes

```python
from beacon.core.exceptions import (
    BeaconError,
    RepositoryNotFoundError,
    CommitNotFoundError,
    InvalidDateError
)
```

## Integration Examples

### Python Script Integration

```python
#!/usr/bin/env python3
import json
from beacon.core.analyzer import GitAnalyzer
from beacon.formatters.json_format import JSONFormatter

# Analyze repository
analyzer = GitAnalyzer("/path/to/repo")
stats = analyzer.analyze_range(since="1 week ago")

# Format as JSON
formatter = JSONFormatter()
print(formatter.format(stats))
```

### CI/CD Pipeline Integration

```yaml
- name: Generate Beacon Report
  run: |
    python -c "
    from beacon.core.analyzer import GitAnalyzer
    from beacon.formatters.json_format import JSONFormatter
    
    analyzer = GitAnalyzer('.')
    stats = analyzer.analyze_range(since='1 week ago')
    formatter = JSONFormatter()
    
    with open('beacon-report.json', 'w') as f:
        f.write(formatter.format(stats))
    "
```

### Custom Formatter

```python
from beacon.core.models import CommitStats, RangeStats
from typing import Union

class CustomFormatter:
    def format(self, stats: Union[CommitStats, RangeStats]) -> str:
        if isinstance(stats, CommitStats):
            return f"Commit {stats.hash}: {stats.lines_added}+ {stats.lines_deleted}-"
        else:
            return f"Range {stats.start_date} to {stats.end_date}: {stats.total_commits} commits"
