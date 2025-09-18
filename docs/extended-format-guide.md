# Extended Format Guide

The extended format (`--format extended`) in Beacon provides comprehensive analytics and insights into your codebase's development patterns, team collaboration, code quality, risk assessment, and test coverage tracking. This guide explains all the features and metrics available in the extended format.

## Overview

The extended format enhances the standard output with additional analytics sections:

1. **Time-Based Analytics** - Understand development velocity and patterns
2. **Team Collaboration** - Analyze how your team works together
3. **Code Quality** - Get insights into code health and maintainability
4. **Risk Assessment** - Identify potential risks and hotspots in your codebase
5. **Test Coverage Tracking** - Monitor test coverage trends and identify areas needing attention

## Time-Based Analytics

```
⏱️ Time-Based Analytics:
• Velocity: 12.3 commits/day
• Peak hours: 10:00, 15:00
• Bus factor: 4
```

### Metrics Explained

- **Velocity**: Average number of commits per day in the analyzed period
- **Peak hours**: Hours with the highest commit activity (UTC)
- **Bus factor**: Number of developers who would need to be unavailable before the project stalls

## Team Collaboration

```
👥 Team Collaboration:
• Core contributors: alice, bob, charlie
• Knowledge distribution: Balanced
• Review participation: 85%
```

### Metrics Explained

- **Core contributors**: Developers with the most significant contributions
- **Knowledge distribution**: How knowledge is spread across the team (Balanced/Concentrated/Overlap)
- **Review participation**: Percentage of commits with code reviews

## Code Quality

```
🛠️ Code Quality:
• Churn rate: 8.2%
• Complexity trend: Stable
• Test coverage: 78% (▲2%)
```

### Metrics Explained

- **Churn rate**: Percentage of code that was recently changed or deleted
- **Complexity trend**: Whether code complexity is increasing or decreasing
- **Test coverage**: Code coverage by tests (when available)

## Risk Assessment

```
⚠️ Risk Assessment:
• Risk score: 3/10
• Hotspots: src/auth/, src/api/
• Stale code: 2 files (>6 months)
```

### Metrics Explained

- **Risk score**: Overall risk assessment (1-10, lower is better)
- **Hotspots**: Directories with high complexity and frequent changes
- **Stale code**: Files that haven't been modified in a long time

## Test Coverage Tracking

```
🧪 Test Coverage:
  Overall: 82.5%
  Lines: 85.0% (850/1,000)
  Branches: 80.0% (400/500)

📈 Coverage Trends:
  Direction: increasing
  Change: +5.0%
  Status: Improving (+6.3%)

  Significant changes:
    📈 2025-01-15: +3.0%

  Top covered files:
    src/main.py: 95.0%
    src/utils.py: 80.0%
    tests/test_main.py: 98.0%

  Files needing attention (<60%):
    src/low_coverage.py: 45.0%
```

### Metrics Explained

- **Overall coverage**: Combined line and branch coverage percentage
- **Lines**: Line coverage with actual counts (covered/total)
- **Branches**: Branch coverage with actual counts (covered/total)
- **Direction**: Coverage trend direction (increasing/decreasing/stable)
- **Change**: Absolute percentage change in coverage
- **Status**: Coverage health status with improvement percentage

### Coverage File Sources

The extended format automatically detects and analyzes coverage data from:
- `coverage.xml` - Cobertura XML format
- `.coverage` - Coverage.py database format
- Reports in common locations like `reports/coverage.xml`

### Coverage Trend Analysis

The system tracks coverage changes over time and identifies:
- **Significant changes**: Coverage changes greater than 2%
- **Improvement trends**: Sustained increases in coverage
- **Declining trends**: Decreasing coverage that needs attention
- **File-level trends**: Individual file coverage changes

### Coverage Quality Indicators

**Excellent (≥90%)**: Green indicators, well-tested code
**Good (70-89%)**: Yellow indicators, adequate coverage
**Needs Attention (<60%)**: Red indicators, requires additional tests

## Using the Extended Format

### Basic Usage

```bash
# Basic extended format
beaconled --format extended

# Analyze specific time range
beaconled --format extended --since "2w" --until "1w"

# Save output to a file
beaconled --format extended > analysis.txt
```

### Integration with Other Tools

The extended format is designed to be both human-readable and machine-parseable. You can pipe the output to other tools for further processing:

```bash
# Count total files changed
beaconled --format extended | grep -A 1 "Total files changed" | tail -n 1

# Extract risk score
beaconled --format extended | grep "Risk score" | awk '{print $3}'
```

## Best Practices

1. **Regular Monitoring**: Run the extended analysis weekly to track trends
2. **Team Reviews**: Discuss the metrics in team meetings to identify areas for improvement
3. **Actionable Insights**: Use the data to inform decisions about technical debt and resource allocation

## Troubleshooting

If you encounter any issues with the extended format:

1. Ensure you have the latest version of Beacon
2. Check that your Git repository has sufficient history
3. Verify that you have the necessary permissions to access the repository

For additional help, refer to the [troubleshooting guide](troubleshooting.md) or [open an issue](https://github.com/shrwnsan/beacon-delivery-compass/issues).
