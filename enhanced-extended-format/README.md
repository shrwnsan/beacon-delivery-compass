# Enhanced Extended Format (Merged into Extended Format)

**Note:** The enhanced-extended format has been merged into the standard `extended` format. This documentation is kept for historical reference.

## Overview

All features previously available in the `enhanced-extended` format are now part of the standard `extended` format. This change was made to simplify the user experience and provide a single, unified format with all features.

## Quick Start

```bash
# Install or update the package
pip install --upgrade beaconled

# Analyze your repository with enhanced analytics
beaconled --format extended --since 1m
```

## Key Features

All these features are now available in the standard `extended` format:

1. **Time-Based Analytics**
   - Commit velocity and trends
   - Peak coding hours
   - Bus factor analysis

2. **Team Collaboration**
   - Core contributor identification
   - Knowledge distribution
   - Review participation metrics

3. **Code Quality**
   - Churn rate analysis
   - Complexity trends
   - Test coverage metrics

4. **Risk Assessment**
   - Risk scoring
   - Code hotspots
   - Security vulnerability detection

## Migration

If you were previously using the `enhanced-extended` format, simply update your commands to use `--format extended` instead. All enhanced features are now included by default.

### Before
```bash
beaconled --format enhanced-extended --since 1m
```

### After
```bash
beaconled --format extended --since 1m
```

## Documentation

For complete documentation on the extended format with all enhanced features, please refer to:
- [Extended Format Guide](../docs/extended-format-guide.md)
- [Migration Guide](../docs/migration/enhanced-extended-migration-guide.md)

## Feedback

We appreciate your feedback on the unified format. If you encounter any issues or have suggestions for improvement, please [open an issue](https://github.com/yourorg/beacon-delivery-compass/issues).
