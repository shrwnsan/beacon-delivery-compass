#!/usr/bin/env python
"""
Setup Script for Product Analytics System
One-time setup to configure the product-led analytics system.
"""

import os
import json
from pathlib import Path
import subprocess

class ProductAnalyticsSetup:
    """Handles one-time setup for product analytics system."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.scripts_dir = self.base_dir / "scripts"
        self.config_dir = self.base_dir / "config"
        
    def run_setup(self):
        """Run complete setup process."""
        print("🚀 Setting up Product Analytics System...")
        
        # Create directory structure
        self._create_directories()
        
        # Create configuration files
        self._create_config_files()
        
        # Create automation scripts
        self._create_automation_scripts()
        
        # Create documentation
        self._create_documentation()
        
        # Set permissions
        self._set_permissions()
        
        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Update config/notifications.json with your settings")
        print("2. Set up environment variables for notifications")
        print("3. Run: python scripts/product_insights_cli.py weekly")
        print("4. Schedule weekly reports using cron or GitHub Actions")
    
    def _create_directories(self):
        """Create necessary directories."""
        directories = [
            self.config_dir,
            self.base_dir / "reports",
            self.base_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    def _create_config_files(self):
        """Create configuration files."""
        
        # Notification configuration
        notification_config = {
            "slack": {
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                "channel": "#product-alerts",
                "enabled": bool(os.getenv("SLACK_WEBHOOK_URL"))
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": os.getenv("EMAIL_USERNAME", ""),
                "password": os.getenv("EMAIL_PASSWORD", ""),
                "enabled": bool(os.getenv("EMAIL_USERNAME"))
            },
            "recipients": {
                "product_managers": ["pm@company.com"],
                "engineering_leads": ["lead@company.com"],
                "executives": ["exec@company.com"]
            },
            "thresholds": {
                "feature_velocity": {"warning": 2, "critical": 1},
                "technical_debt_ratio": {"warning": 30, "critical": 40},
                "customer_driven_index": {"warning": 40, "critical": 30}
            }
        }
        
        with open(self.config_dir / "notifications.json", 'w') as f:
            json.dump(notification_config, f, indent=2)
        
        # Product metrics configuration
        metrics_config = {
            "metrics": {
                "feature_velocity": {
                    "enabled": True,
                    "target": 3.0,
                    "unit": "features/week"
                },
                "customer_driven_index": {
                    "enabled": True,
                    "target": 60.0,
                    "unit": "percent"
                },
                "technical_debt_ratio": {
                    "enabled": True,
                    "target": 20.0,
                    "unit": "percent"
                },
                "release_readiness": {
                    "enabled": True,
                    "target": 80.0,
                    "unit": "score"
                }
            },
            "reporting": {
                "weekly_summary": True,
                "daily_alerts": True,
                "executive_summary": True
            }
        }
        
        with open(self.config_dir / "product_metrics.json", 'w') as f:
            json.dump(metrics_config, f, indent=2)
        
        print("⚙️ Created configuration files")
    
    def _create_automation_scripts(self):
        """Create automation scripts."""
        
        # Weekly report script
        weekly_script = '''#!/bin/bash
# Weekly Product Insights Report Generator
# Add this to your crontab: 0 9 * * MON /path/to/weekly_report.sh

cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true

echo "Generating weekly product insights..."
python scripts/product_insights_cli.py weekly --since "1 week ago" > reports/weekly_report.txt

# Send notifications if configured
python scripts/notification_system.py process insights.json

echo "Weekly report generated: reports/weekly_report.txt"
'''
        
        with open(self.scripts_dir / "weekly_report.sh", 'w') as f:
            f.write(weekly_script)
        
        # GitHub Actions workflow
        github_workflow = '''name: Product Analytics

on:
  schedule:
    - cron: '0 9 * * MON'  # Every Monday at 9 AM
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Generate Product Insights
      run: |
        python scripts/product_insights_cli.py weekly --since "1 week ago" > weekly_report.txt
        python scripts/product_insights_cli.py executive --since "1 week ago" > executive_summary.json
    
    - name: Upload Report
      uses: actions/upload-artifact@v3
      with:
        name: weekly-product-report
        path: |
          weekly_report.txt
          executive_summary.json
    
    - name: Send Slack Notification
      if: env.SLACK_WEBHOOK_URL != ''
      run: |
        python scripts/notification_system.py process executive_summary.json
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
'''
        
        workflow_dir = self.base_dir / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        with open(workflow_dir / "product-analytics.yml", 'w') as f:
            f.write(github_workflow)
        
        print("🤖 Created automation scripts")
    
    def _create_documentation(self):
        """Create documentation files."""
        
        readme_content = '''# Product Analytics System

## Overview
This system transforms commit analytics into actionable business intelligence for product-led teams.

## Quick Start

### 1. Initial Setup
```bash
python scripts/setup_product_analytics.py
```

### 2. Configure Notifications
Edit `config/notifications.json` with your settings:
- Slack webhook URL
- Email credentials
- Recipient lists

### 3. Run Reports
```bash
# Weekly product insights
python scripts/product_insights_cli.py weekly

# Executive summary
python scripts/product_insights_cli.py executive

# Individual commit analysis
python scripts/product_insights_cli.py commit --commit HEAD

# Check alerts
python scripts/product_insights_cli.py alerts
```

### 4. Automate
```bash
# Add to crontab
0 9 * * MON /path/to/scripts/weekly_report.sh

# Or use GitHub Actions (already configured)
```

## Key Metrics

- **Feature Velocity**: Features delivered per week
- **Customer-Driven Index**: % of commits addressing customer needs
- **Technical Debt Ratio**: % of commits addressing technical debt
- **Release Readiness**: 0-100 score for release preparedness
- **Business Impact Score**: % of commits with direct business value

## Environment Variables

```bash
# Slack notifications
export SLACK_WEBHOOK_URL="your-webhook-url"

# Email notifications
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

## Configuration Files

- `config/notifications.json`: Notification settings
- `config/product_metrics.json`: Metric thresholds and targets
- `reports/`: Generated reports
- `logs/`: System logs
'''

        with open(self.base_dir / "PRODUCT_ANALYTICS.md", 'w') as f:
            f.write(readme_content)
        
        print("📚 Created documentation")
    
    def _set_permissions(self):
        """Set executable permissions on scripts."""
        scripts = [
            self.scripts_dir / "weekly_report.sh",
            self.scripts_dir / "product_insights_cli.py",
            self.scripts_dir / "product_analytics.py",
            self.scripts_dir / "notification_system.py"
        ]
        
        for script in scripts:
            if script.exists():
                os.chmod(script, 0o755)
        
        print("🔐 Set script permissions")

if __name__ == "__main__":
    setup = ProductAnalyticsSetup()
    setup.run_setup()