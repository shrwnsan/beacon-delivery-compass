# Analytics Module

This module provides advanced analytics capabilities for the BeaconLED tool's enhanced extended format.

## Components

### TimeAnalyzer
The main analytics processor that generates comprehensive time-based insights from commit data.

**Features:**
- **Velocity Trends**: Analyzes commit frequency over time with trend detection
- **Activity Heatmaps**: Maps activity patterns by day of week and hour
- **Peak Period Detection**: Identifies periods of high activity using statistical thresholds
- **Bus Factor Analysis**: Calculates team risk based on contributor concentration

### Data Models
- `VelocityTrends`: Commit velocity analysis with trend direction and peak identification
- `ActivityHeatmap`: Activity patterns by day and hour with peak detection
- `BusFactor`: Contributor concentration and risk levels
- `TimeAnalytics`: Container for all time-based analysis results

## Usage

```python
from beaconled.analytics import TimeAnalyzer, TimeAnalyzerConfig
from beaconled.core.models import RangeStats

# Configure analyzer
config = TimeAnalyzerConfig(
    velocity_window_days=7,
    peak_threshold=1.5,
    bus_factor_threshold=0.5
)

# Create analyzer
analyzer = TimeAnalyzer(config)

# Analyze commit data
range_stats = RangeStats(...)  # Your commit data
results = analyzer.analyze(range_stats)

# Access results
print(f"Weekly average: {results.velocity_trends.weekly_average}")
print(f"Peak day: {results.activity_heatmap.peak_day}")
print(f"Bus factor: {results.bus_factor.factor}")
```

## Configuration

- `velocity_window_days`: Days to use for rolling velocity calculations (default: 7)
- `peak_threshold`: Standard deviations above mean for peak detection (default: 1.5)
- `bus_factor_threshold`: Percentage threshold for bus factor calculation (default: 0.5)

## Testing

Run tests with:
```bash
pytest tests/unit/analytics/test_time_analyzer.py
```

## Performance

- Designed to handle large repositories efficiently
- Uses streaming processing for memory efficiency
- Typical performance: < 1 second for 1000 commits
