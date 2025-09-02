# Task 08: Rich Output Formatter

## Overview

Enhance the existing ExtendedFormatter to integrate all analytics components and chart rendering capabilities. This task transforms the basic extended output into a comprehensive analytics dashboard with rich visualizations.

## Scope

### Core Components
1. **Enhanced ExtendedFormatter** - Main formatter with analytics integration
2. **AnalyticsEngine integration** - Coordinate all analytics processing
3. **Chart integration** - Embed ASCII charts in output
4. **Configuration system** - Flexible formatting options
5. **Section-based rendering** - Modular output organization

### Dependencies
- **Task 01**: Time-Based Analytics (TimeAnalyzer)
- **Task 02**: Team Collaboration Metrics (TeamAnalyzer)
- **Task 03**: Code Quality Assessment (QualityAnalyzer)
- **Task 05**: ASCII Chart Rendering (ChartRenderer)

### Deliverables
1. Enhanced `src/beaconled/formatters/extended.py`
2. `src/beaconled/analytics/engine.py` (AnalyticsEngine)
3. `tests/unit/formatters/test_enhanced_extended_formatter.py`
4. Integration tests and examples

## Technical Specifications

### Enhanced ExtendedFormatter
```python
class ExtendedFormatter(BaseFormatter):
    """Enhanced extended formatter with rich analytics."""

    def __init__(self, config: FormatterConfig = None):
        super().__init__()
        self.config = config or FormatterConfig()
        self.analytics_engine = AnalyticsEngine(self.config.analytics_config)
        self.chart_renderer = ChartRenderer(self.config.chart_width)

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with enhanced analytics."""
        # Generate comprehensive analytics
        analytics = self.analytics_engine.analyze(stats)

        # Render each section
        sections = []
        sections.append(self._render_overview_section(stats, analytics))
        sections.append(self._render_time_analytics_section(analytics.time_analytics))
        sections.append(self._render_team_analytics_section(analytics.team_analytics))
        sections.append(self._render_quality_section(analytics.quality_analytics))

        return '\n\n'.join(sections)
```

### AnalyticsEngine Integration
```python
class AnalyticsEngine:
    """Central analytics processing engine."""

    def __init__(self, config: AnalyticsConfig):
        self.time_analyzer = TimeAnalyzer(config.time_config)
        self.team_analyzer = TeamAnalyzer(config.team_config)
        self.quality_analyzer = QualityAnalyzer(config.quality_config)

    def analyze(self, range_stats: RangeStats) -> EnhancedAnalytics:
        """Generate comprehensive analytics."""
        return EnhancedAnalytics(
            time_analytics=self.time_analyzer.analyze(range_stats),
            team_analytics=self.team_analyzer.analyze(range_stats),
            quality_analytics=self.quality_analyzer.analyze(range_stats)
        )
```

### Sample Enhanced Output
```
📊 Range Analysis: 2025-01-01 to 2025-08-20 (232 days)

📈 Activity Overview:
  • Total Commits: 1,247 (5.4/day)
  • Active Days: 156 (67% of period)
  • Bus Factor: 3 (top 3 authors made 85% of changes)

👥 Contributors (5 total):
  • alice (42%) - 524 commits, +12,456/-3,214
  • bob (31%) - 387 commits, +8,921/-2,145
  • charlie (12%) - 150 commits, +3,456/-1,234

📅 Activity Heatmap:
  Mon: ████████████ 24%
  Tue: ███████████ 22%
  Wed: ████████████ 25%
  Thu: ██████████ 20%
  Fri: ███████ 14%

📊 Velocity Trend:
25 |    *
   |   * *
20 |  *   *
   | *     *
15 |*       *
   |         *
10 +----------*---
   Jan  Feb  Mar

⚠️ Risk Indicators:
  • High Churn: src/api/endpoints.py (changed 12 times)
  • Large PRs: 3 PRs > 500 lines
  • Busy Files: 5 files changed by only 1 developer
```

## Implementation Guide

### Step 1: Analyze Current ExtendedFormatter
```bash
cd ../beacon-task-08-rich-formatter
# Study existing implementation
cat src/beaconled/formatters/extended.py
```

### Step 2: Create AnalyticsEngine
```python
# src/beaconled/analytics/engine.py
from .time_analyzer import TimeAnalyzer
from .team_analyzer import TeamAnalyzer
from .quality_analyzer import QualityAnalyzer

class AnalyticsEngine:
    """Coordinates all analytics processing."""
    # Implementation details...
```

### Step 3: Enhance ExtendedFormatter
- Integrate AnalyticsEngine
- Add chart rendering capabilities
- Implement section-based output
- Maintain backward compatibility

### Step 4: Configuration System
```python
@dataclass
class FormatterConfig:
    """Configuration for enhanced formatter."""
    chart_width: int = 60
    use_emoji: bool = True
    analytics_config: AnalyticsConfig = field(default_factory=AnalyticsConfig)

@dataclass
class AnalyticsConfig:
    """Configuration for analytics engine."""
    time_config: TimeAnalyzerConfig = field(default_factory=TimeAnalyzerConfig)
    team_config: TeamAnalyzerConfig = field(default_factory=TeamAnalyzerConfig)
    quality_config: QualityAnalyzerConfig = field(default_factory=QualityAnalyzerConfig)
```

### Step 5: Section Rendering Methods
```python
def _render_overview_section(self, stats: RangeStats, analytics: EnhancedAnalytics) -> str:
    """Render overview with key metrics."""

def _render_time_analytics_section(self, time_analytics: TimeAnalytics) -> str:
    """Render time-based analytics with charts."""

def _render_team_analytics_section(self, team_analytics: TeamAnalytics) -> str:
    """Render team collaboration insights."""

def _render_quality_section(self, quality_analytics: QualityAnalytics) -> str:
    """Render code quality metrics."""
```

## Acceptance Criteria

### Functional Requirements
- [ ] Integrate all analytics components seamlessly
- [ ] Generate comprehensive enhanced output format
- [ ] Embed ASCII charts in appropriate sections
- [ ] Maintain backward compatibility with existing extended format
- [ ] Support configurable output sections

### Technical Requirements
- [ ] 90%+ test coverage including integration tests
- [ ] Type hints for all new interfaces
- [ ] Performance: < 5 seconds for 1000 commits
- [ ] Memory efficient: streaming output generation
- [ ] Error handling for missing analytics data

### Integration Requirements
- [ ] Works with existing CLI without changes
- [ ] Integrates with all dependency tasks (1, 2, 3, 5)
- [ ] Provides foundation for Task 09 (Section Renderers)
- [ ] Configurable through environment or config files

## Estimated Timeline

- **Day 1**: Analyze existing formatter, design integration approach
- **Day 2**: Create AnalyticsEngine and basic integration
- **Day 3**: Implement time analytics section with charts
- **Day 4**: Add team analytics and quality sections
- **Day 5**: Configuration system and backward compatibility
- **Day 6**: Integration testing and error handling
- **Day 7**: Performance optimization and documentation

**Total: 7 days**

## Testing Scenarios

### Integration Testing
```python
# Test complete analytics pipeline
range_stats = create_test_range_stats(1000_commits=True)
formatter = ExtendedFormatter()
output = formatter.format_range_stats(range_stats)

# Verify all sections are present
assert "📈 Activity Overview:" in output
assert "👥 Contributors" in output
assert "📅 Activity Heatmap:" in output
assert "⚠️ Risk Indicators:" in output
```

### Backward Compatibility
```python
# Ensure existing functionality still works
old_stats = create_minimal_range_stats()
output = formatter.format_range_stats(old_stats)
# Should not crash, should provide basic analytics
```

### Error Handling
```python
# Test with missing analytics data
incomplete_stats = RangeStats(commits=[])
output = formatter.format_range_stats(incomplete_stats)
# Should handle gracefully, show appropriate messages
```

### Performance Testing
```python
# Large dataset performance
large_stats = create_test_range_stats(commits=10000)
start_time = time.time()
output = formatter.format_range_stats(large_stats)
duration = time.time() - start_time
assert duration < 5.0  # Must complete within 5 seconds
```

## Integration Points

### Current System
- Enhances existing `ExtendedFormatter` class
- Uses existing `RangeStats` and `CommitStats` models
- Maintains CLI compatibility

### Dependency Integration
- **TimeAnalyzer**: Provides velocity trends and activity patterns
- **TeamAnalyzer**: Supplies collaboration metrics
- **QualityAnalyzer**: Delivers code quality insights
- **ChartRenderer**: Generates all ASCII visualizations

### Future Integration
- **Task 09**: Will refactor sections into dedicated renderers
- **Task 10**: Will enhance with emojis and colors
- **Task 11**: Integration testing and optimization

## Performance Requirements

### Analytics Processing
- 100 commits: < 500ms total processing
- 1000 commits: < 3 seconds total processing
- 10000 commits: < 10 seconds total processing

### Output Generation
- Chart rendering: < 100ms per chart
- Section formatting: < 50ms per section
- Complete output: < 1 second after analytics complete

### Memory Usage
- Stream processing where possible
- Efficient string building
- Release analytics objects after use

---

**Note**: This task brings together all the core analytics components into a cohesive, powerful output format. It requires coordination with multiple dependency tasks but provides the foundation for the final enhanced experience.
