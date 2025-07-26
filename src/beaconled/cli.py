#!/usr/bin/env python
"""Command-line interface for Beacon."""

import argparse
import sys

from .core.analyzer import GitAnalyzer
from .formatters.extended import ExtendedFormatter
from .formatters.json_format import JSONFormatter
from .formatters.standard import StandardFormatter


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Beacon - Your delivery compass for empowered product builders"
        )
    )
    parser.add_argument(
        "--version",
        action="version",
        version="beaconled 0.2.0",
        help="Show program's version number and exit"
    )
    parser.add_argument(
        "commit",
        nargs="?",
        default="HEAD",
        help="Commit hash to analyze (default: HEAD)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["standard", "extended", "json"],
        default="standard",
        help="Output format (default: standard)",
    )
    parser.add_argument(
        "-r", "--range", action="store_true", help="Analyze range of commits"
    )
    parser.add_argument(
        "--since",
        default="7d",
        help=("Start date for range analysis. "
              "Formats: 1d (1 day), 2w (2 weeks), 3m (3 months), 1y (1 year) "
              "or YYYY-MM-DD[ HH:MM] (default: 7d)"),
    )
    parser.add_argument(
        "--until",
        default="now",
        help=("End date for range analysis. "
              "Same formats as --since, or 'now' (default: now)"),
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory)",
    )

    args = parser.parse_args()

    try:
        analyzer = GitAnalyzer(args.repo)
        output: str

        if args.range:
            # For range analysis, we need to parse the date strings
            range_stats = analyzer.get_range_analytics(args.since, args.until)
            if args.format == "json":
                json_formatter = JSONFormatter()
                output = json_formatter.format_range_stats(range_stats)
            elif args.format == "extended":
                extended_formatter = ExtendedFormatter()
                output = extended_formatter.format_range_stats(range_stats)
            else:  # standard
                standard_formatter = StandardFormatter()
                output = standard_formatter.format_range_stats(range_stats)
        else:
            # For single commit analysis
            commit_stats = analyzer.get_commit_stats(args.commit)

            if args.format == "json":
                json_formatter = JSONFormatter()
                output = json_formatter.format_commit_stats(commit_stats)
            elif args.format == "extended":
                extended_formatter = ExtendedFormatter()
                output = extended_formatter.format_commit_stats(commit_stats)
            else:  # standard
                standard_formatter = StandardFormatter()
                output = standard_formatter.format_commit_stats(commit_stats)

        # Handle output with proper encoding
        try:
            print(output)
        except UnicodeEncodeError:
            # Fallback for systems with limited encoding support
            # Replace problematic characters with ASCII alternatives
            safe_output = output.encode('ascii', 'replace').decode('ascii')
            print(safe_output)

    except Exception as e:
        # Ensure error messages are also handled properly
        try:
            print(f"Error: {e}", file=sys.stderr)
        except UnicodeEncodeError:
            safe_error = str(e).encode('ascii', 'replace').decode('ascii')
            print(f"Error: {safe_error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
