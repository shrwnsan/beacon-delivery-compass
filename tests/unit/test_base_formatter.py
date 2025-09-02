"""Tests for the BaseFormatter class."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from colorama import Fore

from beaconled.core.models import CommitStats, FileStats, RangeStats
from beaconled.formatters.base_formatter import BaseFormatter


class TestBaseFormatter(unittest.TestCase):
    """Test cases for BaseFormatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = BaseFormatter()

    def test_format_date(self):
        """Test _format_date method."""
        dt = datetime(2025, 7, 20, 10, 30, 45, tzinfo=timezone.utc)
        result = self.formatter._format_date(dt)
        self.assertEqual(result, "2025-07-20 10:30:45")

    def test_format_file_stats(self):
        """Test _format_file_stats method."""
        file_stat = FileStats(path="src/main.py", lines_added=10, lines_deleted=5, lines_changed=15)
        result = self.formatter._format_file_stats(file_stat)
        self.assertIn("src/main.py", result)
        self.assertIn("+10", result)
        self.assertIn("-5", result)

    def test_format_author_stats_singular(self):
        """Test _format_author_stats with singular commit."""
        result = self.formatter._format_author_stats("Alice", 1)
        self.assertEqual(result, "  Alice: 1 commit")

    def test_format_author_stats_plural(self):
        """Test _format_author_stats with plural commits."""
        result = self.formatter._format_author_stats("Alice", 3)
        self.assertEqual(result, "  Alice: 3 commits")

    def test_format_net_change_positive(self):
        """Test _format_net_change with positive net change."""
        result = self.formatter._format_net_change(15, 5)
        self.assertIn("10", result)  # Should contain the number
        self.assertIn(Fore.GREEN, result)  # Should have green color for positive

    def test_format_net_change_negative(self):
        """Test _format_net_change with negative net change."""
        result = self.formatter._format_net_change(5, 15)
        self.assertIn("10", result)  # Should contain the absolute number
        self.assertIn(Fore.RED, result)  # Should have red color for negative

    def test_format_net_change_zero(self):
        """Test _format_net_change with zero net change."""
        result = self.formatter._format_net_change(10, 10)
        self.assertIn("0", result)  # Should contain zero
        self.assertIn(Fore.GREEN, result)  # Zero is considered positive (green)

    def test_get_file_type_breakdown(self):
        """Test _get_file_type_breakdown method."""
        files = [
            FileStats("src/main.py", 10, 5),
            FileStats("src/utils.py", 20, 10),
            FileStats("README.md", 5, 2),
            FileStats("Makefile", 0, 0),  # No extension
        ]

        result = self.formatter._get_file_type_breakdown(files)

        # Check Python files
        self.assertIn("py", result)
        self.assertEqual(result["py"]["count"], 2)
        self.assertEqual(result["py"]["added"], 30)
        self.assertEqual(result["py"]["deleted"], 15)

        # Check Markdown files
        self.assertIn("md", result)
        self.assertEqual(result["md"]["count"], 1)
        self.assertEqual(result["md"]["added"], 5)
        self.assertEqual(result["md"]["deleted"], 2)

        # Check files without extension
        self.assertIn("no-ext", result)
        self.assertEqual(result["no-ext"]["count"], 1)
        self.assertEqual(result["no-ext"]["added"], 0)
        self.assertEqual(result["no-ext"]["deleted"], 0)

    def test_get_file_type_breakdown_empty_list(self):
        """Test _get_file_type_breakdown with empty file list."""
        result = self.formatter._get_file_type_breakdown([])
        self.assertEqual(result, {})

    def test_get_file_type_breakdown_single_file_no_extension(self):
        """Test _get_file_type_breakdown with file that has no extension."""
        files = [FileStats("Dockerfile", 10, 5)]
        result = self.formatter._get_file_type_breakdown(files)

        self.assertIn("no-ext", result)
        self.assertEqual(result["no-ext"]["count"], 1)
        self.assertEqual(result["no-ext"]["added"], 10)
        self.assertEqual(result["no-ext"]["deleted"], 5)

    def test_format_commit_stats_not_implemented(self):
        """Test format_commit_stats raises NotImplementedError."""
        stats = CommitStats(
            hash="abc123",
            author="Test",
            date=datetime.now(timezone.utc),
            message="Test",
        )
        with self.assertRaises(NotImplementedError):
            self.formatter.format_commit_stats(stats)

    def test_format_range_stats_not_implemented(self):
        """Test format_range_stats raises NotImplementedError."""
        stats = RangeStats(
            start_date=datetime.now(timezone.utc), end_date=datetime.now(timezone.utc)
        )
        with self.assertRaises(NotImplementedError):
            self.formatter.format_range_stats(stats)

    @patch("beaconled.formatters.base_formatter.colorama.init")
    def test_colorama_initialization(self, mock_colorama_init):
        """Test that colorama is initialized when BaseFormatter is imported."""
        # Re-import to trigger initialization
        import importlib

        import beaconled.formatters.base_formatter

        importlib.reload(beaconled.formatters.base_formatter)

        # Verify colorama.init was called
        mock_colorama_init.assert_called_once()
