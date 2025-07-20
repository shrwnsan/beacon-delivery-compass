# Beacon

Your delivery compass for empowered product builders.

A comprehensive toolkit for analyzing git repository statistics and development metrics.

## Features

- Commit-level analytics with detailed breakdowns
- Component and file type analysis
- Impact assessment (high/medium/low)
- Range analysis for teams and sprints
- Multiple output formats (standard, extended, JSON)
- Integration with CI/CD pipelines and git hooks

## Installation

We strongly recommend using a virtual environment to avoid conflicts with other Python packages:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install beacon
pip install beacon
```

For development or testing the latest version:

```bash
# Clone and install in development mode
git clone https://github.com/shrwnsan/beacon-delivery-compass.git
cd beacon-delivery-compass
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

```bash
# Analyze latest commit
beacon

# Weekly team report
beacon --range --since "1 week ago"

# JSON output for automation
beacon --format json
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
