# Contributing to Beacon

Thank you for your interest in contributing to Beacon - your delivery compass for empowered product builders!

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/shrwnsan/beaconled-delivery-compass.git
   cd beacon-delivery-compass
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e .[dev]
   ```

## Development Workflow

### Code Quality Standards
We maintain high code quality standards using these tools:

```bash
# Format code
black src tests

# Lint code
flake8 src tests

# Type checking
mypy src

# Run tests
pytest

# Run tests with coverage
pytest --cov=beacon --cov-report=term-missing
```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code patterns and conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all quality checks
   black src tests
   flake8 src tests
   mypy src
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description of changes"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use Black formatter (line length: 88)
- Include type hints for all functions and methods
- Write descriptive docstrings for public functions

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb in present tense
- Keep the first line under 50 characters
- Include more details in the body if needed

### Testing
- Write unit tests for new functionality
- Maintain or improve test coverage
- Test edge cases and error conditions
- Use descriptive test names

## Project Structure

```
src/beacon/                 # Main package
├── cli.py                  # Command-line interface
├── core/                   # Core business logic
│   ├── analyzer.py         # Git analysis engine
│   └── models.py           # Data models
└── formatters/             # Output formatters
    ├── standard.py         # Standard text output
    ├── extended.py         # Extended output
    └── json_format.py      # JSON output
```

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any error messages or logs

## Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Describe the use case clearly
- Explain how it fits with Beacon's mission
- Consider implementation complexity

## Questions?

Feel free to open an issue for questions about:
- Development setup
- Code architecture
- Feature implementation
- Best practices

## License

By contributing to Beacon, you agree that your contributions will be licensed under the MIT License.