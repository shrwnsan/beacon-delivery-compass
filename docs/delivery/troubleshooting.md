# 🛠️ Troubleshooting Guide

This guide helps you resolve common issues when using Beacon Delivery Compass. If you don't find your issue here, please [open a GitHub issue](https://github.com/shrwnsan/beacon-delivery-compass/issues/new).

## 🔍 Table of Contents
- [Installation Issues](#-installation-issues)
- [Command Line Usage](#-command-line-usage)
- [Git Repository Analysis](#-git-repository-analysis)
- [Performance Issues](#-performance-issues)
- [Common Error Messages](#-common-error-messages)
- [Getting Help](#-getting-help)

## 🏗️ Installation Issues

### Python Version Problems

**Symptom**: `Python 3.7+ is required` error

```bash
$ beaconled
Error: Python 3.7 or higher is required
```

**Solution**:
```bash
# Check installed Python version
python --version  # or python3 --version

# If needed, install Python 3.7+
# macOS: brew install python@3.9
# Ubuntu: sudo apt install python3.9
# Windows: Download from python.org

# Create fresh virtual environment
python3.9 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install --upgrade pip
pip install beaconled
```

### Package Installation Failures

**Symptom**: `pip install` fails with dependency errors

**Solution**:
```bash
# Ensure pip is up to date
python -m pip install --upgrade pip

# Try with --no-cache-dir
pip install --no-cache-dir beaconled

# If using a virtual environment, create a fresh one
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install beaconled
```

## 💻 Command Line Usage

### Command Not Found

**Symptom**: `beaconled: command not found`

**Solution**:
1. Ensure virtual environment is activated:
   ```bash
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
2. Verify installation:
   ```bash
   pip list | findstr beaconled  # Windows
   pip list | grep beaconled     # macOS/Linux
   ```
3. Try running with Python module syntax:
   ```bash
   python -m beaconled --help
   ```

## 🔍 Git Repository Analysis

### Git Not Found

**Symptom**: `git: command not found` or `Git executable not found`

**Solution**:
- Install Git from [git-scm.com](https://git-scm.com/)
- Ensure Git is in your system PATH
- Verify with: `git --version`

### Repository Access Issues

**Symptom**: `fatal: not a git repository`

**Solution**:
```bash
# Navigate to a git repository
cd /path/to/your/git/repo

# Or specify the repository path
beaconled /path/to/your/git/repo
```

## ⚡ Performance Issues

### Slow Analysis

**Symptom**: Analysis takes too long on large repositories

**Solution**:
1. Use `--since` to limit the date range:
   ```bash
   beaconled --since 1m
   ```
2. Exclude large directories with `.gitignore`
3. For very large repos, consider using `--limit` to restrict the number of commits

## ❌ Common Error Messages

### `ModuleNotFoundError: No module named '...'`

**Solution**:
```bash
# Reinstall with all dependencies
pip install --force-reinstall beaconled

# Or install missing dependency manually
pip install missing-module-name
```

### `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Avoid using sudo with pip
# Instead, use:
pip install --user beaconled

# Or better, use a virtual environment
python -m venv .venv
source .venv/bin/activate
pip install beaconled
```

## 🆘 Getting Help

If you've tried the solutions above and are still having issues:

1. **Check the documentation**:
   - [Installation Guide](../installation.md)
   - [Basic Usage Guide](../examples/basic-usage.md)

2. **Search existing issues**:
   [GitHub Issues](https://github.com/shrwnsan/beacon-delivery-compass/issues)

3. **Create a new issue** with:
   - Steps to reproduce the problem
   - Full error message
   - Your operating system and Python version
   - Beacon version (`beaconled --version`)

## 🔄 Still Stuck?

- Join our [Discussions](https://github.com/shrwnsan/beacon-delivery-compass/discussions)
- Check the [Documentation](../README.md)
- Review the [changelog](../CHANGELOG.md) for known issues in your version
