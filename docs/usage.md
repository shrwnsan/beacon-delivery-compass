# Usage Guide

This guide covers how to use Beacon effectively for analyzing your git repositories and development metrics.

## Before You Start

**Important**: Always activate your virtual environment before using Beacon:

```bash
# Activate your virtual environment
source beaconled-env/bin/activate  # macOS/Linux
beaconled-env\Scripts\activate     # Windows

# You should see (beaconled-env) in your prompt
```

## Basic Usage

### Analyze Current Commit

```bash
# Analyze the latest commit (HEAD)
beaconled

# Example output:
# Commit: abc12345
# Author: John Doe
# Date: 2025-07-20 10:30:00
# Message: Add new feature for user analytics
# 
# Files changed: 3
# Lines added: 45
# Lines deleted: 12
# Net change: 33
# 
# File changes:
#   src/analytics.py: +30 -5
#   tests/test_analytics.py: +15 -0
#   README.md: +0 -7
```

### Analyze Specific Commit

```bash
# Analyze a specific commit by hash
beaconled abc12345

# You can use short hashes too
beaconled abc123
```

## Output Formats

Beacon supports three output formats to suit different needs:

### Standard Format (Default)

```bash
beaconled --format standard
# or simply
beaconled
```

Clean, human-readable output perfect for quick reviews.

### Extended Format

```bash
beaconled --format extended
```

Includes additional details like file type breakdowns:

```
File type breakdown:
  .py: 2 files, +45 -5
  .md: 1 files, +0 -7
```

### JSON Format

```bash
beaconled --format json
```

Machine-readable output perfect for automation and integration:

```json
{
  "hash": "abc12345",
  "author": "John Doe",
  "date": "2025-07-20T10:30:00+08:00",
  "message": "Add new feature for user analytics",
  "files_changed": 3,
  "lines_added": 45,
  "lines_deleted": 12,
  "files": [
    {
      "path": "src/analytics.py",
      "lines_added": 30,
      "lines_deleted": 5,
      "lines_changed": 35
    }
  ]
}
```

## Range Analysis

Analyze multiple commits over a time period:

### Weekly Reports

```bash
# Analyze last week's commits
beaconled --range --since "1 week ago"

# Example output:
# Range Analysis: 2025-07-13 to 2025-07-20
# 
# Total commits: 15
# Total files changed: 42
# Total lines added: 1,234
# Total lines deleted: 567
# Net change: 667
# 
# Contributors:
#   John Doe: 8 commits
#   Jane Smith: 4 commits
#   Bob Wilson: 3 commits
```

### Custom Date Ranges

```bash
# Specific date range
beaconled --range --since "2025-07-01" --until "2025-07-15"

# Last month
beaconled --range --since "1 month ago"

# Since a specific date
beaconled --range --since "2025-06-01"
```

### Sprint Analysis

```bash
# Two-week sprint analysis with JSON output for reporting
beaconled --range --since "2 weeks ago" --format json > sprint-report.json
```

## Repository Options

### Analyze Different Repository

```bash
# Analyze a different repository
beaconled --repo /path/to/other/repo

# Works with all other options
beaconled --repo /path/to/other/repo --range --since "1 week ago"
```

## Common Workflows

### Daily Standup Preparation

```bash
# Quick check of yesterday's work
beaconled --range --since "1 day ago"
```

### Weekly Team Reports

```bash
# Generate team report for the week
beaconled --range --since "1 week ago" --format extended > weekly-report.txt
```

### Sprint Retrospectives

```bash
# Comprehensive sprint analysis
beaconled --range --since "2 weeks ago" --format json > sprint-metrics.json
```

### Code Review Preparation

```bash
# Analyze specific commits before review
beaconled abc123
beaconled def456
beaconled ghi789
```

### CI/CD Integration

```bash
# Generate metrics for build pipeline
beaconled --format json > build-metrics.json
```

## Pro Tips

### 1. Use Aliases for Common Commands

Add these to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
# Quick aliases
alias beaconled-week="beaconled --range --since '1 week ago'"
alias beaconled-json="beaconled --format json"
alias beaconled-sprint="beaconled --range --since '2 weeks ago' --format extended"
```

### 2. Combine with Other Tools

```bash
# Save weekly report with timestamp
beaconled --range --since "1 week ago" > "report-$(date +%Y-%m-%d).txt"

# Count commits in range
beaconled --range --since "1 week ago" --format json | jq '.total_commits'

# Extract author statistics
beaconled --range --since "1 week ago" --format json | jq '.authors'
```

### 3. Virtual Environment Automation

Create a script to automatically activate your environment:

```bash
#!/bin/bash
# save as ~/bin/beaconled-env
source ~/beaconled-env/bin/activate
beaconled "$@"
deactivate
```

### 4. Repository-Specific Analysis

```bash
# Create project-specific scripts
#!/bin/bash
# save as analyze-project.sh
cd /path/to/your/project
source venv/bin/activate
beaconled --range --since "1 week ago" --format extended
```

## Troubleshooting

### Virtual Environment Not Active

If you see "command not found: beaconled":

```bash
# Make sure your virtual environment is active
source beaconled-env/bin/activate
which beaconled  # Should show path in your venv
```

### Git Repository Issues

```bash
# Make sure you're in a git repository
git status

# Or specify repository path
beaconled --repo /path/to/git/repo
```

### Date Format Issues

Beacon accepts various date formats:
- `"1 week ago"`, `"2 days ago"`, `"1 month ago"`
- `"2025-07-20"`, `"2025-07-20 10:30:00"`
- `"yesterday"`, `"last week"`

## Integration Examples

### GitHub Actions

```yaml
- name: Generate Beacon Report
  run: |
    source venv/bin/activate
    beaconled --range --since "1 week ago" --format json > beaconled-report.json
```

### Git Hooks

```bash
#!/bin/bash
# .git/hooks/post-commit
source venv/bin/activate
beaconled --format extended
```

## Next Steps

- [Integration Guide](integrations.md) - Set up Beacon in your workflow
- [API Reference](api-reference.md) - Complete command reference
- [Contributing](../CONTRIBUTING.md) - Help improve Beacon