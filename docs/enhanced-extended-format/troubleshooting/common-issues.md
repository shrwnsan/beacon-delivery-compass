# Troubleshooting Guide for Enhanced Extended Format

## Common Issues and Solutions

### 1. "enhanced-extended" format not recognized

**Problem:**
```bash
beaconled --format enhanced-extended --since 1w
Error: Invalid format "enhanced-extended"
```

**Solution:**
Ensure you are using the latest version of BeaconLED that includes the enhanced extended format feature.

```bash
# Check your version
beaconled --version

# Update if needed
pip install --upgrade beaconled
```

### 2. No additional analytics sections in output

**Problem:**
The output looks the same as the basic extended format.

**Solution:**
Make sure you are using `--format enhanced-extended` (not just `--format extended`) and scroll down to see all sections.

```bash
# Correct usage
beaconled --format enhanced-extended --since 1w

# Check that you see sections like:
# - Time-Based Analytics
# - Team Collaboration Analytics
# - Code Quality Insights
# - Risk Assessment
```

### 3. Performance seems slow on first run

**Problem:**
The first analysis takes longer than expected.

**Solution:**
This is normal. The first run builds caches for subsequent analyses. Subsequent runs with the same or similar parameters will be faster.

```bash
# First run (slower)
time beaconled --format enhanced-extended --since 1m

# Second run (faster due to caching)
time beaconled --format enhanced-extended --since 1m
```

### 4. Unicode characters not displaying correctly

**Problem:**
Box drawing characters or emojis appear as strange symbols.

**Solution:**
This is usually a terminal encoding issue. Try one of these solutions:

```bash
# Set proper encoding
export PYTHONIOENCODING=utf-8

# Or disable emojis
beaconled --format enhanced-extended --since 1w --no-emoji
```

### 5. Date parsing errors

**Problem:**
```bash
Error: Invalid date format
```

**Solution:**
Ensure all dates are in UTC and use supported formats:

```bash
# Correct relative formats
beaconled --format enhanced-extended --since 1d   # 1 day
beaconled --format enhanced-extended --since 2w   # 2 weeks
beaconled --format enhanced-extended --since 3m   # 3 months
beaconled --format enhanced-extended --since 1y   # 1 year

# Correct absolute formats
beaconled --format enhanced-extended --since 2025-01-01
beaconled --format enhanced-extended --since "2025-01-01 12:00"
```

### 6. Memory issues with large repositories

**Problem:**
High memory usage when analyzing large repositories.

**Solution:**
Use smaller date ranges or disable caching:

```bash
# Use smaller date ranges
beaconled --format enhanced-extended --since 1w  # Instead of --since 1y

# Disable caching (reduces memory but may slow down repeated analyses)
export BEACON_DISABLE_CACHE=1
beaconled --format enhanced-extended --since 1m
```

### 7. Permission errors

**Problem:**
```bash
Error: Permission denied
```

**Solution:**
Ensure you have read permissions on the repository:

```bash
# Check permissions
ls -la /path/to/your/repo/.git

# Run with appropriate permissions
beaconled --format enhanced-extended --repo /path/to/your/repo --since 1w
```

## Performance Tuning

### Optimizing for Large Repositories

1. **Use Appropriate Date Ranges:**
```bash
# Good for large repos
beaconled --format enhanced-extended --since 3m

# May be too much for large repos
beaconled --format enhanced-extended --since 2y
```

2. **Monitor Resource Usage:**
```bash
# Monitor memory usage
/usr/bin/time -l beaconled --format enhanced-extended --since 1m
```

3. **Use Caching Effectively:**
The system caches results based on commit count and date range. Repeated analyses with similar parameters will be faster.

### Environment Variables for Performance

```bash
# Disable caching if memory is limited
export BEACON_DISABLE_CACHE=1

# Set timezone explicitly
export BEACON_TIMEZONE=UTC
```

## FAQ (Frequently Asked Questions)

### Q: Is the enhanced extended format backward compatible?
**A:** Yes, completely. All existing `--format extended` commands work exactly as before.

### Q: Do I need to change my existing scripts?
**A:** No, existing scripts continue to work. However, you may want to update them to take advantage of the enhanced format.

### Q: What is the difference between --format extended and --format enhanced-extended?
**A:** The enhanced format provides additional analytics sections while maintaining the same basic structure.

### Q: How does the caching work?
**A:** Results are cached based on commit count and date range, with a maximum cache size of 100 entries.

### Q: Can I disable the caching?
**A:** Yes, set the `BEACON_DISABLE_CACHE=1` environment variable.

### Q: What timezones are supported?
**A:** All dates and times are interpreted as UTC. Convert local times to UTC before use.

### Q: How do I disable emojis in the output?
**A:** Use the `--no-emoji` flag:
```bash
beaconled --format enhanced-extended --since 1w --no-emoji
```

### Q: What is the bus factor analysis?
**A:** It measures how concentrated knowledge is in your team. A low bus factor means only a few people understand critical parts of the codebase.

### Q: How are risk factors calculated?
**A:** Risk factors consider code churn, knowledge concentration, and recent large changes to identify potentially problematic areas.

### Q: Can I use this with private repositories?
**A:** Yes, as long as you have read access to the repository.

## Debugging Steps

### 1. Verify Installation

```bash
# Check version
beaconled --version

# Check available formats
beaconled --help | grep -A 5 format
```

### 2. Test with Simple Repository

```bash
# Test with current directory
beaconled --format enhanced-extended --since 1d

# Test with specific repository
beaconled --format enhanced-extended --repo /path/to/simple/repo --since 1w
```

### 3. Enable Verbose Output

```bash
# For development versions, you might have debug options
beaconled --format enhanced-extended --since 1w --verbose
```

### 4. Check System Resources

```bash
# Check available memory
free -h

# Check disk space
df -h

# Monitor during execution
top -p $(pgrep beaconled)
```

## Reporting Issues

If you encounter issues not covered by this guide:

1. **Gather Information:**
   - BeaconLED version: `beaconled --version`
   - Operating system and version
   - Python version: `python --version`
   - Error messages
   - Steps to reproduce

2. **Create a Minimal Reproduction:**
   - Try with a small, public repository
   - Use simple date ranges
   - Remove any sensitive information

3. **Report:**
   Create an issue on the GitHub repository with all the gathered information.

## Known Limitations

1. **Repository Size:** Performance may degrade with repositories containing more than 10,000 commits
2. **Date Range:** Very large date ranges (years) may impact performance
3. **Memory:** Memory usage increases with repository size but is capped
4. **Caching:** Cache is limited to 100 entries to prevent memory issues
5. **Unicode Support:** Requires UTF-8 terminal support for best display

## Best Practices

1. **Start Small:** Begin with small date ranges and simple repositories
2. **Regular Analysis:** Schedule regular analyses to track trends over time
3. **Monitor Resources:** Keep an eye on memory and CPU usage during analysis
4. **Update Regularly:** Keep BeaconLED updated to benefit from improvements
5. **Use Appropriate Formats:** Choose between basic and enhanced formats based on your needs
