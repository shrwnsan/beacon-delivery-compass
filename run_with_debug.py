#!/usr/bin/env python3
"""Script to run tests with detailed debug output."""

import sys
import os
import traceback
import importlib.util

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

def import_module(module_path):
    """Import a module from a file path."""
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        print(f"Could not import {module_path}: No module spec found")
        return None
    
    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        print(f"Successfully imported {module_path}")
        return module
    except Exception as e:
        print(f"Error importing {module_path}: {e}")
        traceback.print_exc()
        return None

def main():
    """Run the test with detailed debug output."""
    # Import the test module
    test_path = os.path.join(project_root, 'tests', 'unit', 'test_analyzer.py')
    test_module = import_module(test_path)
    
    if test_module is None:
        print("Failed to import test module")
        return 1
    
    # Try to run the test
    try:
        import unittest
        print("\nRunning tests...")
        test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        return 0 if result.wasSuccessful() else 1
    except Exception as e:
        print(f"Error running tests: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
