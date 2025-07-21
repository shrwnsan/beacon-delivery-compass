"""End-to-end integration tests."""
import json
import subprocess
import unittest


class TestEndToEnd(unittest.TestCase):
    """Integration tests for the complete beaconled workflow."""

    def setUp(self):
        """Set up test environment."""
        self.beacon_cmd = ["python", "-m", "beaconled.cli"]

    def test_beaconled_help(self):
        """Test that beaconled help command works."""
        result = subprocess.run(
            self.beacon_cmd + ["--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Beacon", result.stdout)
        self.assertIn("delivery compass", result.stdout)

    def test_beaconled_current_commit(self):
        """Test analyzing current commit."""
        result = subprocess.run(
            self.beacon_cmd,
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Commit:", result.stdout)
        self.assertIn("Author:", result.stdout)
        self.assertIn("Files changed:", result.stdout)

    def test_beaconled_json_output(self):
        """Test JSON output format."""
        result = subprocess.run(
            self.beacon_cmd + ["--format", "json"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)

        # Verify it's valid JSON
        try:
            data = json.loads(result.stdout)
            self.assertIn("hash", data)
            self.assertIn("author", data)
            self.assertIn("files_changed", data)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_beaconled_range_analysis(self):
        """Test range analysis functionality."""
        result = subprocess.run(
            self.beacon_cmd + ["--range", "--since", "1 week ago"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Range Analysis:", result.stdout)
        self.assertIn("Total commits:", result.stdout)

    def test_beaconled_invalid_commit(self):
        """Test handling of invalid commit hash."""
        result = subprocess.run(
            self.beacon_cmd + ["nonexistent123"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)


if __name__ == '__main__':
    unittest.main()
