# Advanced Usage Examples

This document covers advanced usage patterns including date handling, custom metrics, and integration examples. All dates are handled in UTC.

## Date Handling

### Date Range Analysis with UTC

```python
from beaconled.core.analyzer import GitAnalyzer
from datetime import datetime, timezone

# Initialize analyzer with a repository
analyzer = GitAnalyzer('/path/to/repo')

# Define UTC date range
start = datetime(2025, 7, 1, tzinfo=timezone.utc)  # July 1, 2025 00:00 UTC
end = datetime(2025, 7, 31, 23, 59, 59, tzinfo=timezone.utc)  # July 31, 2025 23:59:59 UTC

# Get analytics for the specified range
stats = analyzer.get_range_analytics(start, end)

print(f"Analysis from {start} to {end}")
print(f"Total commits: {stats.total_commits}")
```

### Handling Empty Commit Ranges

```python
from beaconled.core.analyzer import GitAnalyzer
from datetime import datetime, timezone

try:
    analyzer = GitAnalyzer('/path/to/repo')
    # This range might be empty if no commits exist in this period
    stats = analyzer.get_range_analytics("2026-01-01", "2026-01-31")

    if stats.total_commits == 0:
        print("No commits found in the specified range")
    else:
        print(f"Found {stats.total_commits} commits")

except ValueError as e:
    print(f"Error analyzing range: {e}")
```

## Custom Metric Configurations

### Defining Custom Metrics
Create `custom_metrics.json`:
```json
{
  "complexity_metrics": {
    "cyclomatic_complexity": {
      "threshold": 15,
      "weight": 0.8
    },
    "cognitive_complexity": {
      "threshold": 25,
      "weight": 0.9
    }
  },
  "documentation_metrics": {
    "doc_coverage": {
      "target": 85,
      "extensions": [".py", ".js", ".ts"]
    }
  }
}
```

### Loading Custom Metrics
```python
from beaconled.core.analyzer import GitAnalyzer
import json

analyzer = GitAnalyzer()
with open('custom_metrics.json') as f:
    metrics = json.load(f)

stats = analyzer.get_commit_stats()
complexity_score = sum(
    metric['weight'] * len([f for f in stats.files if f.complexity > metric['threshold']])
    for metric in metrics['complexity_metrics'].values()
)
```

## Team Reporting Workflows

### Executive Summary Report
```bash
#!/bin/bash
# generate-executive-report.sh
source .venv/bin/activate

beaconled --since 1m --format json | \
jq '{
  period: "\(.start_date) to \(.end_date)",
  total_commits: .total_commits,
  contributors: (.authors | length),
  productivity_index: (.total_lines_added / .total_commits | round(1)),
  quality_index: ((.total_files_changed - (.commits[].files[] | select(.impact == "high") | length)) / .total_files_changed * 100 | round(1))
}' > executive-report.json
```

### Engineering Team Report
```bash
#!/bin/bash
# team-report.sh
source .venv/bin/activate

beaconled --since 1w --format json | \
jq '.commits[] | {
  author: .author,
  date: .date,
  message: .message,
  files: .files_changed,
  impact: (.files | map(.impact) | unique | join(", "))
}' > team-report.json
```

## Historical Trend Analysis

### 6-Month Trend Report
```python
# trend-analysis.py
from beaconled.core.analyzer import GitAnalyzer
import matplotlib.pyplot as plt

analyzer = GitAnalyzer()
months = []
commits = []

for i in range(6, 0, -1):
    since = f"{i}m"
    until = f"{i-1}m" if i > 1 else "1m"
    stats = analyzer.get_range_analytics(since, until)
    months.append(stats.start_date.strftime("%b %Y"))
    commits.append(stats.total_commits)

plt.plot(months, commits, marker='o')
plt.title('Commit Trends - Last 6 Months')
plt.xlabel('Month')
plt.ylabel('Commits')
plt.savefig('commit-trends.png')
```

### Code Health Evolution
```bash
beaconled --since 1y --format json | \
jq -s 'group_by(.start_date | fromdate | strftime("%Y-%m")) |
map({
  month: .[0].start_date | fromdate | strftime("%Y-%m"),
  commits: length,
  test_ratio: (map(.files[] | select(.component == "Tests")) | length) / (map(.files) | length) * 100,
  docs_ratio: (map(.files[] | select(.component == "Documentation")) | length) / (map(.files) | length) * 100
})' > code-health-evolution.json
```

## Advanced Filtering Techniques

### Component-Based Filtering
```bash
# Analyze only core logic changes
beaconled --format json | jq '{
  commit: .hash,
  core_changes: [.files[] | select(.component == "Core Logic") | {
    path: .path,
    changes: .lines_changed
  }]
}'
```

### Author Impact Analysis
```bash
# Show impact by author
beaconled --since 1m --format json | \
jq '.commits | group_by(.author) | map({
  author: .[0].author,
  commits: length,
  high_impact: map(.files[] | select(.impact == "high")) | length,
  lines_added: map(.lines_added) | add
}) | sort_by(.lines_added) | reverse'
```

### File Type Focus
```bash
# Track TypeScript file changes
beaconled --since 2w --format json | \
jq '[.commits[].files[] | select(.path | endswith(".ts"))] |
group_by(.path) |
map({
  file: .[0].path,
  changes: length,
  authors: (map(.author) | unique | length)
}) | sort_by(.changes) | reverse | .[0:10]'
```

## Automation Scripts

### Daily Standup Automation
```python
# daily-standup.py
from beaconled.core.analyzer import GitAnalyzer
from datetime import datetime, timedelta

analyzer = GitAnalyzer()
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
stats = analyzer.get_range_analytics("1d")

print(f"🚀 Daily Development Report - {yesterday}")
print(f"Total commits: {stats.total_commits}")
print(f"Files changed: {stats.total_files_changed}")
print("Top contributors:")
for author, count in stats.authors.items():
    print(f"  - {author}: {count} commits")
```

### CI Quality Gate
```python
# ci-quality-gate.py
from beaconled.core.analyzer import GitAnalyzer
import sys

analyzer = GitAnalyzer()
stats = analyzer.get_range_analytics("main")

high_impact_no_tests = sum(
    1 for commit in stats.commits
    for file in commit.files
    if file.impact == "high" and not any(
        f.path.endswith("_test.py") for f in commit.files
    )
)

if high_impact_no_tests > 0:
    print(f"❌ {high_impact_no_tests} high-impact changes without tests")
    sys.exit(1)
else:
    print("✅ All high-impact changes have tests")
    sys.exit(0)
```

### Release Notes Generator
```bash
#!/bin/bash
# generate-release-notes.sh
source .venv/bin/activate

beaconled --since "$(git describe --tags --abbrev=0)" --format json | \
jq -r '"# Release Notes\n",
  "## New Features",
  (.commits[] | select(.message | test("feat"; "i")) |
    "- \(.message) (by \(.author))"),
  "\n## Bug Fixes",
  (.commits[] | select(.message | test("fix"; "i")) |
    "- \(.message) (by \(.author))"),
  "\n## Documentation",
  (.commits[] | select(.message | test("docs"; "i")) |
    "- \(.message) (by \(.author))")' > RELEASE_NOTES.md
```

## Best Practices for Advanced Usage

1. **Custom Metrics**: Start with 2-3 key metrics aligned with team goals
2. **Historical Analysis**: Compare monthly trends rather than daily fluctuations
3. **Automation**: Schedule reports to run during off-peak hours
4. **Filtering**: Combine component and impact filters for focused insights
5. **Visualization**: Use Grafana or similar tools for dynamic dashboards

## Next Steps
- [API Reference](../api/api-reference.md) - Complete command reference
- [Analytics Dashboard](../ANALYTICS_DASHBOARD.md) - Metric interpretation guide
- [Integrations](../integrations.md) - CI/CD and team workflow integration
