# Technology Stack

## Build System
- **Build Backend**: setuptools with pyproject.toml configuration
- **Package Management**: pip with setup.py for distribution
- **Python Versions**: 3.8, 3.9, 3.10, 3.11 (minimum 3.8)

## Dependencies
- **Runtime**: Zero external dependencies - uses only Python standard library
- **Development**: pytest, pytest-cov, black, flake8, mypy

## Code Quality Tools
- **Formatter**: Black (line length: 88, target Python 3.8+)
- **Linter**: flake8 for style checking
- **Type Checker**: mypy with strict configuration
- **Testing**: pytest with coverage reporting

## Common Commands

### Development Setup
```bash
pip install -e .[dev]  # Install in development mode with dev dependencies
```

### Code Quality
```bash
black src tests        # Format code
flake8 src tests       # Lint code
mypy src              # Type checking
```

### Testing
```bash
pytest                # Run all tests
pytest --cov=beacon --cov-report=term-missing  # Run with coverage
```

### Build & Distribution
```bash
python -m build       # Build distribution packages
pip install beacon    # Install from PyPI
```

## Git Commands
- **Always use --no-pager**: When running git commands to read terminal output, use `git --no-pager <command>` to ensure full output is displayed without pagination

## CI/CD
- GitHub Actions workflow testing across Python 3.8-3.11
- Automated linting, type checking, and testing
- Coverage reporting via Codecov