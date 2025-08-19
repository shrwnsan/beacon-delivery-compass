# Basic Usage Examples

This document provides practical examples for getting started with Beacon, including date handling and output formats. All dates are handled in UTC.

## Quick Start Examples

### 1. Analyze Latest Commit
```bash
# Simple analysis with default output
beaconled

# Example output:
# 📊 Commit: abc12345
# 👤 Author: John Doe
# 📅 Date: 2025-07-20 10:30:00+08:00
# 💬 Message: Add new feature for user analytics
#
# 📂 Files changed: 3
# ➕ Lines added: 45
# ➖ Lines deleted: 12
# 🔀 Net change: 33
#
# Changed files:
#   src/analytics.py   (+30 -5)
#   tests/test_analytics.py (+15 -0)
#   README.md          (+0 -7)

# Save to file with UTC timestamp
beaconled > latest-commit-$(date -u +%Y%m%d-%H%M%S).txt

# JSON output
beaconled --format json > commit-data.json

# Extended format with detailed file information
beaconled --format extended

# Example JSON output:
# {
#   "hash": "abc12345",
#   "author": "John Doe",
#   "date": "2025-07-20T10:30:00+08:00",
#   "message": "Add new feature for user analytics",
#   "files_changed": 3,
#   "lines_added": 45,
#   "lines_deleted": 12,
#   "net_change": 33,
#   "files": [
#     {
#       "path": "src/analytics.py",
#       "lines_added": 30,
#       "lines_deleted": 5,
#       "lines_changed": 35,
#       "file_type": ".py",
#       "component": "Core Logic",
#       "impact": "high"
#     },
#     {
#       "path": "tests/test_analytics.py",
#       "lines_added": 15,
#       "lines_deleted": 0,
#       "lines_changed": 15,
#       "file_type": ".py",
#       "component": "Tests",
#       "impact": "medium"
#     },
#     {
#       "path": "README.md",
#       "lines_added": 0,
#       "lines_deleted": 7,
#       "lines_changed": 7,
#       "file_type": ".md",
#       "component": "Documentation",
#       "impact": "low"
#     }
#   ]
# }
```

### 2. Analyze Specific Commit
```bash
# By hash
beaconled abc123def456

# Example output:
# 📊 Commit: abc123def456
# 👤 Author: Jane Smith
# 📅 Date: 2025-07-19 14:22:15
# 💬 Message: Fix security vulnerability in authentication module
#
# 📂 Files changed: 2
# ➕ Lines added: 18
# ➖ Lines deleted: 25
# 🔀 Net change: -7
#
# Changed files:
#   src/auth.py        (+15 -20)
#   tests/test_auth.py (+3 -5)

# By short hash
beaconled abc123

# By relative reference
beaconled HEAD~3

# Example output for HEAD~3:
# 📊 Commit: def456ghi789
# 👤 Author: Bob Wilson
# 📅 Date: 2025-07-18 09:15:30
# 💬 Message: Update documentation for new API endpoints
#
# 📂 Files changed: 1
# ➕ Lines added: 42
# ➖ Lines deleted: 0
# 🔀 Net change: 42
#
# Changed files:
#   docs/api-reference.md (+42 -0)
```

### 3. Range Analysis Examples
```bash
# Last week
beaconled --since 1w

# Example output:
# 📊 Range Analysis: 2025-07-13 to 2025-07-20
#
# 📂 Total commits: 15
# 📂 Total files changed: 42
# ➕ Total lines added: 1,234
# ➖ Total lines deleted: 567
# 🔀 Net change: 667
#
# 👥 Contributors:
#   John Doe: 8 commits
#   Jane Smith: 4 commits
#   Bob Wilson: 3 commits
#
# 📊 Commit frequency:
#   Monday: 2
#   Tuesday: 3
#   Wednesday: 1
#   Thursday: 4
#   Friday: 5

# Last month
beaconled --since 1m

# Example output:
# 📊 Range Analysis: 2025-06-20 to 2025-07-20
#
# 📂 Total commits: 67
# 📂 Total files changed: 156
# ➕ Total lines added: 8,942
# ➖ Total lines deleted: 3,215
# 🔀 Net change: 5,727
#
# 👥 Contributors:
#   John Doe: 32 commits
#   Jane Smith: 21 commits
#   Bob Wilson: 14 commits
#
# 📊 Weekly breakdown:
#   Week 1 (Jun 20-26): 12 commits
#   Week 2 (Jun 27-Jul 3): 18 commits
#   Week 3 (Jul 4-10): 15 commits
#   Week 4 (Jul 11-17): 22 commits

# Custom date range
beaconled --since "2025-07-01" --until "2025-07-31"

# Since last tag
beaconled --since "v1.0.0"

# Example output:
# 📊 Range Analysis: 2025-06-15 to 2025-07-20
#
# 📂 Total commits: 45
# 📂 Total files changed: 112
# ➕ Total lines added: 6,789
# ➖ Total lines deleted: 2,345
# 🔀 Net change: 4,444
#
# 👥 Contributors:
#   John Doe: 21 commits
#   Jane Smith: 15 commits
#   Bob Wilson: 9 commits
```

### 4. Different Output Formats
```bash
# Standard format (default)
beaconled --format standard

# Example output:
# 📊 Commit: abc12345
# 👤 Author: John Doe
# 📅 Date: 2025-07-20 10:30:00
# 💬 Message: Add new feature for user analytics
#
# 📂 Files changed: 3
# ➕ Lines added: 45
# ➖ Lines deleted: 12
# 🔀 Net change: 33
#
# Changed files:
#   src/analytics.py   (+30 -5)
#   tests/test_analytics.py (+15 -0)
#   README.md          (+0 -7)

# Extended format with details
beaconled --format extended

# Example output:
# 📊 Commit: abc12345
# 👤 Author: John Doe
# 📅 Date: 2025-07-20 10:30:00
# 💬 Message: Add new feature for user analytics
#
# 📂 Files changed: 3
# ➕ Lines added: 45
# ➖ Lines deleted: 12
# 🔀 Net change: 33
#
# File type breakdown:
#   .py: 2 files, +45 -5
#   .md: 1 files, +0 -7
#
# Changed files:
#   src/analytics.py   (+30 -5) [Core Logic]
#   tests/test_analytics.py (+15 -0) [Tests]
#   README.md          (+0 -7) [Documentation]
#
# Impact Analysis:
#   High: 1 file (src/analytics.py)
#   Medium: 1 file (tests/test_analytics.py)
#   Low: 1 file (README.md)

# JSON for automation
beaconled --format json | jq '.files_changed'

# Example output:
# 3
```

## Team Workflow Examples

### Daily Standup Script
```bash
#!/bin/bash
# daily-summary.sh
echo "📊 Yesterday's Development Summary"
echo "================================="
beaconled --since 1d --format extended

# Save for team sharing
beaconled --since 1d --format json > daily-report.json
```

### Weekly Report Generation
```bash
#!/bin/bash
# weekly-report.sh
echo "📈 Weekly Development Report (Last Week)"
echo "======================================================"
beaconled --since 1w --format extended

# Generate JSON for dashboard
beaconled --since 1w --format json > weekly-dashboard.json
```

### Sprint Retrospective
```bash
#!/bin/bash
# sprint-retro.sh
SPRINT_LENGTH=2w  # 2 weeks

echo "🎯 Sprint Retrospective Analysis"
echo "==============================="
beaconled --since $SPRINT_LENGTH --format extended

# Team member contributions
beaconled --since $SPRINT_LENGTH --format json | jq '.authors'
```

## Repository Analysis Examples

### Multi-Repository Analysis
```bash
#!/bin/bash
# multi-repo-analysis.sh
REPOS=(
    "/path/to/project-a"
    "/path/to/project-b"
    "/path/to/project-c"
)

for repo in "${REPOS[@]}"; do
    echo "=== Analyzing $(basename $repo) ==="
    beaconled --repo "$repo" --since 1w --format json
done
```

### Component Analysis
```bash
#!/bin/bash
# component-analysis.sh
# Analyze specific directories

# Backend changes
beaconled --since 1w --format json | jq '.files[] | select(.path | startswith("src/backend"))'

# Frontend changes
beaconled --since 1w --format json | jq '.files[] | select(.path | endswith(".tsx") or endswith(".ts"))'

# Documentation changes
beaconled --since 1w --format json | jq '.files[] | select(.path | endswith(".md"))'
```

## Integration Examples

### GitHub Actions Integration
```yaml
# .github/workflows/daily-beaconled.yml
name: Daily Beacon Analysis

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install Beacon
        run: pip install beaconled

      - name: Generate Daily Report
        run: |
          beaconled --since 1d --format json > daily-report.json

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: daily-beaconled-report
          path: daily-report.json
```

### Slack Integration
```python
#!/usr/bin/env python3
# slack-daily-report.py
import json
import requests
from datetime import datetime, timedelta
from beaconled.core.analyzer import GitAnalyzer
from beaconled.formatters.json_format import JSONFormatter

def send_daily_report(webhook_url):
    analyzer = GitAnalyzer()

    # Yesterday's stats
    yesterday = datetime.now() - timedelta(days=1)
    stats = analyzer.analyze_range(
        since=yesterday.strftime("%Y-%m-%d"),
        until=datetime.now().strftime("%Y-%m-%d")
    )

    message = {
        "text": "📊 Daily Development Report",
        "attachments": [{
            "color": "good",
            "fields": [
                {"title": "Commits", "value": str(stats.total_commits), "short": True},
                {"title": "Files Changed", "value": str(stats.total_files_changed), "short": True},
                {"title": "Lines Added", "value": str(stats.total_insertions), "short": True},
                {"title": "Lines Deleted", "value": str(stats.total_deletions), "short": True}
            ]
        }]
    }

    requests.post(webhook_url, json=message)

if __name__ == "__main__":
    import sys
    send_daily_report(sys.argv[1])
```

## Advanced Usage

### Custom Filtering
```bash
# Filter by author
beaconled --since 1w --format json | jq 'select(.author == "John Doe")'

# Filter by file type
beaconled --since 1w --format json | jq '.files[] | select(.path | endswith(".py"))'

# Filter by impact
beaconled --since 1w --format json | jq 'select(.total_insertions > 100)'
```

### Batch Processing
```bash
#!/bin/bash
# batch-analysis.sh
# Process multiple time periods

PERIODS=("1d" "1w" "1m" "3m")
PERIOD_NAMES=("1day" "1week" "1month" "3months")

for i in "${!PERIODS[@]}"; do
    period="${PERIODS[$i]}"
    name="${PERIOD_NAMES[$i]}"
    echo "=== Analysis since $period ==="
    beaconled --since "$period" --format json > "report-$name.json"
done
```

### Performance Monitoring
```bash
#!/bin/bash
# performance-monitor.sh
# Track development velocity over time

LOG_FILE="development-velocity.log"
DATE=$(date +%Y-%m-%d)

# Get weekly stats
stats=$(beaconled --since 1w --format json)
commits=$(echo $stats | jq '.total_commits')
files=$(echo $stats | jq '.total_files_changed')
insertions=$(echo $stats | jq '.total_insertions')
deletions=$(echo $stats | jq '.total_deletions')

echo "$DATE,$commits,$files,$insertions,$deletions" >> $LOG_FILE
```

## Quick Reference Commands

| Task | Command |
|------|---------|
| Latest commit | `beaconled` |
| Specific commit | `beaconled abc123` |
| Last week | `beaconled --since 1w` |
| Last month | `beaconled --since 1m` |
| JSON output | `beaconled --format json` |
| Extended details | `beaconled --format extended` |
| Custom repo | `beaconled --repo /path/to/repo` |
| Date range | `beaconled --since 2025-07-01 --until 2025-07-31` |
| Analyze last 5 commits | `beaconled --count 5` |
| Analyze between commits | `beaconled abc123..xyz789` |
| Analyze by date range (UTC) | `beaconled --since 2025-07-01T00:00 --until 2025-07-31T23:59` |
| Using date only (assumes 00:00 UTC) | `beaconled --since 2025-07-01 --until 2025-07-31` |
| Using relative dates | `beaconled --since 1w` |

## Date Format Reference

### Default Behavior
- When no date range is specified:
  - `--since` defaults to `7d` (7 days ago in UTC)
  - `--until` defaults to `now` (current time in UTC)
- When using `--since` without `--until`, `--until` defaults to `now`
- When using `--until` without `--since`, `--since` defaults to `7d`

### Relative Formats
```
1d      # 1 day ago from now in UTC
2w      # 2 weeks ago from now in UTC
3m      # 3 months ago from now in UTC (approximate, using 4 weeks/month)
1y      # 1 year ago from now in UTC (approximate, using 52 weeks/year)
```

### Absolute Formats (UTC Only)
```
2025-01-15              # January 15, 2025 at 00:00 UTC
2025-01-15 14:30        # January 15, 2025 at 14:30 UTC
2025-01-15 14:30:45     # January 15, 2025 at 14:30:45 UTC
```

### Special Keywords
```
now        # Current time in UTC
```

### Timezone Handling
- All input dates are interpreted as UTC
- Results are displayed in UTC
- No timezone conversion is performed

Example with timezone handling:
```bash
# Analyze commits between 9 AM to 5 PM UTC
beaconled --since 2025-01-15T09:00 --until 2025-01-15T17:00
```
