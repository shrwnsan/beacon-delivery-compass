#!/usr/bin/env python
"""Command-line interface for Beacon."""

import argparse
import sys

from .core.analyzer import GitAnalyzer
from .formatters.extended import ExtendedFormatter
from .formatters.json_format import JSONFormatter
from .formatters.standard import StandardFormatter


def main() -> None:
    """Main CLI entry point for Beacon - Your delivery compass for empowered product builders.
    
    Beacon provides comprehensive git repository analysis with support for single commit
    and date range analysis with flexible date formatting options.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Beacon - Your delivery compass for empowered product builders\n\n"
            "Examples:\n"
            "  # Analyze the latest commit\n"
            "  beaconled\n\n"
            "  # Analyze a specific commit\n"
            "  beaconled abc1234\n\n"
            "  # Analyze changes in the last week\n"
            "  beaconled --range --since "1w"\n\n"
            "  # Analyze changes between specific dates\n"
            "  beaconled --range --since "2025-01-01" --until "2025-01-31"\n\n"
            "  # Output in JSON format\n"
            "  beaconled --format json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        help=("Start date for range analysis.\n"
              "Relative formats:\n"
              "  1d    - 1 day ago\n"
              "  2w    - 2 weeks ago\n"
              "  3m    - 3 months ago\n"
              "  1y    - 1 year ago\n"
              "\n"
              "Absolute formats:\n"
              "  YYYY-MM-DD          - Date only (midnight)\n"
              "  YYYY-MM-DD HH:MM    - Date and time\n"
              "\n"
              "Default: 7d (last 7 days)"),
    )
    parser.add_argument(
        "--until",
        default="now",
        help=("End date for range analysis. Uses same formats as --since.\n"
              "Special value 'now' means current time.\n"
              "Default: now"),
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
