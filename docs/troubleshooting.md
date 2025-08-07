# Troubleshooting Guide

This is the canonical troubleshooting guide for Beacon Delivery Compass. If an issue persists, open a GitHub issue: https://github.com/shrwnsan/beacon-delivery-compass/issues/new

- Installation: [installation.md](docs/installation.md)
- API: [api/api.md](docs/api/api.md)
- Examples: [examples/basic-usage.md](docs/examples/basic-usage.md), [examples/advanced-usage.md](docs/examples/advanced-usage.md)

## Installation Issues

### Python Version Problems
Symptom: "Python 3.8+ is required" or Beacon not available in current interpreter.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install beaconled
```

### Package Installation Failures
```bash
python -m pip install --upgrade pip
pip install --no-cache-dir beaconled
# If needed, recreate a clean virtualenv:
rm -rf .venv && python -m venv .venv && source .venv/bin/activate && pip install beaconled
```

## Command Line Usage

### Command Not Found
```bash
# Ensure venv is active
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Verify install
pip show beaconled

# Run via module if needed
python -m beaconled --help
```

## Git Repository Analysis

### Git Not Found
- Install Git from https://git-scm.com/
- Ensure `git --version` works from your shell.

### Repository Access Issues
```bash
# Run inside a git repository
git status

# Or point Beacon at a repo
beaconled --repo /path/to/your/git/repo
```

## Performance Issues

### Slow Analysis on Large Repos
1) Limit the date range:
```bash
beaconled --range --since "1 month ago"
```
2) Exclude large directories via .gitignore
3) Sample or narrow scope where possible

## Common Error Messages

### ModuleNotFoundError
```bash
pip install --force-reinstall beaconled
# Or install the missing dependency explicitly
pip install &lt;missing-module-name&gt;
```

### PermissionError: [Errno 13]
```bash
# Prefer user installs or virtualenvs
pip install --user beaconled
# or
python -m venv .venv &amp;&amp; source .venv/bin/activate &amp;&amp; pip install beaconled
```

## Getting Help

- Check docs:
  - [installation.md](docs/installation.md)
  - [examples/basic-usage.md](docs/examples/basic-usage.md)
- Search existing issues: https://github.com/shrwnsan/beacon-delivery-compass/issues
- Create a new issue including:
  - Repro steps
  - Full error output
  - OS and Python versions
  - `beaconled --version`

## Still Stuck?

- Discussions: https://github.com/shrwnsan/beacon-delivery-compass/discussions
- Changelog: refer to root [../CHANGELOG.md](CHANGELOG.md)
