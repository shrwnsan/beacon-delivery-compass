# 📦 Installation Guide

This guide covers different ways to install Beacon Delivery Compass, with best practices for maintaining a clean Python development environment.

## 🏁 Prerequisites

- **Python 3.7** or higher
- **Git** (for repository analysis)
- **pip** (Python package installer)

Verify your Python installation:
```bash
python --version  # or python3 --version
```

## 🚀 Recommended Installation (Virtual Environment)

### 1. Create and Activate a Virtual Environment

```bash
# Create a new virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

You'll know the virtual environment is active when you see `(.venv)` in your terminal prompt.

### 2. Install Beacon Delivery Compass

```bash
# Install the latest stable version from PyPI
pip install beaconled

# Verify installation
beaconled --version
```

## 🔧 Alternative Installation Methods

### Development Installation

If you plan to contribute to the project:

```bash
# Clone the repository
git clone https://github.com/shrwnsan/beacon-delivery-compass.git
cd beacon-delivery-compass

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run tests to verify installation
pytest
```

### Global Installation (Not Recommended)

```bash
# Install globally (requires admin/sudo)
pip install --user beaconled
```

## 🔄 Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade beaconled
```

## 🛠️ Troubleshooting

### Common Issues

1. **Command Not Found**
   - Ensure the virtual environment is activated
   - Verify the installation directory is in your system's PATH

2. **Permission Errors**
   - Avoid using `sudo` with pip
   - Use the `--user` flag or a virtual environment

3. **Dependency Conflicts**
   - Create a fresh virtual environment
   - Update pip: `python -m pip install --upgrade pip`

### Getting Help

If you encounter any issues:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search the [GitHub Issues](https://github.com/shrwnsan/beacon-delivery-compass/issues)
3. [Open a new issue](https://github.com/shrwnsan/beacon-delivery-compass/issues/new) if your problem isn't documented

## 🧹 Uninstalling

To remove Beacon Delivery Compass:

```bash
# Deactivate the virtual environment first if active
deactivate

# Uninstall the package
pip uninstall beaconled

# Optional: Remove the virtual environment
rm -rf .venv  # On Windows: rmdir /s /q .venv
```

## 📚 Next Steps

- [Getting Started Guide](usage.md)
- [Configuration Options](configuration.md)
- [Contributing Guidelines](../CONTRIBUTING.md)