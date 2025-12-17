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

"""Configuration constants for beacon-delivery-compass.

This module contains all configuration values used throughout the application,
centralized for better maintainability and easier tuning.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class RiskConfig:
    """Configuration for risk analysis thresholds and weights."""
    # Risk thresholds
    hotspot_threshold: int = 5
    stale_threshold_days: int = 90

    # Risk weights (should sum to 1.0)
    hotspot_weight: float = 0.4
    stale_code_weight: float = 0.3
    security_weight: float = 0.3

    # Risk score multipliers
    hotspot_multiplier: float = 2.0
    stale_multiplier: float = 20.0
    security_multiplier: float = 2.0

    # Security risk keywords
    security_keywords: Tuple[str, ...] = (
        "password",
        "secret",
        "key",
        "token",
        "credential",
        "auth",
        "private_key",
        "api_key",
        "pwd",
    )


@dataclass
class QualityConfig:
    """Configuration for code quality analysis."""
    # Quality thresholds
    churn_threshold: float = 10.0
    test_coverage_warning: float = 70.0
    complexity_warning: int = 10

    # Coverage calculation
    coverage_threshold: float = 80.0
    max_coverage: float = 95.0
    base_coverage: float = 50.0
    coverage_per_commit: float = 2.0


@dataclass
class ReadinessConfig:
    """Configuration for release readiness scoring."""
    # Initial score
    initial_score: int = 100

    # Commit thresholds
    large_commit_files_threshold: int = 15
    high_commit_volume_threshold: int = 50

    # Time thresholds
    last_minute_hours: int = 24
    last_minute_seconds: int = 86400  # 24 hours in seconds

    # Score penalties
    large_commit_penalty: int = 15
    recent_bug_fix_penalty: int = 10
    last_minute_change_penalty: int = 20

    # Maximum penalties
    max_large_commit_penalty: int = 40
    max_bug_fix_penalty: int = 30
    max_last_minute_penalty: int = 30


@dataclass
class PerformanceConfig:
    """Configuration for performance and caching."""
    # Cache settings
    max_cache_size: int = 100

    # Log length limits
    max_log_length: int = 100
    max_error_length: int = 200
    max_repr_length: int = 100


@dataclass
class DisplayConfig:
    """Configuration for display and formatting."""
    # Number of items to show
    top_n_authors: int = 10
    top_n_pairs: int = 10
    top_n_files: int = 10
    max_chart_points: int = 100

    # Activity windows
    last_n_days_rich: int = 7
    last_n_days_extended: int = 30
    last_n_months_heatmap: int = 12

    # Collaboration thresholds
    team_connectivity_threshold: float = 0.5
    collaboration_balance_threshold: float = 0.4


@dataclass
class DateConfig:
    """Configuration for date handling."""
    year_min: int = 1970
    year_max: int = 2100
    min_dates_for_analysis: int = 14  # Need at least 2 weeks


# Global configuration instances
risk_config = RiskConfig()
quality_config = QualityConfig()
readiness_config = ReadinessConfig()
performance_config = PerformanceConfig()
display_config = DisplayConfig()
date_config = DateConfig()