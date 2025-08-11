"""Beacon Delivery Compass - Analyze git repository statistics."""

from .exceptions import (
    BeaconError,
    ConfigurationError,
    ValidationError,
    RepositoryError,
    InvalidRepositoryError,
)

from .core.date_errors import (
    DateParseError,
    DateRangeError,
)
from .core.analyzer import GitAnalyzer
from .core.models import CommitStats, RangeStats

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Core classes
    "GitAnalyzer",
    "CommitStats",
    "RangeStats",
    # Exceptions
    "BeaconError",
    "ConfigurationError",
    "ValidationError",
    "DateParseError",
    "RepositoryError",
    "InvalidRepositoryError",
    "CommitError",
    "DateRangeError",
]
