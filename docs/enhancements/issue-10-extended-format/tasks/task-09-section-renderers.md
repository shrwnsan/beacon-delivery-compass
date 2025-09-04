# Task 09: Enhanced Section Renderers

## Overview

Implement modular section renderers to organize the rich analytics output into well-structured, readable sections. This task refactors the monolithic formatting approach into specialized, maintainable section components.

## Scope

### Core Components
1. **SectionRenderer base class** - Common section rendering interface
2. **TimeAnalyticsRenderer** - Time-based analytics section
3. **TeamAnalyticsRenderer** - Team collaboration section
4. **QualityAnalyticsRenderer** - Code quality section
5. **RiskAnalyticsRenderer** - Risk assessment section
6. **OverviewRenderer** - Summary overview section

### Dependencies
- **Task 08**: Rich Output Formatter (enhanced ExtendedFormatter)

### Deliverables
1. `src/beaconled/formatters/sections/` module with all renderers
2. Refactored `src/beaconled/formatters/extended.py`
3. `tests/unit/formatters/sections/` test suite
4. Section styling guide documentation

## Technical Specifications

### Base SectionRenderer Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class SectionRenderer(ABC):
    """Base class for all section renderers."""

    def __init__(self, config: SectionConfig):
        self.config = config
        self.emoji_renderer = EmojiRenderer(config.visual_config)
        self.chart_renderer = ChartRenderer(config.chart_width)

    @abstractmethod
    def render(self, data: Any) -> str:
        """Render the section with given data."""

    def _format_header(self, title: str, section_type: str) -> str:
        """Format consistent section header."""
        return self.emoji_renderer.format_section_header(title, section_type)

    def _format_metric_line(self, label: str, value: str, emoji_type: str = "") -> str:
        """Format consistent metric line."""
        emoji = self.emoji_renderer.get_metric_emoji(emoji_type) if emoji_type else ""
        return f"  • {emoji} {label}: {value}"
```

### TimeAnalyticsRenderer
```python
class TimeAnalyticsRenderer(SectionRenderer):
    """Renders time-based analytics section."""

    def render(self, analytics: TimeAnalytics) -> str:
        """Render complete time analytics section."""
        lines = []

        # Section header
        lines.append(self._format_header("Time-Based Analysis", "time_analytics"))
        lines.append("")

        # Velocity trends with chart
        lines.extend(self._render_velocity_section(analytics.velocity_trends))
        lines.append("")

        # Activity heatmap
        lines.extend(self._render_activity_section(analytics.activity_heatmap))
        lines.append("")

        # Peak periods and bus factor
        lines.extend(self._render_insights_section(analytics))

        return "\n".join(lines)

    def _render_velocity_section(self, velocity_trends: VelocityTrends) -> List[str]:
        """Render velocity trends with embedded chart."""
        lines = []

        # Velocity summary metrics
        lines.append(self._format_metric_line(
            "Average Velocity", f"{velocity_trends.weekly_average:.1f} commits/day", "velocity"
        ))
        lines.append(self._format_metric_line(
            "Trend Direction", f"{velocity_trends.trend_direction.title()}", "trend"
        ))
        lines.append(self._format_metric_line(
            "Peak Velocity", f"{velocity_trends.peak_velocity[1]:.1f} commits/day ({velocity_trends.peak_velocity[0]})", "peak"
        ))

        # Embedded velocity chart
        if self.config.show_charts:
            lines.append("")
            trend_chart = self.chart_renderer.render_velocity_trend(velocity_trends)
            lines.extend(trend_chart.split('\n'))

        return lines

    def _render_activity_section(self, activity_heatmap: ActivityHeatmap) -> List[str]:
        """Render activity patterns with heatmap."""
        lines = []

        # Activity summary
        lines.append(self._format_metric_line(
            "Peak Activity Day", activity_heatmap.peak_day, "calendar"
        ))
        lines.append(self._format_metric_line(
            "Peak Activity Hour", f"{activity_heatmap.peak_hour:02d}:00", "clock"
        ))

        # Embedded activity heatmap
        if self.config.show_charts:
            lines.append("")
            heatmap_chart = self.chart_renderer.render_activity_heatmap(activity_heatmap)
            lines.extend(heatmap_chart.split('\n'))

        return lines
```

### TeamAnalyticsRenderer
```python
class TeamAnalyticsRenderer(SectionRenderer):
    """Renders team collaboration analytics section."""

    def render(self, analytics: TeamAnalytics) -> str:
        """Render complete team analytics section."""
        lines = []

        # Section header
        lines.append(self._format_header("Team Collaboration", "team_analytics"))
        lines.append("")

        # Collaboration overview
        lines.extend(self._render_collaboration_overview(analytics))
        lines.append("")

        # Knowledge silos
        if analytics.knowledge_silos:
            lines.extend(self._render_knowledge_silos(analytics.knowledge_silos))
            lines.append("")

        # Co-authorship patterns
        lines.extend(self._render_coauthorship(analytics.co_authorship))

        return "\n".join(lines)

    def _render_collaboration_overview(self, analytics: TeamAnalytics) -> List[str]:
        """Render collaboration summary metrics."""
        lines = []

        lines.append(self._format_metric_line(
            "Collaboration Score", f"{analytics.collaboration_score:.1f}/10", "collaboration"
        ))
        lines.append(self._format_metric_line(
            "Bus Factor", f"{analytics.bus_factor} people", "bus_factor"
        ))

        # Team health metrics
        for metric, value in analytics.team_health_metrics.items():
            lines.append(self._format_metric_line(
                metric.replace('_', ' ').title(), f"{value:.1f}", "health"
            ))

        return lines

    def _render_knowledge_silos(self, silos: List[KnowledgeSilo]) -> List[str]:
        """Render knowledge silo warnings."""
        lines = []
        lines.append(f"🏝️  Knowledge Silos Detected ({len(silos)}):")

        for silo in silos[:5]:  # Show top 5 silos
            risk_emoji = "🔴" if silo.risk_level == "high" else "🟡" if silo.risk_level == "medium" else "🟢"
            lines.append(f"    {risk_emoji} {silo.path} (owned {silo.ownership_percentage:.0f}% by {silo.primary_author})")

        if len(silos) > 5:
            lines.append(f"    ... and {len(silos) - 5} more")

        return lines
```

### QualityAnalyticsRenderer
```python
class QualityAnalyticsRenderer(SectionRenderer):
    """Renders code quality analytics section."""

    def render(self, analytics: QualityAnalytics) -> str:
        """Render complete quality analytics section."""
        lines = []

        # Section header
        lines.append(self._format_header("Code Quality Analysis", "quality_analytics"))
        lines.append("")

        # Quality overview
        lines.extend(self._render_quality_overview(analytics))
        lines.append("")

        # Churn analysis
        lines.extend(self._render_churn_analysis(analytics.churn_metrics))
        lines.append("")

        # Large changes and refactoring
        lines.extend(self._render_change_patterns(analytics))

        return "\n".join(lines)

    def _render_quality_overview(self, analytics: QualityAnalytics) -> List[str]:
        """Render quality summary metrics."""
        lines = []

        quality_emoji = "🟢" if analytics.quality_score > 0.8 else "🟡" if analytics.quality_score > 0.6 else "🔴"
        lines.append(self._format_metric_line(
            "Overall Quality Score", f"{quality_emoji} {analytics.quality_score:.1f}/1.0", "quality"
        ))

        # Quality trends
        for trend_name, trend_value in analytics.quality_trends.items():
            trend_emoji = "📈" if trend_value > 0 else "📉" if trend_value < 0 else "➡️"
            lines.append(self._format_metric_line(
                trend_name.replace('_', ' ').title(), f"{trend_emoji} {trend_value:+.1%}", "trend"
            ))

        return lines

    def _render_churn_analysis(self, churn_metrics: ChurnMetrics) -> List[str]:
        """Render code churn analysis."""
        lines = []
        lines.append("📊 Code Stability Analysis:")

        stability_emoji = "🟢" if churn_metrics.stability_score > 0.8 else "🟡" if churn_metrics.stability_score > 0.6 else "🔴"
        lines.append(self._format_metric_line(
            "Stability Score", f"{stability_emoji} {churn_metrics.stability_score:.1f}/1.0", ""
        ))
        lines.append(self._format_metric_line(
            "Churn Ratio", f"{churn_metrics.churn_ratio:.2f} (lower is better)", ""
        ))

        # High churn files
        if churn_metrics.high_churn_files:
            lines.append("")
            lines.append("  ⚠️  High Churn Files:")
            for file_path, churn_ratio in churn_metrics.high_churn_files[:3]:
                lines.append(f"    • {file_path}: {churn_ratio:.2f} churn ratio")

        return lines
```

### RiskAnalyticsRenderer
```python
class RiskAnalyticsRenderer(SectionRenderer):
    """Renders risk assessment section."""

    def render(self, analytics: RiskAnalytics) -> str:
        """Render complete risk analytics section."""
        lines = []

        # Section header
        lines.append(self._format_header("Risk Assessment", "risk_assessment"))
        lines.append("")

        # Overall risk score
        lines.extend(self._render_risk_overview(analytics))
        lines.append("")

        # Top risks
        lines.extend(self._render_top_risks(analytics.top_risks))
        lines.append("")

        # Recommendations
        lines.extend(self._render_recommendations(analytics.recommendations))

        return "\n".join(lines)

    def _render_risk_overview(self, analytics: RiskAnalytics) -> List[str]:
        """Render overall risk assessment."""
        lines = []

        risk_color = "🔴" if analytics.risk_level == "critical" else "🟠" if analytics.risk_level == "high" else "🟡" if analytics.risk_level == "medium" else "🟢"
        lines.append(self._format_metric_line(
            "Overall Risk Level", f"{risk_color} {analytics.risk_level.upper()} ({analytics.overall_risk_score:.2f}/1.0)", ""
        ))

        return lines

    def _render_top_risks(self, risks: List[RiskIndicator]) -> List[str]:
        """Render top risk indicators."""
        lines = []
        lines.append("⚠️  Top Risk Factors:")

        for risk in risks[:5]:  # Show top 5 risks
            risk_emoji = self.emoji_renderer.get_risk_emoji(risk.level)
            lines.append(f"  {risk_emoji} {risk.name}: {risk.description}")

            # Show affected components if any
            if risk.affected_components:
                components = ", ".join(risk.affected_components[:3])
                if len(risk.affected_components) > 3:
                    components += f", +{len(risk.affected_components) - 3} more"
                lines.append(f"      Affects: {components}")

        return lines

    def _render_recommendations(self, recommendations: List[str]) -> List[str]:
        """Render actionable recommendations."""
        lines = []
        lines.append("💡 Recommendations:")

        for i, recommendation in enumerate(recommendations[:5], 1):
            lines.append(f"  {i}. {recommendation}")

        if len(recommendations) > 5:
            lines.append(f"  ... and {len(recommendations) - 5} more recommendations")

        return lines
```

## Implementation Guide

### Step 1: Create Section Module Structure
```bash
cd ../beacon-task-09-section-renderers
mkdir -p src/beaconled/formatters/sections
touch src/beaconled/formatters/sections/__init__.py
touch src/beaconled/formatters/sections/base.py
touch src/beaconled/formatters/sections/time_analytics.py
touch src/beaconled/formatters/sections/team_analytics.py
touch src/beaconled/formatters/sections/quality_analytics.py
touch src/beaconled/formatters/sections/risk_analytics.py
touch src/beaconled/formatters/sections/overview.py
```

### Step 2: Implement Base SectionRenderer
Create the base interface that all section renderers will implement.

### Step 3: Implement Specialized Renderers
Create each specialized renderer with its own formatting logic and chart integration.

### Step 4: Refactor ExtendedFormatter
```python
# In enhanced ExtendedFormatter
class ExtendedFormatter(BaseFormatter):
    def __init__(self, config: FormatterConfig = None):
        super().__init__()
        self.config = config or FormatterConfig()
        self.analytics_engine = AnalyticsEngine(self.config.analytics_config)

        # Initialize section renderers
        self.section_renderers = {
            'overview': OverviewRenderer(self.config.section_config),
            'time': TimeAnalyticsRenderer(self.config.section_config),
            'team': TeamAnalyticsRenderer(self.config.section_config),
            'quality': QualityAnalyticsRenderer(self.config.section_config),
            'risk': RiskAnalyticsRenderer(self.config.section_config)
        }

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with modular section rendering."""
        # Generate analytics
        analytics = self.analytics_engine.analyze(stats)

        # Render sections
        sections = []

        if self.config.show_overview:
            sections.append(self.section_renderers['overview'].render((stats, analytics)))

        if self.config.show_time_analytics:
            sections.append(self.section_renderers['time'].render(analytics.time_analytics))

        if self.config.show_team_analytics:
            sections.append(self.section_renderers['team'].render(analytics.team_analytics))

        if self.config.show_quality_analytics:
            sections.append(self.section_renderers['quality'].render(analytics.quality_analytics))

        if self.config.show_risk_analytics:
            sections.append(self.section_renderers['risk'].render(analytics.risk_analytics))

        return '\n\n'.join(sections)
```

### Step 5: Configuration System
```python
@dataclass
class SectionConfig:
    """Configuration for section renderers."""
    visual_config: VisualConfig
    chart_width: int = 60
    show_charts: bool = True
    max_items_per_section: int = 5

@dataclass
class FormatterConfig:
    """Enhanced formatter configuration."""
    section_config: SectionConfig
    show_overview: bool = True
    show_time_analytics: bool = True
    show_team_analytics: bool = True
    show_quality_analytics: bool = True
    show_risk_analytics: bool = True
```

## Acceptance Criteria

### Functional Requirements
- [ ] Each section renders independently with consistent styling
- [ ] Sections integrate charts and visualizations appropriately
- [ ] Section visibility is configurable
- [ ] Headers and formatting are consistent across sections
- [ ] Error handling for missing or invalid data

### Technical Requirements
- [ ] 90%+ test coverage for each section renderer
- [ ] Type hints for all public interfaces
- [ ] Performance: < 100ms per section rendering
- [ ] Memory efficient section generation
- [ ] Clean separation of concerns between sections

### Maintenance Requirements
- [ ] Easy to add new section types
- [ ] Consistent interface across all renderers
- [ ] Section-specific configuration options
- [ ] Clear documentation for section customization

## Estimated Timeline

- **Day 1**: Create module structure, base SectionRenderer
- **Day 2**: Implement TimeAnalyticsRenderer and TeamAnalyticsRenderer
- **Day 3**: Implement QualityAnalyticsRenderer and RiskAnalyticsRenderer
- **Day 4**: Implement OverviewRenderer, refactor ExtendedFormatter
- **Day 5**: Configuration system and section visibility controls
- **Day 6**: Testing, documentation, and optimization

**Total: 6 days**

## Testing Scenarios

### Section Independence Testing
```python
def test_section_renders_independently():
    renderer = TimeAnalyticsRenderer(config)
    analytics = create_test_time_analytics()

    output = renderer.render(analytics)

    assert "Time-Based Analysis" in output
    assert "Average Velocity" in output
    # Should not depend on other sections

def test_section_handles_missing_data():
    renderer = TeamAnalyticsRenderer(config)
    empty_analytics = TeamAnalytics(knowledge_silos=[], ...)

    output = renderer.render(empty_analytics)

    # Should render gracefully without errors
    assert "Team Collaboration" in output
```

### Configuration Testing
```python
def test_chart_visibility_configuration():
    config_no_charts = SectionConfig(show_charts=False)
    renderer = TimeAnalyticsRenderer(config_no_charts)

    output = renderer.render(time_analytics)

    # Should not contain chart output
    assert "Commits/Day" not in output  # Chart axis label
    assert "Average Velocity" in output  # Summary metrics should remain
```

## Integration Points

### Current System
- Refactors `ExtendedFormatter` from Task 08
- Uses all analytics data from Tasks 1-4
- Integrates charts from Tasks 5-7
- Uses visual enhancements from Task 10

### Future Integration
- `Task 11` (Integration) will test all sections together
- Provides foundation for custom section development
- Enables selective analytics reporting

## Performance Requirements

### Rendering Speed
- Single section: < 50ms
- All sections: < 250ms total
- Chart integration: < 100ms per chart

### Memory Usage
- Independent section processing
- Efficient data structure handling
- Minimal cross-section dependencies

---

**Note**: This task modularizes the formatting system for better maintainability and customization. It provides a clean architecture for extending analytics presentation.
