# Getting Started with Enhanced Extended Format

## Overview

The enhanced extended format provides rich analytics and insights about your repositorys development patterns, team collaboration, and code quality trends. This comprehensive guide will help you get started with using this powerful feature.

## Prerequisites

Before using the enhanced extended format, ensure you have:
- BeaconLED installed (version 1.0.0 or later)
- Git repository to analyze
- Python 3.8 or later (if running from source)

## Basic Usage

### Command Line Interface

To use the enhanced extended format, simply specify it as the output format:

```bash
# Analyze the last 30 days with enhanced format
beaconled --format enhanced-extended --since 30d

# Analyze a specific date range
beaconled --format enhanced-extended --since 2025-01-01 --until 2025-02-01

# Analyze with emoji disabled
beaconled --format enhanced-extended --since 1w --no-emoji
```

### Understanding Date Formats

BeaconLED supports both relative and absolute date formats:

**Relative Dates:**
- `1d` - 1 day ago
- `2w` - 2 weeks ago
- `3m` - 3 months ago
- `1y` - 1 year ago

**Absolute Dates:**
- `YYYY-MM-DD` - Date only (midnight UTC)
- `YYYY-MM-DD HH:MM` - Date and time
- `YYYY-MM-DDTHH:MM:SS` - ISO 8601 format
- `YYYY-MM-DDTHH:MM:SS+00:00` - Explicit UTC timezone

## Understanding the Output

The enhanced extended format provides comprehensive insights organized into several sections:

### 📈 Time-Based Analysis
- **Velocity Trends**: How your commit frequency changes over time
- **Activity Heatmap**: When your team is most active (day/hour patterns)
- **Peak Periods**: Identification of high-activity periods
- **Bus Factor**: How distributed your teams contributions are

### 👥 Team Collaboration Analysis
- **Co-Authorship Patterns**: How team members collaborate on commits
- **Ownership Distribution**: Which files/team members have expertise
- **Knowledge Silos**: Areas where knowledge is concentrated
- **Review Metrics**: Participation in code reviews

### 🔍 Code Quality Insights
- **Churn Metrics**: Files with frequent changes
- **Complexity Trends**: How code complexity evolves
- **Large Changes**: Commits that modify many files/lines

### ⚠️ Risk Assessment
- **Risk Indicators**: Areas of potential concern
- **Hotspot Detection**: Files with high risk factors
- **Stability Metrics**: How stable different parts of the codebase are

## Sample Output

Here is an example of what you might see when running the enhanced extended format:

```
╭───────────────────────────────────────────── 📈 Range Analysis Overview ─────────────────────────────────────────────╮
│ ╭──────────────────┬──────────────────────────╮                                                                      │
│ │ 📅 Period        │ 2025-08-01 to 2025-08-31 │                                                                      │
│ │ 📊 Duration      │ 31 days                  │                                                                      │
│ │ 🔢 Total Commits │ 142                      │                                                                      │
│ │ 📂 Files Changed │ 87                       │                                                                      │
│ │ + Lines Added    │ 2,847                    │                                                                      │
│ │ - Lines Deleted  │ 1,203                    │                                                                      │
│ │ 🔄 Net Change    │ 1,644                    │                                                                      │
│ ╰──────────────────┴──────────────────────────╯                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

     👥 Team Overview      
                           
  Metric            Value  
 ───────────────────────── 
  Contributors          5  
  Total Commits       142  
  Avg Commits/Day     4.6  
  Active Days        28/31 

[Additional sections with detailed analytics...]
```

## Configuration Options

### CLI Options

- `--format enhanced-extended`: Select the enhanced extended format
- `--since DATE`: Start date for analysis
- `--until DATE`: End date for analysis (optional, defaults to now)
- `--no-emoji`: Disable emoji icons in output
- `--repo PATH`: Path to repository (optional, defaults to current directory)

### Environment Variables

- `BEACON_TIMEZONE`: Set timezone for date interpretation (defaults to UTC)
- `BEACON_DISABLE_CACHE`: Disable caching mechanism (for testing)

## Next Steps

After running your first analysis, consider:

1. **Exploring Different Time Periods**: Try analyzing different time ranges to spot trends
2. **Comparing Teams**: Use the collaboration analysis to understand team dynamics
3. **Monitoring Code Quality**: Track churn metrics to identify areas needing attention
4. **Risk Assessment**: Use risk indicators to proactively address potential issues

## Common Use Cases

### Team Health Check
```bash
beaconled --format enhanced-extended --since 3m
```
Analyze team collaboration patterns and identify knowledge silos.

### Release Preparation
```bash
beaconled --format enhanced-extended --since 6w --until 2025-09-15
```
Assess code stability and risk factors before a major release.

### Onboarding Analysis
```bash
beaconled --format enhanced-extended --since 1y
```
Understand repository history and identify areas where new team members can contribute.

## Troubleshooting

If you encounter issues:

1. Ensure all dates are in UTC format
2. Check that the repository path is correct
3. Verify you have read permissions on the repository
4. Try with a smaller date range for large repositories

For detailed troubleshooting, see the [Troubleshooting Guide](../troubleshooting/common-issues.md).
