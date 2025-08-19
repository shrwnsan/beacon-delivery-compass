"""Integration tests for CLI date format handling."""

import json
import unittest
from datetime import datetime, timedelta, timezone

from tests.test_utils import run_beaconled


class TestCLIDateFormats(unittest.TestCase):
    """Test CLI handling of various date formats."""

    def run_cli(self, args, *, expect_success: bool = True):
        """Run CLI command and return result."""
        result = run_beaconled(args, capture_output=True, text=True)
        if expect_success and result.returncode != 0:
            # Print the arguments we attempted to run for easier debugging
            print(f"\nCommand failed: {' '.join(str(a) for a in args)}")
            print(f"Return code: {result.returncode}")
            print("=== STDOUT ===")
            print(result.stdout)
            print("=== STDERR ===")
            print(result.stderr)
        return result

    def test_relative_date_formats(self):
        """Test various relative date formats.

        Test different relative date units.
        """
        # Test different relative date units
        for unit in ["d", "w", "m", "y"]:
            for value in [1, 2, 5]:
                with self.subTest(f"{value}{unit}"):
                    result = self.run_cli(["--since", f"{value}{unit}"])
                    self.assertEqual(result.returncode, 0)
                    self.assertIn("Range Analysis:", result.stdout)

    def test_absolute_date_formats(self):
        """Test various absolute date formats."""
        # Test different date formats with timezone-aware datetimes
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        # Test YYYY-MM-DD format
        result = self.run_cli(["--since", yesterday, "--until", today])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)

        # Test with time component
        result = self.run_cli(
            ["--since", f"{yesterday} 00:00", "--until", f"{today} 23:59"],
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)

    def test_invalid_date_formats(self):
        """Test handling of invalid date formats."""
        # Test various invalid formats with their expected error patterns
        test_cases = [
            ("2023/01/01", ["Could not parse date", "Unsupported date format"]),  # Wrong separator
            ("01-01-2023", ["Could not parse date", "Unsupported date format"]),  # Wrong order
            ("2023-13-01", ["Could not parse date", "Unsupported date format"]),  # Invalid month
            ("2023-01-32", ["Could not parse date", "Unsupported date format"]),  # Invalid day
            (
                "1 d",
                ["Could not parse date", "Unsupported date format"],
            ),  # Space between number and unit
            ("1x", ["Could not parse date", "Unsupported date format"]),  # Invalid unit
            ("0d", ["Could not parse date", "Unsupported date format"]),  # Zero value
            ("1.5d", ["Could not parse date", "Unsupported date format"]),  # Decimal value
        ]

        for date_str, error_patterns in test_cases:
            with self.subTest(invalid_format=date_str):
                result = self.run_cli(
                    ["--since", date_str],
                    expect_success=False,
                )
                self.assertNotEqual(
                    result.returncode,
                    0,
                    f"Expected non-zero exit code for input: {date_str}",
                )
                self.assertIn("Error:", result.stderr)

                # Check if any of the expected error patterns match
                if not any(pattern in result.stderr for pattern in error_patterns):
                    self.fail(
                        f"Expected error message containing one of {error_patterns} for input: {date_str}\n"
                        f"Got: {result.stderr}",
                    )

    def test_edge_case_date_formats(self):
        """Test edge cases that should be handled appropriately."""
        # Test cases that might be edge cases but are handled gracefully
        edge_cases = [
            ("1d ", 0),  # Trailing space - should be valid
            (" 1d", 0),  # Leading space - should be valid
            ("-1d", 2),  # Negative value - CLI argument parsing issue
        ]

        for date_str, expected_code in edge_cases:
            with self.subTest(edge_case=date_str):
                result = self.run_cli(
                    ["--since", date_str],
                    expect_success=(expected_code == 0),
                )
                self.assertEqual(
                    result.returncode,
                    expected_code,
                    f"Expected exit code {expected_code} for input: {date_str}",
                )

    def test_valid_relative_date_formats(self):
        """Test that valid relative date formats work as expected."""
        valid_formats = [
            "1d",
            "2w",
            "3m",
            "1y",
            "1D",
        ]  # Include uppercase D for case-insensitive test
        for fmt in valid_formats:
            with self.subTest(valid_format=fmt):
                result = self.run_cli(["--since", fmt])
                self.assertEqual(
                    result.returncode,
                    0,
                    f"Expected success for valid date format: {fmt}",
                )
                self.assertIn("Range Analysis:", result.stdout)

    def test_date_range_validation(self):
        """Test that end date must be after start date."""
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        # Test with end date before start date
        result = self.run_cli(
            ["--since", today, "--until", yesterday],
            expect_success=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)
        self.assertIn("is before start date", result.stderr)

    def test_combined_with_other_options(self):
        """Test date formats combined with other CLI options."""
        # Test with JSON output
        result = self.run_cli(["--since", "1w", "--format", "json"])
        self.assertEqual(result.returncode, 0)
        try:
            data = json.loads(result.stdout)
            self.assertIn("total_commits", data)
            self.assertIn("start_date", data)
            self.assertIn("end_date", data)
        except json.JSONDecodeError as e:
            self.fail(f"Output is not valid JSON: {e}")

        # Test with extended format
        result = self.run_cli(["--since", "1w", "--format", "extended"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)
        self.assertIn("Total commits:", result.stdout)


if __name__ == "__main__":
    unittest.main()
