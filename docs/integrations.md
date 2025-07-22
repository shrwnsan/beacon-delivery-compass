# Integration Guide

This guide covers how to integrate Beacon into your development workflow, CI/CD pipelines, and team processes.

## Git Hooks Integration

### Post-Commit Hook
Automatically display commit statistics after each commit:

```bash
#!/bin/bash
# .git/hooks/post-commit
source .venv/bin/activate  # Adjust path as needed
beaconled --format standard
```

Make the hook executable:
```bash
chmod +x .git/hooks/post-commit
```

### Pre-Push Hook
Review your changes before pushing:

```bash
#!/bin/bash
# .git/hooks/pre-push
source .venv/bin/activate
echo "📊 Changes since last push:"
beaconled --range --since "1 day ago" --format extended
```

### Pre-Commit Hook (for team standards)
Check commit size and impact:

```bash
#!/bin/bash
# .git/hooks/pre-commit
source .venv/bin/activate

# Check if commit is too large
stats=$(beaconled --format json)
files_changed=$(echo $stats | jq '.files_changed')

if [ "$files_changed" -gt 20 ]; then
    echo "⚠️  Large commit detected ($files_changed files)"
    echo "Consider splitting into smaller commits"
    exit 1
fi
```

## CI/CD Pipeline Integration

### GitHub Actions

#### Basic Integration
```yaml
# .github/workflows/beaconled-analytics.yml
name: Beacon Analytics

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  analytics:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Full history for range analysis
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install Beacon
      run: pip install beaconled
    
    - name: Generate Commit Analytics
      run: |
        beaconled --format json > commit-stats.json
    
    - name: Upload Analytics
      uses: actions/upload-artifact@v3
      with:
        name: beaconled-analytics
        path: commit-stats.json
```

#### Weekly Team Report
```yaml
# .github/workflows/weekly-report.yml
name: Weekly Team Report

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  weekly-report:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install Beacon
      run: pip install beaconled
    
    - name: Generate Weekly Report
      run: |
        beaconled --range --since "1 week ago" --format extended > weekly-report.txt
    
    - name: Send to Slack
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: |
          📊 Weekly Development Report
          ```
          $(cat weekly-report.txt)
          ```
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - analytics

beaconled_analytics:
  stage: analytics
  image: python:3.8
  script:
    - pip install beaconled
    - beaconled --format json > beaconled-report.json
  artifacts:
    paths:
      - beaconled-report.json
    expire_in: 1 week

weekly_report:
  stage: analytics
  image: python:3.8
  only:
    - schedules
  script:
    - pip install beaconled
    - beaconled --range --since "1 week ago" --format extended > weekly-report.txt
    - echo "Weekly report generated"
  artifacts:
    paths:
      - weekly-report.txt
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Generate Analytics') {
            steps {
                sh '''
                    python -m venv .venv
                    source .venv/bin/activate
                    pip install beaconled
                    beaconled --format json > beaconled-report.json
                '''
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'beaconled-report.json'
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'beaconled-report.json',
                reportName: 'Beacon Analytics'
            ])
        }
    }
}
```

## Team Workflow Integration

### Daily Standup Automation

Create a daily standup script:

```bash
#!/bin/bash
# daily-standup.sh
source .venv/bin/activate

echo "🚀 Daily Development Summary"
echo "=========================="
beaconled --range --since "1 day ago" --format extended

# Save to file for sharing
beaconled --range --since "1 day ago" --format json > daily-report.json
```

### Sprint Planning Integration

```bash
#!/bin/bash
# sprint-planning.sh
source .venv/bin/activate

echo "📈 Sprint Analytics"
echo "=================="
beaconled --range --since "2 weeks ago" --format extended

# Generate team velocity metrics
beaconled --range --since "2 weeks ago" --format json | jq '.summary'
```

### Code Review Process

```bash
#!/bin/bash
# pre-review-check.sh
source .venv/bin/activate

# Analyze the PR branch
beaconled --range --since "main" --format extended

# Check for large changes
stats=$(beaconled --range --since "main" --format json)
files_changed=$(echo $stats | jq '.total_files_changed')

if [ "$files_changed" -gt 50 ]; then
    echo "⚠️  Large PR detected ($files_changed files)"
    echo "Consider breaking into smaller PRs"
fi
```

## Slack Integration

### Incoming Webhook

```python
#!/usr/bin/env python3
# slack-reporter.py
import json
import requests
from beaconled.core.analyzer import GitAnalyzer
from beaconled.formatters.json_format import JSONFormatter

def send_to_slack(webhook_url, channel="#dev-updates"):
    analyzer = GitAnalyzer()
    stats = analyzer.analyze_range(since="1 day ago")
    
    # Format for Slack
    message = {
        "channel": channel,
        "username": "Beacon Bot",
        "text": f"📊 Daily Development Report",
        "attachments": [{
            "color": "good",
            "fields": [
                {"title": "Commits", "value": str(stats.total_commits), "short": True},
                {"title": "Files Changed", "value": str(stats.total_files_changed), "short": True},
                {"title": "Lines Added", "value": str(stats.total_insertions), "short": True},
                {"title": "Lines Deleted", "value": str(stats.total_deletions), "short": True}
            ]
        }]
    }
    
    requests.post(webhook_url, json=message)

if __name__ == "__main__":
    import sys
    webhook_url = sys.argv[1]
    send_to_slack(webhook_url)
```

### Slack Bot Integration

```python
# slack-bot.py
from slack_bolt import App
from beaconled.core.analyzer import GitAnalyzer

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/beaconled")
def handle_beaconled_command(ack, say, command):
    ack()
    
    text = command["text"]
    if "weekly" in text:
        stats = analyzer.analyze_range(since="1 week ago")
        say(f"Weekly stats: {stats.total_commits} commits")
    else:
        stats = analyzer.analyze_commit()
        say(f"Latest commit: {stats.files_changed} files changed")
```

## IDE Integration

### VS Code Tasks

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Beacon: Current Commit",
            "type": "shell",
            "command": "source .venv/bin/activate && beaconled",
            "group": "build"
        },
        {
            "label": "Beacon: Weekly Report",
            "type": "shell",
            "command": "source .venv/bin/activate && beaconled --range --since '1 week ago' --format extended",
            "group": "build"
        }
    ]
}
```

### JetBrains IDEs (PyCharm, IntelliJ)

Create `.idea/beaconled.xml`:

```xml
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Beacon Weekly" type="PythonConfigurationType">
    <option name="SCRIPT_NAME" value="beaconled" />
    <option name="PARAMETERS" value="--range --since '1 week ago' --format extended" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
  </configuration>
</component>
```

## Docker Integration

### Dockerfile for Beacon

```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["beaconled"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  beaconled:
    build: .
    volumes:
      - ./:/workspace
    working_dir: /workspace
    command: ["--range", "--since", "1 week ago", "--format", "json"]
```

## Monitoring and Alerting

### Prometheus Metrics

```python
# prometheus-exporter.py
from prometheus_client import Counter, Gauge, start_http_server
from beaconled.core.analyzer import GitAnalyzer

commits_total = Counter('beaconled_commits_total', 'Total commits analyzed')
files_changed = Gauge('beaconled_files_changed', 'Files changed in last commit')
lines_added = Gauge('beaconled_lines_added', 'Lines added in last commit')

def collect_metrics():
    analyzer = GitAnalyzer()
    stats = analyzer.analyze_range(since="1 hour ago")
    
    commits_total.inc(stats.total_commits)
    if stats.total_commits > 0:
        latest = analyzer.analyze_commit()
        files_changed.set(latest.files_changed)
        lines_added.set(latest.lines_added)

if __name__ == "__main__":
    start_http_server(8000)
    while True:
        collect_metrics()
        time.sleep(300)  # Collect every 5 minutes
```

## Best Practices

### Security
- Never commit sensitive data in analytics
- Use environment variables for configuration
- Sanitize output before sharing
- Limit access to repository data

### Performance
- Use date ranges for large repositories
- Cache results for frequently accessed data
- Consider sampling for very active repositories
- Use JSON format for programmatic processing

### Team Adoption
- Start with simple integrations
- Provide clear documentation
- Gather feedback regularly
- Iterate based on team needs
