# Troubleshooting Guide for Enhanced Extended Format

This document provides solutions to common issues you might encounter when using the enhanced extended format feature.

## Common Issues and Solutions

### 1. CLI Format Not Recognized

**Problem**: The `enhanced-extended` format option is not available in the CLI.

**Solution**:
1. Ensure you're using the latest version of the code
2. Check that you're in the correct worktree (`beacon-task-11-integration`)
3. Verify the CLI has been updated with the new format option:

```bash
beaconled --help | grep format
```

You should see `enhanced-extended` in the list of format choices.

### 2. Import Errors

**Problem**: Python import errors when trying to use the analytics components.

**Solution**:
1. Ensure the virtual environment is activated:

```bash
source ../beacon-delivery-compass/.venv/bin/activate
```

2. Verify that all dependencies are installed:

```bash
pip install -r requirements.txt
```

3. Check that you're using the correct Python path:

```bash
PYTHONPATH=. python -c "from src.beaconled.analytics.engine import AnalyticsEngine; print('Success')"
```

### 3. Performance Issues

**Problem**: The enhanced extended format is taking too long to generate output.

**Solutions**:
1. **Large Repository**: For repositories with many commits, consider using smaller date ranges:

```bash
# Instead of analyzing the entire history
beaconled --format enhanced-extended --since 1year

# Analyze a smaller period
beaconled --format enhanced-extended --since 1month
```

2. **Check Caching**: The system includes caching. If you're running repeated analyses with the same parameters, subsequent runs should be faster.

3. **Run Performance Tests**: To diagnose performance issues, run the performance test suite:

```bash
python -m pytest tests/performance/ -v
```

### 4. Memory Issues

**Problem**: High memory usage when analyzing large repositories.

**Solutions**:
1. **Cache Size**: The cache is limited to 100 entries. If you're analyzing many different repositories, this should prevent memory issues.

2. **Repository Size**: For repositories with more than 5000 commits, consider breaking the analysis into smaller chunks:

```bash
# Analyze in smaller periods
beaconled --format enhanced-extended --since 2025-01-01 --until 2025-06-30
beaconled --format enhanced-extended --since 2025-07-01 --until 2025-12-31
```

3. **Monitor Memory Usage**: Use system monitoring tools to check actual memory usage during analysis.

### 5. Output Formatting Issues

**Problem**: The output doesn't look as expected or is missing sections.

**Solutions**:
1. **Check Dependencies**: Ensure all dependencies for rich formatting are installed:

```bash
pip install rich colorama
```

2. **Terminal Compatibility**: Some terminals may not support all formatting features. Try using a different terminal or the `--no-emoji` option:

```bash
beaconled --format enhanced-extended --no-emoji --since 1week
```

3. **Encoding Issues**: If you see encoding errors, try setting the Python encoding:

```bash
PYTHONIOENCODING=utf-8 beaconled --format enhanced-extended --since 1week
```

## Debugging Steps

### 1. Verify Installation

Check that all components are correctly installed:

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(rich|colorama)"

# Check that the analytics engine can be imported
python -c "from beaconled.analytics import AnalyticsEngine, EnhancedExtendedSystem; print('Components imported successfully')"
```

### 2. Test Individual Components

Test each component separately to isolate issues:

```bash
# Test time analyzer
python -c "
from beaconled.analytics import AnalyticsEngine
from beaconled.core.models import RangeStats
engine = AnalyticsEngine()
print('Time analyzer:', engine.time_analyzer)
"

# Test collaboration analyzer
python -c "
from beaconled.analytics import AnalyticsEngine
engine = AnalyticsEngine()
print('Collaboration analyzer:', engine.collaboration_analyzer)
"
```

### 3. Run Specific Tests

Run specific test suites to identify failing components:

```bash
# Run analytics engine tests
python -m pytest tests/integration/test_analytics_engine.py -v

# Run end-to-end pipeline tests
python -m pytest tests/integration/test_end_to_end_pipeline.py -v

# Run performance tests
python -m pytest tests/performance/test_analytics_benchmarks.py -v
```

## Advanced Debugging

### Profiling Performance

To profile the performance of the analytics pipeline:

```bash
python -m cProfile -o profile.out -m src.beaconled.cli --format enhanced-extended --since 1week
```

Then analyze the profile:

```bash
python -c "
import pstats
stats = pstats.Stats('profile.out')
stats.sort_stats('cumulative').print_stats(20)
"
```

### Memory Profiling

To profile memory usage:

```bash
pip install memory-profiler
python -m memory_profiler src/beaconled/cli.py --format enhanced-extended --since 1week
```

## Environment Variables

The following environment variables can affect the behavior of the enhanced extended format:

- `PYTHONIOENCODING`: Set to `utf-8` to ensure proper encoding
- `PYTHONPATH`: Should include the project root for proper imports

## Reporting Issues

If you encounter issues that aren't covered by this guide:

1. **Gather Information**:
   - Version of Python being used
   - Operating system
   - Error messages
   - Steps to reproduce the issue

2. **Run Diagnostic Commands**:
   ```bash
   python --version
   pip list
   beaconled --version
   ```

3. **Include Test Results**:
   ```bash
   python -m pytest tests/integration/ -v
   ```

4. **Report the Issue**: Create a detailed issue report with all the gathered information.

## Known Limitations

1. **Repository Size**: Performance may degrade with repositories containing more than 5000 commits
2. **Date Range**: Very large date ranges may impact performance
3. **Memory**: Memory usage increases with repository size, but is capped at 200MB for 5000 commits
4. **Caching**: Cache is limited to 100 entries to prevent memory issues

## Best Practices

1. **Use Appropriate Date Ranges**: For better performance, use smaller date ranges when possible
2. **Monitor Resource Usage**: Keep an eye on memory and CPU usage during analysis
3. **Update Dependencies**: Regularly update dependencies to ensure optimal performance
4. **Test with Smaller Repositories**: When troubleshooting, test with smaller repositories first
