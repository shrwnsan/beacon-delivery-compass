"""Unit tests for the refactored methods in GitAnalyzer.

Tests for the extracted methods from get_range_analytics:
- _validate_and_normalize_dates
- _fetch_commits_in_range
- _calculate_author_analytics
- _calculate_timeline_analytics
- _calculate_file_analytics
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch, MagicMock as MockMagic

from beaconled.core.analyzer import GitAnalyzer


class TestRefactoredMethods:
    """Test the refactored methods extracted from get_range_analytics."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create analyzer instance without initializing git repo
        self.analyzer = object.__new__(GitAnalyzer)
        self.analyzer.repo_path = "/fake/repo"
        self.analyzer.strict_mode = False
        # Mock _parse_date method
        self.analyzer._parse_date = Mock()

    @patch('beaconled.core.analyzer.DateUtils.validate_date_range')
    def test_validate_and_normalize_dates_with_strings(self, mock_validate):
        """Test date validation with string inputs."""
        # Setup
        mock_validate.return_value = (
            datetime(2023, 1, 1, tzinfo=timezone.utc),
            datetime(2023, 1, 7, tzinfo=timezone.utc)
        )
        self.analyzer._parse_date.side_effect = [
            datetime(2023, 1, 1, tzinfo=timezone.utc),
            datetime(2023, 1, 7, tzinfo=timezone.utc)
        ]

        # Execute
        start, end = self.analyzer._validate_and_normalize_dates("2023-01-01", "2023-01-07")

        # Assert
        assert start == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert end == datetime(2023, 1, 7, tzinfo=timezone.utc)

    @patch('beaconled.core.analyzer.DateUtils.validate_date_range')
    def test_validate_and_normalize_dates_with_now(self, mock_validate):
        """Test date validation with 'now' as end date."""
        # Setup
        expected_start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        expected_end = datetime.now(timezone.utc)
        mock_validate.return_value = (expected_start, expected_end)
        self.analyzer._parse_date = Mock(return_value=expected_start)

        # Execute
        start, end = self.analyzer._validate_and_normalize_dates("2023-01-01", "now")

        # Assert
        assert start == expected_start
        assert end == expected_end

    @patch('beaconled.core.analyzer.DateUtils.validate_date_range')
    def test_validate_and_normalize_dates_with_datetime_objects(self, mock_validate):
        """Test date validation with datetime objects."""
        # Setup
        start_dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_dt = datetime(2023, 1, 7, tzinfo=timezone.utc)
        mock_validate.return_value = (start_dt, end_dt)

        # Execute
        start, end = self.analyzer._validate_and_normalize_dates(start_dt, end_dt)

        # Assert
        assert start == start_dt
        assert end == end_dt
        # Since we're passing datetime objects, _parse_date should not be called
        assert self.analyzer._parse_date.call_count == 0

    @patch('beaconled.core.analyzer.git.Repo')
    def test_fetch_commits_in_range_with_iter_commits(self, mock_repo_class):
        """Test fetching commits using iter_commits."""
        # Setup
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_commits = [
            Mock(hexsha="abc123"),
            Mock(hexsha="def456")
        ]
        mock_repo.iter_commits.return_value = iter(mock_commits)

        start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end = datetime(2023, 1, 7, tzinfo=timezone.utc)

        # Execute
        commits = self.analyzer._fetch_commits_in_range(start, end)

        # Assert
        assert commits == ["abc123", "def456"]
        mock_repo.iter_commits.assert_called_once_with(
            all=True,
            since=start.isoformat(),
            until=end.isoformat()
        )

    @patch('beaconled.core.analyzer.git.Repo')
    def test_fetch_commits_fallback_to_git_log(self, mock_repo_class):
        """Test fallback to git log when iter_commits fails."""
        # Setup
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # iter_commits fails
        mock_repo.iter_commits.side_effect = Exception("iter_commits failed")

        # git log succeeds
        mock_repo.git.log.return_value = "abc123\ndef456\nghi789"

        start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end = datetime(2023, 1, 7, tzinfo=timezone.utc)

        # Execute
        commits = self.analyzer._fetch_commits_in_range(start, end)

        # Assert
        assert commits == ["abc123", "def456", "ghi789"]
        mock_repo.git.log.assert_called_once_with(
            "--all",
            "--reverse",
            "--pretty=format:%H",
            "--no-patch",
            f"--since={start.isoformat()}",
            f"--until={end.isoformat()}"
        )

    @patch('beaconled.core.analyzer.git.Repo')
    def test_fetch_commits_both_methods_fail(self, mock_repo_class):
        """Test when both iter_commits and git log fail."""
        # Setup
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_repo.iter_commits.side_effect = Exception("iter_commits failed")
        mock_repo.git.log.side_effect = Exception("git log failed")

        start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end = datetime(2023, 1, 7, tzinfo=timezone.utc)

        # Execute
        commits = self.analyzer._fetch_commits_in_range(start, end)

        # Assert
        assert commits == []

    def test_calculate_author_analytics(self):
        """Test author statistics calculation."""
        # Setup
        commits = [
            Mock(
                author="John Doe <john@example.com>"
            ),
            Mock(
                author="Jane Smith <jane@example.com>"
            ),
            Mock(
                author="John Doe <john@example.com>"
            )
        ]

        # Execute
        authors = self.analyzer._calculate_author_analytics(commits)

        # Assert
        assert authors == {
            "John Doe <john@example.com>": 2,
            "Jane Smith <jane@example.com>": 1
        }

    def test_calculate_author_analytics_empty_commits(self):
        """Test author statistics with empty commit list."""
        # Execute
        authors = self.analyzer._calculate_author_analytics([])

        # Assert
        assert authors == {}

    def test_calculate_timeline_analytics(self):
        """Test timeline analytics calculation."""
        # Setup
        commits = [
            Mock(
                hash="abc123",
                author="John Doe",
                date=datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
            ),
            Mock(
                hash="def456",
                author="Jane Smith",
                date=datetime(2023, 1, 1, 15, 0, tzinfo=timezone.utc)
            ),
            Mock(
                hash="ghi789",
                author="John Doe",
                date=datetime(2023, 1, 2, 9, 0, tzinfo=timezone.utc)
            )
        ]

        # Execute
        timeline = self.analyzer._calculate_timeline_analytics(commits)

        # Assert
        assert timeline == {
            "2023-01-01": 2,
            "2023-01-02": 1
        }

    def test_calculate_timeline_analytics_strict_mode_error(self):
        """Test timeline analytics with strict mode error."""
        from beaconled.exceptions import InternalError

        # Setup
        self.analyzer.strict_mode = True
        # Create a mock that raises exception when accessing date
        commit = Mock()
        commit.hash = "abc123"
        commit.author = "John Doe"
        commit.date = Mock()
        commit.date.strftime.side_effect = Exception("Date processing failed")
        commits = [commit]

        # Execute & Assert
        with pytest.raises(InternalError, match="Failed to update timeline"):
            self.analyzer._calculate_timeline_analytics(commits)

    def test_calculate_file_analytics(self):
        """Test file analytics calculation."""
        # Setup
        file1 = Mock(path="test.py", lines_added=10, lines_deleted=5)
        file2 = Mock(path="docs.md", lines_added=0, lines_deleted=0)
        file3 = Mock(path="test.py", lines_added=20, lines_deleted=10)

        commits = [
            Mock(
                hash="abc123",
                author="John Doe",
                date=datetime.now(timezone.utc),
                files_changed=2,
                lines_added=10,
                lines_deleted=5,
                files=[file1, file2]
            ),
            Mock(
                hash="def456",
                author="Jane Smith",
                date=datetime.now(timezone.utc),
                files_changed=1,
                lines_added=20,
                lines_deleted=10,
                files=[file3]
            )
        ]

        # Execute
        total_files, total_added, total_deleted, file_types = self.analyzer._calculate_file_analytics(commits)

        # Assert
        assert total_files == 3  # 2 + 1
        assert total_added == 30  # 10 + 20
        assert total_deleted == 15  # 5 + 10

        assert file_types == {
            "py": {
                "files_changed": 2,
                "lines_added": 30,
                "lines_deleted": 15
            },
            "md": {
                "files_changed": 1,
                "lines_added": 0,
                "lines_deleted": 0
            }
        }

    def test_calculate_file_analytics_no_files(self):
        """Test file analytics with commits that have no files."""
        # Setup
        commits = [
            Mock(
                hash="abc123",
                author="John Doe",
                date=datetime.now(timezone.utc),
                files_changed=0,
                lines_added=0,
                lines_deleted=0,
                files=[]
            ),
            Mock(
                hash="def456",
                author="Jane Smith",
                date=datetime.now(timezone.utc),
                files_changed=0,
                lines_added=0,
                lines_deleted=0,
                files=None  # None instead of missing attribute
            )
        ]

        # Execute
        total_files, total_added, total_deleted, file_types = self.analyzer._calculate_file_analytics(commits)

        # Assert
        assert total_files == 0
        assert total_added == 0
        assert total_deleted == 0
        assert file_types == {}

    def test_calculate_file_analytics_files_without_path(self):
        """Test file analytics with file stats that have no path attribute."""
        # Setup - create simple mock objects manually
        file_without_path = Mock()
        # Remove the path attribute entirely
        delattr(file_without_path, 'path') if hasattr(file_without_path, 'path') else None

        # Create file with path that returns a list when split is called
        file_with_path = Mock()
        file_with_path.path = "test.py"
        file_with_path.lines_added = 10
        file_with_path.lines_deleted = 5

        commits = [
            Mock(
                hash="abc123",
                author="John Doe",
                date=datetime.now(timezone.utc),
                files_changed=2,
                lines_added=10,
                lines_deleted=5,
                files=[file_without_path, file_with_path]
            )
        ]

        # Execute
        total_files, total_added, total_deleted, file_types = self.analyzer._calculate_file_analytics(commits)

        # Assert
        assert total_files == 2
        assert total_added == 10
        assert total_deleted == 5
        assert file_types == {
            "py": {
                "files_changed": 1,
                "lines_added": 10,
                "lines_deleted": 5
            }
        }
