# Task 02: Team Collaboration Metrics

## Overview

Implement comprehensive team collaboration analysis for the enhanced extended format. This task analyzes team dynamics, code ownership patterns, collaboration effectiveness, and identifies potential knowledge silos.

## Scope

### Core Components
1. **TeamAnalyzer class** - Main team analytics processor
2. **CoAuthorshipMatrix** - Who works with whom analysis
3. **OwnershipMap** - Code ownership and expertise mapping
4. **KnowledgeSilo detection** - Areas touched by single developers
5. **CollaborationScore** - Overall team collaboration health

### Dependencies
- **None** - This is a foundational task

### Deliverables
1. `src/beaconled/analytics/team_analyzer.py`
2. Team-related models in `src/beaconled/analytics/models.py`
3. `tests/unit/analytics/test_team_analyzer.py`
4. Documentation and examples

## Technical Specifications

### TeamAnalyzer Class
```python
class TeamAnalyzer:
    """Analyzes team collaboration and ownership patterns."""

    def __init__(self, config: TeamAnalyzerConfig):
        self.ownership_threshold = config.ownership_threshold
        self.silo_threshold = config.silo_threshold
        self.collaboration_window_days = config.collaboration_window_days

    def analyze(self, range_stats: RangeStats) -> TeamAnalytics:
        """Generate comprehensive team analytics."""
        return TeamAnalytics(
            co_authorship=self._analyze_co_authorship(range_stats.commits),
            ownership_patterns=self._analyze_ownership(range_stats.commits),
            knowledge_silos=self._identify_knowledge_silos(range_stats.commits),
            collaboration_score=self._calculate_collaboration_score(range_stats)
        )
```

### Data Models
```python
@dataclass
class CoAuthorshipMatrix:
    """Analysis of who works with whom on similar files."""
    author_pairs: Dict[Tuple[str, str], float]  # (author1, author2) -> collaboration_score
    strongest_pairs: List[Tuple[str, str, float]]  # Top collaborating pairs
    isolated_authors: List[str]  # Authors with low collaboration

@dataclass
class OwnershipMap:
    """Code ownership patterns across files and components."""
    file_ownership: Dict[str, List[Tuple[str, float]]]  # file -> [(author, ownership_pct)]
    component_ownership: Dict[str, List[Tuple[str, float]]]  # component -> [(author, ownership_pct)]
    author_expertise: Dict[str, List[Tuple[str, float]]]  # author -> [(file/component, expertise_pct)]

@dataclass
class KnowledgeSilo:
    """Areas of code with concentrated knowledge."""
    path: str
    primary_author: str
    ownership_percentage: float
    risk_level: str  # 'high', 'medium', 'low'
    last_touched_by_others: Optional[datetime]

@dataclass
class TeamAnalytics:
    """Complete team collaboration analysis."""
    co_authorship: CoAuthorshipMatrix
    ownership_patterns: OwnershipMap
    knowledge_silos: List[KnowledgeSilo]
    collaboration_score: float
    bus_factor: int
    team_health_metrics: Dict[str, float]
```

## Implementation Guide

### Step 1: Create Module Structure
```bash
cd ../beacon-task-02-team-metrics
mkdir -p src/beaconled/analytics
touch src/beaconled/analytics/team_analyzer.py
```

### Step 2: Implement Core Analytics

#### Co-authorship Analysis
```python
def _analyze_co_authorship(self, commits: List[CommitStats]) -> CoAuthorshipMatrix:
    """Analyze collaboration patterns between authors."""
    # Group commits by file and time window
    # Calculate collaboration scores based on:
    # - Authors working on same files within time window
    # - Frequency of collaboration
    # - Diversity of collaboration (not just one pair)
```

#### Ownership Pattern Analysis
```python
def _analyze_ownership(self, commits: List[CommitStats]) -> OwnershipMap:
    """Map code ownership across files and components."""
    # Calculate ownership based on:
    # - Lines of code contributed
    # - Frequency of changes
    # - Recency of changes (weighted)
    # - Component-level aggregation
```

#### Knowledge Silo Detection
```python
def _identify_knowledge_silos(self, commits: List[CommitStats]) -> List[KnowledgeSilo]:
    """Identify areas with concentrated knowledge."""
    # Flag files/components where:
    # - Single author has >80% ownership
    # - No other author touched in last N months
    # - Critical path components (high change frequency)
```

### Step 3: Add Configuration
```python
@dataclass
class TeamAnalyzerConfig:
    ownership_threshold: float = 0.8  # 80% single ownership = silo
    silo_threshold: int = 90  # Days without other contributors
    collaboration_window_days: int = 30  # Window for co-authorship
    component_mapping: Dict[str, str] = field(default_factory=dict)
```

### Step 4: Testing Strategy
- Unit tests for each analysis method
- Mock commit data with known collaboration patterns
- Edge cases: single author, equal collaboration, etc.
- Performance tests with large teams

## Acceptance Criteria

### Functional Requirements
- [x] Identify co-authorship patterns accurately
- [x] Map code ownership at file and component levels
- [x] Detect knowledge silos with risk assessment
- [x] Calculate meaningful collaboration scores
- [x] Handle edge cases (single author repos, equal collaboration)

### Technical Requirements
- [x] 90%+ test coverage
- [x] Type hints for all public interfaces
- [x] Docstrings for all public methods
- [x] Performance: < 2 seconds for 1000 commits
- [x] Memory efficient processing

### Analysis Requirements
- [x] Ownership calculations are weighted by recency
- [x] Co-authorship considers temporal proximity
- [x] Silo detection accounts for component criticality
- [x] Collaboration scores are normalized and meaningful

## Estimated Timeline

- **Day 1**: Module structure, basic ownership calculation
- **Day 2**: Co-authorship matrix implementation
- **Day 3**: Knowledge silo detection algorithm
- **Day 4**: Collaboration scoring and team health metrics
- **Day 5**: Component-level analysis and aggregation
- **Day 6**: Testing, edge cases, and optimization

**Total: 6 days**

## Testing Scenarios

### Test Data Requirements
```python
# Diverse team scenario
commits_diverse = create_commits_with_authors([
    ("alice", ["src/auth.py", "src/utils.py"]),
    ("bob", ["src/auth.py", "src/api.py"]),
    ("carol", ["src/utils.py", "tests/"]),
])

# Knowledge silo scenario
commits_silo = create_commits_with_authors([
    ("alice", ["src/critical.py"] * 20),  # Alice owns critical.py
    ("bob", ["src/other.py"] * 5),
])

# High collaboration scenario
commits_collab = create_commits_alternating_authors([
    "alice", "bob", "alice", "carol", "bob"
], same_files=True)
```

### Expected Outcomes
- **Diverse team**: Balanced ownership, high collaboration score
- **Silo scenario**: Critical.py flagged as knowledge silo
- **High collaboration**: Strong co-authorship matrix

## Integration Points

### Current System
- Receives `RangeStats` object with commits list
- Uses existing `CommitStats` model structure
- Returns `TeamAnalytics` for formatter consumption

### Future Integration
- `Task 08` (Rich Formatter) will display team insights
- `Task 04` (Risk Assessment) will use silo data
- `ChartRenderer` will visualize collaboration networks

## Performance Requirements

### Processing Speed
- 100 commits: < 200ms
- 1000 commits: < 2 seconds
- 5000 commits: < 10 seconds

### Memory Usage
- Efficient author/file mapping
- Streaming commit processing
- Lazy evaluation of expensive calculations

---

**Note**: This task provides crucial insights into team dynamics and code health. It has no dependencies and can start immediately alongside Task 01.
