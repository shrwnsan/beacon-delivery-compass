#!/usr/bin/env python
"""
Product Insights CLI
Command-line interface for product-led development analytics.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from analytics_reporter import GitAnalytics
from product_analytics import ProductAnalytics, format_product_report


class ProductInsightsCLI:
    """CLI for product insights and business intelligence."""

    def __init__(self):
        self.git_analytics = GitAnalytics()
        self.product_analytics = None

    def run_weekly_report(self, since: str = "1w") -> str:
        """Generate comprehensive weekly product report."""
        # Get raw analytics
        analytics_data = self.git_analytics.get_range_analytics(since)

        # Generate product insights
        self.product_analytics = ProductAnalytics(analytics_data)
        insights = self.product_analytics.generate_product_insights()

        # Format for stakeholders
        return format_product_report(insights)

    def run_commit_analysis(self, commit_hash: str = "HEAD") -> str:
        """Analyze individual commit for product impact."""
        commit_data = self.git_analytics.get_commit_stats(commit_hash)

        # Create single-commit analytics
        analytics_data = {
            "commits": [commit_data],
            "period": {"since": "single", "until": "single"},
        }

        self.product_analytics = ProductAnalytics(analytics_data)
        insights = self.product_analytics.generate_product_insights()

        return format_product_report(insights)

    def generate_executive_summary(self, since: str = "1w") -> Dict:
        """Generate executive summary for leadership."""
        analytics_data = self.git_analytics.get_range_analytics(since)
        self.product_analytics = ProductAnalytics(analytics_data)
        insights = self.product_analytics.generate_product_insights()

        # Extract key metrics for executives
        summary = {
            "period": since,
            "executive_summary": {
                "feature_velocity": insights["metrics"]["feature_velocity"],
                "customer_focus": insights["metrics"]["customer_driven_index"],
                "release_readiness": insights["metrics"]["release_readiness"],
                "key_alerts": len(insights["alerts"]),
                "priority_actions": len(insights["recommendations"]),
            },
            "business_impact": self._calculate_business_impact(analytics_data),
            "next_actions": insights["recommendations"][:3],  # Top 3 recommendations
        }

        return summary

    def _calculate_business_impact(self, analytics_data: Dict) -> Dict:
        """Calculate business impact metrics."""
        commits = analytics_data.get("commits", [])

        # Business value metrics
        business_commits = [c for c in commits if self._has_direct_business_value(c)]
        customer_commits = [c for c in commits if self._is_customer_facing(c)]

        # Calculate impact scores
        total_commits = len(commits)
        business_impact_score = (len(business_commits) / max(total_commits, 1)) * 100
        customer_impact_score = (len(customer_commits) / max(total_commits, 1)) * 100

        # Component impact
        components = {}
        for commit in commits:
            for comp, count in commit.get("components", {}).items():
                if comp in ["backend", "frontend", "api"]:
                    components[comp] = components.get(comp, 0) + count

        return {
            "business_impact_score": f"{business_impact_score:.1f}%",
            "customer_impact_score": f"{customer_impact_score:.1f}%",
            "component_distribution": components,
            "total_business_value_commits": len(business_commits),
        }

    def _has_direct_business_value(self, commit: Dict) -> bool:
        """Check if commit has direct business value."""
        message = commit["commit"]["message"].lower()
        components = commit.get("components", {})

        # Business value keywords
        business_keywords = [
            "revenue",
            "conversion",
            "sales",
            "customer",
            "user",
            "performance",
            "security",
            "scalability",
            "feature",
            "enhancement",
        ]

        has_business_keyword = any(kw in message for kw in business_keywords)
        has_product_component = any(
            components.get(comp, 0) > 0 for comp in ["backend", "frontend", "api"]
        )

        return has_business_keyword and has_product_component

    def _is_customer_facing(self, commit: Dict) -> bool:
        """Check if commit affects customer experience."""
        message = commit["commit"]["message"].lower()
        components = commit.get("components", {})

        customer_keywords = ["customer", "user", "client", "ui", "ux", "experience"]
        has_customer_keyword = any(kw in message for kw in customer_keywords)

        customer_components = components.get("frontend", 0) > 0 or components.get("api", 0) > 0

        return has_customer_keyword or customer_components


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Product Insights CLI")
    parser.add_argument(
        "command",
        choices=["weekly", "commit", "executive", "alerts"],
        help="Command to run",
    )

    parser.add_argument(
        "--since",
        default="1w",
        help="Start date for analysis (e.g., '1w' for 1 week, '2d' for 2 days, '3m' for 3 months, '1y' for 1 year)",
    )
    parser.add_argument("--commit", default="HEAD", help="Commit hash for single commit analysis")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--repo", default=".", help="Repository path")

    args = parser.parse_args()

    cli = ProductInsightsCLI()

    try:
        if args.command == "weekly":
            report = cli.run_weekly_report(args.since)
            print(report)

        elif args.command == "commit":
            analysis = cli.run_commit_analysis(args.commit)
            print(analysis)

        elif args.command == "executive":
            summary = cli.generate_executive_summary(args.since)
            if args.format == "json":
                print(json.dumps(summary, indent=2))
            else:
                print("📊 Executive Summary")
                print("=" * 30)
                print(f"Period: {summary['period']}")
                print("\n🎯 Key Metrics:")
                for key, value in summary["executive_summary"].items():
                    print(f"   • {key.replace('_', ' ').title()}: {value}")

                print("\n💼 Business Impact:")
                for key, value in summary["business_impact"].items():
                    print(f"   • {key.replace('_', ' ').title()}: {value}")

                print("\n🚀 Next Actions:")
                for i, action in enumerate(summary["next_actions"], 1):
                    print(f"   {i}. {action}")

        elif args.command == "alerts":
            analytics_data = cli.git_analytics.get_range_analytics(args.since)
            product_analytics = ProductAnalytics(analytics_data)
            insights = product_analytics.generate_product_insights()

            if insights["alerts"]:
                print("🚨 Product Development Alerts")
                print("=" * 35)
                for alert in insights["alerts"]:
                    print(f"\n[{alert['severity'].upper()}] {alert['message']}")
                    print(f"Action: {alert['action']}")
            else:
                print("✅ No alerts - all metrics within thresholds")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
