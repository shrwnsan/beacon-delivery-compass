# Configuration Guide

Beacon uses JSON configuration files to customize its behavior. Configuration files are located in the `config/` directory.

## notifications.json
Configures alert thresholds and notification channels for significant code changes.

### Structure
```json
{
  "thresholds": {
    "high_impact": 50,
    "medium_impact": 20
  },
  "channels": ["slack", "email"],
  "slack_webhook": "https://hooks.slack.com/services/...",
  "email_recipients": ["team@example.com"]
}
```

### Fields
- **thresholds**: Defines impact level boundaries
  - `high_impact`: Minimum lines changed for high impact classification
  - `medium_impact`: Minimum lines changed for medium impact classification
- **channels**: Notification delivery methods (slack, email, webhook)
- **slack_webhook**: Webhook URL for Slack integration
- **email_recipients**: List of email addresses to receive notifications

## product_metrics.json
Defines custom product metrics to track alongside code changes.

### Structure
```json
{
  "metrics": [
    {
      "name": "user_engagement",
      "query": "SELECT COUNT(*) FROM events WHERE event_type = 'engagement'",
      "threshold": 1000
    },
    {
      "name": "feature_adoption",
      "query": "SELECT COUNT(DISTINCT user_id) FROM feature_usage",
      "threshold": 500
    }
  ]
}
```

### Fields
- **metrics**: List of custom metrics to track
  - `name`: Unique identifier for the metric
  - `query`: SQL query to fetch metric value
  - `threshold`: Target value for the metric

## Location-Based Configuration
Beacon automatically detects environment-specific configurations:

1. Checks for `config/local/` directory
2. Falls back to `config/` for default configurations

Example directory structure:
```
config/
  notifications.json       # Default configuration
  product_metrics.json     # Default configuration
  local/
    notifications.json     # Environment-specific override
```

## Reloading Configuration
Beacon automatically reloads configuration:
- When files are modified during runtime
- Before each analysis run
- On receiving SIGHUP signal (Unix systems)

## Verification
Check your configuration with:
```bash
beaconled validate-config
```

## Example Workflow
1. Create `config/local/notifications.json` for development environment
2. Set lower thresholds for testing:
```json
{
  "thresholds": {
    "high_impact": 20,
    "medium_impact": 5
  }
}
```
3. Run analysis to see adjusted impact assessments

> **Note**: Always back up configurations before major changes