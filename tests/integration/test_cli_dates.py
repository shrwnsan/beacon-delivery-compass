"""Integration tests for CLI date format handling."""
import json
import subprocess
import unittest
from datetime import datetime, timedelta


class TestCLIDateFormats(unittest.TestCase):
    """Test CLI handling of various date formats."""

    def setUp(self):
        """Set up test environment."""
        self.beacon_cmd = ["beaconled"]

    def run_cli(self, args, expect_success=True):
        """Run CLI command and return result."""
        cmd = self.beacon_cmd + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if expect_success and result.returncode != 0:
            print(f"\nCommand failed: {' '.join(cmd)}")
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
        for unit in ['d', 'w', 'm', 'y']:
            for value in [1, 2, 5]:
                with self.subTest(f"{value}{unit}"):
                    result = self.run_cli(["--range", "--since", f"{value}{unit}"])
                    self.assertEqual(result.returncode, 0)
                    self.assertIn("Range Analysis:", result.stdout)

    def test_absolute_date_formats(self):
        """Test various absolute date formats."""
        # Test different date formats
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test YYYY-MM-DD format
        result = self.run_cli(["--range", "--since", yesterday, "--until", today])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)
        
        # Test with time component
        result = self.run_cli([
            "--range", 
            "--since", f"{yesterday} 00:00", 
            "--until", f"{today} 23:59"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)

    def test_invalid_date_formats(self):
        """Test handling of invalid date formats."""
        # Test various invalid formats with their expected error patterns
        test_cases = [
            ("2023/01/01", "Could not parse date"),  # Wrong separator
            ("01-01-2023", "Could not parse date"),  # Wrong order
            ("2023-13-01", "Could not parse date"),  # Invalid month
            ("2023-01-32", "Could not parse date"),  # Invalid day
            ("1 d", "Could not parse date"),         # Space between number and unit
            ("1x", "Could not parse date"),          # Invalid unit
            ("0d", "Could not parse date"),          # Zero value
            ("1.5d", "Could not parse date"),        # Decimal value
            ("1D", "Could not parse date"),          # Uppercase unit
        ]
        
        for date_str, error_pattern in test_cases:
            with self.subTest(invalid_format=date_str):
                result = self.run_cli(["--range", "--since", date_str], expect_success=False)
                self.assertNotEqual(result.returncode, 0,
                                 f"Expected non-zero exit code for input: {date_str}")
                self.assertIn("Error:", result.stderr)
                self.assertIn(error_pattern, result.stderr,
                            f"Expected error message containing '{error_pattern}' for input: {date_str}\nGot: {result.stderr}")

    def test_edge_case_date_formats(self):
        """Test edge cases that should be handled appropriately."""
        # Test cases that might be edge cases but are handled gracefully
        edge_cases = [
            ("1d ", 0),      # Trailing space - should be valid
            (" 1d", 0),      # Leading space - should be valid
            ("-1d", 2),      # Negative value - CLI argument parsing issue
        ]
        
        for date_str, expected_code in edge_cases:
            with self.subTest(edge_case=date_str):
                result = self.run_cli(["--range", "--since", date_str], expect_success=(expected_code == 0))
                self.assertEqual(result.returncode, expected_code,
                               f"Expected exit code {expected_code} for input: {date_str}")
    
    def test_valid_relative_date_formats(self):
        """Test that valid relative date formats work as expected."""
        valid_formats = ["1d", "2w", "3m", "1y"]
        for fmt in valid_formats:
            with self.subTest(valid_format=fmt):
                result = self.run_cli(["--range", "--since", fmt])
                self.assertEqual(result.returncode, 0,
                              f"Expected success for valid date format: {fmt}")
                self.assertIn("Range Analysis:", result.stdout)

    def test_date_range_validation(self):
        """Test that end date must be after start date."""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test with end date before start date
        result = self.run_cli([
            "--range", 
            "--since", today, 
            "--until", yesterday
        ], expect_success=False)
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)
        self.assertIn("end date (", result.stderr)
        self.assertIn(") is before start date (", result.stderr)

    def test_combined_with_other_options(self):
        """Test date formats combined with other CLI options."""
        # Test with JSON output
        result = self.run_cli([
            "--range",
            "--since", "1w",
            "--format", "json"
        ])
        self.assertEqual(result.returncode, 0)
        try:
            data = json.loads(result.stdout)
            self.assertIn("total_commits", data)
            self.assertIn("start_date", data)
            self.assertIn("end_date", data)
        except json.JSONDecodeError as e:
            self.fail(f"Output is not valid JSON: {e}")
        
        # Test with extended format
        result = self.run_cli([
            "--range",
            "--since", "1w",
            "--format", "extended"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)
        self.assertIn("Total commits:", result.stdout)


if __name__ == '__main__':
    unittest.main()
