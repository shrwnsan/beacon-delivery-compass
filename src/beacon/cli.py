#!/usr/bin/env python
"""Command-line interface for Beacon."""

import argparse
import sys
from typing import Optional

from .core.analyzer import GitAnalyzer
from .formatters.standard import StandardFormatter
from .formatters.extended import ExtendedFormatter
from .formatters.json_format import JSONFormatter


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Beacon - Your delivery compass for empowered product builders"
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
        default="1 week ago",
        help="Start date for range analysis (default: 1 week ago)",
    )
    parser.add_argument(
        "--until", default="HEAD", help="End date for range analysis (default: HEAD)"
    )
    parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )

    args = parser.parse_args()

    try:
        analyzer = GitAnalyzer(args.repo)

        if args.range:
            stats = analyzer.get_range_analytics(args.since, args.until)
            formatter = (
                JSONFormatter() if args.format == "json" else StandardFormatter()
            )
            print(formatter.format_range_stats(stats))
        else:
            stats = analyzer.get_commit_stats(args.commit)

            if args.format == "standard":
                formatter = StandardFormatter()
            elif args.format == "extended":
                formatter = ExtendedFormatter()
            else:
                formatter = JSONFormatter()

            print(formatter.format_commit_stats(stats))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
