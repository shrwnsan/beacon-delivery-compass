# Installation Guide

This guide covers different ways to install Beacon, with a strong emphasis on using virtual environments to maintain a clean Python setup.

## Why Use Virtual Environments?

Virtual environments are essential for Python development because they:
- Prevent package conflicts between different projects
- Allow you to use different versions of packages for different projects
- Keep your system Python clean and stable
- Make it easy to reproduce environments across different machines
- Enable easy cleanup by simply deleting the virtual environment

## Prerequisites

- Python 3.8 or higher
- Git (for repository analysis)

Check your Python version:
```bash
python --version
# or
python3 --version
```

## Recommended Installation (with Virtual Environment)

### 1. Create a Virtual Environment

```bash
# Create a new virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

You'll know the virtual environment is active when you see `(.venv)` in your terminal prompt.

### 2. Install Beacon

```bash
# Install from PyPI (when available)
pip install beaconled

# Or install the latest development version
pip install git+https://github.com/shrwnsan/beaconled-delivery-compass.git
```

### 3. Verify Installation

```bash
beaconled --help
```

## Development Installation

If you want to contribute to Beacon or test the latest features:

### 1. Clone the Repository

```bash
git clone https://github.com/shrwnsan/beaconled-delivery-compass.git
cd beaconled-delivery-compass
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install in Development Mode

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

This installs Beacon in "editable" mode, so changes to the source code are immediately reflected.

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=beaconled --cov-report=term-missing

# Run code quality checks
black src tests
flake8 src tests
mypy src
```

## Alternative Installation Methods

### Using pipx (Isolated Installation)

If you want to install Beacon globally but isolated from other packages:

```bash
# Install pipx if you don't have it
pip install --user pipx
pipx ensurepath

# Install beaconled with pipx
pipx install beaconled
```

### System-wide Installation (Not Recommended)

While possible, we don't recommend system-wide installation as it can cause conflicts:

```bash
# Only if you really need system-wide installation
pip install beaconled
```

## Managing Your Virtual Environment

### Activating and Deactivating

```bash
# Activate (run this each time you open a new terminal)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Deactivate when you're done
deactivate
```

### Updating Beacon

```bash
# Make sure your virtual environment is active
source .venv/bin/activate

# Update to latest version
pip install --upgrade beaconled
```

### Removing the Installation

```bash
# Simply delete the virtual environment directory
rm -rf .venv  # macOS/Linux
rmdir /s .venv  # Windows
```

## Troubleshooting

### Python Version Issues

If you have multiple Python versions installed:

```bash
# Use specific Python version
python3.9 -m venv .venv
python3.10 -m venv .venv
```

### Permission Errors

If you get permission errors, make sure you're using a virtual environment rather than installing system-wide.

### Git Not Found

Beacon requires Git to analyze repositories. Install Git from:
- macOS: `brew install git` or download from [git-scm.com](https://git-scm.com/)
- Linux: `sudo apt-get install git` or equivalent for your distribution
- Windows: Download from [git-scm.com](https://git-scm.com/)

## Next Steps

Once installed, check out:
- [Usage Examples](usage.md) - Learn how to use Beacon effectively
- [Integration Guide](integrations.md) - Integrate Beacon into your workflow
- [API Reference](api-reference.md) - Detailed command reference

## Best Practices Summary

1. **Always use virtual environments** for Python projects
2. **Activate your virtual environment** before running Beacon
3. **Keep your virtual environments organized** (use descriptive names)
4. **Document your environment** (consider using requirements.txt files)
5. **Update regularly** but test in development first