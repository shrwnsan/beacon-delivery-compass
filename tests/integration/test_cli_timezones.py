"""Integration tests for CLI timezone handling."""
import unittest
import subprocess
import os
import sys


class TestCLITimezoneHandling(unittest.TestCase):
    """Test CLI handling of timezone-aware inputs."""

    def setUp(self):
        """Set up test environment."""
        # Use sys.executable to get the Python interpreter path,
        # then construct the path to beaconled
        if sys.platform == "win32":
            self.beacon_cmd = [
                os.path.join(os.getcwd(), ".venv", "Scripts", "beaconled")
            ]
        else:
            self.beacon_cmd = [
                os.path.join(os.getcwd(), ".venv", "bin", "beaconled")
            ]

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = self.beacon_cmd + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return result

    def test_timezone_aware_input_rejection(self):
        """Test that timezone-aware inputs are properly rejected."""
        test_cases = [
            # Timezone-aware formats
            ("2025-01-01T00:00:00+08:00", "timezone-aware datetime"),
            ("2025-01-01 12:00:00-05:00", "timezone offset"),
            ("2025-01-01T12:00:00Z", "Zulu time indicator"),
            ("2025-01-01 12:00:00+00:00", "explicit UTC offset"),
        ]

        for date_str, desc in test_cases:
            with self.subTest(f"Reject timezone-aware input with {desc}"):
                result = self.run_cli(["--range", "--since", date_str])
                self.assertNotEqual(
                    result.returncode, 0,
                    f"Expected non-zero exit code for timezone-aware input: {date_str}"
                )
                self.assertIn(
                    "Error:", result.stderr,
                    f"Expected error message for timezone-aware input: {date_str}"
                )
                self.assertIn(
                    "UTC", result.stderr,
                    f"Error message should mention UTC requirement for input: {date_str}"
                )

    def test_naive_input_acceptance(self):
        """Test that naive (UTC) inputs are properly accepted."""
        test_cases = [
            ("2025-01-01", "date only"),
            ("2025-01-01 12:00:00", "datetime without timezone"),
            ("1d", "relative date"),
            ("now", "special value")
        ]

        for date_str, desc in test_cases:
            with self.subTest(f"Accept naive input with {desc}"):
                # We expect these to fail with a different error (no repo),
                # but not with a timezone error
                result = self.run_cli(["--range", "--since", date_str])
                self.assertNotIn(
                    "timezone", result.stderr.lower(),
                    f"Should not complain about timezone for valid input: {date_str}"
                )


if __name__ == '__main__':
    unittest.main()
