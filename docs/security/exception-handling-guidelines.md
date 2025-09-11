# Security Guidelines: Exception Handling

This document provides guidelines for secure exception handling practices in the BeaconLED project.

## 🛡️ General Principles

### ✅ **Acceptable `try/except/pass` Patterns**

1. **Optional Visualization Features**
   ```python
   try:
       # Optional chart/graph generation
       generate_optional_visualization()
   except (ValueError, ImportError):
       # Graceful degradation is acceptable for optional features
       pass  # nosec B110
   ```

2. **Graceful Degradation in Non-Critical Paths**
   ```python
   try:
       # Enhancement feature that shouldn't break core functionality
       add_trend_line()
   except (ValueError, ZeroDivisionError, TypeError):
       # Application continues without the enhancement
       pass  # nosec B110
   ```

### ❌ **Unacceptable `try/except/pass` Patterns**

1. **Core Business Logic**
   ```python
   # NEVER DO THIS
   try:
       critical_data_processing()
   except Exception:
       pass  # This hides real problems!
   ```

2. **Security-Related Operations**
   ```python
   # NEVER DO THIS
   try:
       validate_user_permissions()
   except Exception:
       pass  # Security vulnerabilities!
   ```

3. **Data Integrity Operations**
   ```python
   # NEVER DO THIS
   try:
       save_important_data()
   except Exception:
       pass  # Data loss risk!
   ```

## 🔧 **Implementation Guidelines**

### **1. Specific Exception Types**
Always catch specific exceptions rather than bare `Exception`:
```python
# Good
except (ValueError, ZeroDivisionError, TypeError):
    pass  # nosec B110

# Bad
except Exception:
    pass
```

### **2. Use `# nosec B110` Comments**
When silent failure is intentional, document it:
```python
except (ValueError, TypeError):
    # Graceful degradation for optional feature
    pass  # nosec B110
```

### **3. Add Explanatory Comments**
Always explain why silent failure is acceptable:
```python
try:
    generate_trend_line()
except (ValueError, ZeroDivisionError):
    # Trend lines are optional visualization enhancements
    # Core functionality continues without them
    pass  # nosec B110
```

## ⚙️ **Bandit Configuration**

Our current Bandit configuration in `pyproject.toml`:

```toml
[tool.bandit]
skips = ["B110"]  # Allow try/except/pass in specific contexts
exclude_dirs = ["tests"]

# Allow B110 in visualization code where graceful degradation is intentional
[tool.bandit.assert_used]
skips = ["**/formatters/chart.py", "**/formatters/ascii_chart.py", "**/formatters/heatmap.py"]
```

### **File-Specific Exceptions**
- **Chart/Visualization Code**: Silent failures are acceptable for optional visual enhancements
- **Test Files**: Excluded from B110 checks as test isolation patterns may require it
- **Core Logic**: No exceptions - all failures must be handled explicitly

## 📋 **Review Checklist**

When adding `try/except/pass` blocks, verify:

- [ ] Is this for an optional/enhancement feature?
- [ ] Would failure here break core functionality? (If yes, don't use pass)
- [ ] Are you catching specific exception types?
- [ ] Is there a comment explaining why silent failure is acceptable?
- [ ] Is the `# nosec B110` comment present?
- [ ] Could this hide security issues? (If yes, don't use pass)

## 🚀 **Future Considerations**

### **Logging Option**
For debugging purposes, consider optional logging:
```python
import logging
logger = logging.getLogger(__name__)

try:
    generate_optional_feature()
except (ValueError, TypeError) as e:
    # Optional: log for debugging, but don't fail
    logger.debug("Optional feature failed: %s", e)
    pass  # nosec B110
```

### **Configuration-Based Behavior**
For development vs. production differences:
```python
import os

try:
    risky_optional_feature()
except Exception as e:
    if os.getenv("ENV") == "development":
        logger.warning("Optional feature failed: %s", e)
    pass  # nosec B110
```

## 📚 **References**

- [Bandit B110 Documentation](https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html)
- [CWE-703: Improper Check or Handling of Exceptional Conditions](https://cwe.mitre.org/data/definitions/703.html)
- [Python Exception Handling Best Practices](https://realpython.com/python-exceptions-handling/)
