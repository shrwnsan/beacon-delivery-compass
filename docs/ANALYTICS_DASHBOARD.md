# Analytics Dashboard

## Overview
The Analytics Dashboard provides comprehensive insights into development activity, team productivity, and code quality metrics for the Crypto Analysis Dashboard project.

## Quick Start

### Generate Commit Statistics
```bash
# Analyze latest commit (standard format)
./docs/scripts/commit-analytics.sh

# Analyze specific commit with detailed breakdown
./docs/scripts/commit-analytics.sh -d -f extended abc123

# Generate JSON output for automation
python docs/scripts/analytics_reporter.py --format json
```

### Weekly Team Report
```bash
# Generate weekly analytics
python docs/scripts/analytics_reporter.py --range --since "1 week ago"

# Monthly summary
python docs/scripts/analytics_reporter.py --range --since "1 month ago"
```

## Sample Outputs

### Standard Commit Format
```
📊 Commit Stats:
8 files changed
455 insertions, 36 deletions
Commit Hash: cce265f
Branch: feature/changelog-documentation
Author: John Developer
Date: 2024-01-15 14:30:00 -0800
Files by Type:
  - .md: 3 files
  - .py: 3 files
  - .ts: 2 files
```

### Extended Analysis Format
```
--Files Added/Modified:
8 files changed in total
462 insertions, 38 deletions
5 new files created
3 existing files improved

--Breakdown by Component:
Backend: 4 files (+250, -20)
Frontend: 3 files (+180, -15)
Documentation: 1 file (+32, -3)

--Impact Analysis:
High Impact: 2 files (core services)
Medium Impact: 4 files (API endpoints, components)
Low Impact: 2 files (documentation, config)

--Commit Details:
Hash: cce265f
Branch: feature/changelog-documentation
Author: John Developer
Date: 2024-01-15 14:30:00 -0800
Message: Add comprehensive changelog documentation
```

## Key Metrics Tracked

### Development Velocity
- **Commits per Day/Week**: Track development activity frequency
- **Lines of Code**: Insertions and deletions over time
- **Files Modified**: Scope of changes per commit
- **Feature Completion Rate**: Story points delivered per sprint

### Code Quality Indicators
- **Test Coverage**: Percentage and trend analysis
- **Component Impact**: High/medium/low impact file changes
- **Technical Debt**: Refactoring vs. feature development ratio
- **Documentation Updates**: Docs changes per feature

### Team Productivity
- **Individual Contributions**: Commit frequency and code ownership
- **Collaboration Patterns**: Cross-component contributions
- **Review Participation**: Code review engagement
- **Knowledge Sharing**: Mentoring and pair programming activity

## Analytics Tools

### Bash Script (`commit-analytics.sh`)
**Purpose**: Quick commit analysis with colored output
**Features**:
- Standard and extended output formats
- File type and component breakdown
- Branch and author filtering
- JSON output for automation

**Usage Examples**:
```bash
# Basic usage
./docs/scripts/commit-analytics.sh

# Detailed analysis
./docs/scripts/commit-analytics.sh -d -f extended

# Analyze specific branch
./docs/scripts/commit-analytics.sh -b feature/new-indicators

# JSON output for CI/CD
./docs/scripts/commit-analytics.sh -f json
```

### Python Reporter (`analytics_reporter.py`)
**Purpose**: Advanced analytics and range analysis
**Features**:
- Single commit detailed analysis
- Range analysis (weekly, monthly)
- Impact assessment
- Team contribution summaries

**Usage Examples**:
```bash
# Analyze latest commit
python docs/scripts/analytics_reporter.py

# Weekly team report
python docs/scripts/analytics_reporter.py --range --since "1 week ago"

# Custom date range
python docs/scripts/analytics_reporter.py --range --since "2024-01-01" --until "2024-01-31"

# JSON output for dashboards
python docs/scripts/analytics_reporter.py --format json --range
```

## Integration with Development Workflow

### Git Hooks Integration
Add to `.git/hooks/post-commit`:
```bash
#!/bin/bash
echo "📊 Commit Analytics:"
./docs/scripts/commit-analytics.sh -f standard
```

### CI/CD Pipeline Integration
Add to GitHub Actions workflow:
```yaml
- name: Generate Commit Analytics
  run: |
    python docs/scripts/analytics_reporter.py --format json > commit-stats.json
    
- name: Upload Analytics
  uses: actions/upload-artifact@v3
  with:
    name: commit-analytics
    path: commit-stats.json
```

### Weekly Reporting Automation
Create a scheduled job:
```bash
# Add to crontab for weekly reports
0 9 * * 1 cd /path/to/project && python docs/scripts/analytics_reporter.py --range --since "1 week ago" | mail -s "Weekly Dev Report" team@company.com
```

## Customization Options

### File Type Categories
Modify the file type analysis in `analytics_reporter.py`:
```python
def _analyze_file_types(self, files: List[str]) -> Dict:
    # Add custom file type categorization
    categories = {
        'source_code': ['.py', '.js', '.ts', '.tsx'],
        'configuration': ['.json', '.yaml', '.yml', '.toml'],
        'documentation': ['.md', '.rst', '.txt'],
        'assets': ['.png', '.jpg', '.svg', '.css']
    }
```

### Component Mapping
Customize component analysis:
```python
def _analyze_components(self, files: List[str]) -> Dict:
    # Define your project structure
    component_patterns = {
        'api_layer': r'^backend/api/',
        'business_logic': r'^backend/services/',
        'ui_components': r'^frontend/src/components/',
        'data_models': r'^backend/models/',
    }
```

### Impact Assessment Rules
Adjust impact analysis criteria:
```python
high_impact_patterns = [
    r'main\.py$',           # Application entry points
    r'config\.(py|js)$',    # Configuration files
    r'requirements\.txt$',   # Dependencies
    r'package\.json$',      # Package definitions
    # Add your critical files
]
```

## Reporting Templates

### Daily Standup Report
```bash
#!/bin/bash
echo "🚀 Daily Development Summary"
echo "=========================="
python docs/scripts/analytics_reporter.py --range --since "1 day ago"
```

### Sprint Review Metrics
```bash
#!/bin/bash
echo "📈 Sprint Analytics"
echo "=================="
python docs/scripts/analytics_reporter.py --range --since "2 weeks ago" --format json | \
jq '.summary | {
  total_commits: .total_commits,
  files_changed: .total_files_changed,
  lines_added: .total_insertions,
  top_contributors: .authors
}'
```

### Release Notes Generator
```bash
#!/bin/bash
echo "📋 Release Notes Data"
echo "===================="
git log --since="1 month ago" --pretty=format:"%h - %s (%an)" | \
while read line; do
  commit_hash=$(echo $line | cut -d' ' -f1)
  ./docs/scripts/commit-analytics.sh $commit_hash -f json
done
```

## Best Practices

### For Product Managers
- Review weekly analytics reports for velocity trends
- Use component breakdown to understand feature development focus
- Track documentation updates alongside feature delivery
- Monitor team collaboration patterns

### For Engineering Managers
- Use individual contribution data for 1:1 discussions
- Identify knowledge sharing opportunities from code ownership patterns
- Track technical debt through refactoring vs. feature ratios
- Monitor code review participation and quality

### For Developers
- Use commit analytics to improve commit quality
- Review impact analysis to understand change scope
- Track personal productivity trends
- Identify opportunities for knowledge sharing

## Troubleshooting

### Common Issues
1. **Git command failures**: Ensure you're in a git repository
2. **Permission errors**: Make scripts executable with `chmod +x`
3. **Python dependencies**: Install required packages if needed
4. **Large repositories**: Consider using `--since` to limit analysis scope

### Performance Optimization
- Use date ranges for large repositories
- Cache results for frequently accessed data
- Consider sampling for very active repositories
- Use JSON format for programmatic processing

## Future Enhancements

### Planned Features
- Web-based analytics dashboard
- Integration with project management tools
- Automated trend analysis and alerts
- Machine learning for productivity insights
- Real-time development metrics

### Integration Opportunities
- Slack/Teams notifications for significant changes
- JIRA/GitHub Issues correlation
- Code quality tool integration
- Performance benchmark tracking