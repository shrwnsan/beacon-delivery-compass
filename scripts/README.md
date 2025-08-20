# Test Scripts

This directory contains test scripts for manual verification and sanity testing of the Beacon CLI tool. These scripts are designed to be run manually to verify end-to-end functionality.

## Purpose

These scripts serve as:
- Manual verification tools for CLI functionality
- Documentation of common usage patterns
- Quick sanity checks before releases
- Reference implementations for common use cases

## Available Scripts

### 1. Basic Usage Test
`test_basic_usage.sh`

Verifies core functionality including:
- Basic command output formats (default, JSON, extended)
- Date range filtering
- Basic metrics output

**Usage:**
```bash
./test_basic_usage.sh
```

### 2. Advanced Usage Test
`test_advanced_usage.sh`

Tests more complex scenarios including:
- Relative date ranges (e.g., "7d", "1m")
- Absolute date formats (YYYY-MM-DD)
- File-level change details
- Edge cases (future dates, empty ranges)

**Usage:**
```bash
./test_advanced_usage.sh
```

## Relationship to Automated Tests

These scripts complement the automated test suite in `/tests`:
- **Automated Tests**: Comprehensive, fine-grained unit and integration tests
- **These Scripts**: End-to-end verification of complete workflows

## Prerequisites

- Bash shell
- `jq` for JSON parsing
- Python environment with required dependencies

## Notes

- These scripts are meant for manual verification, not for CI/CD pipelines
- For automated testing, use the test suite in `/tests`
- Always verify the output matches expected behavior

## Adding New Tests

1. For manual verification: Add to the appropriate script
2. For automated testing: Add to the test suite in `/tests`
