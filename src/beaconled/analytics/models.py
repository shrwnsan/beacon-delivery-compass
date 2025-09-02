"""Data models for analytics components.

This module defines the data structures used by the analytics engine
for time-based analysis, code quality metrics, and team collaboration insights.
"""

from dataclasses import dataclass


@dataclass
class CoAuthorshipMetrics:
    """Metrics for pair-wise collaboration between developers."""

    author_pairs: dict[tuple[str, str], int]  # (author1, author2) -> collaboration_count
    collaboration_strength: dict[tuple[str, str], float]  # Normalized collaboration score
    top_collaborators: list[tuple[str, str, int]]  # Top collaborating pairs


@dataclass
class KnowledgeDistribution:
    """Analysis of code ownership and knowledge distribution."""

    author_expertise: dict[str, dict[str, float]]  # author -> file_type -> expertise_score
    knowledge_silos: list[tuple[str, float]]  # (file_type, concentration_score)
    ownership_patterns: dict[str, list[str]]  # author -> owned_file_types


@dataclass
class ReviewMetrics:
    """Metrics for code review patterns and effectiveness."""

    review_participation: dict[str, int]  # author -> reviews_given
    review_coverage: dict[str, float]  # author -> review_coverage_ratio
    review_quality_indicators: dict[str, float]  # author -> quality_score


@dataclass
class CollaborationPatterns:
    """Overall collaboration pattern analysis."""

    team_connectivity: float  # How well connected the team is (0-1)
    collaboration_balance: float  # Balance of collaboration across team (0-1)
    knowledge_risk: str  # 'low', 'medium', 'high'


@dataclass
class CollaborationMetrics:
    """Comprehensive collaboration analysis results."""

    co_authorship: CoAuthorshipMetrics
    knowledge_distribution: KnowledgeDistribution
    review_metrics: ReviewMetrics
    collaboration_patterns: CollaborationPatterns
