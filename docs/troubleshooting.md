# Troubleshooting Guide

This is the canonical troubleshooting guide for Beacon Delivery Compass. If an issue persists, open a GitHub issue: https://github.com/shrwnsan/beacon-delivery-compass/issues/new

- Installation: [installation.md](docs/installation.md)
- API: [api/api.md](docs/api/api.md)
- Examples: [examples/basic-usage.md](docs/examples/basic-usage.md), [examples/advanced-usage.md](docs/examples/advanced-usage.md)

## Table of Contents
- [Installation Issues](#installation-issues)
- [Command Line Usage](#command-line-usage)
- [Git Repository Analysis](#git-repository-analysis)
- [Extended Format Issues](#extended-format-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)
- [Debugging and Advanced Troubleshooting](#debugging-and-advanced-troubleshooting)
- [Getting Help](#getting-help)

## Installation Issues

### Python Version Problems
Symptom: "Python 3.8+ is required" or Beacon not available in current interpreter.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install beaconled
```

### Package Installation Failures
```bash
python -m pip install --upgrade pip
pip install --no-cache-dir beaconled
# If needed, recreate a clean virtualenv:
rm -rf .venv && python -m venv .venv && source .venv/bin/activate && pip install beaconled
```

## Command Line Usage

### Command Not Found
```bash
# Ensure venv is active
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Verify install
pip show beaconled

# Run via module if needed
python -m beaconled --help
```

## Git Repository Analysis

### Git Not Found
- Install Git from https://git-scm.com/
- Ensure `git --version` works from your shell.

### Repository Access Issues
```bash
# Run inside a git repository
git status

# Or point Beacon at a repo
beaconled --repo /path/to/your/git/repo
```

## Extended Format Issues

### CLI Format Not Recognized

**Problem**: The `extended` format option is not available in the CLI.

**Solution**:
1. Ensure you're using the latest version of the code
2. Verify the CLI has been updated with the new format option:

```bash
beaconled --help | grep format
```

You should see `extended` in the list of format choices.

### Import Errors

**Problem**: Python import errors when trying to use the analytics components.

**Solution**:
1. Ensure the virtual environment is activated:

```bash
source .venv/bin/activate
```

2. Verify that all dependencies are installed:

```bash
pip install -r requirements.txt
```

3. Check that you're using the correct Python path:

```bash
PYTHONPATH=. python -c "from src.beaconled.analytics.engine import AnalyticsEngine; print('Success')"
```

### Memory Issues

**Problem**: High memory usage when analyzing large repositories.

**Solutions**:
1. **Cache Size**: The cache is limited to 100 entries. If you're analyzing many different repositories, this should prevent memory issues.

2. **Repository Size**: For repositories with more than 5000 commits, consider breaking the analysis into smaller chunks:

```bash
# Analyze in smaller periods
beaconled --format extended --since 2025-01-01 --until 2025-06-30
beaconled --format extended --since 2025-07-01 --until 2025-12-31
```

3. **Monitor Memory Usage**: Use system monitoring tools to check actual memory usage during analysis.

### Output Formatting Issues

**Problem**: The output doesn't look as expected or is missing sections.

**Solutions**:
1. **Check Dependencies**: Ensure all dependencies for rich formatting are installed:

```bash
pip install rich colorama
```

2. **Terminal Compatibility**: Some terminals may not support all formatting features. Try using a different terminal or the `--no-emoji` option:

```bash
beaconled --format extended --no-emoji --since 1week
```

3. **Encoding Issues**: If you see encoding errors, try setting the Python encoding:

```bash
PYTHONIOENCODING=utf-8 beaconled --format extended --since 1week
```

## Performance Issues

### Slow Analysis on Large Repos
1) Limit the date range:
```bash
beaconled --since 1m
```
2) Exclude large directories via .gitignore
3) Sample or narrow scope where possible

### Extended Format Performance Issues

**Problem**: The extended format is taking too long to generate output.

**Solutions**:
1. **Large Repository**: For repositories with many commits, consider using smaller date ranges:

```bash
# Instead of analyzing the entire history
beaconled --format extended --since 1year

# Analyze a smaller period
beaconled --format extended --since 1month
```

2. **Check Caching**: The system includes caching. If you're running repeated analyses with the same parameters, subsequent runs should be faster.

3. **Run Performance Tests**: To diagnose performance issues, run the performance test suite:

```bash
python -m pytest tests/performance/ -v
```

## Common Error Messages

### ModuleNotFoundError
```bash
pip install --force-reinstall beaconled
# Or install the missing dependency explicitly
pip install <missing-module-name>
```

### PermissionError: [Errno 13]
```bash
# Prefer user installs or virtualenvs
pip install --user beaconled
# or
python -m venv .venv && source .venv/bin/activate && pip install beaconled
```

## Debugging and Advanced Troubleshooting

### Enable Verbose Output

Add the `-v` or `--verbose` flag to get more detailed output:

```bash
beaconled --format extended --since 1week --verbose
```

### Check Logs

Logs are stored in `~/.beacon/logs/` by default. Check these files for detailed error information.

### Verify Installation

Check that all components are correctly installed:

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(rich|colorama)"

# Check that the analytics engine can be imported
python -c "from beaconled.analytics import AnalyticsEngine; print('Components imported successfully')"
```

### Test Individual Components

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

### Run Specific Tests

Run specific test suites to identify failing components:

```bash
# Run analytics engine tests
python -m pytest tests/integration/test_analytics_engine.py -v

# Run end-to-end pipeline tests
python -m pytest tests/integration/test_end_to_end_pipeline.py -v

# Run performance tests
python -m pytest tests/performance/test_analytics_benchmarks.py -v
```

### Profiling Performance

To profile the performance of the analytics pipeline:

```bash
python -m cProfile -o profile.out -m src.beaconled.cli --format extended --since 1week
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
python -m memory_profiler src/beaconled/cli.py --format extended --since 1week
```

## Environment Variables

The following environment variables can affect the behavior of Beacon:

- `PYTHONIOENCODING`: Set to `utf-8` to ensure proper encoding
- `PYTHONPATH`: Should include the project root for proper imports
- `BEACON_DEBUG=1`: Enable debug logging
- `BEACON_NO_CACHE=1`: Disable caching
- `BEACON_CACHE_DIR`: Custom cache directory

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

## Getting Help

- Check docs:
  - [installation.md](docs/installation.md)
  - [examples/basic-usage.md](docs/examples/basic-usage.md)
- Search existing issues: https://github.com/shrwnsan/beacon-delivery-compass/issues
- Create a new issue including:
  - Repro steps
  - Full error output
  - OS and Python versions
  - `beaconled --version`

## Still Stuck?

- Discussions: https://github.com/shrwnsan/beacon-delivery-compass/discussions
- Changelog: refer to root [../CHANGELOG.md](CHANGELOG.md)
