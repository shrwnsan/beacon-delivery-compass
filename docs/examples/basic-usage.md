# Basic Usage Examples

This document provides practical examples for getting started with Beacon.

## Quick Start Examples

### 1. Analyze Latest Commit
```bash
# Simple analysis
beaconled

# Save to file
beaconled > latest-commit.txt

# JSON output for processing
beaconled --format json > commit-data.json
```

### 2. Analyze Specific Commit
```bash
# By hash
beaconled abc123def456

# By short hash
beaconled abc123

# By relative reference
beaconled HEAD~3
```

### 3. Range Analysis Examples
```bash
# Last week
beaconled --range --since "1 week ago"

# Last month
beaconled --range --since "1 month ago"

# Custom date range
beaconled --range --since "2025-07-01" --until "2025-07-31"

# Since last tag
beaconled --range --since "v1.0.0"
```

### 4. Different Output Formats
```bash
# Standard format (default)
beaconled --format standard

# Extended format with details
beaconled --format extended

# JSON for automation
beaconled --format json | jq '.files_changed'
```

## Team Workflow Examples

### Daily Standup Script
```bash
#!/bin/bash
# daily-summary.sh
echo "📊 Yesterday's Development Summary"
echo "================================="
beaconled --range --since "1 day ago" --format extended

# Save for team sharing
beaconled --range --since "1 day ago" --format json > daily-report.json
```

### Weekly Report Generation
```bash
#!/bin/bash
# weekly-report.sh
WEEK_START=$(date -d "last Monday" +%Y-%m-%d)
WEEK_END=$(date -d "last Sunday" +%Y-%m-%d)

echo "📈 Weekly Development Report ($WEEK_START to $WEEK_END)"
echo "======================================================"
beaconled --range --since "$WEEK_START" --until "$WEEK_END" --format extended

# Generate JSON for dashboard
beaconled --range --since "$WEEK_START" --until "$WEEK_END" --format json > weekly-dashboard.json
```

### Sprint Retrospective
```bash
#!/bin/bash
# sprint-retro.sh
SPRINT_LENGTH=14  # days

echo "🎯 Sprint Retrospective Analysis"
echo "==============================="
beaconled --range --since "${SPRINT_LENGTH} days ago" --format extended

# Team member contributions
beaconled --range --since "${SPRINT_LENGTH} days ago" --format json | jq '.authors'
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
    beaconled --repo "$repo" --range --since "1 week ago" --format json
done
```

### Component Analysis
```bash
#!/bin/bash
# component-analysis.sh
# Analyze specific directories

# Backend changes
beaconled --range --since "1 week ago" --format json | jq '.files[] | select(.path | startswith("src/backend"))'

# Frontend changes
beaconled --range --since "1 week ago" --format json | jq '.files[] | select(.path | endswith(".tsx") or endswith(".ts"))'

# Documentation changes
beaconled --range --since "1 week ago" --format json | jq '.files[] | select(.path | endswith(".md"))'
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
          beaconled --range --since "1 day ago" --format json > daily-report.json
      
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
beaconled --range --since "1 week ago" --format json | jq 'select(.author == "John Doe")'

# Filter by file type
beaconled --range --since "1 week ago" --format json | jq '.files[] | select(.path | endswith(".py"))'

# Filter by impact
beaconled --range --since "1 week ago" --format json | jq 'select(.total_insertions > 100)'
```

### Batch Processing
```bash
#!/bin/bash
# batch-analysis.sh
# Process multiple time periods

PERIODS=("1 day ago" "1 week ago" "1 month ago" "3 months ago")

for period in "${PERIODS[@]}"; do
    echo "=== Analysis since $period ==="
    beaconled --range --since "$period" --format json > "report-${period// /-}.json"
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
stats=$(beaconled --range --since "1 week ago" --format json)
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
| Last week | `beaconled --range --since "1 week ago"` |
| Last month | `beaconled --range --since "1 month ago"` |
| JSON output | `beaconled --format json` |
| Extended details | `beaconled --format extended` |
| Custom repo | `beaconled --repo /path/to/repo` |
| Date range | `beaconled --range --since "2025-07-01" --until "2025-07-31"` |
