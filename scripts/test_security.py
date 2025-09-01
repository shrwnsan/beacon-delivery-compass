#!/usr/bin/env python3
"""
Test script to verify security scanning tools work properly.
This helps validate the security checks before pushing to CI.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print("=" * 60)

    try:
        subprocess.run(
            command,
            capture_output=False,  # Show output in real-time
            check=True,
            cwd=Path(__file__).parent.parent,
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        print("   Make sure you have installed the development dependencies:")
        print("   pip install -e .[dev]")
        return False


def main():
    """Run all security checks locally."""
    print("🔍 Running Local Security Checks")
    print("=" * 60)

    # Check if we're in the right directory
    project_root = Path(__file__).parent.parent
    if not (project_root / "pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Are you in the right directory?")
        sys.exit(1)

    all_passed = True

    # Test 1: pip-audit for vulnerability scanning
    all_passed &= run_command(["pip-audit", "--desc"], "Vulnerability scanning with pip-audit")

    # Test 2: bandit for security linting
    all_passed &= run_command(
        ["bandit", "-r", "src/beaconled", "-c", "pyproject.toml"], "Security linting with bandit"
    )

    # Test 3: Alternative - pip-audit with JSON output for detailed info
    print(f"\n{'=' * 60}")
    print("Optional: Detailed vulnerability report (JSON format)")
    print("=" * 60)
    run_command(
        ["pip-audit", "--format=json", "--output", "vulnerability-report.json"],
        "Generate detailed vulnerability report",
    )

    print(f"\n{'=' * 60}")
    if all_passed:
        print("🎉 All security checks passed!")
        print("Your code is ready for CI pipeline.")
    else:
        print("❌ Some security checks failed.")
        print("Please fix the issues before pushing to CI.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
