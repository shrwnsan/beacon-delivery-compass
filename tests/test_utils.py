"""Test utilities for the Beacon Delivery Compass test suite."""

import os
import subprocess
import sys


def get_beaconled_cmd() -> list[str]:
    """
    Get the appropriate beaconled command for testing.

    Returns:
        List of command parts to execute beaconled.
    """
    # Use the Python module approach to ensure it works in development
    # This avoids dependency on beaconled being installed as a command
    return [sys.executable, "-m", "beaconled.cli"]


def run_beaconled(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Run beaconled with the given arguments.

    Args:
        args: List of command line arguments to pass to beaconled
        **kwargs: Additional arguments to pass to subprocess.run()

    Returns:
        CompletedProcess object with the result of the command execution.
    """
    cmd = get_beaconled_cmd() + args
    return subprocess.run(cmd, check=False, **kwargs)
