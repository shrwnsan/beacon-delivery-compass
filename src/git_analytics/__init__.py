"""Git Analytics Toolkit - A comprehensive toolkit for git repository analysis."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.analyzer import GitAnalyzer
from .core.models import CommitStats, RangeStats

__all__ = ["GitAnalyzer", "CommitStats", "RangeStats"]
