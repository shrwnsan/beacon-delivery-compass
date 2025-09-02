# Collaboration Analytics Module

This module provides comprehensive team collaboration analysis for the BeaconLED tool's enhanced extended format.

## Components

### CollaborationAnalyzer
The main analyzer that generates comprehensive team collaboration insights from commit data.

**Features:**
- **Co-authorship Analysis**: Identifies frequent collaborator pairs and collaboration strength
- **Knowledge Distribution**: Maps code ownership patterns and identifies knowledge silos
- **Review Metrics**: Analyzes review participation and coverage patterns
- **Collaboration Patterns**: Calculates team connectivity and collaboration balance

### Data Models
- `CoAuthorshipMetrics`: Pair-wise collaboration analysis between developers
- `KnowledgeDistribution`: Code ownership and knowledge silo identification
- `ReviewMetrics`: Review participation and effectiveness analysis
- `CollaborationPatterns`: Overall team collaboration health metrics
- `CollaborationMetrics`: Container for all collaboration analysis results

## Usage

```python
from beaconled.analytics import CollaborationAnalyzer, CollaborationConfig
from beaconled.core.models import RangeStats

# Configure analyzer
config = CollaborationConfig(
    min_collaboration_threshold=3,
    knowledge_silo_threshold=0.8,
    review_coverage_target=0.7
)

# Create analyzer
analyzer = CollaborationAnalyzer(config)

# Analyze commit data
range_stats = RangeStats(...)  # Your commit data
results = analyzer.analyze(range_stats)

# Access results
print(f"Team connectivity: {results.collaboration_patterns.team_connectivity:.2f}")
print(f"Top collaborators: {results.co_authorship.top_collaborators[:3]}")
print(f"Knowledge risk: {results.collaboration_patterns.knowledge_risk}")
```

## Configuration

- `min_collaboration_threshold`: Minimum commits for collaboration consideration (default: 3)
- `knowledge_silo_threshold`: Concentration threshold for knowledge silos (default: 0.8)
- `review_coverage_target`: Target review coverage ratio (default: 0.7)

## Analysis Types

### Co-authorship Analysis
- Identifies developers who frequently work on the same files
- Calculates collaboration strength scores
- Ranks top collaborating pairs

### Knowledge Distribution
- Maps which developers have expertise in which file types
- Identifies knowledge silos (single-person dependencies)
- Tracks code ownership patterns

### Review Metrics
- Measures review participation across the team
- Calculates review coverage ratios
- Provides quality indicators

### Collaboration Patterns
- Team connectivity score (how well-connected the team is)
- Collaboration balance (ratio of collaborative vs individual work)
- Overall knowledge risk assessment

## Testing

Run tests with:
```bash
pytest tests/unit/analytics/test_collaboration_analyzer.py
```

## Performance

- Designed to handle large development teams efficiently
- Processes collaboration patterns in O(n) time
- Memory efficient with streaming analysis
- Typical performance: < 1 second for 1000 commits

## Integration

This module integrates with:
- **RangeStats**: Consumes commit and author data
- **Future ChartRenderer**: Provides data for collaboration network graphs
- **ExtendedFormatter**: Supplies collaboration insights for display
- **RiskAssessment**: Contributes to knowledge risk evaluation
