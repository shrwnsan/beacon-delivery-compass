#!/usr/bin/env python3
"""Security validation script for CI/CD pipeline.

This script performs security hardening validation including:
- Hard link detection for shared CI environments
- Path validation with TOCTOU protection
- File integrity verification
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beaconled.utils.security import is_hard_link, secure_path_exists, sanitize_path


def main() -> None:
    """Run security hardening validation."""
    print("Running security hardening validation...")

    # Check for hard links in critical directories
    critical_dirs = [Path("."), Path("src"), Path("tests")]
    issues_found = 0

    for directory in critical_dirs:
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            issues_found += 1
            continue

        if not secure_path_exists(directory):
            print(f"❌ Security validation failed for: {sanitize_path(directory)}")
            issues_found += 1
            continue

        print(f"✅ Directory secure: {sanitize_path(directory)}")

        # Check for hard links in directory contents
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    if is_hard_link(file_path):
                        print(f"⚠️  Hard link detected: {sanitize_path(file_path)}")
                        issues_found += 1
                except Exception as e:
                    print(f"❌ Error checking {sanitize_path(file_path)}: {e}")
                    issues_found += 1

    if issues_found > 0:
        print(f"❌ Security hardening validation failed with {issues_found} issues")
        sys.exit(1)
    else:
        print("✅ All security hardening checks passed")


if __name__ == "__main__":
    main()
