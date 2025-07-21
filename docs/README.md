# Beacon Documentation

Welcome to the Beacon documentation! This is your delivery compass for empowered product builders.

## 📚 Documentation Structure

### Getting Started
- **[Installation Guide](installation.md)** - Set up Beacon in your environment
- **[Usage Guide](usage.md)** - Learn how to use Beacon effectively
- **[Basic Examples](examples/basic-usage.md)** - Quick start examples and common workflows

### Core Documentation
- **[API Reference](api-reference.md)** - Complete command-line and Python API reference
- **[Analytics Dashboard](ANALYTICS_DASHBOARD.md)** - Understanding your development metrics
- **[Development Analytics](DEVELOPMENT_ANALYTICS.md)** - Deep dive into development patterns

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

   # Weekly team report
   beaconled --range --since "1 week ago"

   # JSON output for automation
   beaconled --format json
   ```

3. **Explore Examples**
   - Check out [basic usage examples](examples/basic-usage.md)
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

## 🔗 Quick Links

- **GitHub Repository**: [beaconled-delivery-compass](https://github.com/shrwnsan/beaconled-delivery-compass)
- **Issues & Support**: [GitHub Issues](https://github.com/shrwnsan/beaconled-delivery-compass/issues)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## 📋 Documentation Index

| Document | Purpose |
|----------|---------|
| [Installation](installation.md) | Setup and installation guide |
| [Usage](usage.md) | Complete usage guide |
| [API Reference](api-reference.md) | Command-line and Python API |
| [Analytics Dashboard](ANALYTICS_DASHBOARD.md) | Understanding metrics |
| [Integrations](integrations.md) | CI/CD and workflow integration |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |
| [Examples](examples/basic-usage.md) | Practical usage examples |
| [Scripts](scripts-readme.md) | Analytics scripts documentation |

## 💡 Next Steps

1. Start with [Installation](installation.md) to get Beacon running
2. Read the [Usage Guide](usage.md) for comprehensive instructions
3. Try the [Basic Examples](examples/basic-usage.md) for hands-on learning
4. Explore [Integrations](integrations.md) for team workflows
5. Check [Troubleshooting](troubleshooting.md) if you encounter issues

---

**Beacon** - Your delivery compass for empowered product builders. Track, analyze, and understand your development patterns with zero dependencies and maximum insight.
