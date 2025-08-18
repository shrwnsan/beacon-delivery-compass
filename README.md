# Beacon Delivery Compass

[![PyPI version](https://badge.fury.io/py/beaconled.svg)](https://badge.fury.io/py/beaconled)
[![Python Version](https://img.shields.io/pypi/pyversions/beaconled.svg)](https://pypi.org/project/beaconled/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Your delivery compass for empowered product builders. A comprehensive toolkit for analyzing git repository statistics and development metrics.

## Features

- **Commit-Level Analytics**: Get detailed breakdowns of commit activity, including impact and component analysis.
- **Product Analytics**: Gain deeper insights with a comprehensive product analytics system.
- **Team & Sprint Analysis**: Analyze development patterns for specific teams and time ranges.
- **Multiple Output Formats**: Choose from standard, extended, and JSON formats to fit your needs.
- **Flexible Date Handling**:
  - Timezone-aware date processing, standardized to UTC.
  - Support for both relative (`1d`, `2w`) and absolute (`YYYY-MM-DD`) dates.
- **Reliable Git Integration**: Built on `GitPython` for robust and secure repository operations.
- **Rich Output**: Enjoy colorized and well-formatted terminal output, powered by `rich`.
- **Code Quality**:
  - Fully type-safe codebase with strict `mypy` checking.
  - Comprehensive test suite with high coverage.
  - Consistent code style enforced by `ruff` and `black`.

## Development & Contribution

We welcome contributions! For details on how to contribute, please see our [Contribution Guidelines](CONTRIBUTING.md).

### Project Roadmap

Our development priorities and planned improvements are tracked in the [Enhancement Plan](docs/development/roadmap.md). This document provides visibility into:
- Upcoming features and improvements
- Current technical debt
- Performance optimization plans
- Testing and quality assurance goals

### Code Quality

Beacon is built with a strong focus on code quality and maintainability. We use pre-commit hooks to ensure consistent code quality across the project.

#### Pre-commit Configuration

We provide two pre-commit configurations:

1. **Development Mode** (`.pre-commit-dev.yaml`):
   - More lenient rules for local development
   - Focuses on critical issues only
   - Faster feedback loop

   ```bash
   # Setup development pre-commit hooks
   make dev-setup
   ```

2. **Production Mode** (`.pre-commit-config.yaml`):
   - Strict rules for CI/CD and production
   - Enforces all code quality standards
   - Includes all linters and formatters

   ```bash
   # Setup production pre-commit hooks
   make prod-setup
   ```

#### Key Quality Tools

- **Type Safety**: Full static type checking with [mypy](https://mypy-lang.org/)
- **Code Style**: Consistent code formatting with [Black](https://black.readthedocs.io/)
- **Linting**: Code quality enforcement with [Ruff](https://github.com/charliermarsh/ruff)
- **Documentation**: Comprehensive docstrings and API documentation

#### Development Workflow

1. During active development, use `dev-setup` for faster commits
2. Before pushing changes, run `prod-setup` to ensure all checks pass
3. Use `git commit --no-verify` sparingly when needed

#### Manual Checks

```bash
# Run type checking
mypy --ignore-missing-imports src/beaconled

# Run all code quality checks
make lint
```

## Testing

Beacon includes a comprehensive test suite with a user-friendly test runner. The test runner provides several options for running tests:

### Running Tests

Run the test suite with the interactive menu:

```bash
python run_tests.py
```

### Test Runner Options

1. **Simple Environment Test**
   - Verifies the basic test environment is set up correctly

2. **Run All Tests**
   - Executes all test cases across all categories (unit, integration, performance)

3. **Run Specific Test Category**
   - Select from available test categories:
     - Unit Tests: Core functionality tests
     - Integration Tests: Component interaction tests
     - Performance Tests: Benchmark and performance tests

4. **Show Environment Info**
   - Displays detailed information about the test environment

### Running Specific Tests

You can also run specific test files or directories directly:

```bash
# Run all unit tests
python -m pytest tests/unit/

# Run a specific test file
python -m pytest tests/unit/test_analyzer.py

# Run tests with coverage report
python -m pytest --cov=src tests/
```

## Installation

Beacon requires:
- Python 3.10+
- Git 2.23+
- GitPython 3.1.0+

We recommend installing in a virtual environment.

### Quick Install

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install from PyPI
pip install beaconled
```

### Verify Installation

```bash
beaconled --version
```

For more detailed instructions, including development setup and troubleshooting, see the [Installation Guide](docs/installation.md).

## Quick Start

### Date and Timezone Handling

Beacon provides flexible date parsing with consistent UTC handling, making it reliable for distributed teams.

#### Relative Date Formats
```
1d      # 1 day ago from now in UTC
2w      # 2 weeks ago from now in UTC
3m      # 3 months ago from now in UTC (approximate, using 4 weeks/month)
1y      # 1 year ago from now in UTC (approximate, using 52 weeks/year)
```

#### Absolute Date Formats (UTC Only)
```
2025-01-15              # January 15, 2025 at 00:00 UTC
2025-01-15 14:30        # January 15, 2025 at 14:30 UTC
```

#### Timezone Handling
Beacon uses UTC for all date handling to ensure consistency:
- All input dates are interpreted as UTC
- Results are displayed in UTC
- No timezone conversion is performed

Example:
```bash
# Analyze commits between 9 AM to 5 PM UTC
beaconled --range --since "2025-01-15 09:00" --until "2025-01-15 17:00"
```

### Basic Usage

Analyze a git repository:
```bash
beaconled /path/to/repo
```

Generate a weekly team report:
```bash
beaconled --range --since "1w" --until "now"
```

### Examples

#### Basic Usage
Analyze changes in the last 3 days:
```bash
beaconled --range --since "3d"
```

#### Date Range Analysis
Analyze changes between specific dates with timezone support:
```bash
# Using relative dates
beaconled --range --since "1w" --until "now"

# Using absolute dates in UTC
beaconled --range --since "2025-01-01 00:00" --until "2025-01-31 23:59"

# Using date only (assumes 00:00 UTC)
beaconled --range --since "2025-01-01" --until "2025-01-31"
```

#### Team Performance Analysis
Generate a detailed team performance report for the last 2 weeks:
```bash
beaconled --range --since "2w" --format extended
```

#### Integration with CI/CD
Example GitHub Actions workflow for automated reporting:
```yaml
name: Weekly Report
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Beacon
        run: pip install beaconled
      - name: Generate weekly report
        run: |
          beaconled --range --since "1w" --format json > weekly-report.json
          # Upload report artifact
          gh release upload weekly weekly-report.json
```

For more detailed usage examples, please refer to the [Usage Examples](docs/examples/basic-usage.md).

## Sample Outputs

### Analyzing a Git Repository

When analyzing a repository, Beacon provides commit details, file changes, and metrics in the standard format:

```bash
beaconled /path/to/my-project
```

```bash
Repository Analysis: /path/to/my-project
Analysis Period: Last 30 commits

=== COMMIT SUMMARY ===
Total Commits: 30
Contributors: 4
Date Range: 2025-01-15 to 2025-01-23

=== COMMIT DETAILS ===
[2025-01-23 14:32] feat: Add user authentication module (John Doe)
  Impact: HIGH - 8 files changed, 245 insertions, 12 deletions
  Components: auth/, middleware/, tests/

[2025-01-23 10:15] fix: Resolve database connection timeout (Jane Smith)
  Impact: MEDIUM - 3 files changed, 28 insertions, 15 deletions
  Components: database/, config/

[2025-01-22 16:45] docs: Update API documentation (Mike Johnson)
  Impact: LOW - 2 files changed, 67 insertions, 3 deletions
  Components: docs/

=== FILE CHANGE METRICS ===
Most Active Files:
  src/auth/login.py: 12 changes
  config/database.py: 8 changes
  tests/test_auth.py: 6 changes

File Type Breakdown:
  Python (.py): 18 files, 456 lines changed
  Markdown (.md): 4 files, 89 lines changed
  JSON (.json): 2 files, 23 lines changed

=== IMPACT ASSESSMENT ===
High Impact Commits: 8 (27%)
Medium Impact Commits: 15 (50%)
Low Impact Commits: 7 (23%)
```

### Generating Weekly Team Reports

For range analysis with contributor breakdown and commit frequency:

```bash
beaconled --range --since "1w" --format standard
```

```bash
Weekly Team Report
Analysis Period: 2025-01-16 to 2025-01-23 (7 days)

=== TEAM OVERVIEW ===
Total Contributors: 4
Total Commits: 23
Average Commits/Day: 3.3
Active Days: 6/7

=== CONTRIBUTOR BREAKDOWN ===
John Doe: 9 commits (39%)
  - High Impact: 3 commits
  - Medium Impact: 4 commits
  - Low Impact: 2 commits
  - Most Active: Monday, Wednesday

Jane Smith: 7 commits (30%)
  - High Impact: 2 commits
  - Medium Impact: 3 commits
  - Low Impact: 2 commits
  - Most Active: Tuesday, Thursday

Mike Johnson: 4 commits (17%)
  - High Impact: 1 commit
  - Medium Impact: 2 commits
  - Low Impact: 1 commit
  - Most Active: Friday

Sarah Wilson: 3 commits (13%)
  - High Impact: 0 commits
  - Medium Impact: 2 commits
  - Low Impact: 1 commit
  - Most Active: Monday

=== COMMIT FREQUENCY ===
Monday: 5 commits (22%)
Tuesday: 4 commits (17%)
Wednesday: 6 commits (26%)
Thursday: 3 commits (13%)
Friday: 3 commits (13%)
Saturday: 1 commit (4%)
Sunday: 1 commit (4%)

=== COMPONENT ACTIVITY ===
Most Changed Components:
  frontend/: 8 commits, 234 lines
  backend/api/: 6 commits, 189 lines
  tests/: 5 commits, 156 lines
  docs/: 4 commits, 78 lines
```

## Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions and troubleshooting
- [Usage Guide](docs/examples/basic-usage.md) - Comprehensive usage documentation
- [System Architecture](docs/development/architecture/overview.md) - High-level system design and component relationships
- [Roadmap](ROADMAP.md) - Development plans and upcoming features
- [Integration Guide](docs/delivery/integrations.md) - Instructions for integrating with CI/CD pipelines and git hooks
- [API Reference](docs/api/api.md) - Detailed API documentation
- [Changelog](CHANGELOG.md) - Release notes and version history

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

Check out our [Roadmap](ROADMAP.md) to see what we're working on and what's coming next!
