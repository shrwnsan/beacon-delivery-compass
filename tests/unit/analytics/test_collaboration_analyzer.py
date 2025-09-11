"""Unit tests for CollaborationAnalyzer."""

import pytest
from datetime import datetime, timedelta, timezone

from beaconled.analytics.collaboration_analyzer import CollaborationAnalyzer, CollaborationConfig
from beaconled.core.models import CommitStats, FileStats, RangeStats


class TestCollaborationAnalyzer:
    """Test cases for CollaborationAnalyzer class."""

    @pytest.fixture
    def config(self):
        """Default test configuration."""
        return CollaborationConfig(
            min_collaboration_threshold=3, knowledge_silo_threshold=0.8, review_coverage_target=0.7
        )

    @pytest.fixture
    def analyzer(self, config):
        """CollaborationAnalyzer instance for testing."""
        return CollaborationAnalyzer(config)

    @pytest.fixture
    def sample_commits(self):
        """Sample commit data for testing."""
        base_date = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        commits = []

        # Create commits with different authors and file collaborations
        authors = ["alice", "bob", "charlie", "diana"]
        files = ["src/main.py", "src/utils.py", "tests/test_main.py", "docs/README.md"]

        for i in range(20):
            author = authors[i % len(authors)]
            date = base_date + timedelta(days=i % 7, hours=i % 24)

            # Create files for this commit
            commit_files = []
            num_files = (i % 3) + 1  # 1-3 files per commit
            for j in range(num_files):
                file_path = files[(i + j) % len(files)]
                commit_files.append(
                    FileStats(path=file_path, lines_added=(i + j) * 10, lines_deleted=(i + j) * 2)
                )

            commits.append(
                CommitStats(
                    hash=f"commit_{i:03d}",
                    author=author,
                    date=date,
                    message=f"Commit {i} by {author}",
                    files_changed=len(commit_files),
                    lines_added=sum(f.lines_added for f in commit_files),
                    lines_deleted=sum(f.lines_deleted for f in commit_files),
                    files=commit_files,
                )
            )

        return commits

    @pytest.fixture
    def sample_range_stats(self, sample_commits):
        """Sample RangeStats for testing."""
        return RangeStats(
            start_date=min(c.date for c in sample_commits),
            end_date=max(c.date for c in sample_commits),
            commits=sample_commits,
        )

    def test_analyze_empty_commits(self, analyzer):
        """Test analysis with empty commit list."""
        empty_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 2, tzinfo=timezone.utc),
            commits=[],
        )

        result = analyzer.analyze(empty_stats)

        assert result.co_authorship.author_pairs == {}
        assert result.knowledge_distribution.author_expertise == {}
        assert result.collaboration_patterns.team_connectivity == 0.0

    def test_analyze_co_authorship(self, analyzer, sample_commits):
        """Test co-authorship analysis."""
        co_authorship = analyzer._analyze_co_authorship(
            RangeStats(
                start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2023, 1, 7, tzinfo=timezone.utc),
                commits=sample_commits,
            )
        )

        assert isinstance(co_authorship.author_pairs, dict)
        assert isinstance(co_authorship.collaboration_strength, dict)
        assert isinstance(co_authorship.top_collaborators, list)

        # Should have some collaboration pairs
        if co_authorship.author_pairs:
            for pair, count in co_authorship.author_pairs.items():
                assert isinstance(pair, tuple)
                assert len(pair) == 2
                assert isinstance(count, int)
                assert count > 0

    def test_analyze_knowledge_distribution(self, analyzer, sample_range_stats):
        """Test knowledge distribution analysis."""
        knowledge = analyzer._analyze_knowledge_distribution(sample_range_stats)

        assert isinstance(knowledge.author_expertise, dict)
        assert isinstance(knowledge.knowledge_silos, list)
        assert isinstance(knowledge.ownership_patterns, dict)

        # Check author expertise structure
        for author, file_types in knowledge.author_expertise.items():
            assert isinstance(author, str)
            assert isinstance(file_types, dict)
            for file_type, score in file_types.items():
                assert isinstance(file_type, str)
                assert isinstance(score, float)
                assert 0 <= score <= 1

    def test_analyze_review_metrics(self, analyzer, sample_range_stats):
        """Test review metrics analysis."""
        review_metrics = analyzer._analyze_review_metrics(sample_range_stats)

        assert isinstance(review_metrics.review_participation, dict)
        assert isinstance(review_metrics.review_coverage, dict)
        assert isinstance(review_metrics.review_quality_indicators, dict)

        # Should have metrics for all authors
        for author in sample_range_stats.authors.keys():
            assert author in review_metrics.review_participation
            assert author in review_metrics.review_coverage
            assert author in review_metrics.review_quality_indicators

            assert isinstance(review_metrics.review_participation[author], int)
            assert isinstance(review_metrics.review_coverage[author], float)
            assert isinstance(review_metrics.review_quality_indicators[author], float)

    def test_identify_patterns(self, analyzer, sample_range_stats):
        """Test collaboration pattern identification."""
        patterns = analyzer._identify_patterns(sample_range_stats)

        assert isinstance(patterns.team_connectivity, float)
        assert isinstance(patterns.collaboration_balance, float)
        assert patterns.knowledge_risk in ["low", "medium", "high"]

        assert 0 <= patterns.team_connectivity <= 1
        assert 0 <= patterns.collaboration_balance <= 1

    def test_full_analysis(self, analyzer, sample_range_stats):
        """Test complete analysis pipeline."""
        result = analyzer.analyze(sample_range_stats)

        assert hasattr(result, "co_authorship")
        assert hasattr(result, "knowledge_distribution")
        assert hasattr(result, "review_metrics")
        assert hasattr(result, "collaboration_patterns")

        # Verify all components are properly populated
        assert isinstance(result.co_authorship.author_pairs, dict)
        assert isinstance(result.knowledge_distribution.author_expertise, dict)
        assert isinstance(result.review_metrics.review_participation, dict)
        assert isinstance(result.collaboration_patterns.team_connectivity, float)

    def test_single_author_scenario(self, analyzer):
        """Test analysis with single author."""
        single_author_commits = [
            CommitStats(
                hash="commit_001",
                author="single_author",
                date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                message="Single author commit",
                files_changed=1,
                lines_added=10,
                lines_deleted=2,
                files=[FileStats(path="src/main.py", lines_added=10, lines_deleted=2)],
            )
        ]

        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            commits=single_author_commits,
        )

        result = analyzer.analyze(range_stats)

        # Should have minimal collaboration
        assert len(result.co_authorship.author_pairs) == 0
        assert result.collaboration_patterns.collaboration_balance == 0.0

    def test_file_type_extraction(self, analyzer):
        """Test file type extraction utility."""
        test_cases = [
            ("src/main.py", "py"),
            ("src/utils.js", "js"),
            ("docs/README.md", "md"),
            ("Makefile", "unknown"),
            ("src/test_main.py", "py"),
        ]

        for file_path, expected_type in test_cases:
            assert analyzer._get_file_type(file_path) == expected_type

    def test_config_parameters(self):
        """Test configuration parameter effects."""
        custom_config = CollaborationConfig(
            min_collaboration_threshold=5, knowledge_silo_threshold=0.9, review_coverage_target=0.8
        )
        analyzer = CollaborationAnalyzer(custom_config)

        assert analyzer.min_collaboration_threshold == 5
        assert analyzer.knowledge_silo_threshold == 0.9
        assert analyzer.review_coverage_target == 0.8

    def test_knowledge_silos_detection(self, analyzer):
        """Test knowledge silos detection."""
        # Create commits where one author dominates a file type
        specialized_commits = [
            CommitStats(
                hash="commit_001",
                author="python_expert",
                date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                message="Python work",
                files_changed=5,
                lines_added=50,
                lines_deleted=10,
                files=[
                    FileStats(path="src/main.py", lines_added=10, lines_deleted=2),
                    FileStats(path="src/utils.py", lines_added=10, lines_deleted=2),
                    FileStats(path="src/helpers.py", lines_added=10, lines_deleted=2),
                    FileStats(path="src/core.py", lines_added=10, lines_deleted=2),
                    FileStats(path="src/api.py", lines_added=10, lines_deleted=2),
                ],
            ),
            CommitStats(
                hash="commit_002",
                author="js_developer",
                date=datetime(2023, 1, 2, tzinfo=timezone.utc),
                message="JS work",
                files_changed=1,
                lines_added=20,
                lines_deleted=5,
                files=[FileStats(path="src/app.js", lines_added=20, lines_deleted=5)],
            ),
        ]

        range_stats = RangeStats(
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 2, tzinfo=timezone.utc),
            commits=specialized_commits,
        )

        knowledge = analyzer._analyze_knowledge_distribution(range_stats)

        # Should detect python expert as having high concentration in .py files
        assert "python_expert" in knowledge.author_expertise
        assert "py" in knowledge.author_expertise["python_expert"]
