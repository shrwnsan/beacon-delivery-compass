# Testing Guide

This document provides an overview of the testing strategy, test organization, and how to run tests in the Beacon Delivery Compass project.

## Table of Contents
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Intelligent Test Selection with pytest-testmon](#intelligent-test-selection-with-pytest-testmon)
- [Test Types](#test-types)
- [Test Coverage](#test-coverage)
- [Performance Testing](#performance-testing)
- [CI/CD Integration](#cicd-integration)
- [Writing New Tests](#writing-new-tests)

## Test Organization

Tests are organized in the `tests/` directory with the following structure:

```
tests/
├── unit/                  # Unit tests
│   ├── test_analyzer.py   # Tests for core analyzer functionality
│   ├── test_cli.py        # Tests for command-line interface
│   ├── test_formatters/   # Tests for different output formatters
│   ├── test_timezone_handling.py  # Timezone and DST tests
│   └── test_property_based.py     # Property-based tests
│
├── integration/          # Integration tests
│   └── test_integration.py
│
├── performance/          # Performance benchmarks
│   ├── conftest.py       # Performance test configuration
│   └── test_large_repo_benchmark.py  # Large repository benchmarks
│
└── conftest.py           # Global test configuration
```

## Running Tests

### Quickstart
```bash
# 1. Ensure virtual environment is active
source .venv/bin/activate

# 2. Install dependencies (if not already done)
pip install -r requirements.txt -r test_requirements.txt

# 3. Run tests
pytest -q --maxfail=1 --disable-warnings
```

### Prerequisites
```bash
# Install development dependencies
pip install -e ".[dev]"
```

### Running All Tests
```bash
# Run all tests except performance tests
pytest

# Run tests with coverage report
pytest --cov=src/beaconled --cov-report=term-missing
```

## Intelligent Test Selection with pytest-testmon

To dramatically improve test execution speed during development, we use **pytest-testmon** - a tool that runs only the tests affected by your code changes.

### Why pytest-testmon?

**Performance Impact:**
- **Before**: Running all 239 tests on every change → 20-30 seconds
- **After**: Running only 5-15 relevant tests → 2-5 seconds
- **Speedup**: 5-10x faster for typical development changes

### How It Works

pytest-testmon automatically:
1. **Tracks dependencies** between code files and tests
2. **Detects files changed** since the last run
3. **Selects only tests** that could be affected by those changes

### Usage

```bash
# Run tests with intelligent selection (default in precommit)
pytest --testmon

# Force full test run (when needed)
pytest --testmon --force

# See testmon statistics
pytest --testmon --stats

# Clear testmon data (rarely needed)
pytest --testmon-deselect-all
```

### Real-world Examples

```bash
# Changed: src/beaconled/utils/date_utils.py
# Result: Runs only 8 date-related tests instead of 239

# Changed: src/beaconled/cli.py (help text only)
# Result: Runs only 4 CLI tests instead of 239

# Changed: src/beaconled/core/analyzer.py (bug fix)
# Result: Runs 22 analyzer + integration tests instead of 239
```

### Integration with Precommit

pytest-testmon is automatically integrated into your precommit hooks:

```bash
# Normal workflow - testmon runs automatically
git add .
git commit -m "your changes"
```

### Best Practices

1. **Trust testmon** - it's usually right about what needs testing
2. **Force full runs** when making architectural changes
3. **Monitor performance** to ensure expected speedups
4. **Share .testmondata** (optional) with your team

### Running Specific Test Types
```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only performance tests (requires --runslow flag)
pytest --runslow tests/performance/

# Run tests matching a specific pattern
pytest -k "test_parse_date"
```

## Test Types

### 1. Unit Tests
- Test individual functions and methods in isolation
- Use mocks for external dependencies
- Focus on edge cases and error conditions
- Located in `tests/unit/`

### 2. Integration Tests
- Test interactions between components
- May use real dependencies (e.g., actual git repositories)
- Located in `tests/integration/`

### 3. Property-Based Tests
- Test properties that should hold true for all inputs
- Use Hypothesis to generate test cases
- Located in `tests/unit/test_property_based.py`

### 4. Performance Tests
- Benchmark performance with large repositories
- Marked with `@pytest.mark.performance`
- Located in `tests/performance/`

## Test Coverage

We aim to maintain high test coverage (90%+). To check coverage:

```bash
# Generate HTML coverage report
pytest --cov=src/beaconled --cov-report=html

# Open the HTML report
open htmlcov/index.html
```

## Performance Testing

### Running Performance Benchmarks

```bash
# Run all performance tests
pytest --runslow tests/performance/

# Generate a test repository for manual testing
python -m tests.performance.test_large_repo_benchmark --create-test-repo test-repo-large
```

### Performance Test Configuration

Performance tests are configured in `pyproject.toml`:

```toml
[performance]
warmup_iterations = 3     # Number of warmup iterations
benchmark_iterations = 10 # Number of benchmark iterations
timeout = 300             # Timeout in seconds (5 minutes)
```

## CI/CD Integration

Tests are automatically run on push and pull requests via GitHub Actions. The CI pipeline includes:

1. Unit and integration tests across multiple Python versions
2. Code coverage reporting
3. Code quality checks (ruff, mypy, bandit)
4. Security audit (pip-audit)
5. Performance tests (on schedule)

### pytest-testmon in CI/CD

The intelligent test selection with pytest-testmon provides significant performance benefits in CI/CD:

#### **Performance Impact**
| Scenario | Before | After | Improvement |
|----------|--------|--------|-------------|
| Initial commit | 2-3 min | 2-3 min | No change |
| Small code change | 2-3 min | 15-30 sec | **5-10x faster** |
| Documentation change | 2-3 min | 5-10 sec | **10-20x faster** |
| Bug fix in core | 2-3 min | 30-60 sec | **3-5x faster** |

#### **CI Behavior**
- **First run/clean environment**: Runs all tests to initialize testmon data
- **Subsequent runs**: Only runs tests affected by code changes
- **Pull requests**: Smart selection based on files changed in PR
- **No configuration changes needed**: Existing CI commands work seamlessly

#### **Benefits**
- **Faster PR feedback**: Contributors get quicker feedback on changes
- **Reduced CI costs**: Lower CI minutes usage (potentially 70-80% savings)
- **Maintained quality**: Same test coverage and security checks
- **Better developer experience**: Faster iteration cycles

#### **Coverage Integration**
- **No impact on coverage reporting**: Codecov integration unchanged
- **Full coverage accuracy maintained**: Testmon ensures all affected code is tested
- **Cross-platform testing**: Windows, macOS, Linux validation unaffected

## Writing New Tests

### Unit Test Example

```python
def test_parse_date():
    """Test date parsing with various formats."""
    analyzer = GitAnalyzer(".")

    # Test relative dates
    assert analyzer._parse_date("1d") == ...

    # Test absolute dates
    assert analyzer._parse_date("2025-01-01") == ...

    # Test error cases
    with pytest.raises(DateParseError):
        analyzer._parse_date("invalid-date")
```

### Property-Based Test Example

```python
from hypothesis import given, strategies as st

@given(st.dates())
def test_roundtrip_datetime(date):
    """Test that parsing and formatting a date preserves its value."""
    formatted = date.isoformat()
    parsed = _parse_date(formatted)
    assert parsed.date() == date
```

### Performance Test Example

```python
@pytest.mark.performance
def test_large_repo_analysis(benchmark):
    """Benchmark analysis of a large repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup test repository
        repo_path = os.path.join(temp_dir, 'test-repo')
        create_test_repo(repo_path, num_commits=1000, num_files=100)

        # Run benchmark
        analyzer = GitAnalyzer(repo_path)
        result = benchmark(analyzer.get_range_analytics)

        # Verify results
        assert result is not None
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on state from other tests.
2. **Descriptive Names**: Test names should clearly describe what they're testing.
3. **Minimal Fixtures**: Keep test data minimal and focused.
4. **Property-Based Testing**: Use property-based tests for functions with well-defined properties.
5. **Performance Testing**: Add performance tests for critical paths and monitor for regressions.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the package is installed in development mode: `pip install -e .`
2. **Test Failures**: Check for environment-specific issues or timing-related problems.
3. **Performance Test Timeouts**: Adjust the timeout in `pyproject.toml` if needed.
4. **Virtual Environment Confusion**: Ensure `.venv` is active and remove any stray `./venv` directory.

### Debugging Tests

```bash
# Run tests with debug output
pytest -vvs tests/unit/test_example.py

# Drop into debugger on failure
pytest --pdb tests/unit/test_example.py

# Run with logging
pytest --log-cli-level=DEBUG tests/unit/test_example.py
```
