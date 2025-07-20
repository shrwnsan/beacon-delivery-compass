# Project Structure

## Source Layout
```
src/git_analytics/           # Main package (src layout)
├── __init__.py             # Package initialization
├── cli.py                  # Command-line interface entry point
├── core/                   # Core business logic
│   ├── analyzer.py         # Git repository analysis engine
│   └── models.py           # Data models (dataclasses)
├── formatters/             # Output formatting modules
│   ├── standard.py         # Standard text output
│   ├── extended.py         # Extended detailed output
│   └── json_format.py      # JSON output format
└── integrations/           # External integrations (future)
```

## Architecture Patterns
- **Separation of Concerns**: CLI, core logic, and formatters are separate
- **Data Models**: Use dataclasses for structured data (CommitStats, RangeStats, FileStats)
- **Strategy Pattern**: Multiple formatter implementations with common interface
- **Dependency Injection**: Analyzer accepts repository path, formatters are pluggable

## Key Conventions
- **Entry Point**: `beacon` command maps to `git_analytics.cli:main`
- **Error Handling**: CLI catches exceptions and exits with status code 1
- **Git Integration**: Uses subprocess to call git commands directly
- **Type Hints**: Full type annotations required (enforced by mypy)
- **Docstrings**: All public functions and classes documented

## Supporting Directories
- `tests/` - Test suite (unit, integration, fixtures)
- `docs/` - Documentation and examples
- `examples/` - Usage examples and integrations
- `scripts/` - Utility scripts and automation tools

## Configuration Files
- `pyproject.toml` - Build system and tool configuration
- `setup.py` - Package metadata and entry points
- `.github/workflows/` - CI/CD automation