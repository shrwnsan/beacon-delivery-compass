# Architecture Design - Enhanced Extended Format

## Overview

This document provides a detailed technical architecture for implementing the enhanced extended output format as specified in Issue #10. The design emphasizes modularity, testability, and maintainability while ensuring the system can handle the complex analytics requirements.

## 🏗️ Core Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitAnalyzer   │────│   RangeStats    │────│ AnalyticsEngine │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  ChartRenderer  │────│ExtendedFormatter│────│ RiskAssessment  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow Architecture

```
Git Repository
      ↓
GitAnalyzer (existing)
      ↓
RangeStats (enhanced)
      ↓
AnalyticsEngine (new)
   ↓        ↓         ↓
TimeAnalytics  TeamAnalytics  QualityAnalytics
      ↓        ↓         ↓
ChartRenderer (new)
      ↓
ExtendedFormatter (enhanced)
      ↓
Rich Output with Analytics
```

## 🔧 Component Design

### 1. AnalyticsEngine

The central component that orchestrates all analytical computations.

```python
class AnalyticsEngine:
    """Central analytics processing engine."""

    def __init__(self, config: AnalyticsConfig):
        self.time_analyzer = TimeAnalyzer(config.time_config)
        self.team_analyzer = TeamAnalyzer(config.team_config)
        self.quality_analyzer = QualityAnalyzer(config.quality_config)
        self.risk_assessor = RiskAssessment(config.risk_config)

    def analyze(self, range_stats: RangeStats) -> EnhancedAnalytics:
        """Generate comprehensive analytics for range statistics."""
        return EnhancedAnalytics(
            time_analytics=self.time_analyzer.analyze(range_stats),
            team_analytics=self.team_analyzer.analyze(range_stats),
            quality_analytics=self.quality_analyzer.analyze(range_stats),
            risk_analytics=self.risk_assessor.assess(range_stats)
        )
```

### 2. TimeAnalyzer

Handles time-based analytics including velocity trends and activity patterns.

```python
class TimeAnalyzer:
    """Analyzes temporal patterns in commit data."""

    def analyze(self, range_stats: RangeStats) -> TimeAnalytics:
        return TimeAnalytics(
            velocity_trends=self._calculate_velocity_trends(range_stats.commits),
            activity_heatmap=self._generate_activity_heatmap(range_stats.commits),
            peak_periods=self._identify_peak_periods(range_stats.commits),
            bus_factor=self._calculate_bus_factor(range_stats.authors)
        )

    def _calculate_velocity_trends(self, commits: List[CommitStats]) -> VelocityTrends:
        """Calculate commit velocity over time periods."""

    def _generate_activity_heatmap(self, commits: List[CommitStats]) -> ActivityHeatmap:
        """Generate day-of-week and hour-of-day activity patterns."""

    def _identify_peak_periods(self, commits: List[CommitStats]) -> List[PeakPeriod]:
        """Identify periods of highest activity."""

    def _calculate_bus_factor(self, authors: Dict[str, int]) -> BusFactor:
        """Calculate team bus factor and key contributors."""
```

### 3. TeamAnalyzer

Analyzes team collaboration patterns and code ownership.

```python
class TeamAnalyzer:
    """Analyzes team collaboration and ownership patterns."""

    def analyze(self, range_stats: RangeStats) -> TeamAnalytics:
        return TeamAnalytics(
            co_authorship=self._analyze_co_authorship(range_stats.commits),
            ownership_patterns=self._analyze_ownership(range_stats.commits),
            knowledge_silos=self._identify_knowledge_silos(range_stats.commits),
            collaboration_score=self._calculate_collaboration_score(range_stats)
        )

    def _analyze_co_authorship(self, commits: List[CommitStats]) -> CoAuthorshipMatrix:
        """Analyze which authors work on similar files/components."""

    def _analyze_ownership(self, commits: List[CommitStats]) -> OwnershipMap:
        """Map code ownership patterns across files and components."""

    def _identify_knowledge_silos(self, commits: List[CommitStats]) -> List[KnowledgeSilo]:
        """Identify areas of code touched by only one developer."""
```

### 4. QualityAnalyzer

Assesses code quality metrics and change patterns.

```python
class QualityAnalyzer:
    """Analyzes code quality metrics and change patterns."""

    def analyze(self, range_stats: RangeStats) -> QualityAnalytics:
        return QualityAnalytics(
            churn_metrics=self._calculate_churn_metrics(range_stats.commits),
            complexity_trends=self._analyze_complexity_trends(range_stats.commits),
            large_changes=self._identify_large_changes(range_stats.commits),
            refactoring_patterns=self._detect_refactoring(range_stats.commits)
        )

    def _calculate_churn_metrics(self, commits: List[CommitStats]) -> ChurnMetrics:
        """Calculate code churn ratios and patterns."""

    def _analyze_complexity_trends(self, commits: List[CommitStats]) -> ComplexityTrends:
        """Track file complexity changes over time."""

    def _identify_large_changes(self, commits: List[CommitStats]) -> List[LargeChange]:
        """Identify commits with unusually large changes."""
```

### 5. ChartRenderer

Generates ASCII charts and visualizations for the terminal output.

```python
class ChartRenderer:
    """Renders ASCII charts and visualizations."""

    def __init__(self, width: int = 60):
        self.width = width

    def render_heatmap(self, data: ActivityHeatmap) -> str:
        """Render day-of-week activity heatmap."""

    def render_trend_line(self, data: VelocityTrends) -> str:
        """Render velocity trend line chart."""

    def render_bar_chart(self, data: Dict[str, int], title: str) -> str:
        """Render horizontal bar chart."""

    def render_distribution(self, data: Dict[str, float]) -> str:
        """Render distribution chart."""
```

### 6. Enhanced Data Models

```python
@dataclass
class EnhancedAnalytics:
    """Container for all analytics results."""
    time_analytics: TimeAnalytics
    team_analytics: TeamAnalytics
    quality_analytics: QualityAnalytics
    risk_analytics: RiskAnalytics

@dataclass
class TimeAnalytics:
    """Time-based analysis results."""
    velocity_trends: VelocityTrends
    activity_heatmap: ActivityHeatmap
    peak_periods: List[PeakPeriod]
    bus_factor: BusFactor

@dataclass
class TeamAnalytics:
    """Team collaboration analysis results."""
    co_authorship: CoAuthorshipMatrix
    ownership_patterns: OwnershipMap
    knowledge_silos: List[KnowledgeSilo]
    collaboration_score: float

@dataclass
class QualityAnalytics:
    """Code quality analysis results."""
    churn_metrics: ChurnMetrics
    complexity_trends: ComplexityTrends
    large_changes: List[LargeChange]
    refactoring_patterns: RefactoringPatterns
```

## 🎨 Enhanced ExtendedFormatter

The formatter will be redesigned to use a modular section-based approach:

```python
class ExtendedFormatter(BaseFormatter):
    """Enhanced extended formatter with rich analytics."""

    def __init__(self, config: FormatterConfig):
        self.analytics_engine = AnalyticsEngine(config.analytics_config)
        self.chart_renderer = ChartRenderer(config.chart_width)
        self.section_renderers = {
            'overview': OverviewSectionRenderer(),
            'time': TimeAnalyticsSectionRenderer(),
            'team': TeamAnalyticsSectionRenderer(),
            'quality': QualityAnalyticsSectionRenderer(),
            'risk': RiskSectionRenderer()
        }

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with enhanced analytics."""
        analytics = self.analytics_engine.analyze(stats)

        sections = []
        sections.append(self.section_renderers['overview'].render(stats, analytics))
        sections.append(self.section_renderers['time'].render(analytics.time_analytics))
        sections.append(self.section_renderers['team'].render(analytics.team_analytics))
        sections.append(self.section_renderers['quality'].render(analytics.quality_analytics))
        sections.append(self.section_renderers['risk'].render(analytics.risk_analytics))

        return '\n\n'.join(sections)
```

### Section Renderers

Each section has its own dedicated renderer for maintainability:

```python
class TimeAnalyticsSectionRenderer:
    """Renders time-based analytics section."""

    def render(self, analytics: TimeAnalytics) -> str:
        """Render complete time analytics section."""
        output = [f"{Fore.CYAN}📈 Time-Based Analysis{Style.RESET_ALL}"]

        # Velocity trends with ASCII chart
        output.append(self._render_velocity_section(analytics.velocity_trends))

        # Activity heatmap
        output.append(self._render_heatmap_section(analytics.activity_heatmap))

        # Peak periods
        output.append(self._render_peak_periods(analytics.peak_periods))

        # Bus factor
        output.append(self._render_bus_factor(analytics.bus_factor))

        return '\n'.join(output)
```

## 🔒 Configuration System

```python
@dataclass
class AnalyticsConfig:
    """Configuration for analytics engine."""
    time_config: TimeAnalyzerConfig
    team_config: TeamAnalyzerConfig
    quality_config: QualityAnalyzerConfig
    risk_config: RiskAssessmentConfig

@dataclass
class TimeAnalyzerConfig:
    """Configuration for time-based analysis."""
    velocity_window_days: int = 7
    peak_threshold: float = 1.5
    bus_factor_threshold: float = 0.85

@dataclass
class FormatterConfig:
    """Configuration for enhanced formatter."""
    chart_width: int = 60
    use_emoji: bool = True
    color_coding: bool = True
    analytics_config: AnalyticsConfig
```

## 🧪 Testing Strategy

### Unit Testing Structure
```
tests/unit/analytics/
├── test_analytics_engine.py
├── test_time_analyzer.py
├── test_team_analyzer.py
├── test_quality_analyzer.py
├── test_risk_assessment.py
└── test_chart_renderer.py

tests/unit/formatters/
├── test_enhanced_extended_formatter.py
├── test_section_renderers.py
└── test_output_formatting.py
```

### Integration Testing
```
tests/integration/
├── test_end_to_end_enhanced_format.py
├── test_analytics_pipeline.py
└── test_performance_benchmarks.py
```

## 📦 Module Organization

```
src/beaconled/
├── analytics/                  # New analytics module
│   ├── __init__.py
│   ├── engine.py              # AnalyticsEngine
│   ├── time_analyzer.py       # TimeAnalyzer
│   ├── team_analyzer.py       # TeamAnalyzer
│   ├── quality_analyzer.py    # QualityAnalyzer
│   ├── risk_assessment.py     # RiskAssessment
│   └── models.py              # Analytics data models
├── visualization/             # New visualization module
│   ├── __init__.py
│   ├── chart_renderer.py      # ChartRenderer
│   └── ascii_charts.py        # ASCII chart utilities
└── formatters/
    ├── extended.py            # Enhanced ExtendedFormatter
    └── sections/              # Section renderers
        ├── __init__.py
        ├── overview.py
        ├── time_analytics.py
        ├── team_analytics.py
        ├── quality_analytics.py
        └── risk_analytics.py
```

## 🚀 Performance Considerations

### Optimization Strategies
1. **Lazy Evaluation**: Compute analytics only when needed
2. **Caching**: Cache expensive calculations within analysis session
3. **Streaming Processing**: Process large commit sets incrementally
4. **Configurable Depth**: Allow users to control analysis depth

### Memory Management
- Use generators for large data processing
- Implement data structures that can be garbage collected early
- Stream chart rendering to avoid memory buildup

### Performance Targets
- Analysis time: < 5 seconds for 1000 commits
- Memory usage: < 100MB for typical repositories
- Output generation: < 1 second after analysis complete

## 🔄 Migration Strategy

### Backward Compatibility
- Existing ExtendedFormatter behavior preserved
- New features enabled through configuration flags
- Gradual feature rollout possible

### Integration Points
- Minimal changes to existing GitAnalyzer
- RangeStats enhanced with optional analytics data
- CLI unchanged, new features automatic in extended mode

---

This architecture provides a solid foundation for implementing the enhanced extended format while maintaining system reliability and extensibility.
