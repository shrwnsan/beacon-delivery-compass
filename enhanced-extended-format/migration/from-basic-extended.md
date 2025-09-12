# Migration Guide: From Basic to Extended Format

**Note:** The enhanced-extended format has been merged into the standard `extended` format. This guide has been updated to reflect the current state of the codebase.

## Overview

This guide helps you migrate from the basic extended format to the enhanced extended format that is now part of the standard `extended` format. The enhanced format includes additional analytics and visualizations that provide deeper insights into your repository's activity and health.

## What's New in the Extended Format

The extended format now includes all the features that were previously part of the `enhanced-extended` format:

1. **Time-Based Analytics**
   - Commit velocity and trends
   - Peak coding hours
   - Bus factor analysis

2. **Team Collaboration**
   - Core contributor identification
   - Knowledge distribution
   - Review participation metrics

3. **Code Quality**
   - Churn rate analysis
   - Complexity trends
   - Test coverage metrics

4. **Risk Assessment**
   - Risk scoring
   - Code hotspots
   - Security vulnerability detection

## Migration Steps

### 1. Update Your Commands

**Before (Basic Extended Format):**
```bash
beaconled --format extended --since 30d
```

**After (Enhanced Extended Format):**
```bash
beaconled --format extended --since 30d
```

> **Note**: The command remains the same, but the output now includes enhanced analytics by default.

### 2. Update Your Scripts

If you have scripts that parse the extended format output, they should continue to work as before. The basic structure of the output remains the same, with additional sections for the enhanced analytics.

### 3. Update Your Documentation

Update any internal documentation that references the `enhanced-extended` format to use `extended` instead.

## Example Output

The enhanced extended format adds several new sections to the output. Here's an example of what to expect:

```
📊 Time-Based Analytics
  • Commit Velocity: 12.3 commits/day
  • Peak Hours: 10:00, 15:00
  • Bus Factor: 4

👥 Team Collaboration
  • Core Contributors: alice, bob
  • Knowledge Distribution: Balanced
  • Review Participation: 85%

🛠️ Code Quality
  • Churn Rate: 8.2%
  • Complexity Trend: Stable
  • Test Coverage: 78%

⚠️ Risk Assessment
  • Risk Score: 3/10
  • Hotspots: src/auth/, src/api/
  • Stale Code: 2 files
```

## Backward Compatibility

The extended format maintains backward compatibility with the basic extended format. If you were using the basic extended format, your existing commands and scripts should continue to work without modification.

## Troubleshooting

If you encounter any issues with the enhanced format:

1. Check that you're using the latest version of the package
2. Verify that your command is using `--format extended`
3. Check the [troubleshooting guide](../integration/troubleshooting.md) for common issues

## Getting Help

If you need assistance with the migration or have questions about the enhanced format:

1. Check the [documentation](https://github.com/yourorg/beacon-delivery-compass/docs)
2. Search existing issues on GitHub
3. [Open a new issue](https://github.com/yourorg/beacon-delivery-compass/issues/new) with your question or problem
