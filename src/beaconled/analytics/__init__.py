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

"""Analytics module for enhanced time-based and quality metrics.

This module provides advanced analytics capabilities for the BeaconLED tool,
including time-based analysis, code quality assessment, and team collaboration
insights for the enhanced extended format.
"""

from .collaboration_analyzer import CollaborationAnalyzer, CollaborationConfig
from .engine import AnalyticsEngine, ExtendedFormatSystem
from .models import (
    ActivityHeatmap,
    BusFactor,
    CoAuthorshipMetrics,
    CollaborationMetrics,
    CollaborationPatterns,
    KnowledgeDistribution,
    ReviewMetrics,
    TimeAnalytics,
    VelocityTrends,
)
from .time_analyzer import TimeAnalyzer, TimeAnalyzerConfig

__all__ = [
    "ActivityHeatmap",
    "AnalyticsEngine",
    "BusFactor",
    "CoAuthorshipMetrics",
    "CollaborationAnalyzer",
    "CollaborationConfig",
    "CollaborationMetrics",
    "CollaborationPatterns",
    "ExtendedFormatSystem",
    "KnowledgeDistribution",
    "ReviewMetrics",
    "TimeAnalytics",
    "TimeAnalyzer",
    "TimeAnalyzerConfig",
    "VelocityTrends",
]
