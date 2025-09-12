# Troubleshooting Guide

This guide helps you resolve common issues when using the Beacon Delivery Compass.

## Common Issues

### 1. CLI Format Not Recognized

**Problem**: The `enhanced-extended` format option is not available in the CLI.

**Solution**:
1. The `enhanced-extended` format has been merged into the standard `extended` format.
2. Update your commands to use `--format extended` instead of `--format enhanced-extended`.
3. All enhanced analytics features are now available in the standard extended format.

To verify available formats:
```bash
beaconled --help | grep format
```

### 2. Import Errors

**Problem**: You see import errors when running the tool.

**Solution**:
1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Check your Python version (3.8+ required)
3. Verify your PYTHONPATH is set correctly

### 3. Performance Issues

For large repositories, you might experience slow performance. Try these optimizations:

1. **Reduce Analysis Scope**:
   ```bash
   # Instead of analyzing the entire history
   beaconled --format extended --since 1y

   # Analyze a smaller period
   beaconled --format extended --since 1m
   ```

2. **Check Caching**: The system includes caching. If you're running repeated analyses with the same parameters, subsequent runs should be faster.

3. **Memory Usage**: For very large repositories, you might need to increase Python's memory limits.

### 4. Output Formatting Issues

If you encounter display issues:

1. **Terminal Width**: The output is optimized for terminals at least 120 characters wide.
2. **Terminal Compatibility**: Some terminals may not support all formatting features. Try using a different terminal or the `--no-emoji` option:
   ```bash
   beaconled --format extended --no-emoji --since 1w
   ```

3. **Encoding Issues**: If you see encoding errors, try setting the Python encoding:
   ```bash
   PYTHONIOENCODING=utf-8 beaconled --format extended --since 1w
   ```

## Debugging Steps

### 1. Enable Verbose Output

Add the `-v` or `--verbose` flag to get more detailed output:

```bash
beaconled --format extended --since 1week --verbose
```

### 2. Check Logs

Logs are stored in `~/.beacon/logs/` by default. Check these files for detailed error information.

### 3. Profile Performance

To profile the performance of the analytics pipeline:

```bash
python -m cProfile -o profile.out -m src.beaconled.cli --format extended --since 1week
```

Then analyze the profile:

```bash
python -m pstats profile.out
```

### 4. Memory Profiling

To check for memory leaks:

```bash
pip install memory-profiler
python -m memory_profiler src/beaconled/cli.py --format extended --since 1week
```

## Environment Variables

You can control various aspects of the tool using environment variables:

- `BEACON_DEBUG=1`: Enable debug logging
- `BEACON_NO_CACHE=1`: Disable caching
- `BEACON_CACHE_DIR`: Custom cache directory

## Getting Help

If you're still experiencing issues:
1. Check the [documentation](https://github.com/yourorg/beacon-delivery-compass/docs)
2. Search existing issues on GitHub
3. Open a new issue with detailed reproduction steps
