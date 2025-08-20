# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for combined time units in concise format (e.g., "1w2d" for 1 week and 2 days)

### Changed
- **Time Format Standardization**: Updated all time-related parameters to support concise format (e.g., "1w" instead of "1 week ago")
  - Added support for formats like "1d" (1 day), "2w" (2 weeks), "3m" (3 months), "1y" (1 year)
  - Maintained backward compatibility with verbose formats ("1 week ago", "2 days ago", etc.)
  - Updated documentation and examples to use the new concise format
  - Modified all scripts and GitHub Actions workflows to use the new format
  - Updated test cases to verify both old and new formats work correctly

### Fixed
- Improved date parsing performance by simplifying the regular expressions
- Ensured consistent timezone handling across all date-related functions
- Updated help text and documentation to clearly explain the supported time formats

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
