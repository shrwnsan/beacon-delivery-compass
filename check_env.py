#!/usr/bin/env python3
"""Diagnostic script to check Python environment and imports."""

import sys
import os

def check_import(module_name):
    """Check if a module can be imported and report its version if available."""
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'no version info')
        print(f"✓ {module_name} imported successfully (version: {version})")
        return True
    except ImportError as e:
        print(f"✗ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error importing {module_name}: {e}")
        return False

def main():
    """Run environment checks."""
    print("\n=== Python Environment Check ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print("\n=== Python Path ===")
    for path in sys.path:
        print(f"  {path}")
    
    print("\n=== Checking Dependencies ===")
    dependencies = [
        'unittest',
        'pytest',
        'git',
        'beaconled'
    ]
    
    all_imports_ok = all(check_import(dep) for dep in dependencies)
    
    print("\n=== Test Environment Status ===")
    if all_imports_ok:
        print("✓ All required dependencies are importable")
    else:
        print("✗ Some dependencies could not be imported")
    
    # Try to import the test module directly
    print("\n=== Test Module Check ===")
    try:
        import tests.unit.test_analyzer
        print("✓ Successfully imported test_analyzer")
    except Exception as e:
        print(f"✗ Failed to import test_analyzer: {e}")
        print("\nError details:")
        import traceback
        traceback.print_exc()
    
    return 0 if all_imports_ok else 1

if __name__ == "__main__":
    sys.exit(main())
