# Beacon Documentation

Welcome to the Beacon documentation! This is your delivery compass for empowered product builders.

## 📚 Documentation Structure

### Getting Started
- **[Installation Guide](installation.md)** - Set up Beacon in your environment
- **[Usage Guide](usage.md)** - Learn how to use Beacon effectively
- **[Basic Examples](examples/basic-usage.md)** - Quick start examples and common workflows
- **[Advanced Examples](examples/advanced-usage.md)** - Custom metrics and automation

### Core Documentation
- **[System Architecture](architecture.md)** - High-level system design and component relationships
- **[API Reference](api-reference.md)** - Complete command-line and Python API reference
- **[Analytics Dashboard](ANALYTICS_DASHBOARD.md)** - Understanding your development metrics
- **[Development Analytics](DEVELOPMENT_ANALYTICS.md)** - Deep dive into development patterns
- **[Product Analytics](PRODUCT_ANALYTICS.md)** - Measuring product impact metrics
- **[Configuration Guide](configuration.md)** - Customizing Beacon's behavior
- **[Dependency Management](DEPENDENCY_MANAGEMENT.md)** - Strategy for managing dependencies and installation issues

### Integration & Automation
- **[Integration Guide](integrations.md)** - CI/CD, Git hooks, and team workflows
- **[Scripts Documentation](scripts-readme.md)** - Using the provided analytics scripts

### Troubleshooting
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

## 🚀 Quick Start

1. **Install Beacon**
   ```bash
   pip install beaconled
   ```

2. **Basic Usage**
   ```bash
   # Analyze latest commit
   beaconled

   # Example output:
   # 📊 Commit: abc12345
   # 👤 Author: John Doe
   # 📅 Date: 2025-07-20 10:30:00
   # 💬 Message: Add new feature for user analytics
   #
   # 📂 Files changed: 3
   # ➕ Lines added: 45
   # ➖ Lines deleted: 12
   # 🔀 Net change: 33
   #
   # Changed files:
   #   src/analytics.py   (+30 -5)
   #   tests/test_analytics.py (+15 -0)
   #   README.md          (+0 -7)

   # Weekly team report
   beaconled --range --since "1 week ago"

   # Example output:
   # 📊 Range Analysis: 2025-07-13 to 2025-07-20
   #
   # 📂 Total commits: 15
   # 📂 Total files changed: 42
   # ➕ Total lines added: 1,234
   # ➖ Total lines deleted: 567
   # 🔀 Net change: 667
   #
   # 👥 Contributors:
   #   John Doe: 8 commits
   #   Jane Smith: 4 commits
   #   Bob Wilson: 3 commits
   #
   # 📊 Commit frequency:
   #   Monday: 2
   #   Tuesday: 3
   #   Wednesday: 1
   #   Thursday: 4
   #   Friday: 5

   # JSON output for automation
   beaconled --format json
   ```

3. **Explore Examples**
   - Check out [basic usage examples](examples/basic-usage.md)
   - Explore [advanced usage examples](examples/advanced-usage.md)
   - Try the [analytics scripts](../scripts/)

## 📊 Key Features

- **Zero Dependencies**: Uses only Python standard library
- **Multiple Formats**: Standard, extended, and JSON output
- **Range Analysis**: Team and sprint reporting
- **CI/CD Ready**: GitHub Actions, GitLab CI, Jenkins integration
- **Team Friendly**: Perfect for standups and retrospectives

## 🎯 Use Cases

- **Daily Standups**: Quick development summaries
- **Sprint Planning**: Velocity and impact analysis
- **Code Reviews**: Change impact assessment
- **Team Reports**: Weekly and monthly analytics
- **CI/CD Integration**: Automated metrics collection
- **Product Analytics**: Feature impact measurement

## 🔗 Quick Links

- **GitHub Repository**: [beaconled-delivery-compass](https://github.com/shrwnsan/beaconled-delivery-compass)
- **Issues & Support**: [GitHub Issues](https://github.com/shrwnsan/beaconled-delivery-compass/issues)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## 📋 Documentation Index

| Document | Purpose |
|----------|---------|
| [Installation](installation.md) | Setup and installation guide |
| [Usage](usage.md) | Complete usage guide |
| [System Architecture](architecture.md) | High-level system design |
| [API Reference](api-reference.md) | Command-line and Python API |
| [Analytics Dashboard](ANALYTICS_DASHBOARD.md) | Understanding metrics |
| [Product Analytics](PRODUCT_ANALYTICS.md) | Product impact measurement |
| [Configuration Guide](configuration.md) | Customizing Beacon's behavior |
| [Integrations](integrations.md) | CI/CD and workflow integration |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |
| [Basic Examples](examples/basic-usage.md) | Practical usage examples |
| [Advanced Examples](examples/advanced-usage.md) | Custom metrics and automation |
| [Scripts](scripts-readme.md) | Analytics scripts documentation |

## 💡 Next Steps

1. Start with [Installation](installation.md) to get Beacon running
2. Read the [Usage Guide](usage.md) for comprehensive instructions
3. Try the [Basic Examples](examples/basic-usage.md) for hands-on learning
4. Explore [Advanced Examples](examples/advanced-usage.md) for custom workflows
5. Set up [Integrations](integrations.md) for team workflows
6. Check [Troubleshooting](troubleshooting.md) if you encounter issues

---

**Beacon** - Your delivery compass for empowered product builders. Track, analyze, and understand your development patterns with zero dependencies and maximum insight.
