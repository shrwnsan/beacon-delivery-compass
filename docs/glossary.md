# Beacon Glossary

## Core Terms
- **Impact Assessment**: Classification of changes as High/Medium/Low based on:
  - File type (e.g., core logic vs. tests)
  - Change size (lines added/deleted)
  - Criticality of affected components
- **Component Analysis**: Grouping of files by functional area (e.g., "Core Logic", "Tests", "Documentation")
- **Net Change**: Total lines added minus lines deleted across all files in a commit or range
- **Range Analysis**: Aggregated metrics across multiple commits (e.g., weekly reports, sprint analyses)

## Output Formats
- **Standard Format**: Human-readable console output with essential metrics
- **Extended Format**: Detailed breakdown including file types, components, and impact analysis
- **JSON Format**: Machine-readable output for integrations and automation

## Configuration
- **Thresholds**: Configurable values that determine impact levels and notification triggers
- **Channels**: Notification delivery methods (Slack, email, webhook)
- **Metrics**: Custom product metrics tracked alongside code changes

## Integration
- **CI/CD**: Continuous Integration/Continuous Deployment pipelines
- **Git Hooks**: Scripts that run automatically when certain Git events occur
- **Webhooks**: HTTP callbacks for sending data to external systems

## Development
- **Virtual Environment**: Isolated Python environment for dependency management
- **Editable Install**: Development mode where code changes are immediately reflected
- **Test Coverage**: Percentage of code covered by automated tests

## File Types
- **Core Logic**: Source files implementing main functionality (e.g., `.py` files in `src/`)
- **Tests**: Automated test cases (e.g., `test_*.py` files)
- **Documentation**: Guides and references (e.g., `.md` files)

## Related Documentation
- [System Architecture](architecture.md) - Component relationships
- [Configuration Guide](configuration.md) - Customizing Beacon's behavior
- [Usage Guide](usage.md) - Practical application of these concepts
