# Integration Guide for Extended Format

This document provides guidance on integrating and using the extended format feature in BeaconLED.

## Overview

The extended format brings together all the analytics components (time-based, team collaboration, quality assessment, and risk indicators) with rich visualization capabilities to provide comprehensive insights into your git repository.

## System Architecture

The extended format is built on the following components:

1. **Analytics Engine** - Integrates all analytics components
2. **Extended System** - Coordinates the full pipeline
3. **CLI Integration** - Provides command-line access to the extended format

### Analytics Engine

The `AnalyticsEngine` class integrates all analytics components:

```python
from beaconled.analytics import AnalyticsEngine

engine = AnalyticsEngine()
analytics = engine.analyze(range_stats)
```

### Extended System

The `ExtendedSystem` coordinates the full pipeline:

```python
from beaconled.analytics import ExtendedSystem

system = ExtendedSystem()
result = system.analyze_and_format(range_stats)
```

## CLI Usage

To use the extended format from the command line:

```bash
# For range analysis
beaconled --format extended --since 1month

# For single commit analysis
beaconled --format extended <commit-hash>

# Without emojis
beaconled --format extended --no-emoji --since 1week
```

## Performance Optimization

The analytics engine includes caching to improve performance for repeated analyses:

- Caching is based on commit count and date range
- Cache size is limited to 100 entries to prevent memory issues
- Cached results are automatically invalidated when cache size limit is reached

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check that the virtual environment is activated

2. **Performance Issues**
   - For large repositories, consider using smaller date ranges
   - The system is optimized for repositories up to 5000 commits

3. **CLI Format Not Recognized**
   - Ensure you're using the latest version of the code
   - The `extended` format option should be available in the help

### Debugging Performance

To debug performance issues, you can run the performance tests:

```bash
python -m pytest tests/performance/ -v
```

### Memory Usage

The system is designed to use less than 200MB of memory for repositories with up to 5000 commits. If you experience memory issues:

1. Try analyzing smaller date ranges
2. Ensure the cache size limit is working correctly
3. Check for memory leaks with repeated analyses

## API Documentation

### AnalyticsEngine

```python
class AnalyticsEngine:
    def __init__(self) -> None:
        """Initialize the analytics engine with all component analyzers."""

    def analyze(self, range_stats: RangeStats) -> dict:
        """Perform comprehensive analysis on range statistics.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary containing all analytics results
        """
```

### ExtendedSystem

```python
class ExtendedSystem:
    def __init__(self) -> None:
        """Initialize the extended system."""

    def analyze_and_format(self, range_stats: RangeStats) -> str:
        """Complete analysis and formatting pipeline.

        Args:
            range_stats: The range statistics to analyze and format

        Returns:
            Formatted string with enhanced analytics
        """
```

## Testing

The integration includes comprehensive tests:

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test the full pipeline
3. **Performance Tests** - Validate performance requirements
4. **Backward Compatibility Tests** - Ensure existing functionality still works

To run all tests:

```bash
# Run all tests
python -m pytest

# Run integration tests only
python -m pytest tests/integration/

# Run performance tests only
python -m pytest tests/performance/
```

## Performance Benchmarks

The system meets the following performance targets:

- TimeAnalyzer: < 1s for 1000 commits
- TeamAnalyzer: < 2s for 1000 commits
- QualityAnalyzer: < 3s for 1000 commits
- RiskAssessment: < 0.5s after analytics complete
- All charts: < 500ms total
- ASCII art generation: < 100ms per chart
- Section formatting: < 200ms total
- Peak memory: < 200MB for 5000 commits
