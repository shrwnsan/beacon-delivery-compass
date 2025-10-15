# Copyright 2025 Beacon, shrwnsan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Beacon Delivery Compass - Analyze git repository statistics."""

from .core.analyzer import GitAnalyzer
from .core.date_errors import DateParseError, DateRangeError
from .core.models import CommitStats, RangeStats
from .exceptions import (
    BeaconError,
    CommitError,
    ConfigurationError,
    InvalidRepositoryError,
    RepositoryError,
    ValidationError,
)

__version__ = "0.3.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "BeaconError",
    "CommitError",
    "CommitStats",
    "ConfigurationError",
    "DateParseError",
    "DateRangeError",
    "GitAnalyzer",
    "InvalidRepositoryError",
    "RangeStats",
    "RepositoryError",
    "ValidationError",
]
