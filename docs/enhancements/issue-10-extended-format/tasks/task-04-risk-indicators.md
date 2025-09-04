# Task 04: Risk Indicator System

## Overview

Implement a comprehensive risk assessment system that combines insights from time, team, and quality analytics to identify potential risks in the codebase and development process.

## Scope

### Core Components
1. **RiskAssessment class** - Main risk evaluation processor
2. **RiskIndicator models** - Individual risk classifications
3. **RiskThresholds** - Configurable risk level definitions
4. **RiskAggregation** - Combined risk scoring algorithms
5. **RiskRecommendations** - Actionable risk mitigation suggestions

### Dependencies
- **Task 01**: Time-Based Analytics (for bus factor, velocity trends)
- **Task 02**: Team Collaboration Metrics (for knowledge silos)
- **Task 03**: Code Quality Assessment (for churn, large changes)

### Deliverables
1. `src/beaconled/analytics/risk_assessment.py`
2. Risk-related models in `src/beaconled/analytics/models.py`
3. `tests/unit/analytics/test_risk_assessment.py`
4. Risk mitigation documentation

## Technical Specifications

### RiskAssessment Class
```python
class RiskAssessment:
    """Evaluates various risk factors and provides integrated assessment."""

    def __init__(self, config: RiskAssessmentConfig):
        self.thresholds = config.thresholds
        self.weights = config.risk_weights
        self.mitigation_strategies = config.mitigation_strategies

    def assess(self, analytics: EnhancedAnalytics) -> RiskAnalytics:
        """Generate comprehensive risk assessment."""
        return RiskAnalytics(
            bus_factor_risk=self._assess_bus_factor_risk(analytics.time_analytics),
            knowledge_silo_risk=self._assess_knowledge_silos(analytics.team_analytics),
            technical_debt_risk=self._assess_technical_debt(analytics.quality_analytics),
            velocity_risk=self._assess_velocity_risk(analytics.time_analytics),
            overall_risk_score=self._calculate_overall_risk(analytics),
            recommendations=self._generate_recommendations(analytics)
        )
```

### Data Models
```python
@dataclass
class RiskIndicator:
    """Individual risk factor assessment."""
    name: str
    level: str  # 'low', 'medium', 'high', 'critical'
    score: float  # 0.0 to 1.0
    description: str
    impact: str
    likelihood: str
    affected_components: List[str]
    mitigation_suggestions: List[str]

@dataclass
class RiskThresholds:
    """Configurable thresholds for risk assessment."""
    bus_factor_critical: int = 1
    bus_factor_high: int = 2
    knowledge_silo_threshold: float = 0.8
    churn_ratio_high: float = 0.6
    velocity_drop_significant: float = 0.3
    large_change_threshold: int = 500

@dataclass
class RiskAnalytics:
    """Complete risk assessment results."""
    bus_factor_risk: RiskIndicator
    knowledge_silo_risk: RiskIndicator
    technical_debt_risk: RiskIndicator
    velocity_risk: RiskIndicator
    overall_risk_score: float
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    top_risks: List[RiskIndicator]
    recommendations: List[str]
```

## Implementation Guide

### Step 1: Create Module Structure
```bash
cd ../beacon-task-04-risk-indicators
mkdir -p src/beaconled/analytics
touch src/beaconled/analytics/risk_assessment.py
```

### Step 2: Implement Risk Assessment Methods

#### Bus Factor Risk Assessment
```python
def _assess_bus_factor_risk(self, time_analytics: TimeAnalytics) -> RiskIndicator:
    """Assess risk from low bus factor."""
    bus_factor = time_analytics.bus_factor.factor

    if bus_factor <= self.thresholds.bus_factor_critical:
        level = "critical"
        score = 0.9
        description = f"Critical: Only {bus_factor} person(s) handle majority of changes"
    elif bus_factor <= self.thresholds.bus_factor_high:
        level = "high"
        score = 0.7
        description = f"High: Only {bus_factor} people handle majority of changes"
    else:
        level = "low"
        score = 0.2
        description = f"Good: {bus_factor} people actively contribute"

    return RiskIndicator(
        name="Bus Factor Risk",
        level=level,
        score=score,
        description=description,
        # ... other fields
    )
```

#### Knowledge Silo Risk Assessment
```python
def _assess_knowledge_silos(self, team_analytics: TeamAnalytics) -> RiskIndicator:
    """Assess risk from knowledge silos."""
    silos = team_analytics.knowledge_silos
    high_risk_silos = [s for s in silos if s.risk_level == "high"]

    if len(high_risk_silos) > 5:
        level = "critical"
        score = 0.85
    elif len(high_risk_silos) > 2:
        level = "high"
        score = 0.6
    elif len(high_risk_silos) > 0:
        level = "medium"
        score = 0.4
    else:
        level = "low"
        score = 0.1
```

#### Technical Debt Risk Assessment
```python
def _assess_technical_debt(self, quality_analytics: QualityAnalytics) -> RiskIndicator:
    """Assess risk from technical debt and quality issues."""
    churn_ratio = quality_analytics.churn_metrics.churn_ratio
    large_changes = len(quality_analytics.large_changes)
    quality_score = quality_analytics.quality_score

    # Combine multiple quality indicators
    debt_score = (
        (churn_ratio * 0.4) +
        (min(large_changes / 10, 1.0) * 0.3) +
        ((1.0 - quality_score) * 0.3)
    )
```

#### Velocity Risk Assessment
```python
def _assess_velocity_risk(self, time_analytics: TimeAnalytics) -> RiskIndicator:
    """Assess risk from velocity changes and trends."""
    velocity_trend = time_analytics.velocity_trends

    if velocity_trend.trend_direction == "decreasing":
        # Calculate severity based on rate of decrease
        trend_score = abs(velocity_trend.weekly_average - velocity_trend.peak_velocity[1])
        # Implementation details...
```

### Step 3: Risk Aggregation and Scoring
```python
def _calculate_overall_risk(self, analytics: EnhancedAnalytics) -> float:
    """Calculate weighted overall risk score."""
    risks = [
        self.bus_factor_risk.score * self.weights.bus_factor,
        self.knowledge_silo_risk.score * self.weights.knowledge_silos,
        self.technical_debt_risk.score * self.weights.technical_debt,
        self.velocity_risk.score * self.weights.velocity
    ]

    return sum(risks) / len(risks)
```

### Step 4: Generate Recommendations
```python
def _generate_recommendations(self, analytics: EnhancedAnalytics) -> List[str]:
    """Generate actionable risk mitigation recommendations."""
    recommendations = []

    # Bus factor recommendations
    if self.bus_factor_risk.level in ["high", "critical"]:
        recommendations.extend([
            "Consider knowledge sharing sessions",
            "Document critical processes and code",
            "Encourage pair programming on key components"
        ])

    # Knowledge silo recommendations
    for silo in analytics.team_analytics.knowledge_silos:
        if silo.risk_level == "high":
            recommendations.append(f"Cross-train team members on {silo.path}")

    # Technical debt recommendations
    if self.technical_debt_risk.level == "high":
        recommendations.extend([
            "Schedule refactoring sessions for high-churn files",
            "Implement code review requirements for large changes",
            "Consider breaking down large commits"
        ])

    return recommendations
```

## Acceptance Criteria

### Functional Requirements
- [ ] Accurately assess bus factor risks using team analytics
- [ ] Identify knowledge silo risks with severity levels
- [ ] Evaluate technical debt from quality metrics
- [ ] Calculate meaningful overall risk scores
- [ ] Generate actionable mitigation recommendations

### Technical Requirements
- [ ] 90%+ test coverage
- [ ] Type hints for all public interfaces
- [ ] Configurable risk thresholds and weights
- [ ] Performance: < 500ms for complete assessment
- [ ] Integration with all dependency analytics

### Risk Assessment Requirements
- [ ] Risk levels are consistent and meaningful
- [ ] Scoring algorithms are transparent and auditable
- [ ] Recommendations are specific and actionable
- [ ] Risk factors are weighted appropriately

## Estimated Timeline

- **Day 1**: Module structure, risk indicator models
- **Day 2**: Bus factor and knowledge silo risk assessment
- **Day 3**: Technical debt and velocity risk assessment
- **Day 4**: Risk aggregation and overall scoring
- **Day 5**: Recommendation generation and testing

**Total: 5 days**

## Testing Scenarios

### Test Data Requirements
```python
# High-risk scenario
high_risk_analytics = EnhancedAnalytics(
    time_analytics=TimeAnalytics(bus_factor=BusFactor(factor=1, ...)),
    team_analytics=TeamAnalytics(knowledge_silos=[
        KnowledgeSilo(path="critical.py", risk_level="high", ...)
    ]),
    quality_analytics=QualityAnalytics(churn_metrics=ChurnMetrics(churn_ratio=0.8))
)

# Low-risk scenario
low_risk_analytics = EnhancedAnalytics(
    time_analytics=TimeAnalytics(bus_factor=BusFactor(factor=5, ...)),
    team_analytics=TeamAnalytics(knowledge_silos=[]),
    quality_analytics=QualityAnalytics(churn_metrics=ChurnMetrics(churn_ratio=0.2))
)
```

### Expected Risk Outputs
```
⚠️ Risk Assessment:
• Overall Risk Level: HIGH (0.72/1.0)

🔴 Critical Risks:
  • Bus Factor Risk: Only 1 person handles 85% of changes
    - Mitigation: Knowledge sharing sessions, documentation

🟡 Medium Risks:
  • Technical Debt: High churn in 3 critical files
    - Mitigation: Schedule refactoring, code review requirements

💡 Recommendations:
  1. Cross-train team members on src/critical.py
  2. Implement mandatory code review for >100 line changes
  3. Document authentication and deployment processes
```

## Integration Points

### Current System
- Receives `EnhancedAnalytics` from all dependency tasks
- Combines risk factors using configurable weights
- Returns `RiskAnalytics` for formatter consumption

### Dependency Integration
- **TimeAnalytics**: Bus factor, velocity trends
- **TeamAnalytics**: Knowledge silos, collaboration health
- **QualityAnalytics**: Churn metrics, large changes

### Future Integration
- `Task 08` (Rich Formatter) will display risk assessment
- Risk data can guide development priority decisions
- Recommendations can be exported for project management

## Configuration Example
```python
@dataclass
class RiskAssessmentConfig:
    thresholds: RiskThresholds = field(default_factory=RiskThresholds)
    risk_weights: Dict[str, float] = field(default_factory=lambda: {
        "bus_factor": 0.3,
        "knowledge_silos": 0.25,
        "technical_debt": 0.25,
        "velocity": 0.2
    })
```

---

**Note**: This task synthesizes insights from multiple analytics to provide actionable risk assessment. It depends on Tasks 1-3 but provides valuable integrated analysis for decision-making.
