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

Beacon requires Python 3.7+ and Git. We recommend installing in a virtual environment.

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

Analyze a git repository:

```bash
beaconled /path/to/repo
```

Generate a weekly team report:
```bash
beaconled --range --since "1 week ago"
```

For more detailed usage examples, please refer to the [Usage Examples](docs/usage.md).

## Documentation

- [Installation Guide](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/installation.md)
- [Usage Examples](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/usage.md)
- [Integration Guide](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/integrations.md)
- [API Reference](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/api-reference.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
