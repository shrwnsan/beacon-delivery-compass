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
beaconled --since 1d --format extended
```

### Integrating with `pre-commit` Framework
For more robust commit message enforcement, integrate with the `pre-commit` framework:

1.  **Install `pre-commit`:**
    ```bash
    pip install pre-commit
    ```

2.  **Create a `.pre-commit-config.yaml` file in the root of your repository:**
    ```yaml
    repos:
    -   repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.4.0
        hooks:
        -   id: check-added-large-files
        -   id: check-yaml
        -   id: end-of-file-fixer
        -   id: trailing-whitespace

    # Add beaconled hook here (example)
    # -   repo: local
    #     hooks:
    #     -   id: beaconled-commit-message
    #         name: Check commit message with beaconled
    #         entry: beaconled --commit
    #         language: system
    #         types: [text]
    ```

3.  **Configure the `beaconled` hook:**
    *   You'll need to create a custom hook that uses `beaconled` to check the commit message. The example above shows how to define a local hook that runs `beaconled --commit` on each commit.
    *   You may need to adjust the `entry` and `types` settings to match your specific needs.  For example, you might want to use a script to parse the output of `beaconled` and enforce specific commit message formats.

4.  **Install the pre-commit hooks:**
    ```bash
    pre-commit install
    ```

5.  **Run the pre-commit hooks:**
    ```bash
    pre-commit run --all-files
    ```

Now, every time you commit changes, the pre-commit hooks will run automatically and check your commit messages. If any issues are found, the commit will be rejected, and you'll need to fix the commit message before you can commit the changes.

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
      uses: actions/upload-artifact@v4
      with:
        name: beaconled-analytics
        path: commit-stats.json
```

#### Advanced GitHub Actions Workflow
```yaml
# .github/workflows/beaconled-advanced.yml
name: Beacon Advanced Analytics

on:
  schedule:
    - cron: '0 0 * * 1'  # Run every Monday at midnight
  workflow_dispatch:

jobs:
  analytics:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install beaconled

    - name: Generate weekly report
      run: |
        beaconled --since 2w --until 1d --format json > sprint-report.json

    - name: Upload report
      uses: actions/upload-artifact@v4
      with:
        name: weekly-analytics-${{ matrix.python-version }}
        path: sprint-report.json

    - name: Send to Slack
      if: matrix.python-version == '3.8'
      uses: slackapi/slack-github-action@v1.23.0
      with:
        channel-id: 'C12345678' # Slack channel ID
        slack-message: "Weekly analytics report generated for Python ${{ matrix.python-version }}"
      env:
        SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
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
    - beaconled --since 1w --format extended > weekly-report.txt
    - echo "Weekly report generated"
  artifacts:
    paths:
      - weekly-report.txt
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
beaconled --since 1d --format extended

# Save to file for sharing
beaconled --since 1d --format json > daily-report.json
```

### Sprint Planning Integration

```bash
#!/bin/bash
# sprint-planning.sh
source .venv/bin/activate

echo "📈 Sprint Analytics"
echo "=================="
beaconled --since 2w --format extended

# Generate team velocity metrics
beaconled --since 1w --format json | jq '.total_commits'
```

### Code Review Process

```bash
#!/bin/bash
# pre-review-check.sh
source .venv/bin/activate

# Analyze changes since main branch
beaconled --since main --format extended

# Check for large changes
stats=$(beaconled --since main --format json)
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
    stats = analyzer.analyze_range(since="1d")

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
        stats = analyzer.analyze_range(since="1w")
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
            "command": "source .venv/bin/activate && beaconled --since '1 week ago' --format extended",
            "group": "build"
        },
        {
            "label": "Beacon: Custom Range",
            "type": "shell",
            "command": "source .venv/bin/activate && beaconled --since '${input:sinceDate}' --format extended",
            "group": "build",
            "problemMatcher": []
        }
    ],
    "inputs": [
        {
            "id": "sinceDate",
            "type": "promptString",
            "description": "Enter since date (e.g., '1 week ago'):"
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
    <option name="PARAMETERS" value="--since 1w --format extended" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
  </configuration>
  <configuration default="false" name="Beacon Custom" type="PythonConfigurationType">
    <option name="SCRIPT_NAME" value="beaconled" />
    <option name="PARAMETERS" value="--since $since$ --format $format$" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="PARAM_ENV">
      <map>
        <entry key="since" value="1w" />
        <entry key="format" value="extended" />
      </map>
    </option>
  </configuration>
</component>
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

## Next Steps
- [API Reference](api-reference.md) - Complete command reference
- [Usage Guide](usage.md) - Practical examples and workflows
- [Analytics Dashboard](ANALYTICS_DASHBOARD.md) - Metric interpretation guide
