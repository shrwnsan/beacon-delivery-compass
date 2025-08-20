#!/bin/bash
# Weekly Product Insights Report Generator
# Add this to your crontab: 0 9 * * MON /path/to/weekly_report.sh

cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true

echo "Generating weekly product insights..."
python scripts/product_insights_cli.py weekly --since 1w > reports/weekly_report.txt

# Send notifications if configured
python scripts/notification_system.py process insights.json

echo "Weekly report generated: reports/weekly_report.txt"
