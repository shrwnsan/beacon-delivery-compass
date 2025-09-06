# Task 06: Heatmap Visualization System

## Overview

Extend the ASCII chart rendering system with specialized heatmap visualization capabilities for activity patterns, particularly day-of-week and hour-of-day analysis from time-based analytics.

## Scope

### Core Components
1. **HeatmapRenderer** - Specialized heatmap chart generator
2. **ActivityHeatmap visualization** - Day/hour activity patterns
3. **IntensityMapping** - Color/character intensity scaling
4. **GridLayout** - Structured heatmap grid rendering
5. **LegendGeneration** - Heatmap legend and scale display

### Dependencies
- **Task 05**: ASCII Chart Rendering Engine (base ChartRenderer)

### Deliverables
1. `src/beaconled/visualization/heatmap_renderer.py`
2. Enhanced `src/beaconled/visualization/chart_renderer.py`
3. `tests/unit/visualization/test_heatmap_renderer.py`
4. Heatmap examples and documentation

## Technical Specifications

### HeatmapRenderer Class
```python
class HeatmapRenderer:
    """Specialized renderer for heatmap visualizations."""

    def __init__(self, width: int = 60):
        self.width = width
        self.intensity_chars = ['░', '▒', '▓', '█']  # Light to dark

    def render_activity_heatmap(self, data: ActivityHeatmap) -> str:
        """Render day-of-week vs hour-of-day heatmap."""

    def render_2d_heatmap(self, data: Dict[Tuple[str, str], float],
                         x_labels: List[str], y_labels: List[str],
                         title: str = "") -> str:
        """Render generic 2D heatmap."""
```

### Sample Heatmap Output
```
📅 Activity Heatmap - Commits by Day and Hour (UTC):

        00 02 04 06 08 10 12 14 16 18 20 22
Monday    ░  ░  ▒  ▒  ▓  █  █  ▓  ▒  ░  ░  ░
Tuesday   ░  ░  ░  ▒  ▓  █  █  ▓  ▓  ▒  ░  ░
Wednesday ░  ░  ▒  ▓  █  █  ▓  ▓  ▒  ░  ░  ░
Thursday  ░  ░  ░  ▒  ▓  █  █  ▓  ▒  ▒  ░  ░
Friday    ░  ░  ▒  ▒  ▓  ▓  ▓  ▒  ░  ░  ░  ░
Saturday  ░  ░  ░  ░  ░  ░  ▒  ▒  ░  ░  ░  ░
Sunday    ░  ░  ░  ░  ░  ░  ░  ▒  ░  ░  ░  ░

Legend: ░ 1-2  ▒ 3-5  ▓ 6-10  █ 11+ commits
Peak Activity: Wednesday 10:00-12:00 (15 commits)
```

## Implementation Guide

### Step 1: Extend ChartRenderer
```bash
cd ../beacon-task-06-heatmap-viz
# Extend existing chart renderer
```

### Step 2: Implement Heatmap Core Logic
```python
def _map_value_to_intensity(self, value: float, min_val: float, max_val: float) -> str:
    """Map numerical value to intensity character."""
    if max_val == min_val:
        return self.intensity_chars[0]

    normalized = (value - min_val) / (max_val - min_val)
    index = int(normalized * (len(self.intensity_chars) - 1))
    return self.intensity_chars[min(index, len(self.intensity_chars) - 1)]

def _create_grid_layout(self, data: Dict, x_labels: List[str],
                       y_labels: List[str]) -> List[List[str]]:
    """Create 2D grid with intensity characters."""
    grid = []
    values = list(data.values())
    min_val, max_val = min(values), max(values)

    for y_label in y_labels:
        row = []
        for x_label in x_labels:
            value = data.get((y_label, x_label), 0.0)
            intensity = self._map_value_to_intensity(value, min_val, max_val)
            row.append(intensity)
        grid.append(row)

    return grid
```

### Step 3: Activity Pattern Specialization
```python
def render_activity_heatmap(self, data: ActivityHeatmap) -> str:
    """Render commit activity heatmap by day and hour."""
    # Convert ActivityHeatmap data structure to 2D grid format
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = [f"{h:02d}" for h in range(0, 24, 2)]  # Every 2 hours

    # Create 2D data mapping
    heatmap_data = {}
    for day in days:
        for hour_str in hours:
            hour = int(hour_str)
            # Aggregate hourly data from ActivityHeatmap
            value = data.by_hour.get(hour, 0) + data.by_hour.get(hour + 1, 0)
            heatmap_data[(day, hour_str)] = value

    return self.render_2d_heatmap(heatmap_data, hours, days,
                                 "Activity Heatmap - Commits by Day and Hour")
```

### Step 4: Legend and Scaling
```python
def _generate_legend(self, min_val: float, max_val: float) -> List[str]:
    """Generate legend showing intensity scale."""
    legend_lines = []
    range_per_char = (max_val - min_val) / len(self.intensity_chars)

    legend_items = []
    for i, char in enumerate(self.intensity_chars):
        range_start = min_val + (i * range_per_char)
        range_end = min_val + ((i + 1) * range_per_char)
        if i == len(self.intensity_chars) - 1:
            legend_items.append(f"{char} {int(range_start)}+")
        else:
            legend_items.append(f"{char} {int(range_start)}-{int(range_end)}")

    legend_lines.append("Legend: " + "  ".join(legend_items))
    return legend_lines
```

## Acceptance Criteria

### Functional Requirements
- [x] Render day-of-week vs hour-of-day activity heatmaps
- [x] Support generic 2D heatmap visualization
- [x] Generate appropriate legends and scales
- [x] Handle various data ranges and densities
- [x] Integrate with ActivityHeatmap data model

### Technical Requirements
- [x] 90%+ test coverage
- [x] Type hints for all public interfaces
- [x] Performance: < 100ms for typical heatmaps
- [x] Memory efficient grid generation
- [x] Extends existing ChartRenderer cleanly

### Visual Requirements
- [x] Clear visual distinction between intensity levels
- [x] Proper alignment and spacing in grid
- [x] Readable labels and legends
- [x] Consistent with other chart styles

## Estimated Timeline

- **Day 1**: Extend ChartRenderer, basic 2D heatmap
- **Day 2**: Intensity mapping and character selection
- **Day 3**: Activity heatmap specialization
- **Day 4**: Legend generation and formatting

**Total: 4 days**

## Testing Scenarios

### Test Data
```python
# Activity heatmap data
activity_data = ActivityHeatmap(
    by_day_of_week={"Monday": 20, "Tuesday": 15, "Wednesday": 25, ...},
    by_hour={9: 5, 10: 12, 11: 8, 14: 15, 15: 10, ...},
    peak_day="Wednesday",
    peak_hour=10
)

# Generic 2D data
generic_data = {
    ("A", "1"): 5.0, ("A", "2"): 10.0, ("A", "3"): 15.0,
    ("B", "1"): 8.0, ("B", "2"): 12.0, ("B", "3"): 3.0,
    ("C", "1"): 20.0, ("C", "2"): 1.0, ("C", "3"): 7.0,
}
```

## Integration Points

### Current System
- Extends `ChartRenderer` from Task 05
- Uses `ActivityHeatmap` from Task 01 (Time Analytics)

### Future Integration
- `Task 08` (Rich Formatter) will use heatmaps in time analytics section
- Can be used for other 2D data visualizations (file ownership, etc.)

---

**Note**: This task provides specialized heatmap capabilities building on the foundation from Task 05. It enables rich visualization of temporal patterns.
