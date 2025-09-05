# Task 05: ASCII Chart Rendering Engine

## Overview

Implement a comprehensive ASCII chart rendering system for terminal-based data visualization. This task creates the foundation for all chart-based outputs in the enhanced extended format.

## Scope

### Core Components
1. **ChartRenderer class** - Main chart generation engine
2. **BarChart renderer** - Horizontal and vertical bar charts
3. **LineChart renderer** - Simple line charts for trends
4. **DistributionChart renderer** - Data distribution visualization
5. **Chart utilities** - Common formatting and scaling functions

### Dependencies
- **None** - This is a foundational visualization task

### Deliverables
1. `src/beaconled/visualization/chart_renderer.py`
2. `src/beaconled/visualization/ascii_charts.py`
3. `tests/unit/visualization/test_chart_renderer.py`
4. Chart examples and documentation

## Technical Specifications

### ChartRenderer Class
```python
class ChartRenderer:
    """Renders ASCII charts and visualizations."""

    def __init__(self, width: int = 60, height: int = 20):
        self.width = width
        self.height = height

    def render_bar_chart(self, data: Dict[str, int], title: str = "") -> str:
        """Render horizontal bar chart."""

    def render_line_chart(self, data: Dict[str, float], title: str = "") -> str:
        """Render simple line chart."""

    def render_distribution(self, data: List[float], title: str = "") -> str:
        """Render data distribution chart."""
```

### Chart Types

#### Horizontal Bar Chart
```
Repository Activity by Day:
Monday    ████████████ 24 commits
Tuesday   ███████████  22 commits
Wednesday ████████████ 25 commits
Thursday  ██████████   20 commits
Friday    ███████      14 commits
Saturday  █            2 commits
Sunday    █            1 commit
```

#### Simple Line Chart
```
Commit Velocity Trend:
25 |    *
   |   * *
20 |  *   *
   | *     *
15 |*       *
   |         *
10 +----------*---
   Jan  Feb  Mar
```

#### Distribution Chart
```
Lines Changed Distribution:
   0-10   |████████████████████ 80%
  11-50   |████ 16%
  51-100  |█ 3%
  100+    |█ 1%
```

## Implementation Guide

### Step 1: Create Module Structure
```bash
cd ../beacon-task-05-ascii-charts
mkdir -p src/beaconled/visualization
touch src/beaconled/visualization/__init__.py
touch src/beaconled/visualization/chart_renderer.py
touch src/beaconled/visualization/ascii_charts.py
```

### Step 2: Implement Core Components

#### Chart Scaling and Utilities
```python
def scale_data(values: List[float], max_width: int) -> List[int]:
    """Scale numerical values to fit chart width."""

def format_bar(value: int, max_value: int, width: int, char: str = '█') -> str:
    """Create ASCII bar of appropriate length."""

def truncate_label(label: str, max_length: int) -> str:
    """Truncate labels to fit chart formatting."""
```

#### Bar Chart Implementation
- Support both horizontal and vertical orientations
- Handle varying data types (int, float)
- Auto-scale to fit terminal width
- Support custom bar characters

#### Line Chart Implementation
- Simple point-to-point line rendering
- ASCII approximation of curves
- Axis labeling and scaling
- Grid lines for readability

### Step 3: Terminal Compatibility
- Handle different terminal widths
- Graceful degradation for narrow terminals
- Unicode vs ASCII character fallbacks
- Color support detection

### Step 4: Testing Strategy
- Unit tests for each chart type
- Edge cases: empty data, single data point
- Different terminal widths (40, 80, 120 chars)
- Character encoding compatibility

## Acceptance Criteria

### Functional Requirements
- [x] Render horizontal bar charts with proper scaling
- [x] Generate simple line charts for trend data
- [x] Create distribution charts for data analysis
- [x] Handle empty datasets gracefully
- [x] Support custom chart dimensions

### Technical Requirements
- [x] 90%+ test coverage
- [x] Type hints for all public interfaces
- [x] Docstrings with usage examples
- [x] Performance: < 100ms for typical datasets
- [x] Memory efficient rendering

### Visual Requirements
- [x] Charts render correctly in 80-character terminals
- [x] Proper alignment and spacing
- [x] Clear labels and legends
- [x] Consistent visual style across chart types

## Estimated Timeline

- **Day 1**: Module structure, basic bar chart renderer
- **Day 2**: Line chart implementation
- **Day 3**: Distribution chart and scaling utilities
- **Day 4**: Terminal compatibility and character handling
- **Day 5**: Edge case handling and optimization
- **Day 6**: Testing and documentation

**Total: 6 days**

## Testing Scenarios

### Chart Types Testing
```python
# Bar chart with various data sizes
data = {"A": 10, "B": 25, "C": 15, "D": 30}
chart = renderer.render_bar_chart(data, "Sample Data")

# Line chart with trend data
trend_data = {"Jan": 10.5, "Feb": 15.2, "Mar": 12.8, "Apr": 18.1}
line_chart = renderer.render_line_chart(trend_data, "Monthly Trends")

# Distribution with percentages
distribution = [1, 5, 10, 25, 50, 75, 90, 95, 99]
dist_chart = renderer.render_distribution(distribution, "Percentiles")
```

### Edge Cases
- Empty data: `{}`
- Single data point: `{"only": 42}`
- Very long labels: `{"Very_Long_Label_That_Exceeds_Width": 10}`
- Large values: `{"item": 999999}`
- Negative values: `{"loss": -50}`

### Terminal Compatibility
- Test on different widths: 40, 60, 80, 120, 160 characters
- Unicode vs ASCII character support
- Color terminal vs monochrome

## Integration Points

### Current System
- Independent module with no external dependencies
- Provides charts for any data visualization needs

### Future Integration
- `Task 06` (Heatmap Visualization) will extend this renderer
- `Task 07` (Trend Analysis) will use line charts
- `Task 08` (Rich Formatter) will consume all chart types

## Performance Requirements

### Rendering Speed
- Small datasets (< 20 items): < 10ms
- Medium datasets (< 100 items): < 50ms
- Large datasets (< 1000 items): < 100ms

### Memory Usage
- Efficient string building
- No persistent chart storage
- Streaming output generation

---

**Note**: This task provides the foundation for all ASCII visualization in the enhanced extended format. It has no dependencies and can start immediately.
