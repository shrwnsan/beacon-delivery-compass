# Git Analytics Toolkit

A comprehensive toolkit for analyzing git repository statistics and development metrics.

## Features

- Commit-level analytics with detailed breakdowns
- Component and file type analysis
- Impact assessment (high/medium/low)
- Range analysis for teams and sprints
- Multiple output formats (standard, extended, JSON)
- Integration with CI/CD pipelines and git hooks

## Installation

```bash
pip install git-analytics-toolkit
```

## Quick Start

```bash
# Analyze latest commit
git-analytics

# Weekly team report
git-analytics --range --since "1 week ago"

# JSON output for automation
git-analytics --format json
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Usage Examples](docs/usage.md)
- [Integration Guide](docs/integrations.md)
- [API Reference](docs/api-reference.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
