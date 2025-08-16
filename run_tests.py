#!/usr/bin/env python3
"""
Consolidated test runner for the beacon-delivery-compass project.

This script combines the functionality of multiple test runners into a single,
comprehensive test runner with the following features:
- Environment verification
- Test discovery
- Support for running specific test modules or all tests
- Verbose output
- Clean error handling
"""

import argparse
import os
import sys
import unittest
from typing import List

import pytest

# Default test directory
TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests"))


def print_environment_info():
    """Print information about the current environment."""
    print("\n" + "=" * 80)
    print("TEST ENVIRONMENT INFORMATION")
    print("=" * 80)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print("=" * 80 + "\n")


class SimpleTest(unittest.TestCase):
    """Simple test case to verify the test environment."""

    def test_environment(self):
        """Verify the test environment is set up correctly."""
        self.assertTrue(True, "Test environment is working")


def run_simple_test():
    """Run a simple test to verify the test environment."""
    print("Running simple environment test...")
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.TestLoader().loadTestsFromTestCase(SimpleTest)
    )
    return 0 if result.wasSuccessful() else 1


def run_pytest(test_paths: List[str], verbose: bool = True):
    """Run tests using pytest.

    Args:
        test_paths: List of test paths to run
        verbose: Whether to show verbose output
    """
    print(f"\nRunning tests with pytest: {', '.join(test_paths) or 'all tests'}")

    # Build pytest arguments
    args = []
    if verbose:
        args.append("-v")
    args.extend(test_paths)

    # Run pytest
    return pytest.main(args)


def count_test_cases(test_file: str, show_progress: bool = True) -> int:
    """Count the number of test cases in a test file."""
    if show_progress:
        print(f"\rAnalyzing {os.path.basename(test_file)}...", end="", flush=True)

    try:
        # Try to use pytest to collect tests without running them
        args = [test_file, "--collect-only", "-q"]
        # Suppress output during test collection
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                result = pytest.main(args)
            finally:
                sys.stdout = old_stdout

        if result != 0:
            return 0

        # Count test cases in the file
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                collector = pytest.main([test_file, "--collect-only"])
            finally:
                sys.stdout = old_stdout

        if collector == 0:
            # Fall back to simple line counting if collection fails
            with open(test_file, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip().startswith("def test_"))
        return 0
    except Exception:
        return 0
    finally:
        if show_progress:
            print("\r" + " " * 50 + "\r", end="", flush=True)


def discover_tests() -> dict:
    """Discover all test files in the test directories and count test cases."""
    test_data = {}
    print("\nDiscovering test files...")

    # First, find all test files
    for root, _, files in os.walk(TEST_DIR):
        category = os.path.basename(root)
        if category in ["unit", "integration", "performance"]:
            test_files = [f for f in files if f.startswith("test_") and f.endswith(".py")]
            if test_files:
                test_data[category] = {
                    "files": [os.path.join(root, f) for f in test_files],
                    "test_cases": 0,
                }

    # Then count test cases with progress indicator
    total_files = sum(len(data["files"]) for data in test_data.values())
    if total_files > 0:
        print(f"Analyzing {total_files} test files...")
        for category, data in test_data.items():
            for test_file in data["files"]:
                test_count = count_test_cases(test_file, show_progress=True)
                test_data[category]["test_cases"] += test_count
        print("\r" + " " * 50 + "\r", end="")  # Clear progress line

    return test_data


def print_test_menu():
    """Print interactive test menu."""
    print("\n" + "=" * 50)
    print("BEACON-DELIVERY-COMPASS TEST RUNNER".center(50))
    print("=" * 50)
    print("\nTest Runner Menu:")
    print("1. Run simple environment test")
    print("2. Run all tests")
    print("3. Run specific test category")
    print("4. Show environment info")
    print("0. Exit")
    print("\n" + "-" * 50)


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run tests for beacon-delivery-compass")
    parser.add_argument(
        "test_paths",
        nargs="*",
        default=None,
        help="Test files or directories to run (default: interactive mode)",
    )
    parser.add_argument("--simple", action="store_true", help="Run only a simple environment test")
    parser.add_argument(
        "--no-verbose",
        action="store_false",
        dest="verbose",
        help="Disable verbose output",
    )
    parser.add_argument("--env", action="store_true", help="Show environment information and exit")

    args = parser.parse_args()

    if args.env:
        print_environment_info()
        return 0

    if args.simple:
        return run_simple_test()

    # Interactive mode if no paths provided
    if not args.test_paths:
        while True:
            print_test_menu()
            try:
                choice = input("\nEnter your choice: ")
                if choice == "0":
                    return 0
                elif choice == "1":
                    return run_simple_test()
                elif choice == "2":
                    return run_pytest([TEST_DIR], True)
                elif choice == "3":
                    tests = discover_tests()
                    print("\nAvailable test categories:")
                    for i, cat in enumerate(sorted(tests.keys()), 1):
                        file_count = len(tests[cat]["files"])
                        test_count = tests[cat]["test_cases"]
                        print(
                            f"{i}. {cat.capitalize()} ({file_count} files, {test_count} test cases)"
                        )

                    cat_choice = input("\nSelect category (0 to cancel): ")
                    if cat_choice.isdigit() and 0 < int(cat_choice) <= len(tests):
                        category = sorted(tests.keys())[int(cat_choice) - 1]
                        return run_pytest(tests[category]["files"], True)
                elif choice == "4":
                    print_environment_info()
            except (ValueError, IndexError):
                print("Invalid choice. Please try again.")
    else:
        # Non-interactive mode with provided paths
        if args.verbose:
            print_environment_info()
        return run_pytest(args.test_paths, args.verbose)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running tests: {e}", file=sys.stderr)
        sys.exit(1)
