#!/usr/bin/env python3
"""Script to fix datetime timezone issues in test files."""

import re
from pathlib import Path


def fix_datetime_issues(file_path: Path) -> bool:
    """Fix datetime timezone issues in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # First, handle imports
    if "from datetime import datetime" in content and "timezone" not in content:
        content = content.replace(
            "from datetime import datetime", "from datetime import datetime, timezone"
        )

    # Handle datetime() calls
    def fix_datetime(match):
        args = match.group(1)
        # Skip if already has tzinfo
        if "tzinfo=" in args:
            return match.group(0)
        # Add timezone.utc to the datetime call
        if args.strip():
            return f"datetime({args}, tzinfo=timezone.utc)"
        return "datetime(tzinfo=timezone.utc)"

    # Pattern for datetime() calls
    pattern = r"datetime\(([^)]*)\)"
    new_content = re.sub(pattern, fix_datetime, content)

    # Handle strptime() calls that need timezone
    def fix_strptime(match):
        line = match.group(0)
        # Skip if already has timezone handling
        if ".replace(" in line or ".astimezone(" in line:
            return line
        # Add .replace(tzinfo=timezone.utc) after strptime call
        return f"{line}.replace(tzinfo=timezone.utc)"

    # Look for strptime calls without timezone handling
    strptime_pattern = r"^(\s*\w+\s*=\s*datetime\.strptime\([^)]+\))(?!\s*\.(replace|astimezone)\([^)]*tzinfo[^)]*\))"
    new_content = re.sub(strptime_pattern, fix_strptime, new_content, flags=re.MULTILINE)

    # Add timezone import if not present
    if "from datetime import timezone" not in new_content and "import datetime" not in new_content:
        new_content = new_content.replace(
            "from datetime import datetime", "from datetime import datetime, timezone"
        )

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    """Main function to fix datetime issues in test files."""
    test_dirs = [
        Path(__file__).parent.parent / "tests" / "unit",
        Path(__file__).parent.parent / "tests" / "integration",
    ]
    fixed_files = 0

    for test_dir in test_dirs:
        for test_file in test_dir.glob("test_*.py"):
            if fix_datetime_issues(test_file):
                print(f"Fixed datetime issues in {test_file}")
                fixed_files += 1

    print(f"Fixed datetime issues in {fixed_files} files")


if __name__ == "__main__":
    main()
