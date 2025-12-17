# Security Documentation for Beacon

## Overview

This document describes the security measures implemented in Beacon to prevent information disclosure through error messages and file paths. The security sanitization utilities are designed to protect sensitive information while maintaining useful debugging capabilities.

## Purpose

The security module (`src/beaconled/utils/security.py`) provides utilities for:

1. **Path Sanitization** - Removes sensitive directory structures from file paths
2. **Error Message Sanitization** - Removes sensitive information from error messages
3. **Safe Object Representation** - Provides safe string representations for debugging

## Security Assumptions

### What We Protect Against

- **Information Disclosure**: Preventing exposure of user directories, usernames, and sensitive paths in error messages
- **Path-based Attacks**: Sanitizing file paths that could reveal system structure
- **Case-sensitive Bypasses**: Using case-insensitive patterns to prevent bypass attempts

### What We Trust

- **Local Filesystem**: We assume the local filesystem is not malicious
- **Process Integrity**: We assume the process itself is not compromised
- **User Intent**: We assume users have legitimate access to the repositories they analyze

## Implementation Details

### Path Sanitization (`sanitize_path`)

```python
# Returns only the last N components of a path
sanitize_path("/home/user/projects/myapp/config/settings.py")
# Returns: "config/settings.py"
```

**Features:**
- Cross-platform support (Unix, macOS, Windows)
- Proper handling of Windows drive letters
- Configurable maximum components (default: 2)
- Safe fallback on errors

### Error Message Sanitization (`sanitize_error_message`)

**Protected Patterns:**
- `/home/[username]` → `/home/****`
- `/Users/[username]` → `/Users/****`
- `/root/` → `/root/****`
- `/opt/[directory]` → `/opt/****`
- `/srv/[directory]` → `/srv/****`
- `/var/home/[username]` → `/var/home/****`
- `C:\Users\[username]` → `C:/Users/****`
- `~[username]` → `~****`

**Features:**
- Case-insensitive matching to prevent bypass
- Length limiting (default: 200 characters)
- Handles multiple sensitive paths in one message

## Limitations

### Known Limitations

1. **URL-encoded Paths**: Percent-encoded paths (e.g., `/home/%75%73%65%72`) are not decoded before sanitization
2. **Windows UNC Paths**: Limited support for complex UNC path patterns
3. **Symbolic Links**: Does not follow symlinks to check if they point to sensitive locations
4. **Non-ASCII Characters**: While handled safely, patterns may not match all Unicode character variations

### Out of Scope

The following are intentionally out of scope:

- **Malicious Insider Protection**: We do not protect against users with legitimate system access
- **Memory Dumps**: Protection against memory dump attacks is not implemented
- **Network Traffic**: Encryption of network communications is handled elsewhere
- **Authentication**: User authentication and authorization are separate concerns

## Usage Examples

### Basic Usage

```python
from beaconled.utils.security import sanitize_path, sanitize_error_message

# Sanitize a file path
safe_path = sanitize_path("/home/alice/sensitive/project/file.txt")
# Returns: "project/file.txt"

# Sanitize an error message
safe_message = sanitize_error_message(
    "Failed to read /home/bob/config/secrets.conf"
)
# Returns: "Failed to read /home/****/config/secrets.conf"
```

### Exception Handling

```python
from beaconled.exceptions import InvalidRepositoryError
from pathlib import Path

# Exceptions automatically use sanitization
try:
    # ... some operation that fails
    pass
except Exception as e:
    # Create an exception with sanitized message
    error = InvalidRepositoryError(
        repo_path=Path("/home/user/secret/repo"),
        message="Not a git repository"
    )
    # The public message is sanitized, but full path is available for logging
    print(str(error))  # Safe, sanitized message
    print(error.details["repo_path"])  # Full path for logging
```

## Defense in Depth

The security implementation follows a defense-in-depth approach:

1. **Input Sanitization**: All user-provided paths are sanitized before display
2. **Length Limiting**: Error messages are truncated to prevent information leakage
3. **Safe Defaults**: Functions use secure defaults (e.g., 2 path components)
4. **Error Handling**: Sanitization failures result in safe fallbacks, not crashes
5. **Comprehensive Testing**: 33 tests covering edge cases and bypass attempts

## Threat Model

### Primary Threats

1. **Information Disclosure via Error Messages**
   - Attacker gains knowledge of system structure
   - Usernames and home directory paths are exposed
   - Sensitive project names are revealed

2. **Path Enumeration**
   - Attacker learns about directory structure
   - Pattern of user activity is exposed

### Mitigation Strategies

- Replace sensitive path components with generic placeholders
- Limit the depth of exposed path information
- Use case-insensitive patterns to prevent bypasses
- Implement multiple layers of sanitization

## Testing

The security module includes comprehensive tests covering:

- ✅ Case-insensitive path variations
- ✅ Unicode and non-ASCII characters
- ✅ Deeply nested paths
- ✅ Windows path edge cases
- ✅ Multiple sensitive paths in one message
- ✅ Empty and boundary conditions
- ✅ Cross-platform compatibility

Run tests with:
```bash
pytest tests/test_security_sanitization.py -v
```

## Security Considerations for Developers

When working with security-sensitive code:

1. **Always Sanitize**: Never display raw file paths in user-facing messages
2. **Use Safe Functions**: Prefer `sanitize_path()` and `sanitize_error_message()`
3. **Log Full Details**: Use `log_sensitive_error()` to log full details at debug level
4. **Consider Platform**: Account for differences between Unix, macOS, and Windows
5. **Test Edge Cases**: Include non-ASCII characters and edge cases in tests

## Future Improvements

Potential enhancements to consider:

1. **Enhanced UNC Path Support**: Better handling of Windows UNC path patterns
2. **Configurable Patterns**: Allow users to define additional sensitive patterns
3. **Unicode Normalization**: Handle Unicode equivalence classes for better matching
4. **Performance Optimization**: Cache compiled regex patterns for better performance

## Reporting Security Issues

If you discover a security vulnerability:

1. Do not open a public issue
2. Send details to the project maintainers privately
3. Include steps to reproduce the vulnerability
4. Allow time for the issue to be addressed before disclosure

## References

- [OWASP Information Exposure](https://owasp.org/www-project-top-ten/2017/A4_2017-XML_External_Entities_(XXE))
- [CWE-200: Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html)

---

*Last updated: 2025-12-17*
