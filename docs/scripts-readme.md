# Development Analytics Scripts

This directory contains scripts for generating development analytics and commit statistics for Beacon - your delivery compass for empowered product builders.

## Scripts Overview

### `commit-analytics.sh`
**Purpose**: Quick commit analysis with colored terminal output  
**Language**: Bash  
**Best for**: Daily development workflow, git hooks, quick stats

**Quick Usage**:
```bash
# Analyze latest commit
./docs/scripts/commit-analytics.sh

# Detailed breakdown
./docs/scripts/commit-analytics.sh -d -f extended

# JSON output for automation
./docs/scripts/commit-analytics.sh -f json
```

### `analytics_reporter.py`
**Purpose**: Advanced analytics with range analysis and detailed reporting  
**Language**: Python  
**Best for**: Weekly reports, trend analysis, team metrics

**Quick Usage**:
```bash
# Analyze latest commit
python docs/scripts/analytics_reporter.py

# Weekly team report
python docs/scripts/analytics_reporter.py --range --since "1 week ago"

# JSON output for dashboards
python docs/scripts/analytics_reporter.py --format json
```

## Sample Outputs

### Standard Format
```
📊 Commit Stats:
8 files changed
455 insertions, 36 deletions
Commit Hash: cce265f
Branch: feature/changelog-documentation
Author: John Developer
Date: 2024-01-15 14:30:00 -0800
```

### Extended Format
```
--Files Added/Modified:
8 files changed in total
462 insertions, 38 deletions
5 new files created
3 existing files improved

--Breakdown by Component:
Backend: 4 files
Frontend: 3 files
Documentation: 1 file

--Impact Analysis:
High Impact: 2 files (core services)
Medium Impact: 4 files (API endpoints)
Low Impact: 2 files (documentation)
```

## Integration Examples

### Git Hook (Post-Commit)
Add to `.git/hooks/post-commit`:
```bash
#!/bin/bash
echo "📊 Commit Analytics:"
./docs/scripts/commit-analytics.sh
```

### CI/CD Pipeline
```yaml
- name: Generate Analytics
  run: python docs/scripts/analytics_reporter.py --format json > analytics.json
```

### Weekly Automation
```bash
# Crontab entry for Monday 9 AM reports
0 9 * * 1 cd /project && python docs/scripts/analytics_reporter.py --range --since "1 week ago"
```

## Requirements

### Bash Script
- Git repository
- Bash shell (macOS/Linux)
- Standard Unix tools (grep, sed, awk)

### Python Script
- Python 3.8+ (managed by pyenv)
- Git repository
- No additional dependencies (uses standard library)

## Troubleshooting

### Common Issues
1. **Permission denied**: Run `chmod +x docs/scripts/*.sh`
2. **Git not found**: Ensure you're in a git repository
3. **Python not found**: Check pyenv setup and Python installation

### Performance Tips
- Use date ranges for large repositories
- Use JSON format for programmatic processing
- Cache results for frequently accessed data

## Customization

Both scripts can be customized for your specific needs:
- Modify file type categorization
- Adjust component mapping
- Change impact assessment rules
- Add custom output formats

See the main [Analytics Dashboard documentation](../ANALYTICS_DASHBOARD.md) for detailed customization options.