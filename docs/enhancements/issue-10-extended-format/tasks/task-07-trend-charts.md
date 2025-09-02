# Task 07: Trend Analysis Charts

## Overview

Implement specialized trend visualization capabilities for displaying velocity changes, quality metrics evolution, and other time-series data using ASCII line charts and trend indicators.

## Scope

### Core Components
1. **TrendRenderer** - Specialized trend chart generator
2. **VelocityTrendChart** - Commit velocity over time visualization
3. **QualityTrendChart** - Quality metrics progression charts
4. **TrendlineCalculation** - Statistical trend analysis
5. **TimeAxisFormatting** - Time period labeling and scaling

### Dependencies
- **Task 05**: ASCII Chart Rendering Engine (base ChartRenderer)

### Deliverables
1. `src/beaconled/visualization/trend_renderer.py`
2. Enhanced `src/beaconled/visualization/chart_renderer.py`
3. `tests/unit/visualization/test_trend_renderer.py`
4. Trend chart examples and documentation

## Technical Specifications

### TrendRenderer Class
```python
class TrendRenderer:
    """Specialized renderer for trend and time-series visualizations."""

    def __init__(self, width: int = 60, height: int = 15):
        self.width = width
        self.height = height
        self.trend_chars = {'up': '/', 'down': '\\', 'flat': '-', 'point': '*'}

    def render_velocity_trend(self, data: VelocityTrends) -> str:
        """Render commit velocity trend chart."""

    def render_quality_trend(self, data: List[Tuple[datetime, float]],
                           title: str = "Quality Trend") -> str:
        """Render quality metrics over time."""

    def render_timeline_chart(self, data: Dict[str, float],
                            title: str = "") -> str:
        """Render generic timeline chart."""
```

### Sample Trend Chart Output
```
📈 Commit Velocity Trend (Last 12 Weeks):

Commits/Day
12 |
   |     *
10 |    * *
   |   *   *
 8 |  *     *
   | *       *
 6 |*         *
   |           *
 4 |            **
   |              *
 2 |               *
   +----------------*--
   W1  W3  W5  W7  W9  W11

Trend: Declining (-15% over period)
Current: 3.2 commits/day (below 6-week average of 4.8)

📊 Quality Evolution (Last 6 Months):

Quality Score
10 |              **
   |             *  *
 8 |           **    *
   |          *
 6 |        **
   |       *
 4 |     **
   |   **
 2 | **
   +------------------
   Jan  Feb  Mar  Apr  May  Jun

Trend: Improving (+22% over period)
Peak: 9.1 (May), Current: 8.7 (Good)
```

## Implementation Guide

### Step 1: Extend ChartRenderer
```bash
cd ../beacon-task-07-trend-charts
# Extend existing chart renderer with trend capabilities
```

### Step 2: Implement Time-Series Processing
```python
def _normalize_time_series(self, data: List[Tuple[datetime, float]]) -> List[Tuple[int, float]]:
    """Convert datetime series to chart coordinates."""
    if not data:
        return []

    # Sort by date
    sorted_data = sorted(data, key=lambda x: x[0])

    # Map to chart coordinates
    min_date = sorted_data[0][0]
    max_date = sorted_data[-1][0]
    date_range = (max_date - min_date).days

    normalized = []
    for date, value in sorted_data:
        days_from_start = (date - min_date).days
        x_coord = int((days_from_start / date_range) * (self.width - 10))  # Leave space for labels
        normalized.append((x_coord, value))

    return normalized

def _scale_values(self, values: List[float]) -> List[int]:
    """Scale values to fit chart height."""
    if not values:
        return []

    min_val, max_val = min(values), max(values)
    if min_val == max_val:
        return [self.height // 2] * len(values)

    scaled = []
    for value in values:
        normalized = (value - min_val) / (max_val - min_val)
        y_coord = int(normalized * (self.height - 1))
        scaled.append(self.height - 1 - y_coord)  # Invert Y-axis

    return scaled
```

### Step 3: Trend Line Generation
```python
def _generate_trend_line(self, points: List[Tuple[int, int]]) -> List[str]:
    """Generate ASCII art trend line connecting points."""
    if len(points) < 2:
        return []

    chart_lines = [' ' * self.width for _ in range(self.height)]

    # Plot points
    for x, y in points:
        if 0 <= x < self.width and 0 <= y < self.height:
            chart_lines[y] = chart_lines[y][:x] + '*' + chart_lines[y][x+1:]

    # Connect points with trend characters
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        self._draw_line_segment(chart_lines, x1, y1, x2, y2)

    return chart_lines

def _draw_line_segment(self, chart_lines: List[str], x1: int, y1: int, x2: int, y2: int):
    """Draw line segment between two points."""
    if x2 == x1:
        return  # Vertical line, skip

    # Simple line drawing using slope
    dx = x2 - x1
    dy = y2 - y1
    slope = dy / dx if dx != 0 else 0

    for x in range(min(x1, x2) + 1, max(x1, x2)):
        if 0 <= x < self.width:
            y = int(y1 + slope * (x - x1))
            if 0 <= y < self.height:
                if slope > 0.3:
                    char = '/'
                elif slope < -0.3:
                    char = '\\'
                else:
                    char = '-'
                chart_lines[y] = chart_lines[y][:x] + char + chart_lines[y][x+1:]
```

### Step 4: Velocity Trend Specialization
```python
def render_velocity_trend(self, data: VelocityTrends) -> str:
    """Render commit velocity trend chart."""
    # Convert VelocityTrends data to time series
    time_series = []
    for date_str, velocity in data.daily_velocity.items():
        date = datetime.strptime(date_str, "%Y-%m-%d")
        time_series.append((date, velocity))

    # Calculate trend statistics
    trend_direction = data.trend_direction
    trend_emoji = "📈" if trend_direction == "increasing" else "📉" if trend_direction == "decreasing" else "➡️"

    # Generate chart
    chart = self.render_timeline_chart(
        {date.strftime("%W"): vel for date, vel in time_series},
        f"{trend_emoji} Commit Velocity Trend"
    )

    # Add trend summary
    current_velocity = time_series[-1][1] if time_series else 0
    peak_date, peak_velocity = data.peak_velocity

    summary = [
        "",
        f"Trend: {trend_direction.title()} ({'↗️' if trend_direction == 'increasing' else '↘️' if trend_direction == 'decreasing' else '→'})",
        f"Current: {current_velocity:.1f} commits/day",
        f"Peak: {peak_velocity:.1f} commits/day ({peak_date})",
        f"Average: {data.weekly_average:.1f} commits/day"
    ]

    return chart + '\n' + '\n'.join(summary)
```

### Step 5: Axis Labels and Legends
```python
def _generate_y_axis_labels(self, min_val: float, max_val: float) -> List[str]:
    """Generate Y-axis labels for value range."""
    labels = []
    step = (max_val - min_val) / (self.height - 1) if max_val != min_val else 1

    for i in range(self.height):
        value = max_val - (i * step)  # Top to bottom
        labels.append(f"{value:>3.0f}")

    return labels

def _generate_time_labels(self, time_points: List[datetime], max_labels: int = 8) -> List[str]:
    """Generate time axis labels."""
    if not time_points:
        return []

    # Select representative time points
    if len(time_points) <= max_labels:
        return [tp.strftime("%b") for tp in time_points]

    step = len(time_points) // max_labels
    selected = time_points[::step][:max_labels]
    return [tp.strftime("%b") for tp in selected]
```

## Acceptance Criteria

### Functional Requirements
- [ ] Render commit velocity trends with time axis
- [ ] Display quality metric evolution charts
- [ ] Generate trend lines connecting data points
- [ ] Calculate and display trend statistics
- [ ] Support configurable chart dimensions

### Technical Requirements
- [ ] 90%+ test coverage
- [ ] Type hints for all public interfaces
- [ ] Performance: < 150ms for typical trend charts
- [ ] Memory efficient chart generation
- [ ] Extends existing ChartRenderer cleanly

### Visual Requirements
- [ ] Clear trend lines with appropriate ASCII characters
- [ ] Readable time axis labels
- [ ] Proper value scaling and axis labels
- [ ] Trend direction indicators and summaries

## Estimated Timeline

- **Day 1**: Extend ChartRenderer, basic timeline chart
- **Day 2**: Time-series processing and scaling algorithms
- **Day 3**: Trend line generation and ASCII art
- **Day 4**: Velocity trend specialization
- **Day 5**: Quality trend charts and axis labeling

**Total: 5 days**

## Testing Scenarios

### Test Data
```python
# Velocity trend data
velocity_data = VelocityTrends(
    daily_velocity={
        "2025-01-01": 4.2,
        "2025-01-08": 5.1,
        "2025-01-15": 3.8,
        "2025-01-22": 6.2,
        "2025-01-29": 2.9
    },
    weekly_average=4.4,
    trend_direction="decreasing",
    peak_velocity=("2025-01-22", 6.2)
)

# Quality evolution data
quality_timeline = [
    (datetime(2025, 1, 1), 6.2),
    (datetime(2025, 2, 1), 6.8),
    (datetime(2025, 3, 1), 7.1),
    (datetime(2025, 4, 1), 8.3),
    (datetime(2025, 5, 1), 8.9),
    (datetime(2025, 6, 1), 8.7)
]
```

### Expected Outputs
- Trend charts show clear directional movement
- Statistical summaries provide meaningful insights
- Time axis labels are readable and appropriately spaced
- Trend lines connect data points logically

## Integration Points

### Current System
- Extends `ChartRenderer` from Task 05
- Uses `VelocityTrends` from Task 01 (Time Analytics)
- Uses quality data from Task 03 (Code Quality Assessment)

### Future Integration
- `Task 08` (Rich Formatter) will use trend charts in analytics sections
- `Task 11` (Integration) will test trend visualizations end-to-end
- Can be extended for other time-series data

## Performance Requirements

### Rendering Speed
- Small datasets (< 50 points): < 50ms
- Medium datasets (< 200 points): < 100ms
- Large datasets (< 1000 points): < 150ms

### Memory Usage
- Efficient time-series processing
- Streaming chart generation
- Minimal data structure overhead

---

**Note**: This task provides essential trend visualization capabilities building on the ASCII chart foundation. It enables users to see patterns and changes over time in their development metrics.
