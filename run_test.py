#!/usr/bin/env python3
"""Simple test runner for debugging test issues."""

import sys
import unittest
from tests.unit.test_date_utils import TestDateParser


def main():
    """Run the tests and print the results."""
    print("Python version:", sys.version)
    print("Python path:", sys.path)

    # Create a test suite
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromTestCase(TestDateParser)

    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Exit with appropriate status code
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
