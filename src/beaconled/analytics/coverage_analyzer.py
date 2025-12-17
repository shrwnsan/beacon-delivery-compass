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

"""Test coverage analyzer for parsing and analyzing coverage reports.

This module provides functionality to parse coverage reports in various formats
and analyze coverage trends over time.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from beaconled.exceptions import InvalidRepositoryError, ValidationError

try:
    from defusedxml.ElementTree import fromstring as ET_fromstring  # noqa: N812
    from defusedxml.ElementTree import parse as ET_parse  # noqa: N812

    HAS_DEFUSEDXML = True
except ImportError:
    import xml.etree.ElementTree as ET  # noqa: S405

    ET_parse = ET.parse  # type: ignore[assignment]  # noqa: S314
    ET_fromstring = ET.fromstring  # type: ignore[assignment]  # noqa: S314
    HAS_DEFUSEDXML = False

from beaconled.core.models import CoverageStats, CoverageTrend

# Logger
logger = logging.getLogger(__name__)


class CoverageAnalyzer:
    """Analyzes test coverage data from various report formats."""

    def __init__(self, repo_path: str = ".") -> None:
        """Initialize the coverage analyzer.

        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path).resolve()

    def parse_coverage_xml(self, xml_path: str | Path) -> CoverageStats:
        """Parse coverage data from a coverage.xml file.

        Args:
            xml_path: Path to the coverage.xml file

        Returns:
            CoverageStats object with parsed coverage data

        Raises:
            FileNotFoundError: If the coverage file doesn't exist
            ValueError: If the coverage file is malformed
        """
        xml_file = Path(xml_path)
        if not xml_file.exists():
            msg = f"Coverage file not found: {xml_path}"
            raise InvalidRepositoryError(str(xml_path), reason="Coverage file not found")

        try:
            tree = ET_parse(xml_file)
            root = tree.getroot()

            # Extract overall coverage statistics
            lines_valid = int(root.get("lines-valid", 0))  # type: ignore[union-attr]
            lines_covered = int(root.get("lines-covered", 0))  # type: ignore[union-attr]
            branches_valid = int(root.get("branches-valid", 0))  # type: ignore[union-attr]
            branches_covered = int(root.get("branches-covered", 0))  # type: ignore[union-attr]
            line_rate = float(root.get("line-rate", 0.0))  # type: ignore[union-attr]
            branch_rate = float(root.get("branch-rate", 0.0))  # type: ignore[union-attr]
            timestamp = datetime.fromtimestamp(
                int(root.get("timestamp", 0)) / 1000,  # type: ignore[union-attr]
                tz=timezone.utc,
            )

            # Parse file-level coverage
            file_coverage: dict[str, float] = {}
            for package in root.findall(".//package"):  # type: ignore[union-attr]
                for cls in package.findall(".//class"):  # type: ignore[union-attr]
                    filename = cls.get("filename", "")  # type: ignore[union-attr]
                    if filename:
                        file_line_rate = float(cls.get("line-rate", 0.0))  # type: ignore[union-attr]
                        file_coverage[filename] = file_line_rate * 100

            return CoverageStats(
                timestamp=timestamp,
                total_lines=lines_valid,
                covered_lines=lines_covered,
                line_rate=line_rate,
                total_branches=branches_valid,
                covered_branches=branches_covered,
                branch_rate=branch_rate,
                file_coverage=file_coverage,
            )

        except Exception as e:
            msg = f"Invalid XML format in coverage file: {e}"
            raise ValidationError(msg, field="coverage_xml", value=xml_path) from e
        except (ValueError, TypeError) as e:
            msg = f"Invalid coverage data in XML file: {e}"
            raise ValidationError(msg, field="coverage_data", value=xml_path) from e

    def parse_coverage_db(self, db_path: str | Path = ".coverage") -> CoverageStats:
        """Parse coverage data from a .coverage database file.

        Args:
            db_path: Path to the .coverage file

        Returns:
            CoverageStats object with parsed coverage data

        Raises:
            FileNotFoundError: If the coverage file doesn't exist
            ImportError: If coverage module is not available
        """
        try:
            import coverage
        except ImportError as e:
            msg = "coverage module is required to parse .coverage files"
            raise ImportError(msg) from e

        db_file = Path(db_path)
        if not db_file.exists():
            msg = f"Coverage database file not found: {db_path}"
            raise InvalidRepositoryError(str(db_path), reason="Coverage database file not found")

        try:
            cov = coverage.Coverage(data_file=str(db_file))
            cov.load()

            # Get overall coverage data
            total_lines = cov._analyze("").numbers.n_statements
            line_rate = cov._analyze("").numbers.pc_covered
            covered_lines = int(total_lines * line_rate) if total_lines > 0 else 0

            # Get file-level coverage
            file_coverage: dict[str, float] = {}
            for filename in cov.get_data().measured_files():
                file_analysis = cov._analyze(filename)
                file_total = file_analysis.numbers.n_statements
                file_rate = file_analysis.numbers.pc_covered
                file_covered = int(file_total * file_rate) if file_total > 0 else 0
                file_coverage[filename] = (
                    (file_covered / file_total * 100) if file_total > 0 else 0.0
                )

            return CoverageStats(
                timestamp=datetime.now(timezone.utc),
                total_lines=total_lines,
                covered_lines=covered_lines,
                line_rate=line_rate,
                file_coverage=file_coverage,
            )

        except Exception as e:
            msg = f"Error parsing coverage database: {e}"
            raise ValidationError(msg, field="coverage_db", value=db_path) from e

    def find_coverage_files(self) -> list[Path]:
        """Find coverage files in the repository.

        Returns:
            List of paths to coverage files found
        """
        coverage_files = []
        repo_root = self.repo_path

        # Look for common coverage file locations
        search_paths = [
            repo_root / "coverage.xml",
            repo_root / ".coverage",
            repo_root / "reports" / "coverage.xml",
            repo_root / "test-reports" / "coverage.xml",
        ]

        for path in search_paths:
            if path.exists():
                coverage_files.append(path)

        # Also search for coverage files in subdirectories
        for pattern in ["**/*.coverage", "**/coverage.xml"]:
            coverage_files.extend(repo_root.glob(pattern))

        return sorted(set(coverage_files))

    def analyze_coverage_trends(self, coverage_history: list[CoverageStats]) -> CoverageTrend:
        """Analyze coverage trends over time.

        Args:
            coverage_history: List of coverage stats in chronological order

        Returns:
            CoverageTrend object with trend analysis
        """
        if len(coverage_history) < 2:
            return CoverageTrend()

        # Sort by timestamp to ensure chronological order
        sorted_history = sorted(coverage_history, key=lambda x: x.timestamp)

        start_coverage = sorted_history[0]
        end_coverage = sorted_history[-1]

        # Calculate trend direction and magnitude
        start_percentage = start_coverage.overall_percentage
        end_percentage = end_coverage.overall_percentage

        trend_direction = "stable"
        trend_magnitude = abs(end_percentage - start_percentage)

        if end_percentage > start_percentage + 1.0:
            trend_direction = "increasing"
        elif end_percentage < start_percentage - 1.0:
            trend_direction = "decreasing"

        # Find significant change points (> 2% change)
        change_points = []
        for i in range(1, len(sorted_history)):
            prev_cov = sorted_history[i - 1]
            curr_cov = sorted_history[i]
            change = abs(curr_cov.overall_percentage - prev_cov.overall_percentage)
            if change > 2.0:
                change_points.append({
                    "timestamp": curr_cov.timestamp,
                    "previous_coverage": prev_cov.overall_percentage,
                    "current_coverage": curr_cov.overall_percentage,
                    "change": curr_cov.overall_percentage - prev_cov.overall_percentage,
                })

        # Analyze file-level trends
        file_trends: dict[str, dict[str, float]] = {}
        all_files: set[str] = set()
        for cov in sorted_history:
            all_files.update(cov.file_coverage.keys())

        for filename in all_files:
            file_values = []
            for cov in sorted_history:
                if filename in cov.file_coverage:
                    file_values.append(cov.file_coverage[filename])

            if len(file_values) >= 2:
                file_start = file_values[0]
                file_end = file_values[-1]
                file_trends[filename] = {
                    "start": file_start,
                    "end": file_end,
                    "change": file_end - file_start,
                }

        return CoverageTrend(
            start_coverage=start_coverage,
            end_coverage=end_coverage,
            change_points=change_points,
            trend_direction=trend_direction,
            trend_magnitude=trend_magnitude,
            file_trends=file_trends,
        )

    def get_latest_coverage(self) -> CoverageStats | None:
        """Get the latest coverage data from available files.

        Returns:
            Latest coverage stats or None if no coverage files found
        """
        coverage_files = self.find_coverage_files()
        if not coverage_files:
            return None

        latest_coverage = None
        latest_timestamp = datetime.min.replace(tzinfo=timezone.utc)

        for file_path in coverage_files:
            try:
                if file_path.suffix == ".xml":
                    coverage = self.parse_coverage_xml(file_path)
                elif file_path.name.startswith(".coverage"):
                    coverage = self.parse_coverage_db(file_path)
                else:
                    continue

                if coverage.timestamp > latest_timestamp:
                    latest_timestamp = coverage.timestamp
                    latest_coverage = coverage

            except Exception as e:
                logger.warning("Failed to parse coverage file %s: %s", file_path, e)
                continue

        return latest_coverage

    def get_coverage_history(self, max_files: int = 10) -> list[CoverageStats]:
        """Get coverage history from multiple coverage files.

        Args:
            max_files: Maximum number of historical files to analyze

        Returns:
            List of coverage stats in chronological order
        """
        coverage_files = self.find_coverage_files()
        if not coverage_files:
            return []

        # Limit to recent files to avoid performance issues
        recent_files = sorted(coverage_files, key=lambda x: x.stat().st_mtime, reverse=True)[
            :max_files
        ]

        coverage_history = []
        for file_path in recent_files:
            try:
                if file_path.suffix == ".xml":
                    coverage = self.parse_coverage_xml(file_path)
                elif file_path.name.startswith(".coverage"):
                    coverage = self.parse_coverage_db(file_path)
                else:
                    continue

                coverage_history.append(coverage)

            except Exception as e:
                logger.warning("Failed to parse coverage file %s: %s", file_path, e)
                continue

        # Sort by timestamp
        return sorted(coverage_history, key=lambda x: x.timestamp)
