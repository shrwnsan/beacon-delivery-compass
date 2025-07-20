# Troubleshooting Guide

This guide helps you resolve common issues when using Beacon.

## Installation Issues

### Python Version Problems

**Problem**: "Python 3.8+ required" error
```bash
$ beacon
Error: Python 3.8 or higher is required
```

**Solution**:
```bash
# Check Python version
python --version
python3 --version

# Install Python 3.8+ if needed
# macOS: brew install python@3.8
# Ubuntu: sudo apt install python3.8
# Windows: Download from python.org

# Use specific Python version
python3.8 -m venv venv
source venv/bin/activate
pip install beacon
```

### Virtual Environment Issues

**Problem**: "command not found: beacon"
```bash
$ beacon
beacon: command not found
```

**Solution**:
```bash
# Ensure virtual environment is active
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Check if beacon is installed
pip list | grep beacon

# Reinstall if needed
pip install beacon
```

### Permission Errors

**Problem**: "Permission denied" during installation
```bash
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install beacon

# Or use --user flag (not recommended)
pip install --user beacon
```

## Git Repository Issues

### Not a Git Repository

**Problem**: "Not a git repository" error
```bash
$ beacon
Error: Not a git repository (or any of the parent directories)
```

**Solution**:
```bash
# Check if you're in a git repository
git status

# Initialize git repository if needed
git init

# Or specify repository path
beacon --repo /path/to/git/repo
```

### Empty Repository

**Problem**: "No commits found" error
```bash
$ beacon
Error: No commits found in repository
```

**Solution**:
```bash
# Check if repository has commits
git log --oneline

# Make an initial commit if needed
git add .
git commit -m "Initial commit"
```

### Shallow Clone Issues

**Problem**: Limited history in shallow clones
```bash
$ beacon --range --since "1 month ago"
Error: Requested range exceeds available history
```

**Solution**:
```bash
# Unshallow the repository
git fetch --unshallow

# Or clone with full history
git clone --no-single-branch --no-tags https://github.com/user/repo.git
```

## Command Line Issues

### Invalid Arguments

**Problem**: "Invalid argument" errors
```bash
$ beacon --format invalid
Error: Invalid format: 'invalid'
```

**Solution**:
```bash
# Check available formats
beacon --help

# Use valid formats: standard, extended, json
beacon --format standard
beacon --format extended
beacon --format json
```

### Date Format Issues

**Problem**: "Invalid date format" error
```bash
$ beacon --range --since "next week"
Error: Invalid date format: 'next week'
```

**Solution**:
```bash
# Use valid date formats
beacon --range --since "1 week ago"
beacon --range --since "2025-07-01"
beacon --range --since "yesterday"
beacon --range --since "2 days ago"
```

### Commit Hash Issues

**Problem**: "Commit not found" error
```bash
$ beacon abc123
Error: Commit 'abc123' not found
```

**Solution**:
```bash
# Check available commits
git log --oneline -10

# Use full hash or longer prefix
beacon abc123def456789
beacon HEAD~5
```

## Output and Formatting Issues

### JSON Parsing Errors

**Problem**: Malformed JSON output
```bash
$ beacon --format json | jq .
parse error: Invalid numeric literal
```

**Solution**:
```bash
# Check for error messages in output
beacon --format json 2>&1 | head -20

# Ensure clean JSON output
beacon --format json > output.json
cat output.json | jq .
```

### Unicode/Encoding Issues

**Problem**: Garbled characters in output
```bash
$ beacon
Commit: abc123
Author: JÃ¶hn DÃ¶e
```

**Solution**:
```bash
# Set proper locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# On Windows, use PowerShell or WSL
# Or use JSON format for programmatic processing
beacon --format json
```

## Performance Issues

### Large Repository Performance

**Problem**: Slow analysis on large repositories
```bash
$ beacon --range --since "1 year ago"
[...hangs for minutes...]
```

**Solution**:
```bash
# Use shorter time ranges
beacon --range --since "1 week ago"
beacon --range --since "1 month ago"

# Use specific date ranges
beacon --range --since "2025-07-01" --until "2025-07-31"

# Analyze specific commits instead
beacon abc123
beacon HEAD~10..HEAD
```

### Memory Issues

**Problem**: Out of memory errors on large repos
```bash
$ beacon --range --since "1 year ago"
MemoryError
```

**Solution**:
```bash
# Use shorter ranges
beacon --range --since "1 week ago"

# Use sampling approach
beacon --range --since "1 month ago" --until "2 weeks ago"
```

## Integration Issues

### Git Hooks Not Working

**Problem**: Git hooks don't execute
```bash
# Hook file exists but doesn't run
```

**Solution**:
```bash
# Make hook executable
chmod +x .git/hooks/post-commit

# Check shebang line
head -1 .git/hooks/post-commit
# Should be: #!/bin/bash

# Test hook manually
./.git/hooks/post-commit
```

### CI/CD Pipeline Issues

**Problem**: Beacon not found in CI/CD
```bash
/bin/sh: 1: beacon: not found
```

**Solution**:
```yaml
# In CI/CD configuration
- name: Install Beacon
  run: |
    python -m pip install --upgrade pip
    pip install beacon

# Or use full path
- name: Run Beacon
  run: |
    python -m venv venv
    source venv/bin/activate
    pip install beacon
    beacon --format json
```

### Docker Issues

**Problem**: Beacon fails in Docker
```bash
docker: Error response from daemon: OCI runtime create failed
```

**Solution**:
```dockerfile
# Use proper base image
FROM python:3.8-slim

# Install git
RUN apt-get update && apt-get install -y git

# Set working directory
WORKDIR /workspace

# Install beacon
RUN pip install beacon

# Ensure git repository is available
COPY . .
```

## Platform-Specific Issues

### Windows Issues

**Problem**: Path separator issues
```bash
beacon --repo C:\Users\name\repo
Error: Invalid path format
```

**Solution**:
```bash
# Use forward slashes or quotes
beacon --repo "C:/Users/name/repo"
beacon --repo "C:\\Users\\name\\repo"
```

### macOS Issues

**Problem**: Xcode command line tools missing
```bash
xcrun: error: invalid active developer path
```

**Solution**:
```bash
# Install Xcode command line tools
xcode-select --install

# Or specify git path
export GIT_PYTHON_GIT_EXECUTABLE=/usr/local/bin/git
```

### Linux Issues

**Problem**: Git not found
```bash
git: command not found
```

**Solution**:
```bash
# Install git
sudo apt-get install git  # Ubuntu/Debian
sudo yum install git      # CentOS/RHEL
sudo pacman -S git        # Arch
```

## Network and Proxy Issues

### Corporate Proxy Issues

**Problem**: pip install fails behind proxy
```bash
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None))
```

**Solution**:
```bash
# Configure pip for proxy
pip install --proxy http://proxy.company.com:8080 beacon

# Or set environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
pip install beacon
```

## Debugging Steps

### Enable Verbose Output

```bash
# Run with debug information
python -m beacon --debug

# Check Python path
python -c "import sys; print(sys.path)"

# Check beacon installation
python -c "import beacon; print(beacon.__file__)"
```

### Check Git Configuration

```bash
# Verify git is working
git --version
git config --list

# Check repository status
git status
git log --oneline -5
```

### Test Basic Functionality

```bash
# Test git log directly
git log --numstat --format="%H|%an|%ad|%s" -1

# Test beacon components
python -c "from beacon.core.analyzer import GitAnalyzer; print('OK')"
```

## Getting Help

### Collect System Information

```bash
# Create diagnostic report
echo "=== System Information ===" > beacon-debug.txt
python --version >> beacon-debug.txt
git --version >> beacon-debug.txt
pip list | grep beacon >> beacon-debug.txt
echo "=== Git Status ===" >> beacon-debug.txt
git status >> beacon-debug.txt
echo "=== Beacon Test ===" >> beacon-debug.txt
beacon --format json 2>&1 >> beacon-debug.txt
```

### Report Issues

When reporting issues, include:
1. Operating system and version
2. Python version (`python --version`)
3. Git version (`git --version`)
4. Beacon version (`pip show beacon`)
5. Full error message
6. Steps to reproduce
7. Diagnostic report (from above)

### Community Support

- **GitHub Issues**: https://github.com/shrwnsan/beacon-delivery-compass/issues
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check docs/ directory for updates

## Quick Fixes Reference

| Issue | Quick Fix |
|-------|-----------|
| Command not found | `source venv/bin/activate` |
| Not a git repo | `git init` or `beacon --repo /path` |
| Python version | `python3.8 -m venv venv` |
| Permission denied | Use virtual environment |
| Large repo slow | Use `--since "1 week ago"` |
| Invalid date | Use "1 week ago" format |
| Commit not found | Check `git log --oneline` |
| JSON parse error | Check for error messages first |
