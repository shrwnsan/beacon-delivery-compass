# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Enhanced Extended Format Features**: Integrated all enhanced-extended format features into the standard extended format
  - Added time-based analytics including velocity, peak hours, and bus factor
  - Integrated team collaboration metrics with core contributor identification
  - Added code quality analysis with churn rate and complexity trends
  - Implemented risk assessment with security vulnerability detection
  - Added comprehensive test coverage for all new analytics features

### Changed
- **Format Consolidation**: Merged enhanced-extended format into extended format
  - Removed `--format enhanced-extended` CLI option
  - All enhanced features are now available in the standard `--format extended`
  - Updated all documentation to reflect the unified format
  - Improved output formatting for better readability of analytics

### Deprecated
- **Enhanced-Extended Format**: The separate `enhanced-extended` format is deprecated in favor of the enhanced `extended` format
  - A migration guide is available at `docs/migration/enhanced-extended-migration-guide.md`
  - Backward compatibility is maintained for existing scripts using the extended format

### Fixed
- **Analytics Integration**: Fixed issues with analytics engine integration
  - Improved error handling for missing analytics data
  - Fixed type hints and return types in analytics components
  - Enhanced test coverage for analytics functionality

## [v0.3.0] - 2025-08-20

### Added
- **Advanced Usage Framework**: Comprehensive advanced usage examples and testing infrastructure
  - Added `docs/examples/advanced-usage.md` with 10+ advanced use cases including executive reporting, team health analysis, and technical debt tracking
  - Created `scripts/test_advanced_usage.sh` with 10 comprehensive test scenarios covering all documented features
  - Added organized output management in `scripts/test_outputs/` directory with flag-based cleanup system
  - Implemented interpretive scoring guidance for health metrics with 0-100 scales and clear explanations
- **Strategic Product Vision**: Added comprehensive product strategy documentation
  - Created `docs/development/product-strategy.md` with market analysis, user personas, and implementation roadmap
  - Added "Built-in Product Delivery Health Reports" stretch goal to development roadmap
  - Established clear path from custom scripts to native CLI features
- **Enhanced Documentation Structure**: Reorganized and improved documentation
  - Streamlined README.md with user-focused structure prioritizing installation and usage examples
  - Added comprehensive sample outputs with realistic data
  - Improved documentation cross-references and navigation

### Changed
- **Time Format Standardization**: Updated all time-related parameters to support concise format (e.g., "1w" instead of "1 week ago")
  - Added support for formats like "1d" (1 day), "2w" (2 weeks), "3m" (3 months), "1y" (1 year)
  - Maintained backward compatibility with verbose formats ("1 week ago", "2 days ago", etc.)
  - Updated documentation and examples to use the new concise format
  - Modified all scripts and GitHub Actions workflows to use the new format
  - Updated test cases to verify both old and new formats work correctly
- **README Structure**: Reorganized README.md for better user adoption
  - Moved installation and quick start sections to the top
  - Prioritized sample outputs and usage examples over development details
  - Reduced content by ~50% while maintaining essential information
  - Improved "show, don't tell" approach with concrete examples

### Fixed
- **Number Formatting**: Implemented comprehensive comma formatting for better readability
  - Added comma separators to all large numbers (1,000+) across all output formats
  - Fixed individual commit statistics formatting (Lines added, Lines deleted, Net change)
  - Fixed range analysis statistics formatting (Total commits, Total lines, etc.)
  - Fixed component activity lines formatting (e.g., "docs/ 7 commits, 1,348 lines")
  - Fixed file type breakdown formatting in extended output
  - Applied consistent formatting to all numeric displays throughout the application
- **Duration Calculation**: Fixed off-by-one error in date range calculations
  - `--since 9d` now correctly displays "(9 days)" instead of "(10 days)"
  - Updated duration logic to match user expectations for relative dates
  - Maintained accuracy for same-day analyses
- **Date Parsing Performance**: Improved date parsing performance by simplifying regular expressions
- **Timezone Handling**: Ensured consistent timezone handling across all date-related functions
- **Documentation**: Updated help text and documentation to clearly explain supported time formats

## [v0.2.1] - 2025-08-19

### Fixed
- Streamlined ignore rules and removed stray files
- Ensured File type breakdown always appears in extended format
- Updated pytest.ini coverage configuration

## [v0.2.0] - 2025-07-25
### Added
- **New Date Parser Utility**: Added a dedicated `DateParser` class in `utils.date_utils` for better code organization and maintainability.
  - Centralized date parsing, validation, and manipulation logic
  - Improved error handling and validation
  - Better separation of concerns
  - More consistent behavior across the codebase

### Changed
- **Refactored Date Handling**: Migrated from `GitDateParser` to the new `DateParser` utility:
  - Moved all date parsing logic to a dedicated utility module
  - Maintained backward compatibility with `GitDateParser` as a wrapper
  - Updated all tests to use the new implementation
  - Improved documentation and type hints

- **Refactored Git Integration**: Migrated from direct subprocess calls to GitPython for:
  - Better error handling and exception management
  - Improved cross-platform compatibility
  - More maintainable and testable code
  - Enhanced security by avoiding shell command injection risks
  - More reliable repository operations

## [v0.1.1] - 2025-07-25

### Added
- Comprehensive product analytics system implementation
- Enhanced weekly reports with product insights
- Color output support using colorama
- Complete documentation suite including:
  - Architecture documentation
  - Configuration guide
  - Glossary of terms
  - Integration examples
  - Security audit documentation
- Git commands section in tech stack documentation
- Visualization examples in product analytics documentation

### Fixed
- Duplicate --version argument in CLI parser
- Unicode encoding issue on Windows when redirecting output
- Various flake8 linting errors

### Security
- Comprehensive security hardening and vulnerability resolution
- Added detailed security audit documentation (2025-07-24)
- Updated security policy and procedures

### Changed
- Migrated from setup.py to pyproject.toml for build configuration
- Standardized virtual environment naming to .venv convention
- Updated package name from beacon to beaconled
- Updated repository URL to match renamed repo: beacon-delivery-compass

### Removed
- Old egg-info directory

## [v0.1.0] - 2025-07-24

### Added
- Initial public release on PyPI
- Core git analytics functionality
- CLI interface for repository analysis
- Initial documentation suite
- Rebranded from "Git Analytics Toolkit" to "Beacon Delivery Compass"

### Changed
- Renamed package directory from git_analytics to beaconled
- Updated all branding and documentation

### Fixed
- Copyright year updated to 2025
- Addressed all flake8 linting errors
