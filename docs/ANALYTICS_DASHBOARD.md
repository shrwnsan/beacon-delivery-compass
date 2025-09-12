# Analytics Dashboard

A short interpretation guide for Product/PM stakeholders. Use this to read weekly reports quickly.

## The 4 signals to read first
- Velocity: commits, files, lines added/removed. Expect consistency week to week. Big swings = context change or risk.
- Impact: which components changed (core logic, tests, docs, config). Healthy mixes include tests with core changes.
- Risk movement: large diffs in core or concentrated ownership indicate higher risk; call out in review.
- Scope churn: net change vs previous period; negative can be cleanup, positive may be new feature work.

## What “good” looks like
- Balanced additions/deletions across components
- Tests present for high-impact core changes
- No single contributor dominates core areas
- Week-over-week velocity within expected band

## Example interpretation
- High additions with few deletions: new feature work; confirm test coverage and downstream impacts.
- Many config changes: investigate release/deployment changes or environment stability.
- Spike in core logic without tests: flag for verification and follow-up.

## Where the numbers come from
Generated from git history using Beacon’s CLI. For details on producing reports, see Engineer Quickstart: delivery/quickstart.md.

---

Developer details, dashboards, and integrations are below (optional).

## Detailed metrics and examples
- Commit Frequency, Files Changed, Lines Added/Deleted, Net Change, Component Impact
- Health indicators: balanced vs warning vs critical
- Sample visualizations and scripts for analytics

## Developer Reference

### Programmatic Access

For automation and dashboard integration, use JSON format:

```bash
# Weekly team metrics in JSON
beaconled --since 1w --format json

# Example JSON output structure:
{
  "period": {"since": "1w", "until": "now"},
  "total_commits": 25,
  "total_files_changed": 87,
  "total_insertions": 1543,
  "total_deletions": 432,
  "authors": {
    "john.doe@example.com": 12,
    "jane.smith@example.com": 13
  },
  "file_types": {
    ".py": 45,
    ".md": 8,
    ".json": 3
  }
}
```

### CI/CD Integration

**GitHub Actions:**
```yaml
- name: Generate Analytics
  run: |
    beaconled --since 1w --format json > weekly-metrics.json
    # Process metrics for dashboard/notifications
```

**GitLab CI:**
```yaml
analytics:
  script:
    - pip install beaconled
    - beaconled --since 1w --format json
  artifacts:
    reports:
      analytics: weekly-metrics.json
```

### Dashboard Integrations

**Grafana/InfluxDB:**
```python
#!/usr/bin/env python3
import json
from influxdb import InfluxDBClient
from beaconled.core.analyzer import GitAnalyzer

analyzer = GitAnalyzer()
stats = analyzer.get_range_analytics("1w")

# Push to InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
point = {
    "measurement": "dev_metrics",
    "fields": {
        "commits": stats.total_commits,
        "files_changed": stats.total_files_changed,
        "velocity": stats.total_commits / 7  # commits per day
    }
}
client.write_points([point])
```

**Slack Integration:**
```bash
#!/bin/bash
# slack-weekly-report.sh
METRICS=$(beaconled --since 1w --format json)
COMMITS=$(echo $METRICS | jq '.total_commits')
FILES=$(echo $METRICS | jq '.total_files_changed')

curl -X POST -H 'Content-type: application/json' \
  --data "{
    'text': '📊 Weekly Dev Summary: $COMMITS commits, $FILES files changed'
  }" \
  $SLACK_WEBHOOK_URL
```

### Analytics Scripts

Ready-to-use scripts are available in the repository:

- `scripts/analytics_reporter.py` - Advanced analytics with range analysis
- `scripts/commit-analytics.sh` - Quick commit analysis for git hooks
- See [Development Scripts Documentation](development/scripts.md) for full reference

### Custom Metric Calculations

**Velocity Tracking:**
```python
from beaconled.core.analyzer import GitAnalyzer

analyzer = GitAnalyzer()
weekly_stats = analyzer.get_range_analytics("1w")

# Calculate key metrics
velocity = weekly_stats.total_commits / 7  # commits per day
churn = weekly_stats.total_deletions / weekly_stats.total_insertions
impact_score = weekly_stats.total_files_changed / weekly_stats.total_commits

print(f"Daily velocity: {velocity:.1f} commits")
print(f"Code churn: {churn:.2f} (lower is better)")
print(f"Change complexity: {impact_score:.1f} files per commit")
```

### Troubleshooting

**Large Repositories:**
- Use specific date ranges instead of relative times
- Consider sampling for very active repos (>1000 commits/week)
- Use `--format json` for faster processing

**Performance Optimization:**
```bash
# Fast analysis for large repos
beaconled --since "2024-01-01" --until "2024-01-07" --format json

# Batch processing multiple periods
for week in 1 2 3 4; do
  beaconled --since "${week}w" --until "$((week-1))w" --format json
done
```

For more detailed integration examples, see:
- [Integration Guide](delivery/integrations.md)
- [Development Scripts](development/scripts.md)
- [Product Analytics](development/analytics/product.md)
