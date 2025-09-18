# Security Scanning Solutions

## Problem Analysis

The CI pipeline is failing during security checks with the following error:
```
AttributeError: module 'typer' has no attribute 'rich_utils'
```

This is a compatibility issue between `safety` version 3.6.0 and `typer` version 0.16.0. The `safety` package is trying to access `typer.rich_utils.STYLE_HELPTEXT`, but this attribute has been moved or removed in newer versions of `typer`.

## Solutions

### Option 1: Switch to pip-audit (✅ Recommended)

**Why pip-audit is better:**
- Developed and maintained by the Python Packaging Authority (PyPA)
- More actively maintained than safety
- Better performance and reliability
- Native integration with Python ecosystem
- Uses the same vulnerability database as safety (PyPI Advisory Database)
- Cleaner output and better error handling

**Implementation:**
```bash
# Install pip-audit
pip install pip-audit

# Basic vulnerability scan
pip-audit --desc

# Generate detailed JSON report
pip-audit --format=json --output=vulnerability-report.json

# Scan specific requirements file
pip-audit --requirement=requirements.txt
```

**CI Configuration:**
```yaml
- name: Check for known vulnerabilities
  run: pip-audit --desc
```

### Option 2: Pin safety and typer versions

If you prefer to stick with safety, you can pin compatible versions:

```toml
# In pyproject.toml
[project.optional-dependencies]
dev = [
    # ... other dependencies ...
    "safety==3.2.7",  # Known working version
    "typer<0.16.0",   # Exclude problematic typer versions
]
```

**Pros:**
- Minimal changes to existing setup
- Known working configuration

**Cons:**
- Uses older, potentially less secure versions
- May conflict with other dependencies
- Not a long-term solution

### Option 3: Use alternative vulnerability scanners

**A. Using OSV-Scanner:**
```bash
# Install osv-scanner
go install github.com/google/osv-scanner/cmd/osv-scanner@latest

# Scan current directory
osv-scanner --format=json ./
```

**B. Using Snyk:**
```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate and test
snyk auth
snyk test --file=requirements.txt
```

## Enhanced Security Setup (Complete Solution)

### 1. Update pyproject.toml

```toml
[project.optional-dependencies]
dev = [
    # ... other dependencies ...

    # Security tools
    "bandit>=1.7.0",           # Static security analysis
    "pip-audit>=2.6.1",       # Vulnerability scanning
    "semgrep>=1.45.0",        # Advanced static analysis (optional)
]
```

### 2. Enhanced CI Configuration

```yaml
security:
  name: Security Checks
  runs-on: ubuntu-latest
  needs: test
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Check for known vulnerabilities
      run: |
        echo "🔍 Scanning for known vulnerabilities..."
        pip-audit --desc

    - name: Generate vulnerability report
      run: |
        echo "📋 Generating detailed vulnerability report..."
        pip-audit --format=json --output=vulnerability-report.json

    - name: Upload vulnerability report
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: vulnerability-report
        path: vulnerability-report.json

    - name: Run security linter
      run: |
        echo "🔎 Running security linter..."
        bandit -r src/beaconled -c pyproject.toml

    - name: Optional - Advanced static analysis
      if: github.event_name == 'push' && github.ref == 'refs/heads/main'
      run: |
        echo "🔬 Running advanced static analysis..."
        # Install semgrep if you want more advanced analysis
        # python -m pip install semgrep
        # semgrep --config=auto src/
```

### 3. Local Testing Script

Use the provided security tools to test security locally:

```bash
# Run bandit security scanning
bandit -r src/beaconled -c pyproject.toml

# Run pip-audit for dependency security
pip-audit --desc

# Test with precommit hooks
pre-commit run --all-files
```

### 4. Pre-commit Hook (Optional)

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  # ... other repos ...

  - repo: local
    hooks:
      - id: pip-audit
        name: pip-audit
        entry: pip-audit
        args: [--desc]
        language: system
        pass_filenames: false

      - repo: https://github.com/PyCQA/bandit
        rev: '1.7.5'
        hooks:
          - id: bandit
            args: [-c, pyproject.toml]
```

## Comparison of Security Tools

| Tool | Pros | Cons | Best For |
|------|------|------|----------|
| **pip-audit** | ✅ PyPA maintained<br>✅ Fast & reliable<br>✅ Great CI integration | ❌ Python-only | Most Python projects |
| **safety** | ✅ Established tool<br>✅ Good documentation | ❌ Compatibility issues<br>❌ Less maintained | Legacy projects |
| **bandit** | ✅ Static code analysis<br>✅ Finds code issues | ❌ No dependency scan<br>❌ False positives | Code quality |
| **semgrep** | ✅ Advanced analysis<br>✅ Custom rules | ❌ Complex setup<br>❌ Slower | Large codebases |

## Migration Steps

1. **Update dependencies** (already done):
   ```bash
   # Remove safety, add pip-audit
   pip uninstall safety
   pip install pip-audit
   ```

2. **Update CI configuration** (already done):
   - Replace `safety check --full-report` with `pip-audit --desc`

3. **Test locally**:
   ```bash
   bandit -r src/beaconled -c pyproject.toml
   pip-audit --desc
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "fix: replace safety with pip-audit for security scanning"
   git push
   ```

## Troubleshooting

### Common Issues

1. **pip-audit not found**:
   ```bash
   pip install pip-audit
   # or
   pip install -e .[dev]
   ```

2. **No vulnerabilities found**:
   This is good! pip-audit will exit with code 0 when no vulnerabilities are found.

3. **bandit configuration issues**:
   Make sure your `pyproject.toml` has proper bandit configuration:
   ```toml
   [tool.bandit]
   exclude_dirs = ["tests", "scripts"]
   skips = ["B101"]  # Skip assert_used test
   ```

### Verification Commands

```bash
# Check if pip-audit is working
pip-audit --version

# Basic vulnerability scan
pip-audit

# Check bandit configuration
bandit --help

# Test bandit on source code
bandit -r src/beaconled -c pyproject.toml
```

## Conclusion

The recommended approach is to switch to `pip-audit` as it's more reliable, actively maintained, and integrates better with the Python ecosystem. The changes have been implemented in your project configuration and should resolve the CI pipeline issues.
