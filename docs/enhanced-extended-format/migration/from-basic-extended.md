# Migrating from Basic Extended Format to Enhanced Extended Format

## Overview

The enhanced extended format is a superset of the basic extended format, providing additional analytics and insights while maintaining full backward compatibility. This guide will help you transition smoothly to the enhanced format.

## Key Differences

### Enhanced Analytics
The enhanced extended format provides additional analytics sections:

1. **Time-Based Analysis**: Velocity trends, activity heatmaps, peak periods, bus factor
2. **Team Collaboration Analysis**: Co-authorship patterns, ownership distribution, knowledge silos
3. **Code Quality Insights**: Churn metrics, complexity trends, large changes
4. **Risk Assessment**: Risk indicators, hotspot detection, stability metrics

### Improved Formatting
- Richer visual presentation with better use of Unicode box drawing characters
- Enhanced color coding and emoji support
- Better organization of information into logical sections

### Performance Improvements
- Caching mechanism for repeated analyses
- Optimized processing algorithms
- Better memory management for large repositories

## Migration Steps

### 1. Update Your Commands

**Before (Basic Extended Format):**
```bash
beaconled --format extended --since 30d
```

**After (Enhanced Extended Format):**
```bash
beaconled --format enhanced-extended --since 30d
```

Note: The basic `--format extended` still works and produces the same output as before for backward compatibility.

### 2. Review New Output Sections

When you run with `--format enhanced-extended`, you will see additional sections:

```
# New sections in enhanced format:
- Time-Based Analytics
- Team Collaboration Analytics
- Code Quality Insights
- Risk Assessment
```

### 3. Update Your Parsing Scripts (if applicable)

If you have scripts that parse the extended format output, you may need to update them to handle the new sections. The basic structure remains the same, with additional sections added.

## Feature Comparison

| Feature | Basic Extended Format | Enhanced Extended Format |
|---------|----------------------|--------------------------|
| Basic Repository Stats | ✅ | ✅ |
| Contributor Analysis | ✅ | ✅ |
| File Type Breakdown | ✅ | ✅ |
| Temporal Analysis | ✅ | ✅ |
| Time-Based Analytics | ❌ | ✅ |
| Team Collaboration Analytics | ❌ | ✅ |
| Code Quality Insights | ❌ | ✅ |
| Risk Assessment | ❌ | ✅ |
| Rich Formatting | Limited | Enhanced |
| Caching | ❌ | ✅ |
| Performance Optimization | Standard | Improved |

## Backward Compatibility

The enhanced extended format maintains full backward compatibility:

- All existing `--format extended` commands work exactly as before
- Output structure for basic sections remains unchanged
- No breaking changes to CLI interface
- All existing scripts and integrations continue to work

## New Capabilities

### Time-Based Analytics
```bash
# Both commands work, but enhanced format provides more insights
beaconled --format extended --since 3m
beaconled --format enhanced-extended --since 3m
```

### Team Collaboration Analysis
The enhanced format provides insights into:
- How team members collaborate on commits
- Areas where knowledge is concentrated
- Review participation and effectiveness

### Code Quality Monitoring
Track:
- Files with frequent changes (churn metrics)
- Code complexity trends
- Large changes that might introduce bugs

### Risk Assessment
Identify:
- Risk factors in your codebase
- Hotspot files requiring attention
- Knowledge distribution risks

## Configuration Changes

### CLI Options
No new required options, but some new optional ones:

```bash
# New options in enhanced format:
beaconled --format enhanced-extended --since 30d --no-emoji  # Disable emojis
```

### Environment Variables
New environment variables for advanced usage:

```bash
# Disable caching (for testing)
export BEACON_DISABLE_CACHE=1

# Set timezone (default is UTC)
export BEACON_TIMEZONE=UTC
```

## Common Migration Scenarios

### Scenario 1: Simple Analysis
**Before:**
```bash
beaconled --format extended --since 1w
```

**After:**
```bash
beaconled --format enhanced-extended --since 1w
```

### Scenario 2: Integration with Scripts
**Before:**
```bash
beaconled --format extended --since 1m > analysis.txt
python parse_analysis.py analysis.txt
```

**After:**
```bash
# Same command still works
beaconled --format extended --since 1m > analysis.txt
python parse_analysis.py analysis.txt

# Or use enhanced format for more insights
beaconled --format enhanced-extended --since 1m > enhanced_analysis.txt
python parse_enhanced_analysis.py enhanced_analysis.txt
```

### Scenario 3: Scheduled Reports
**Before:**
```bash
# In cron job
0 9 * * 1 beaconled --format extended --since 1w | mail -s "Weekly Analysis" team@example.com
```

**After:**
```bash
# Same command still works
0 9 * * 1 beaconled --format extended --since 1w | mail -s "Weekly Analysis" team@example.com

# Or enhance with richer format
0 9 * * 1 beaconled --format enhanced-extended --since 1w | mail -s "Weekly Analysis" team@example.com
```

## Troubleshooting Migration Issues

### Issue 1: "enhanced-extended" format not recognized
**Solution:** Ensure you are using the latest version of BeaconLED.

```bash
beaconled --version
# Should show version 1.0.0 or later
```

### Issue 2: Output looks the same
**Solution:** The basic sections look similar, but scroll down to see new sections.

### Issue 3: Performance seems slower initially
**Solution:** First run builds cache, subsequent runs will be faster.

## Best Practices for Enhanced Format

1. **Use Appropriate Time Ranges**: For better insights, analyze meaningful time periods
2. **Regular Analysis**: Schedule regular enhanced format analyses to track trends
3. **Team Reviews**: Use collaboration insights in team retrospectives
4. **Risk Monitoring**: Regularly check risk assessment for potential issues
5. **Quality Tracking**: Monitor code quality metrics to maintain standards

## Next Steps

After migrating:

1. **Explore New Sections**: Review the additional analytics sections
2. **Share Insights**: Discuss findings with your team
3. **Adjust Processes**: Use insights to improve development practices
4. **Schedule Regular Analysis**: Make enhanced format analysis part of your routine
