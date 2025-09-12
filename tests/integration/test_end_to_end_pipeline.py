"""End-to-end integration tests for the enhanced extended format system.

These tests verify the complete pipeline works with real repository data
and produces expected output with performance benchmarks.
"""

import time
from datetime import datetime, timedelta, timezone

from beaconled.analytics.engine import AnalyticsEngine, ExtendedFormatSystem
from beaconled.core.models import CommitStats, RangeStats
from beaconled.formatters.extended import ExtendedFormatter
from beaconled.formatters.rich_formatter import RichFormatter


class TestEndToEndPipeline:
    """End-to-end tests for the complete analytics and formatting pipeline."""

    def test_full_pipeline_with_small_repo(self):
        """Test complete pipeline with small repository data."""
        # Create small test repository data
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)

        # Create commits with realistic patterns
        commits = []
        authors = {"Alice": 0, "Bob": 0, "Charlie": 0}

        for i in range(50):  # 50 commits
            author = list(authors.keys())[i % 3]  # Rotate through authors
            authors[author] += 1

            commit = CommitStats(
                hash=f"a{i:039d}",  # Fake hash
                author=f"{author} <{author.lower()}@example.com>",
                date=start_date + timedelta(days=i // 2),  # 2 commits per day on average
                message=f"Commit {i}",
                files_changed=(i % 5) + 1,  # 1-5 files changed
                lines_added=(i % 100) + 10,  # 10-110 lines added
                lines_deleted=(i % 50),  # 0-50 lines deleted
            )
            commits.append(commit)

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=50,
            total_files_changed=sum(c.files_changed for c in commits),
            total_lines_added=sum(c.lines_added for c in commits),
            total_lines_deleted=sum(c.lines_deleted for c in commits),
            commits=commits,
            authors=authors,
        )

        # Test the complete pipeline
        system = ExtendedFormatSystem()
        system.set_formatter(RichFormatter())  # Or ExtendedFormatter()

        # Benchmark the pipeline
        start_time = time.time()
        result = system.format_analysis(range_stats)
        end_time = time.time()

        # Verify we get expected output
        assert isinstance(result, str)
        assert len(result) > 0

        # Performance check - should be fast for small repo
        execution_time = end_time - start_time
        assert execution_time < 2.0  # Should complete in under 2 seconds

        # Should contain key information
        assert "Enhanced analysis complete" in result or "Range Analysis" in result

    def test_performance_benchmarks(self):
        """Test performance benchmarks with various repository sizes."""
        # Test with different repository sizes
        repo_sizes = [
            {"name": "small", "commits": 100, "max_time": 2.0},
            {"name": "medium", "commits": 500, "max_time": 5.0},
        ]

        for repo_config in repo_sizes:
            self._benchmark_repo_size(repo_config)

    def _benchmark_repo_size(self, config: dict):
        """Benchmark a specific repository size."""
        # Create test data
        start_date = datetime.now(timezone.utc) - timedelta(days=90)
        end_date = datetime.now(timezone.utc)

        commits = []
        authors = {"Alice": 0, "Bob": 0, "Charlie": 0, "Diana": 0, "Eve": 0}

        for i in range(config["commits"]):
            author = list(authors.keys())[i % 5]  # Rotate through 5 authors
            authors[author] += 1

            commit = CommitStats(
                hash=f"b{i:039d}",  # Fake hash
                author=f"{author} <{author.lower()}@example.com>",
                date=start_date + timedelta(days=i // 5),  # 5 commits per day on average
                message=f"Performance test commit {i}",
                files_changed=(i % 10) + 1,  # 1-10 files changed
                lines_added=(i % 200) + 20,  # 20-220 lines added
                lines_deleted=(i % 100),  # 0-100 lines deleted
            )
            commits.append(commit)

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=config["commits"],
            total_files_changed=sum(c.files_changed for c in commits),
            total_lines_added=sum(c.lines_added for c in commits),
            total_lines_deleted=sum(c.lines_deleted for c in commits),
            commits=commits,
            authors=authors,
        )

        # Test the analytics engine performance
        engine = AnalyticsEngine()

        start_time = time.time()
        analytics = engine.analyze(range_stats)
        analytics_time = time.time() - start_time

        # Verify analytics results
        assert "time" in analytics
        assert "collaboration" in analytics
        assert analytics["time"] is not None
        assert analytics["collaboration"] is not None

        # Performance check
        assert analytics_time < config["max_time"], (
            f"Analytics for {config['name']} repo took {analytics_time:.2f}s, expected < {config['max_time']}s"
        )

        # Test the full system performance
        system = ExtendedFormatSystem()
        system.set_formatter(ExtendedFormatter())

        start_time = time.time()
        result = system.format_analysis(range_stats)
        total_time = time.time() - start_time

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0

        # Total performance check
        assert total_time < config["max_time"] * 2, (
            f"Full pipeline for {config['name']} repo took {total_time:.2f}s, expected < {config['max_time'] * 2}s"
        )


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_empty_repository(self):
        """Test handling of empty repository."""
        from beaconled.formatters.standard import StandardFormatter

        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        end_date = datetime.now(timezone.utc)

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=0,
            total_files_changed=0,
            total_lines_added=0,
            total_lines_deleted=0,
            commits=[],
            authors={},
        )

        system = ExtendedFormatSystem()
        system.set_formatter(StandardFormatter())
        result = system.format_analysis(range_stats)

        # Should handle gracefully
        assert isinstance(result, str)
        assert len(result) > 0

    def test_single_commit_repository(self):
        """Test handling of single commit repository."""
        from beaconled.formatters.standard import StandardFormatter

        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        end_date = datetime.now(timezone.utc)

        commit = CommitStats(
            hash="c" * 40,
            author="Single Author <single@example.com>",
            date=start_date + timedelta(hours=12),
            message="Only commit",
            files_changed=1,
            lines_added=10,
            lines_deleted=0,
        )

        range_stats = RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=1,
            total_files_changed=1,
            total_lines_added=10,
            total_lines_deleted=0,
            commits=[commit],
            authors={"Single Author": 1},
        )

        system = ExtendedFormatSystem()
        system.set_formatter(StandardFormatter())
        result = system.format_analysis(range_stats)

        # Should handle gracefully
        assert isinstance(result, str)
        assert len(result) > 0
