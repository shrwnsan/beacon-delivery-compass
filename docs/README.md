# Beacon Delivery Compass — For Product Leaders

Drive outcomes with engineering reality. Beacon turns Git activity into actionable insights you can use to run weekly product reviews, align roadmaps, and forecast delivery.

Who this is for:
- Product Managers and Leads
- Heads of Engineering / CTOs
- Program Managers and Analytics Leads

What you get in 10 minutes:
- Clear delivery signals (velocity, scope churn, impact)
- Weekly-ready product review report
- KPIs that tie engineering activity to product outcomes

Start here:
- View a sample Weekly Report (no install): ./samples/weekly_report.txt and ./samples/weekly_report.json
- Interpret the signals (PM guide): ./ANALYTICS_DASHBOARD.md
- Engineers: quick examples: ./examples/basic-usage.md and ./examples/advanced-usage.md
- Installation: ./installation.md

Why Beacon
- Truth from source: uses your Git history—no manual status collecting
- Weekly cadence by default: equips product rituals, not replaces them
- Lightweight: single binary CLI, JSON output for BI/automation

Core Outcomes
- Visibility: changes, impact, and risk movement per week
- Predictability: trend lines for planning and capacity
- Accountability: decisions anchored in code reality

Key Concepts
- Commit Analytics: who/what/how much changed
- Impact: file/component-level influence scoring
- Range Analytics: period-based metrics (e.g., sprint, week)

Next: ./ANALYTICS_DASHBOARD.md

# Beacon Documentation

Welcome to the Beacon documentation! This is your delivery compass for empowered product builders.

## 📚 Documentation Structure

### Getting Started
- **[Installation Guide](installation.md)** - Set up Beacon in your environment
- **[Basic Examples](examples/basic-usage.md)** - Quick start examples and common workflows
- **[Advanced Examples](examples/advanced-usage.md)** - Custom metrics and automation

### Core Documentation
- **[System Architecture](architecture.md)** - High-level system design and component relationships
- **[API](api/api.md)** - Python/CLI concepts and stability
- **[Analytics Dashboard](ANALYTICS_DASHBOARD.md)** - Understanding your development metrics
- **[Configuration Guide](configuration.md)** - Customizing Beacon's behavior

### Integration & Automation
- **[Integration Guide](integrations.md)** - CI/CD, Git hooks, and team workflows
- **[Scripts Documentation](development/scripts.md)** - Using the provided analytics scripts

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
   beaconled --since 1w

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
- View a sample weekly report: [samples/weekly_report.txt](samples/weekly_report.txt) and [samples/weekly_report.json](samples/weekly_report.json)
- PM Signal interpretation: [delivery/interpretation.md](delivery/interpretation.md)
- Engineers: [basic usage examples](examples/basic-usage.md), [advanced usage examples](examples/advanced-usage.md), and [analytics scripts](../scripts/)

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
| [Analytics Dashboard](ANALYTICS_DASHBOARD.md) | PM interpretation of signals |
| [Installation](installation.md) | Setup and installation guide |
| [Basic Examples](examples/basic-usage.md) | Practical usage examples |
| [Advanced Examples](examples/advanced-usage.md) | Custom metrics and automation |
| [Integrations](delivery/integrations.md) | CI/CD and workflow integration |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |
| [API](api/api.md) | API concepts and usage |
| [Configuration Guide](configuration.md) | Customizing Beacon's behavior |
| [Architecture](architecture.md) | System design overview |
| [Scripts (dev)](development/scripts.md) | Analytics scripts (developer/internal) |

## 💡 Next Steps

1. Start with [Installation](installation.md) to get Beacon running
2. Try the [Basic Examples](examples/basic-usage.md) for hands-on learning
3. Explore [Advanced Examples](examples/advanced-usage.md) for custom workflows
4. Set up [Integrations](delivery/integrations.md) for team workflows
5. Check [Troubleshooting](troubleshooting.md) if you encounter issues

---

**Beacon** - Your delivery compass for empowered product builders. Track, analyze, and understand your development patterns with zero dependencies and maximum insight.
