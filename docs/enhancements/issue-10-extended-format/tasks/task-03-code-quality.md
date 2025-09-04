# Task 03: Code Quality Assessment

## Overview

Implement comprehensive code quality metrics analysis for the enhanced extended format. This task analyzes code churn patterns, complexity trends, identifies large/risky changes, and tracks quality evolution over time.

## Scope

### Core Components
1. **QualityAnalyzer class** - Main quality assessment processor
2. **ChurnMetrics** - Code churn and stability analysis
3. **ComplexityTrends** - File complexity evolution tracking
4. **LargeChange detection** - Unusually large commits identification
5. **RefactoringPatterns** - Code improvement pattern recognition

### Dependencies
- **None** - This is a foundational task

### Deliverables
1. `src/beaconled/analytics/quality_analyzer.py`
2. Quality-related models in `src/beaconled/analytics/models.py`
3. `tests/unit/analytics/test_quality_analyzer.py`
4. Documentation and examples

## Technical Specifications

### QualityAnalyzer Class
```python
class QualityAnalyzer:
    """Analyzes code quality metrics and change patterns."""

    def __init__(self, config: QualityAnalyzerConfig):
        self.churn_threshold = config.churn_threshold
        self.large_change_threshold = config.large_change_threshold
        self.complexity_window_days = config.complexity_window_days

    def analyze(self, range_stats: RangeStats) -> QualityAnalytics:
        """Generate comprehensive quality analytics."""
        return QualityAnalytics(
            churn_metrics=self._calculate_churn_metrics(range_stats.commits),
            complexity_trends=self._analyze_complexity_trends(range_stats.commits),
            large_changes=self._identify_large_changes(range_stats.commits),
            refactoring_patterns=self._detect_refactoring(range_stats.commits),
            quality_score=self._calculate_quality_score(range_stats)
        )
```

### Data Models
```python
@dataclass
class ChurnMetrics:
    """Code churn analysis and stability metrics."""
    churn_ratio: float  # deleted_lines / (added_lines + deleted_lines)
    high_churn_files: List[Tuple[str, float]]  # (file, churn_ratio)
    stability_score: float  # Lower churn = higher stability
    churn_trend: str  # 'improving', 'degrading', 'stable'
    hotspot_files: List[str]  # Files changed frequently

@dataclass
class ComplexityTrends:
    """File complexity evolution over time."""
    file_complexity_changes: Dict[str, List[Tuple[datetime, int]]]  # file -> [(date, complexity)]
    complexity_growth: Dict[str, float]  # file -> growth_rate
    complexity_hotspots: List[Tuple[str, int]]  # (file, current_complexity)
    average_complexity_trend: str  # 'increasing', 'decreasing', 'stable'

@dataclass
class LargeChange:
    """Represents an unusually large change."""
    commit_hash: str
    author: str
    date: datetime
    files_changed: int
    lines_added: int
    lines_deleted: int
    risk_score: float
    change_type: str  # 'feature', 'refactor', 'fix', 'unknown'

@dataclass
class RefactoringPatterns:
    """Detected refactoring and improvement patterns."""
    refactoring_commits: List[str]  # Commits identified as refactoring
    improvement_trend: str  # 'improving', 'degrading', 'stable'
    test_coverage_changes: Dict[str, float]  # file -> coverage_delta
    documentation_changes: int  # Net documentation line changes

@dataclass
class QualityAnalytics:
    """Complete code quality analysis."""
    churn_metrics: ChurnMetrics
    complexity_trends: ComplexityTrends
    large_changes: List[LargeChange]
    refactoring_patterns: RefactoringPatterns
    quality_score: float
    quality_trends: Dict[str, float]
```

## Implementation Guide

### Step 1: Create Module Structure
```bash
cd ../beacon-task-03-code-quality
mkdir -p src/beaconled/analytics
touch src/beaconled/analytics/quality_analyzer.py
```

### Step 2: Implement Core Analytics

#### Churn Metrics Calculation
```python
def _calculate_churn_metrics(self, commits: List[CommitStats]) -> ChurnMetrics:
    """Calculate code churn ratios and stability metrics."""
    # For each file, calculate:
    # - Total lines added vs deleted over time
    # - Frequency of changes (change hotspots)
    # - Churn ratio = deleted / (added + deleted)
    # - Stability score based on change frequency and churn
```

#### Complexity Trends Analysis
```python
def _analyze_complexity_trends(self, commits: List[CommitStats]) -> ComplexityTrends:
    """Track complexity evolution using simple heuristics."""
    # Estimate complexity using:
    # - File size changes over time
    # - Number of functions/classes (from diffs)
    # - Cyclomatic complexity approximation
    # - Nested structure depth changes
```

#### Large Change Detection
```python
def _identify_large_changes(self, commits: List[CommitStats]) -> List[LargeChange]:
    """Identify commits with unusually large changes."""
    # Flag commits that are statistical outliers:
    # - Files changed > 95th percentile
    # - Lines changed > 95th percentile
    # - Combination of both (compound risk)
    # - Classify change type based on commit message
```

#### Refactoring Pattern Detection
```python
def _detect_refactoring(self, commits: List[CommitStats]) -> RefactoringPatterns:
    """Identify refactoring and quality improvement patterns."""
    # Detect patterns like:
    # - High line churn with neutral net change (refactoring)
    # - Test file additions/improvements
    # - Documentation updates
    # - Code organization changes (file moves/renames)
```

### Step 3: Add Configuration
```python
@dataclass
class QualityAnalyzerConfig:
    churn_threshold: float = 0.7  # High churn = >70% deleted/total
    large_change_threshold: int = 500  # Lines changed
    complexity_window_days: int = 90  # Window for trend analysis
    refactoring_keywords: List[str] = field(default_factory=lambda: [
        'refactor', 'cleanup', 'reorganize', 'simplify', 'optimize'
    ])
```

### Step 4: Testing Strategy
- Unit tests for each metric calculation
- Mock commit data with known quality patterns
- Edge cases: empty files, massive changes, etc.
- Performance tests with large repositories

## Acceptance Criteria

### Functional Requirements
- [ ] Calculate meaningful churn ratios and stability scores
- [ ] Track complexity trends over time periods
- [ ] Identify large/risky changes with risk scoring
- [ ] Detect refactoring patterns and quality improvements
- [ ] Generate overall quality scores and trends

### Technical Requirements
- [ ] 90%+ test coverage
- [ ] Type hints for all public interfaces
- [ ] Docstrings for all public methods
- [ ] Performance: < 3 seconds for 1000 commits
- [ ] Memory efficient processing

### Analysis Requirements
- [ ] Churn calculations account for file type differences
- [ ] Complexity trends use meaningful approximations
- [ ] Large change detection uses statistical methods
- [ ] Quality scores are normalized and interpretable

## Estimated Timeline

- **Day 1**: Module structure, basic churn calculation
- **Day 2**: Complexity trend analysis implementation
- **Day 3**: Large change detection and risk scoring
- **Day 4**: Refactoring pattern recognition
- **Day 5**: Quality score calculation and normalization
- **Day 6**: Edge case handling and optimization
- **Day 7**: Testing, documentation, and integration prep
- **Day 8**: Performance tuning and final validation

**Total: 8 days**

## Testing Scenarios

### Test Data Requirements
```python
# High churn scenario
commits_high_churn = create_commits_with_pattern([
    ("file.py", +100, -80),  # High churn ratio
    ("file.py", +50, -60),
    ("file.py", +200, -150),
])

# Large change scenario
commits_large_change = [
    create_commit("massive_refactor", files_changed=25, lines_added=2000, lines_deleted=1500),
    create_commit("normal_change", files_changed=3, lines_added=50, lines_deleted=10),
]

# Refactoring pattern
commits_refactoring = [
    create_commit("refactor: simplify auth logic", +100, -120),  # Net negative but high churn
    create_commit("add tests for auth module", +50, -0),  # Test improvements
]
```

### Expected Outcomes
- **High churn**: Files flagged as unstable, lower quality scores
- **Large changes**: Commits flagged as high-risk, detailed analysis
- **Refactoring**: Recognized as improvement activity, positive quality impact

## Integration Points

### Current System
- Receives `RangeStats` object with commits list
- Uses existing `CommitStats` model structure
- Returns `QualityAnalytics` for formatter consumption

### Future Integration
- `Task 08` (Rich Formatter) will display quality insights
- `Task 04` (Risk Assessment) will use quality metrics
- `ChartRenderer` will visualize quality trends

## Performance Requirements

### Processing Speed
- 100 commits: < 300ms
- 1000 commits: < 3 seconds
- 5000 commits: < 15 seconds

### Memory Usage
- Efficient file change tracking
- Streaming commit processing
- Lazy evaluation of complex calculations

## Quality Metrics Examples

### Churn Analysis Output
```
Code Stability Analysis:
• Overall Churn Ratio: 0.23 (23% of changes are deletions)
• Stability Score: 7.8/10 (High stability)
• High Churn Files:
  - src/legacy/old_api.py: 0.65 churn ratio
  - config/settings.py: 0.58 churn ratio
• Change Hotspots: 3 files changed >10 times
```

### Quality Trends Output
```
Quality Evolution:
• Complexity Trend: Decreasing (-12% over period)
• Test Coverage Trend: Increasing (+15% test files)
• Documentation Trend: Improving (+230 doc lines)
• Refactoring Activity: 8 cleanup commits detected
```

---

**Note**: This task provides essential insights into code health and technical debt. It has no dependencies and can start immediately alongside other foundational tasks.
