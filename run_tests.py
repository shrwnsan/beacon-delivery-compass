#!/usr/bin/env python3
"""Simple test runner to verify the test environment."""

import sys
import unittest

def run_tests():
    """Run the test suite and return the test result."""
    print("Starting test runner...")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    
    # Try to import the test module
    try:
        from tests.unit import test_analyzer
        print("Successfully imported test_analyzer module")
    except ImportError as e:
        print(f"Error importing test_analyzer: {e}")
        return 1
    
    # Run the tests
    print("Running tests...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_analyzer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
