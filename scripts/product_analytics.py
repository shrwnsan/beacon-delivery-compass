#!/usr/bin/env python
"""
Product Analytics Engine
Transforms commit analytics into actionable business intelligence for product-led teams.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class CommitType(Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCS = "docs"
    CONFIG = "config"
    TEST = "test"
    MAINTENANCE = "maintenance"


class BusinessImpact(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class ProductMetrics:
    """Core product metrics derived from commit data."""

    feature_velocity: float  # features per week
    customer_driven_index: float  # % of commits linked to customer needs
    technical_debt_ratio: float  # % of commits addressing technical debt
    impact_ratio: Dict[str, float]  # business vs maintenance split
    release_readiness: float  # 0-100 score for release readiness


class ProductAnalytics:
    """Analyzes commits through a product lens."""

    def __init__(self, analytics_data: Dict):
        self.data = analytics_data
        self.commit_classifier = CommitClassifier()

    def calculate_product_metrics(self) -> ProductMetrics:
        """Calculate key product metrics from commit data."""
        commits = self.data.get("commits", [])

        # Feature velocity
        feature_commits = [c for c in commits if self._is_feature_commit(c)]
        period_days = self._get_period_days()
        feature_velocity = len(feature_commits) / max(period_days / 7, 1)

        # Customer-driven index
        customer_commits = [c for c in commits if self._is_customer_driven(c)]
        customer_driven_index = (len(customer_commits) / max(len(commits), 1)) * 100

        # Technical debt ratio
        debt_commits = [c for c in commits if self._is_technical_debt(c)]
        technical_debt_ratio = (len(debt_commits) / max(len(commits), 1)) * 100

        # Impact ratio
        business_impact = len([c for c in commits if self._has_business_impact(c)])
        maintenance = len([c for c in commits if self._is_maintenance(c)])
        impact_ratio = {
            "business": business_impact,
            "maintenance": maintenance,
            "ratio": business_impact / max(maintenance, 1),
        }

        # Release readiness score
        release_readiness = self._calculate_release_readiness(commits)

        return ProductMetrics(
            feature_velocity=feature_velocity,
            customer_driven_index=customer_driven_index,
            technical_debt_ratio=technical_debt_ratio,
            impact_ratio=impact_ratio,
            release_readiness=release_readiness,
        )

    def generate_product_insights(self) -> Dict:
        """Generate actionable product insights."""
        metrics = self.calculate_product_metrics()

        insights = {
            "metrics": {
                "feature_velocity": f"{metrics.feature_velocity:.1f} features/week",
                "customer_driven_index": f"{metrics.customer_driven_index:.1f}%",
                "technical_debt_ratio": f"{metrics.technical_debt_ratio:.1f}%",
                "business_impact_ratio": f"{metrics.impact_ratio['ratio']:.1f}:1",
                "release_readiness": f"{metrics.release_readiness}/100",
            },
            "recommendations": self._generate_recommendations(metrics),
            "alerts": self._generate_alerts(metrics),
            "trends": self._analyze_trends(),
        }

        return insights

    def _is_feature_commit(self, commit: Dict) -> bool:
        """Determine if commit adds new features."""
        message = commit["commit"]["message"].lower()
        return any(
            keyword in message
            for keyword in ["feat", "feature", "add", "implement", "new", "enhance"]
        )

    def _is_customer_driven(self, commit: Dict) -> bool:
        """Determine if commit addresses customer needs."""
        message = commit["commit"]["message"].lower()
        return any(
            keyword in message
            for keyword in [
                "customer",
                "user",
                "client",
                "request",
                "feedback",
                "issue",
                "bug",
            ]
        )

    def _is_technical_debt(self, commit: Dict) -> bool:
        """Determine if commit addresses technical debt."""
        message = commit["commit"]["message"].lower()
        return any(
            keyword in message
            for keyword in [
                "refactor",
                "cleanup",
                "optimize",
                "performance",
                "debt",
                "legacy",
            ]
        )

    def _has_business_impact(self, commit: Dict) -> bool:
        """Determine if commit has direct business impact."""
        components = commit.get("components", {})
        return (
            components.get("frontend", 0) > 0
            or components.get("api", 0) > 0
            or components.get("backend", 0) > 0
        )

    def _is_maintenance(self, commit: Dict) -> bool:
        """Determine if commit is maintenance work."""
        components = commit.get("components", {})
        return (
            components.get("tests", 0) > 0
            or components.get("documentation", 0) > 0
            or components.get("configuration", 0) > 0
        )

    def _calculate_release_readiness(self, commits: List[Dict]) -> float:
        """Calculate release readiness score (0-100)."""
        if not commits:
            return 0

        # Factors affecting release readiness
        test_coverage = self._get_test_coverage_score(commits)
        stability = self._get_stability_score(commits)
        documentation = self._get_documentation_score(commits)

        # Weighted average
        return test_coverage * 0.4 + stability * 0.4 + documentation * 0.2

    def _get_test_coverage_score(self, commits: List[Dict]) -> float:
        """Calculate test coverage score."""
        test_commits = [
            c for c in commits if c.get("components", {}).get("tests", 0) > 0
        ]
        return min(100, (len(test_commits) / max(len(commits), 1)) * 100)

    def _get_stability_score(self, commits: List[Dict]) -> float:
        """Calculate stability score based on bug fixes."""
        bug_commits = [c for c in commits if "bug" in c["commit"]["message"].lower()]
        return max(0, 100 - (len(bug_commits) * 10))

    def _get_documentation_score(self, commits: List[Dict]) -> float:
        """Calculate documentation completeness score."""
        doc_commits = [
            c for c in commits if c.get("components", {}).get("documentation", 0) > 0
        ]
        return min(100, (len(doc_commits) / max(len(commits), 1)) * 100)

    def _generate_recommendations(self, metrics: ProductMetrics) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations = []

        if metrics.feature_velocity < 3:
            recommendations.append("Consider increasing feature development velocity")

        if metrics.customer_driven_index < 50:
            recommendations.append("Increase focus on customer-driven development")

        if metrics.technical_debt_ratio > 30:
            recommendations.append("Schedule technical debt reduction sprint")

        if metrics.release_readiness < 70:
            recommendations.append("Improve release readiness through better testing")

        if metrics.impact_ratio["ratio"] < 1:
            recommendations.append("Shift focus from maintenance to business impact")

        return recommendations

    def _generate_alerts(self, metrics: ProductMetrics) -> List[Dict]:
        """Generate alerts for critical thresholds."""
        alerts = []

        if metrics.feature_velocity < 2:
            alerts.append(
                {
                    "type": "velocity",
                    "severity": "high",
                    "message": "Feature velocity below threshold",
                    "action": "Review resource allocation",
                }
            )

        if metrics.technical_debt_ratio > 40:
            alerts.append(
                {
                    "type": "debt",
                    "severity": "critical",
                    "message": "Technical debt ratio critically high",
                    "action": "Immediate refactoring required",
                }
            )

        if metrics.customer_driven_index < 30:
            alerts.append(
                {
                    "type": "customer_focus",
                    "severity": "medium",
                    "message": "Low customer-driven development",
                    "action": "Conduct user research",
                }
            )

        return alerts

    def _analyze_trends(self) -> Dict:
        """Analyze trends over time."""
        # This would require historical data
        return {
            "velocity_trend": "stable",
            "quality_trend": "improving",
            "customer_focus_trend": "increasing",
        }

    def _get_period_days(self) -> int:
        """Calculate the period in days."""
        # Simplified calculation - would need proper date parsing
        return 7


class CommitClassifier:
    """Classifies commits by type and impact."""

    def classify_commit(self, commit: Dict) -> Dict:
        """Classify a single commit."""
        message = commit["commit"]["message"].lower()

        commit_type = self._determine_type(message)
        business_impact = self._determine_impact(commit)

        return {
            "type": commit_type.value,
            "business_impact": business_impact.value,
            "keywords": self._extract_keywords(message),
        }

    def _determine_type(self, message: str) -> CommitType:
        """Determine commit type from message."""
        if any(kw in message for kw in ["feat", "feature", "add"]):
            return CommitType.FEATURE
        elif any(kw in message for kw in ["fix", "bug", "patch"]):
            return CommitType.BUGFIX
        elif any(kw in message for kw in ["refactor", "cleanup"]):
            return CommitType.REFACTOR
        elif any(kw in message for kw in ["docs", "readme", "documentation"]):
            return CommitType.DOCS
        elif any(kw in message for kw in ["config", "setup", "env"]):
            return CommitType.CONFIG
        elif any(kw in message for kw in ["test", "spec"]):
            return CommitType.TEST
        else:
            return CommitType.MAINTENANCE

    def _determine_impact(self, commit: Dict) -> BusinessImpact:
        """Determine business impact level."""
        components = commit.get("components", {})

        if components.get("backend", 0) > 0 or components.get("api", 0) > 0:
            return BusinessImpact.HIGH
        elif components.get("frontend", 0) > 0:
            return BusinessImpact.MEDIUM
        elif components.get("tests", 0) > 0 or components.get("documentation", 0) > 0:
            return BusinessImpact.LOW
        else:
            return BusinessImpact.NONE

    def _extract_keywords(self, message: str) -> List[str]:
        """Extract relevant keywords from commit message."""
        keywords = []
        business_keywords = [
            "customer",
            "user",
            "client",
            "revenue",
            "conversion",
            "engagement",
            "performance",
            "security",
            "scalability",
            "ux",
            "ui",
        ]

        for keyword in business_keywords:
            if keyword in message:
                keywords.append(keyword)

        return keywords


def format_product_report(insights: Dict) -> str:
    """Format product insights for stakeholders."""
    output = []

    output.append("🎯 Product Development Intelligence Report")
    output.append("=" * 50)

    # Metrics
    output.append("\n📊 Key Metrics:")
    for metric, value in insights["metrics"].items():
        output.append(f"   • {metric.replace('_', ' ').title()}: {value}")

    # Recommendations
    if insights["recommendations"]:
        output.append("\n💡 Recommendations:")
        for rec in insights["recommendations"]:
            output.append(f"   • {rec}")

    # Alerts
    if insights["alerts"]:
        output.append("\n🚨 Alerts:")
        for alert in insights["alerts"]:
            output.append(f"   • [{alert['severity'].upper()}] {alert['message']}")
            output.append(f"     Action: {alert['action']}")

    # Trends
    output.append("\n📈 Trends:")
    for trend, status in insights["trends"].items():
        output.append(f"   • {trend.replace('_', ' ').title()}: {status}")

    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    import sys

    sys.path.append(".")

    from scripts.analytics_reporter import GitAnalytics

    analytics = GitAnalytics()
    data = analytics.get_range_analytics("1w")

    product_analytics = ProductAnalytics(data)
    insights = product_analytics.generate_product_insights()

    print(format_product_report(insights))
