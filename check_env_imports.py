#!/usr/bin/env python3
"""Script to check Python environment and imports."""

import sys
import os
import importlib


def check_import(module_name):
    """Check if a module can be imported."""
    try:
        module = importlib.import_module(module_name)
        print(
            f"✓ Successfully imported {module_name} (version: {getattr(module, '__version__', 'no version info')})"
        )
        return True
    except ImportError as e:
        print(f"✗ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error importing {module_name}: {e}")
        return False


def main():
    """Main function to check the environment and imports."""
    print("\n=== Python Environment ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print("\n=== Python Path ===")
    for path in sys.path:
        print(f"  {path}")

    print("\n=== Checking Dependencies ===")
    dependencies = [
        "unittest",
        "pytest",
        "git",
        "beaconled",
        "beaconled.core.analyzer",
        "beaconled.core.models",
        "beaconled.core.date_errors",
        "beaconled.exceptions",
    ]

    all_imports_ok = all(check_import(dep) for dep in dependencies)

    print("\n=== Test Environment Status ===")
    if all_imports_ok:
        print("✓ All required dependencies are importable")
    else:
        print("✗ Some dependencies could not be imported")

    return 0 if all_imports_ok else 1


if __name__ == "__main__":
    sys.exit(main())
