# Development Scripts

This directory contains scripts for development workflow automation, analytics, and productivity tools for Beacon - your delivery compass for empowered product builders.

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
python docs/scripts/analytics_reporter.py --since 1w

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
0 9 * * 1 cd /project && python docs/scripts/analytics_reporter.py --since 1w
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

---

## Precommit Setup Scripts

### Overview

The enhanced precommit configuration catches 100% of lint, type, security, and test issues **locally** before they reach CI, eliminating the "commit then fix in CI" anti-pattern.

### Key Features

- **Comprehensive Coverage**: Fast file checks, code quality, type safety, security, testing
- **Performance Optimized**: Smart ordering, file filtering, conditional execution
- **Smart Configuration**: Path consistency, clear error handling, flexible execution

### Setup Scripts

#### `setup.sh` & `setup.bat`
**Purpose**: Cross-platform development environment setup
**Language**: Bash (Unix/macOS) & Batch (Windows)
**Best for**: Initial development environment setup

```bash
# Unix/macOS setup
./scripts/setup.sh

# Windows setup
scripts/setup.bat
```

#### `product_insights_cli.py`
**Purpose**: Product insights and analytics reporting
**Language**: Python
**Best for**: Automated weekly reports and stakeholder updates

```bash
# Generate weekly report
python scripts/product_insights_cli.py weekly --since 1w

# Generate executive summary
python scripts/product_insights_cli.py executive --since 1w
```

#### `notification_system.py`
**Purpose**: Stakeholder notification system for product insights
**Language**: Python
**Best for**: Automated Slack notifications and alerts

```bash
# Process executive summary and send notifications
python scripts/notification_system.py process executive_summary.json
```

### Usage Patterns

#### Normal Development Workflow
```bash
# Make your changes
git add .

# Commit - precommit runs automatically
git commit -m "your commit message"
```

#### Fast Development Feedback
```bash
# Quick checks during development
make quick-check

# Or run individual checks
make lint
make typecheck
```

#### Full Validation
```bash
# Run all checks manually
make precommit-all
```

### Performance Characteristics

#### Execution Time Analysis
- **Fast checks** (file format, linting): 1-5 seconds
- **Type checking**: 5-15 seconds
- **Security checks**: 10-30 seconds
- **Unit tests**: 15-60 seconds
- **Integration tests**: 30-120 seconds (only when needed)

#### Optimization Strategies
1. **Parallel execution**: Multiple tools run simultaneously
2. **File filtering**: Only check relevant files
3. **Conditional logic**: Skip unnecessary checks
4. **Caching**: Tool-specific caches speed up repeated runs

### Troubleshooting

#### Common Issues

**Pre-commit hooks not running**
```bash
# Ensure hooks are installed
pre-commit install

# Check hook status
pre-commit --version
pre-commit installed
```

**Permission denied on scripts**
```bash
chmod +x scripts/*.sh
```

**Missing dependencies**
```bash
# Install all development dependencies
pip install -e .[dev]
```

### Benefits Achieved

#### Before This Enhancement
- ❌ Lint/type errors caught in CI
- ❌ Broken tests only found in CI
- ❌ Security issues only caught in CI
- ❌ Inconsistent tool configurations
- ❌ Slow feedback loops

#### After This Enhancement
- ✅ **100% of issues caught locally**
- ✅ **Immediate feedback during development**
- ✅ **Consistent tool configurations**
- ✅ **Fast feedback loops**
- ✅ **Quality-focused development workflow**

For detailed configuration information, see the [testing documentation](testing.md#intelligent-test-selection-with-pytest-testmon).
