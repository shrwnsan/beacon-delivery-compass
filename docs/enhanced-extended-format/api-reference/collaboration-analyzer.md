# CollaborationAnalyzer API Reference

## Class: CollaborationAnalyzer

Analyzes team collaboration patterns in commit data.

### Constructor

```python
CollaborationAnalyzer(config: CollaborationConfig)
```

**Parameters:**
- `config`: Configuration object with analysis parameters

### Configuration

#### CollaborationConfig

Configuration object for CollaborationAnalyzer.

**Attributes:**
- `min_collaboration_threshold` (int): Minimum commits for collaboration consideration (default: 3)
- `knowledge_silo_threshold` (float): Concentration threshold for knowledge silos (default: 0.8)
- `review_coverage_target` (float): Target review coverage ratio (default: 0.7)

### Methods

#### analyze(range_stats: RangeStats) -> CollaborationMetrics

Generate comprehensive collaboration metrics.

**Parameters:**
- `range_stats`: Repository statistics for the analysis period

**Returns:**
- `CollaborationMetrics`: Complete collaboration analysis results

**Example:**
```python
analyzer = CollaborationAnalyzer(CollaborationConfig())
result = analyzer.analyze(range_stats)
print(f"Collaboration patterns: {result.collaboration_patterns.team_connectivity}")
```

### Data Models

#### CollaborationMetrics

Complete collaboration analysis results.

**Attributes:**
- `co_authorship` (CoAuthorshipMetrics): Co-authorship patterns between developers
- `knowledge_distribution` (KnowledgeDistribution): Knowledge distribution across file types
- `review_metrics` (ReviewMetrics): Review participation and effectiveness
- `collaboration_patterns` (CollaborationPatterns): Team connectivity and collaboration balance

#### CoAuthorshipMetrics

Co-authorship patterns between developers.

**Attributes:**
- `author_pairs` (dict[tuple[str, str], int]): Number of commits co-authored by each pair
- `collaboration_strength` (dict[tuple[str, str], float]): Strength of collaboration between each pair
- `top_collaborators` (list[tuple[str, str]]): Most collaborative author pairs

#### KnowledgeDistribution

Knowledge distribution across file types.

**Attributes:**
- `author_expertise` (dict[str, dict[str, int]]): Expertise by author and file type
- `knowledge_silos` (list[str]): File types with concentrated knowledge
- `ownership_patterns` (dict[str, str]): Primary owner for each file type

#### ReviewMetrics

Review participation and effectiveness.

**Attributes:**
- `review_participation` (dict[str, int]): Number of reviews participated in by each author
- `review_coverage` (dict[str, float]): Percentage of commits reviewed by each author
- `review_quality_indicators` (dict[str, float]): Quality metrics for each authors reviews

#### CollaborationPatterns

Team connectivity and collaboration balance.

**Attributes:**
- `team_connectivity` (float): Overall team connectivity score (0-1)
- `collaboration_balance` (float): Balance of collaboration across team (0-1)
- `knowledge_risk` (str): Risk assessment of knowledge distribution ("high", "medium", "low")
