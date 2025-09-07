# TimeAnalyzer API Reference

## Class: TimeAnalyzer

Analyzes temporal patterns in commit data.

### Constructor

```python
TimeAnalyzer(config: TimeAnalyzerConfig)
```

**Parameters:**
- `config`: Configuration object with analysis parameters

### Configuration

#### TimeAnalyzerConfig

Configuration object for TimeAnalyzer.

**Attributes:**
- `velocity_window_days` (int): Number of days for rolling velocity calculation (default: 7)
- `peak_threshold` (float): Standard deviations above mean for peak detection (default: 1.5)
- `bus_factor_threshold` (float): Percentage threshold for bus factor calculation (default: 0.5)

### Methods

#### analyze(range_stats: RangeStats) -> TimeAnalytics

Generate comprehensive time-based analytics.

**Parameters:**
- `range_stats`: Repository statistics for the analysis period

**Returns:**
- `TimeAnalytics`: Complete time-based analysis results

**Example:**
```python
analyzer = TimeAnalyzer(TimeAnalyzerConfig())
result = analyzer.analyze(range_stats)
print(f"Velocity trend: {result.velocity_trends.trend_direction}")
```

### Data Models

#### TimeAnalytics

Complete time-based analysis results.

**Attributes:**
- `velocity_trends` (VelocityTrends): Commit velocity patterns over time
- `activity_heatmap` (ActivityHeatmap): Activity patterns by day and hour
- `peak_periods` (list[PeakPeriod]): Identified peak activity periods
- `bus_factor` (BusFactor): Team distribution analysis

#### VelocityTrends

Commit velocity patterns over time.

**Attributes:**
- `daily_velocity` (dict[str, int]): Commits per day
- `trend_direction` (str): Overall trend ("increasing", "decreasing", "stable")
- `average_velocity` (float): Average commits per day

#### ActivityHeatmap

Activity patterns by day and hour.

**Attributes:**
- `hourly_distribution` (dict[int, int]): Activity by hour of day (0-23)
- `daily_distribution` (dict[str, int]): Activity by day of week
- `peak_hours` (list[int]): Most active hours
- `peak_days` (list[str]): Most active days

#### PeakPeriod

Identified peak activity period.

**Attributes:**
- `start_date` (datetime): Start of peak period
- `end_date` (datetime): End of peak period
- `commit_count` (int): Number of commits during period
- `intensity` (float): Relative intensity compared to average

#### BusFactor

Team distribution analysis.

**Attributes:**
- `min_authors_needed` (int): Minimum authors needed to cover threshold
- `coverage_percentage` (float): Percentage of work covered by those authors
- `risk_level` (str): Risk assessment ("high", "medium", "low")
