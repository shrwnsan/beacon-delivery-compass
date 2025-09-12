# Extended Format Guide

The extended format (`--format extended`) in Beacon provides comprehensive analytics and insights into your codebase's development patterns, team collaboration, code quality, and risk assessment. This guide explains all the features and metrics available in the extended format.

## Overview

The extended format enhances the standard output with additional analytics sections:

1. **Time-Based Analytics** - Understand development velocity and patterns
2. **Team Collaboration** - Analyze how your team works together
3. **Code Quality** - Get insights into code health and maintainability
4. **Risk Assessment** - Identify potential risks and hotspots in your codebase

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
