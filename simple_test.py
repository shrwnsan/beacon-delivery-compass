#!/usr/bin/env python3
"""Simple test to verify the test environment."""

import sys
import unittest

class SimpleTest(unittest.TestCase):
    """Simple test case to verify the test environment."""
    
    def test_simple(self):
        """A simple test that should always pass."""
        self.assertTrue(True, "This test should always pass")

if __name__ == "__main__":
    print("Running simple test...")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {__file__}")
    print("Python path:", sys.path)
    unittest.main()
