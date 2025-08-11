"""End-to-end integration tests."""

import json
import unittest
from tests.test_utils import run_beaconled


class TestEndToEnd(unittest.TestCase):
    """Integration tests for the complete beaconled workflow."""

    def test_beaconled_help(self):
        """Test that beaconled help command works."""
        result = run_beaconled(["--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Beacon", result.stdout)
        self.assertIn("delivery compass", result.stdout)

    def test_beaconled_current_commit(self):
        """Test analyzing current commit."""
        result = run_beaconled([], capture_output=True, text=True)
        if result.returncode != 0:
            print("\n=== stderr ===")
            print(result.stderr)
            print("=== stdout ===")
            print(result.stdout)
        self.assertEqual(result.returncode, 0, "Command failed with non-zero exit code")
        self.assertIn("Commit:", result.stdout)
        self.assertIn("Author:", result.stdout)
        self.assertIn("Files changed:", result.stdout)

    def test_beaconled_json_output(self):
        """Test JSON output format."""
        result = run_beaconled(["--format", "json"], capture_output=True, text=True)
        if result.returncode != 0:
            print("\n=== stderr ===")
            print(result.stderr)
            print("=== stdout ===")
            print(result.stdout)
        self.assertEqual(result.returncode, 0, "Command failed with non-zero exit code")
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.fail(f"Output is not valid JSON: {e}")

        try:
            data = json.loads(result.stdout)
            self.assertIn("hash", data)
            self.assertIn("author", data)
            self.assertIn("files_changed", data)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_beaconled_range_analysis(self):
        """Test range analysis functionality."""
        args = ["--range", "--since", "7d"]
        print(f"\nRunning command: beaconled {' '.join(args)}")
        result = run_beaconled(args, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print("=== STDOUT ===")
        print(result.stdout)
        print("=== STDERR ===")
        print(result.stderr)
        print("=============")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)
        self.assertIn("Total commits:", result.stdout)

    def test_beaconled_invalid_commit(self):
        """Test handling of invalid commit hash."""
        result = run_beaconled(["nonexistent123"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)

    def test_beaconled_extended_output(self):
        """Test extended output format."""
        result = run_beaconled(["--format", "extended"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Commit:", result.stdout)
        self.assertIn("Author:", result.stdout)
        self.assertIn("Date:", result.stdout)
        self.assertIn("Message:", result.stdout)
        self.assertIn("Files changed:", result.stdout)
        self.assertIn("Lines added:", result.stdout)
        self.assertIn("Lines deleted:", result.stdout)
        self.assertIn("File type breakdown:", result.stdout)

    def test_beaconled_range_analysis_extended(self):
        """Test range analysis with extended output."""
        result = run_beaconled(
            ["--range", "--since", "7d", "--format", "extended"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)
        self.assertIn("to", result.stdout)
        self.assertIn("Total commits:", result.stdout)
        self.assertIn("Total commits:", result.stdout)
        self.assertIn("Total files changed:", result.stdout)
        self.assertIn("Total lines added:", result.stdout)
        self.assertIn("Total lines deleted:", result.stdout)
        self.assertIn("Contributors:", result.stdout)
        self.assertIn("Temporal Analysis - Daily Activity Timeline:", result.stdout)


if __name__ == "__main__":
    unittest.main()
