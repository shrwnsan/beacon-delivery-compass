"""Performance benchmarking tests for the enhanced extended format system.

These tests measure and validate the performance of various components
to ensure they meet the required benchmarks.
"""

import time
from datetime import datetime, timedelta, timezone

from beaconled.analytics import AnalyticsEngine
from beaconled.core.models import CommitStats, RangeStats


class TestPerformanceBenchmarks:
    """Performance benchmarking tests."""

    def test_time_analyzer_performance(self):
        """Benchmark the time analyzer performance."""
        # Create large test dataset
        range_stats = self._create_large_test_repo(1000)  # 1000 commits

        engine = AnalyticsEngine()

        # Benchmark time analytics
        start_time = time.time()
        time_analytics = engine.time_analyzer.analyze(range_stats)
        time_duration = time.time() - start_time

        # Should complete in under 1 second for 1000 commits
        assert time_duration < 1.0, f"Time analytics took {time_duration:.2f}s, expected < 1.0s"

        # Verify results
        assert time_analytics is not None
        assert hasattr(time_analytics, "velocity_trends")
        assert hasattr(time_analytics, "activity_heatmap")

    def test_collaboration_analyzer_performance(self):
        """Benchmark the collaboration analyzer performance."""
        # Create large test dataset
        range_stats = self._create_large_test_repo(1000)  # 1000 commits

        engine = AnalyticsEngine()

        # Benchmark collaboration analytics
        start_time = time.time()
        collaboration_analytics = engine.collaboration_analyzer.analyze(range_stats)
        collaboration_duration = time.time() - start_time

        # Should complete in under 2 seconds for 1000 commits
        assert collaboration_duration < 2.0, (
            f"Collaboration analytics took {collaboration_duration:.2f}s, expected < 2.0s"
        )

        # Verify results
        assert collaboration_analytics is not None
        assert hasattr(collaboration_analytics, "co_authorship")
        assert hasattr(collaboration_analytics, "knowledge_distribution")

    def test_full_analytics_engine_performance(self):
        """Benchmark the full analytics engine performance."""
        # Test different repository sizes
        test_cases = [
            {"commits": 100, "max_time": 0.5},
            {"commits": 500, "max_time": 1.5},
            {"commits": 1000, "max_time": 3.0},
        ]

        engine = AnalyticsEngine()

        for case in test_cases:
            range_stats = self._create_large_test_repo(case["commits"])

            start_time = time.time()
            result = engine.analyze(range_stats)
            duration = time.time() - start_time

            assert duration < case["max_time"], (
                f"Analytics for {case['commits']} commits took {duration:.2f}s, expected < {case['max_time']}s"
            )

            # Verify results structure
            assert "time" in result
            assert "collaboration" in result

    def _create_large_test_repo(self, num_commits: int) -> RangeStats:
        """Create a large test repository for benchmarking."""
        start_date = datetime.now(timezone.utc) - timedelta(days=365)
        end_date = datetime.now(timezone.utc)

        # Create authors
        authors = [
            f"Author{i}" for i in range(min(20, num_commits // 10))
        ]  # 1 author per 10 commits, max 20
        if not authors:
            authors = ["Author0"]

        # Create commits
        commits = []
        for i in range(num_commits):
            author = authors[i % len(authors)]

            commit = CommitStats(
                hash=f"d{i:039d}",  # Fake hash
                author=f"{author} <{author.lower()}@example.com>",
                date=start_date
                + timedelta(days=i * 365 // num_commits),  # Evenly distribute over the year
                message=f"Benchmark commit {i}",
                files_changed=(i % 15) + 1,  # 1-15 files changed
                lines_added=(i % 500) + 50,  # 50-550 lines added
                lines_deleted=(i % 250),  # 0-250 lines deleted
            )
            commits.append(commit)

        # Calculate totals
        total_files = sum(c.files_changed for c in commits)
        total_added = sum(c.lines_added for c in commits)
        total_deleted = sum(c.lines_deleted for c in commits)

        # Create author counts
        author_counts = {}
        for author in authors:
            author_counts[author] = num_commits // len(authors)

        return RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=num_commits,
            total_files_changed=total_files,
            total_lines_added=total_added,
            total_lines_deleted=total_deleted,
            commits=commits,
            authors=author_counts,
        )


class TestMemoryUsage:
    """Tests for memory usage and leaks."""

    def test_no_memory_leaks_in_repeated_analysis(self):
        """Test that repeated analysis doesn't cause memory leaks."""
        # This would require more sophisticated memory profiling
        # For now, we'll do a basic test
        range_stats = self._create_test_repo(100)
        engine = AnalyticsEngine()

        # Run analysis multiple times
        for _ in range(10):
            result = engine.analyze(range_stats)
            assert result is not None

            # Force garbage collection
            import gc

            gc.collect()

    def _create_test_repo(self, num_commits: int) -> RangeStats:
        """Create a test repository."""
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)

        commits = []
        for i in range(num_commits):
            commit = CommitStats(
                hash=f"e{i:039d}",
                author="Test Author <test@example.com>",
                date=start_date + timedelta(days=i),
                message=f"Test commit {i}",
                files_changed=2,
                lines_added=50,
                lines_deleted=10,
            )
            commits.append(commit)

        return RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=num_commits,
            total_files_changed=num_commits * 2,
            total_lines_added=num_commits * 50,
            total_lines_deleted=num_commits * 10,
            commits=commits,
            authors={"Test Author": num_commits},
        )
