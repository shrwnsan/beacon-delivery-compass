# Advanced Usage Examples

This document covers advanced usage patterns including date handling, custom metrics, and integration examples. All dates are handled in UTC.

Each example below explains **what the analysis does**, **why it's valuable**, and **what insights you'll gain** from running it in your development workflow.

## Date Handling

### Date Range Analysis with UTC

**What this does**: Analyzes commit activity within a specific time window using precise UTC timestamps.

**Why it's valuable**:
- **Sprint Planning**: See exactly how much work was completed in the last sprint
- **Release Preparation**: Audit all changes since your last release
- **Performance Reviews**: Generate objective data about team productivity over quarters
- **Incident Response**: Quickly identify all changes made during a problematic time period

**What you'll get**: Commit counts, author activity, and code change volumes for any date range you specify.

```python
from beaconled.core.analyzer import GitAnalyzer
from datetime import datetime, timezone

# Initialize analyzer with a repository
analyzer = GitAnalyzer('/path/to/repo')

# Define UTC date range using datetime objects
start = datetime(2025, 7, 1, tzinfo=timezone.utc)  # July 1, 2025 00:00 UTC
end = datetime(2025, 7, 31, 23, 59, 59, tzinfo=timezone.utc)  # July 31, 2025 23:59:59 UTC

# Or use concise string format
# stats = analyzer.get_range_analytics("2025-07-01", "2025-07-31")

# Or use relative dates
# stats = analyzer.get_range_analytics("7d")  # Last 7 days
# stats = analyzer.get_range_analytics("1m")  # Last month (4 weeks)

# Get analytics for the specified range
stats = analyzer.get_range_analytics(start, end)

print(f"Analysis from {start} to {end}")
print(f"Total commits: {stats.total_commits}")
```

### Handling Empty Commit Ranges

**What this does**: Gracefully handles time periods with no development activity.

**Why it's valuable**:
- **Holiday Planning**: Confirm no critical changes happened during vacation periods
- **Deployment Windows**: Verify code freeze periods were respected
- **Audit Compliance**: Prove no unauthorized changes occurred during maintenance windows

**What you'll get**: Clear confirmation of zero activity or error messages explaining why data is missing.

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


## Team Reporting Workflows

### Executive Summary Report

**What this does**: Creates a high-level dashboard of team productivity metrics.

**Why executives need this**:
- **Investment Decisions**: See if engineering resources are being used effectively
- **Team Performance**: Compare productivity across different time periods
- **Resource Planning**: Understand team velocity to plan hiring or project timelines
- **Stakeholder Updates**: Provide concrete numbers for board meetings or investor calls

**What you'll get**: A JSON file with total commits, active contributors, and productivity index (lines of code per commit) that executives can easily understand.

```bash
#!/bin/bash
# generate-executive-report.sh
source .venv/bin/activate

beaconled --since 1m --format json | \
jq '{
  period: "\(.start_date) to \(.end_date)",
  total_commits: .total_commits,
  contributors: (.authors | length),
  productivity_index: (if .total_commits > 0 then (.total_lines_added / .total_commits) else 0 end | floor * 10 / 10)
}' > executive-report.json
```

### Engineering Team Report

**What this does**: Generates detailed activity logs for engineering managers and team leads.

**Why engineering managers need this**:
- **1:1 Meetings**: Come prepared with specific examples of each developer's contributions
- **Performance Reviews**: Have objective data about commit frequency and types of work
- **Workload Distribution**: Identify if work is evenly distributed or if some developers are overloaded
- **Recognition**: Spot developers who deserve public recognition for their contributions

**What you'll get**: A detailed JSON file with every commit, author, timestamp, and file count - perfect for understanding individual contributions and team dynamics.

```bash
#!/bin/bash
# team-report.sh
source .venv/bin/activate

beaconled --since 1w --format json | \
jq '.commits[] | {
  author: .author,
  date: .date,
  message: .message,
  files: .files_changed
}' > team-report.json
```

## Historical Trend Analysis

### 6-Month Trend Report

**What this does**: Creates a visual chart showing how development activity changes over time.

**Why this matters for long-term planning**:
- **Capacity Planning**: See seasonal patterns in your team's output
- **Project Planning**: Understand your team's natural velocity cycles
- **Hiring Decisions**: Identify periods when you consistently need more capacity
- **Process Improvement**: Spot drops in productivity that might indicate process problems

**What you'll get**: A PNG chart file showing commit trends over 6 months that you can include in presentations or planning documents.

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

**What this does**: Provides comprehensive analysis of codebase stability, technical debt indicators, and refactoring impact over time.

**Why this is critical for development teams**:
- **Technical Debt Tracking**: Identify areas where code is becoming harder to maintain
- **Refactoring Impact**: Measure the effectiveness of refactoring efforts
- **Release Risk Assessment**: Understand stability before major releases
- **Team Velocity**: Track how codebase health affects development speed
- **Architecture Decisions**: Make data-driven choices about system architecture

#### Basic Health Overview

**What you'll get**: Essential metrics showing the relationship between commits and files changed, helping you understand codebase stability trends.

```bash
# Basic code health metrics
beaconled --since 1y --format json | \
jq '{
  period: "\(.start_date) to \(.end_date)",
  total_commits: .total_commits,
  total_files_changed: .total_files_changed,
  stability_metrics: {
    avg_files_per_commit: (if .total_commits > 0 then (.total_files_changed / .total_commits | floor * 100 / 100) else 0 end),
    commit_frequency: (.total_commits / 365 | floor * 100 / 100),
    change_intensity: (if .total_commits > 0 then (.total_lines_added / .total_commits | floor) else 0 end)
  }
}' > code-health-basic.json
```

#### Multi-Period Health Comparison

**What this does**: Compares code health metrics across different time periods to identify trends.

**Why it's valuable**: Helps you see if your codebase is becoming more or less stable over time, and whether refactoring efforts are paying off.

```bash
#!/bin/bash
# multi-period-health.sh - Compare health across 3 monthly periods
echo '{"health_evolution": [' > health-comparison.json

for i in {3..1}; do
  start="${i}m"
  end=$((i-1))
  end_period="${end}m"

  if [ $end -eq 0 ]; then
    end_period="now"
  fi

  beaconled --since "$start" --until "$end_period" --format json | \
  jq --arg period "Month_$i" '{
    period: $period,
    commits: .total_commits,
    files_changed: .total_files_changed,
    stability_score: (if .total_commits > 0 then (100 - (.total_files_changed / .total_commits * 10) | floor) else 100 end),
    churn_ratio: (if .total_commits > 0 then (.total_files_changed / .total_commits | floor * 100 / 100) else 0 end)
  }'

  if [ $i -gt 1 ]; then
    echo ','
  fi
done >> health-comparison.json

echo ']}' >> health-comparison.json
echo "Generated health-comparison.json with 3-month trend analysis"
```

#### Technical Debt Assessment

**What this does**: Identifies patterns that indicate growing technical debt or quality issues.

**Why teams need this**: Helps prioritize refactoring efforts and identify risky areas before they become major problems.

```bash
# Technical debt analysis
beaconled --since 3m --format json | \
jq '{
  analysis_period: "\(.start_date) to \(.end_date)",
  total_commits: .total_commits,

  debt_indicators: {
    # High-churn commits (>10 files changed)
    large_change_commits: [
      .commits[] | select(.files_changed > 10) | {
        hash: .hash[0:7],
        files_changed: .files_changed,
        author: .author,
        message: (.message | split("\n")[0] | .[0:60])
      }
    ],

    # Potential bug fix commits
    bug_fix_commits: [
      .commits[] | select(.message | test("fix|bug|patch|hotfix"; "i")) | {
        hash: .hash[0:7],
        message: (.message | split("\n")[0] | .[0:60]),
        date: .date
      }
    ],

    # Health metrics
    avg_files_per_commit: (if .total_commits > 0 then (.total_files_changed / .total_commits | floor * 100 / 100) else 0 end),
    large_commit_percentage: (if .total_commits > 0 then ([.commits[] | select(.files_changed > 10)] | length / .total_commits * 100 | floor) else 0 end),
    bug_fix_percentage: (if .total_commits > 0 then ([.commits[] | select(.message | test("fix|bug|patch|hotfix"; "i"))] | length / .total_commits * 100 | floor) else 0 end)
  },

  # Simple health score (0-100, higher is better)
  health_score: (
    100 -
    (if .total_commits > 0 then (.total_files_changed / .total_commits * 8) else 0 end) -
    ([.commits[] | select(.files_changed > 10)] | length * 2) -
    ([.commits[] | select(.message | test("fix|bug|patch|hotfix"; "i"))] | length * 1)
  ) | floor | if . < 0 then 0 else . end
}' > technical-debt-assessment.json
```

#### Release Readiness Health Check

**What this does**: Assesses code stability and risk factors before a release.

**Why it's critical**: Helps teams make informed decisions about release timing and identifies areas that need extra testing.

```bash
# Pre-release health assessment
beaconled --since "2w" --format json | \
jq '{
  release_period: "\(.start_date) to \(.end_date)",
  total_commits: .total_commits,

  risk_assessment: {
    # Recent large changes (high risk)
    large_commits_count: [.commits[] | select(.files_changed > 15)] | length,

    # Bug fixes in release window
    recent_bug_fixes: [.commits[] | select(.message | test("fix|bug|hotfix"; "i"))] | length,

    # Very recent changes (last 24 hours)
    last_minute_changes: [
      .commits[] | select(
        (.date | strptime("%Y-%m-%d %H:%M:%S") | mktime) > (now - 86400)
      )
    ] | length,

    # Activity level assessment
    commit_velocity: (if .total_commits > 0 then (.total_commits / 14) else 0 end | floor * 100 / 100)
  },

  # Release readiness score (0-100, higher is safer to release)
  readiness_score: (
    100 -
    ([.commits[] | select(.files_changed > 15)] | length * 15) -
    ([.commits[] | select(.message | test("fix|bug|hotfix"; "i"))] | length * 10) -
    (if .total_commits > 50 then 25 else 0 end) -
    ([
      .commits[] | select(
        (.date | strptime("%Y-%m-%d %H:%M:%S") | mktime) > (now - 86400)
      )
    ] | length * 20)
  ) | floor | if . < 0 then 0 else . end,

  recommendation: (
    if (
      100 -
      ([.commits[] | select(.files_changed > 15)] | length * 15) -
      ([.commits[] | select(.message | test("fix|bug|hotfix"; "i"))] | length * 10) -
      (if .total_commits > 50 then 25 else 0 end)
    ) >= 80 then "✅ Ready for release"
    elif (
      100 -
      ([.commits[] | select(.files_changed > 15)] | length * 15) -
      ([.commits[] | select(.message | test("fix|bug|hotfix"; "i"))] | length * 10)
    ) >= 60 then "⚠️  Proceed with caution - extra testing recommended"
    else "🚫 High risk - consider delaying release"
    end
  )
}' > release-readiness.json
```

#### Advanced Health Visualization (Python Script)

**What this does**: Creates visual charts showing code health trends over time.

**Why visualization matters**: Charts make it easy to spot trends, communicate with stakeholders, and make data-driven decisions about technical debt.

```python
#!/usr/bin/env python3
# health-visualization.py - Requires: pip install matplotlib pandas
"""
Code Health Visualization Script
Generates charts showing codebase health trends using beaconled data

Usage: python health-visualization.py
Output: Saves charts as PNG files
"""

import subprocess
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def get_beaconled_data(since_period, until_period="now"):
    """Get data from beaconled CLI"""
    cmd = ["beaconled", "--since", since_period, "--format", "json"]
    if until_period != "now":
        cmd.extend(["--until", until_period])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def create_health_trends():
    """Create health trend visualization"""
    # Collect weekly data for last 8 weeks
    weeks_data = []
    for week in range(8, 0, -1):
        since = f"{week}w"
        until = f"{week-1}w" if week > 1 else "now"

        data = get_beaconled_data(since, until)
        if data and data.get('total_commits', 0) > 0:
            commits = data['total_commits']
            files_changed = data.get('total_files_changed', 0)

            weeks_data.append({
                'week': f"Week -{week}",
                'commits': commits,
                'files_per_commit': files_changed / commits if commits > 0 else 0,
                'stability_index': max(0, 100 - (files_changed / commits * 10)) if commits > 0 else 0
            })

    if not weeks_data:
        print("No data available for visualization")
        return

    df = pd.DataFrame(weeks_data)

    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Code Health Evolution - Last 8 Weeks', fontsize=16)

    # Weekly commits
    ax1.plot(df['week'], df['commits'], marker='o', linewidth=2, color='#2E86AB')
    ax1.set_title('Weekly Commit Volume')
    ax1.set_ylabel('Commits')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)

    # Files per commit (focus metric)
    ax2.plot(df['week'], df['files_per_commit'], marker='s', linewidth=2, color='#A23B72')
    ax2.set_title('Files Changed per Commit\n(Lower = More Focused Changes)')
    ax2.set_ylabel('Files/Commit')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)

    # Stability index
    ax3.plot(df['week'], df['stability_index'], marker='^', linewidth=2, color='#F18F01')
    ax3.set_title('Stability Index\n(Higher = More Stable)')
    ax3.set_ylabel('Stability Score')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)

    # Summary metrics
    ax4.axis('off')
    current_stability = df['stability_index'].iloc[-1] if len(df) > 0 else 0
    avg_files_per_commit = df['files_per_commit'].mean()
    total_commits = df['commits'].sum()

    summary_text = f"""
    📊 Health Summary

    Current Stability: {current_stability:.1f}/100
    Avg Files/Commit: {avg_files_per_commit:.1f}
    Total Commits: {int(total_commits)}

    Trend: {"📈 Improving" if len(df) > 1 and df['stability_index'].iloc[-1] > df['stability_index'].iloc[0] else "📉 Declining" if len(df) > 1 else "📊 Stable"}
    """
    ax4.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

    plt.tight_layout()
    plt.savefig('code-health-trends.png', dpi=300, bbox_inches='tight')
    print("📊 Generated code-health-trends.png")
    plt.close()

if __name__ == "__main__":
    try:
        create_health_trends()
        print("✅ Health visualization complete!")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install matplotlib pandas")
    except FileNotFoundError:
        print("❌ beaconled command not found. Make sure it's installed and in PATH")
    except Exception as e:
        print(f"❌ Error generating visualization: {e}")
```

## Advanced Filtering Techniques

### Component-Based Filtering (Not Available Yet)

**What this will do**: Analyze changes by logical components (frontend, backend, database, tests).

**Why teams will want this**:
- **Specialization Insights**: See which developers work on which parts of the system
- **Risk Management**: Identify components that change frequently (higher risk)
- **Architecture Decisions**: Understand coupling between different system components
- **Team Organization**: Organize teams around the components they actually work on

**What you'll get in future releases**: Component-level metrics showing which parts of your system get the most attention and which developers are experts in each area.

```bash
# Note: Component analysis requires file-level data not yet available in current version
# This is a placeholder for future functionality
echo "Component-based filtering is planned for a future release"
echo "Current version provides commit-level analysis only"
```

### Author Impact Analysis

**What this does**: Ranks developers by their code contribution volume and activity.

**Why this is valuable for team management**:
- **Fair Recognition**: Identify developers who contribute a lot but might not be vocal in meetings
- **Workload Balance**: Spot developers who might be carrying too much of the load
- **Mentorship Opportunities**: Connect high-output developers with newer team members
- **Succession Planning**: Identify key contributors and ensure knowledge isn't siloed

**What you'll get**: A ranked list of developers showing commits, files touched, and lines of code - helping you understand who your key contributors are and how work is distributed.

```bash
# Show impact by author (simplified version)
beaconled --since 1m --format json | \
jq '.commits | group_by(.author) | map({
  author: .[0].author,
  commits: length,
  files_changed: (map(.files_changed // 0) | add),
  lines_added: (map(.lines_added // 0) | add)
}) | sort_by(.lines_added) | reverse'
```

### File Type Focus (Commit-level Analysis)

**What this does**: Identifies commits related to specific technologies or file types.

**Why this helps with technology decisions**:
- **Migration Tracking**: See how much effort is being spent on old vs new technologies
- **Skill Development**: Identify which developers are working with which technologies
- **Technical Debt**: Find code areas that require frequent changes (potential refactor targets)
- **Training Needs**: See which technologies your team touches most often

**What you'll get**: A filtered list of commits related to specific file types or technologies, helping you understand where your team spends their time and what skills are most important.

```bash
# Track Python-related commits (since file-level data not yet available)
beaconled --since 2w --format json | \
jq '[.commits[] | select(.message | contains(".py")) | {
  hash: .hash,
  message: (.message | split("\n")[0]),
  author: .author,
  date: .date
}] | .[0:10]'
```

## Automation Scripts

### Daily Standup Automation

**What this does**: Automatically generates a summary of yesterday's development activity.

**Why this improves standups**:
- **Preparation**: Everyone comes to standup with concrete data about what happened
- **Accountability**: No more vague "worked on stuff" - see exactly what was accomplished
- **Blocked Work Identification**: Quickly spot if someone had zero commits (might be blocked)
- **Team Coordination**: See if multiple people worked on similar areas (potential conflicts)

**What you'll get**: A daily report showing commits, files changed, and top contributors from the last 24 hours - perfect for starting productive standup discussions.

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

**What this does**: Automatically checks if high-impact changes include corresponding tests.

**Why this prevents production issues**:
- **Quality Assurance**: Catch risky changes before they reach production
- **Testing Culture**: Encourage developers to write tests for important changes
- **Risk Mitigation**: Automatically flag changes that might need extra review
- **Deployment Safety**: Block releases that don't meet quality standards

**What you'll get**: An automated pass/fail check that integrates with your CI pipeline, helping maintain code quality without manual oversight.

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

**What this does**: Automatically creates professional release notes from your commit messages.

**Why this saves time and improves communication**:
- **Customer Communication**: Automatically inform users about new features and fixes
- **Internal Documentation**: Keep track of what changed between releases
- **Marketing Support**: Provide marketing team with feature lists for announcements
- **Compliance**: Maintain detailed change logs for audit requirements

**What you'll get**: A properly formatted Markdown file with features, bug fixes, and documentation changes organized by category - ready to publish or share with stakeholders.

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

## Implementation Guide

### Getting Started Roadmap

**Week 1: Foundation**
- Set up the Executive Summary Report for monthly leadership updates
- Implement the Daily Standup Automation for immediate team value
- Create your first 6-month trend analysis to establish baseline metrics

**Week 2-3: Team Integration**
- Deploy the Engineering Team Report for weekly manager reviews
- Set up the Release Notes Generator to automate your next release
- Begin Author Impact Analysis to understand contribution patterns

**Week 4+: Advanced Analytics**
- Implement Code Health Evolution tracking for long-term planning
- Set up CI Quality Gates if you have a robust testing culture
- Customize examples for your specific technology stack and workflows

### Measuring Success

**Leadership Metrics** (Monthly Reviews):
- Productivity trends are stable or improving over time
- Team velocity is predictable for project planning
- Resource allocation decisions are data-driven rather than gut-feeling

**Team Metrics** (Weekly Reviews):
- Work distribution is balanced across team members
- Recognition is based on objective contribution data
- Technical discussions reference concrete change patterns

**Process Metrics** (Daily/CI Integration):
- Release notes are generated automatically and accurately
- Quality gates catch risky changes before production
- Standup discussions are focused on actual work accomplished

## Best Practices for Advanced Usage

1. **Start Simple**: Begin with 2-3 key reports that solve immediate pain points
2. **Consistent Timing**: Run reports at the same time each week/month for trend accuracy
3. **Stakeholder Alignment**: Customize reports for your audience (executives vs. engineers)
4. **Automation First**: Schedule reports to run automatically rather than manually
5. **Actionable Insights**: Focus on metrics that lead to concrete decisions or changes

## Next Steps
- [API Reference](../api/api-reference.md) - Complete command reference
- [Analytics Dashboard](../ANALYTICS_DASHBOARD.md) - Metric interpretation guide
- [Integrations](../integrations.md) - CI/CD and team workflow integration
