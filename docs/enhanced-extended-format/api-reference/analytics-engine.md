# AnalyticsEngine API Reference

## Class: AnalyticsEngine

Integrated analytics engine that coordinates all analytics components.

### Constructor

```python
AnalyticsEngine()
```

**Description:**
Initializes the analytics engine with all component analyzers and caching mechanism.

### Methods

#### analyze(range_stats: RangeStats) -> dict

Perform comprehensive analysis on range statistics.

**Parameters:**
- `range_stats`: The range statistics to analyze

**Returns:**
- `dict`: Dictionary containing all analytics results with keys:
  - `"time"`: Time-based analytics results
  - `"collaboration"`: Team collaboration analytics results

**Example:**
```python
engine = AnalyticsEngine()
analytics = engine.analyze(range_stats)
time_analytics = analytics["time"]
collaboration_analytics = analytics["collaboration"]
```

### Caching

The AnalyticsEngine implements caching to optimize performance for repeated analyses:

- Caching is based on commit count and date range
- Cache size is limited to 100 entries to prevent memory issues
- Cached results are automatically invalidated when cache size limit is reached

## Class: EnhancedExtendedSystem

Integrated system for enhanced extended format that coordinates the full pipeline.

### Constructor

```python
EnhancedExtendedSystem()
```

**Description:**
Initializes the enhanced extended system with analytics engine and formatting components.

### Attributes

- `analytics_engine` (AnalyticsEngine): The analytics engine for processing repository data
- `chart_renderer` (ChartRenderer | None): Chart rendering component (future implementation)
- `heatmap_renderer` (HeatmapRenderer | None): Heatmap rendering component (future implementation)
- `extended_formatter` (RichFormatter | None): Formatting component for output

### Methods

#### analyze_and_format(range_stats: RangeStats) -> str

Complete analysis and formatting pipeline.

**Parameters:**
- `range_stats`: The range statistics to analyze and format

**Returns:**
- `str`: Formatted string with enhanced analytics

**Example:**
```python
system = EnhancedExtendedSystem()
result = system.analyze_and_format(range_stats)
print(result)
```
