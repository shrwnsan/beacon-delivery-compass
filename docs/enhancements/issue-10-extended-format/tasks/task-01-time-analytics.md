# Task 01: Time-Based Analytics Implementation

## Overview

Implement comprehensive time-based analytics for the enhanced extended format. This task creates the foundation for temporal analysis including commit velocity trends, activity heatmaps, peak period identification, and bus factor calculation.

## Scope

### Core Components
1. **TimeAnalyzer class** - Main analytics processor
2. **VelocityTrends model** - Commit velocity over time
3. **ActivityHeatmap model** - Day/hour activity patterns
4. **PeakPeriod detection** - High activity identification
5. **BusFactor calculation** - Team risk assessment

### Dependencies
- **None** - This is a foundational task

### Deliverables
1. `src/beaconled/analytics/time_analyzer.py`
2. `src/beaconled/analytics/models.py` (time-related models)
3. `tests/unit/analytics/test_time_analyzer.py`
4. Documentation and examples

## Technical Specifications

### TimeAnalyzer Class
```python
class TimeAnalyzer:
    """Analyzes temporal patterns in commit data."""

    def __init__(self, config: TimeAnalyzerConfig):
        self.velocity_window_days = config.velocity_window_days
        self.peak_threshold = config.peak_threshold
        self.bus_factor_threshold = config.bus_factor_threshold

    def analyze(self, range_stats: RangeStats) -> TimeAnalytics:
        """Generate comprehensive time-based analytics."""
        return TimeAnalytics(
            velocity_trends=self._calculate_velocity_trends(range_stats.commits),
            activity_heatmap=self._generate_activity_heatmap(range_stats.commits),
            peak_periods=self._identify_peak_periods(range_stats.commits),
            bus_factor=self._calculate_bus_factor(range_stats.authors)
        )
```

### Data Models
```python
@dataclass
class VelocityTrends:
    """Commit velocity trends over time."""
    daily_velocity: Dict[str, float]  # date -> commits/day
    weekly_average: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    peak_velocity: Tuple[str, float]  # (date, velocity)

@dataclass
class ActivityHeatmap:
    """Activity patterns by day of week and hour."""
    by_day_of_week: Dict[str, int]  # Monday -> commit_count
    by_hour: Dict[int, int]  # hour -> commit_count
    peak_day: str
    peak_hour: int

@dataclass
class BusFactor:
    """Team bus factor analysis."""
    factor: int  # Number of people who do 50% of work
    key_contributors: List[Tuple[str, float]]  # (author, percentage)
    risk_level: str  # 'low', 'medium', 'high'
```

## Implementation Guide

### Step 1: Create Module Structure
```bash
cd ../beacon-task-01-time-analytics
mkdir -p src/beaconled/analytics
touch src/beaconled/analytics/__init__.py
touch src/beaconled/analytics/time_analyzer.py
touch src/beaconled/analytics/models.py
```

### Step 2: Implement Core Analytics
1. **Velocity calculation**: Rolling window analysis of commits per day
2. **Activity heatmap**: Group commits by day-of-week and hour-of-day
3. **Peak detection**: Identify periods above threshold activity
4. **Bus factor**: Calculate concentration of contributions

### Step 3: Add Configuration
```python
@dataclass
class TimeAnalyzerConfig:
    velocity_window_days: int = 7
    peak_threshold: float = 1.5  # Standard deviations above mean
    bus_factor_threshold: float = 0.5  # 50% of work
```

### Step 4: Testing Strategy
- Unit tests for each analysis method
- Edge cases: empty commits, single author, etc.
- Performance tests with large datasets
- Integration tests with RangeStats

## Acceptance Criteria

### Functional Requirements
- [ ] Calculate accurate commit velocity trends
- [ ] Generate day-of-week and hour-of-day heatmaps
- [ ] Identify peak activity periods
- [ ] Calculate team bus factor correctly
- [ ] Handle edge cases (no commits, single contributor)

### Technical Requirements
- [ ] 90%+ test coverage
- [ ] Type hints for all public interfaces
- [ ] Docstrings for all public methods
- [ ] Performance: < 1 second for 1000 commits
- [ ] Memory efficient: stream processing for large datasets

### Integration Requirements
- [ ] Integrates with existing RangeStats model
- [ ] Compatible with future ChartRenderer
- [ ] Configurable through TimeAnalyzerConfig
- [ ] No breaking changes to existing code

## Estimated Timeline

- **Day 1-2**: Module structure, basic velocity calculation
- **Day 3-4**: Activity heatmap and peak detection
- **Day 5-6**: Bus factor calculation and edge cases
- **Day 7**: Testing, documentation, integration prep

**Total: 7 days**

## Testing Scenarios

### Test Data Requirements
- Small dataset: 10 commits over 1 week
- Medium dataset: 100 commits over 1 month
- Large dataset: 1000 commits over 6 months
- Edge cases: Single commit, single author, no commits

### Performance Benchmarks
- 100 commits: < 100ms
- 1000 commits: < 1 second
- 10000 commits: < 10 seconds

## Integration Points

### Current System
- Receives `RangeStats` object with commits list
- Uses existing `CommitStats` model structure
- Returns `TimeAnalytics` for formatter consumption

### Future Integration
- `ChartRenderer` will use `VelocityTrends` for trend charts
- `ExtendedFormatter` will display all time analytics
- `RiskAssessment` may use `BusFactor` data

---

**Note**: This task is foundational and has no dependencies. It can start immediately and will unblock several downstream tasks.
