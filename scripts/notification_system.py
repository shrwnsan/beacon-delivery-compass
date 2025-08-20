#!/usr/bin/env python
"""
Stakeholder Notification System
Automated notifications for product insights and alerts.
"""

import json
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List

import requests


class NotificationSystem:
    """Handles stakeholder notifications for product insights."""

    def __init__(self, config_path: str = "config/notifications.json"):
        self.config = self._load_config(config_path)
        self.notification_queue = []

    def _load_config(self, config_path: str) -> Dict:
        """Load notification configuration."""
        default_config = {
            "slack": {
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                "channel": "#product-alerts",
                "enabled": bool(os.getenv("SLACK_WEBHOOK_URL")),
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": os.getenv("EMAIL_USERNAME", ""),
                "password": os.getenv("EMAIL_PASSWORD", ""),
                "enabled": bool(os.getenv("EMAIL_USERNAME")),
            },
            "recipients": {
                "product_managers": ["pm@company.com"],
                "engineering_leads": ["lead@company.com"],
                "executives": ["exec@company.com"],
            },
            "thresholds": {
                "feature_velocity": {"warning": 2, "critical": 1},
                "technical_debt_ratio": {"warning": 30, "critical": 40},
                "customer_driven_index": {"warning": 40, "critical": 30},
            },
        }

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                # Validate config structure
                self._validate_config(config)
                return {**default_config, **config}
        except FileNotFoundError:
            return default_config
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON in config file: {e}"
            raise ValueError(msg)

    def _validate_config(self, config: Dict) -> None:
        """Validate configuration structure and values."""
        # Validate webhook URLs
        if "slack" in config and "webhook_url" in config["slack"]:
            webhook_url = config["slack"]["webhook_url"]
            if webhook_url and not webhook_url.startswith("https://hooks.slack.com/"):
                msg = "Invalid Slack webhook URL format"
                raise ValueError(msg)

        # Validate email settings
        if "email" in config:
            email_config = config["email"]
            if email_config.get("enabled", False):
                if not email_config.get("username"):
                    msg = "Email username required when email is enabled"
                    raise ValueError(msg)
                if not email_config.get("smtp_server"):
                    msg = "SMTP server required when email is enabled"
                    raise ValueError(msg)
                if not isinstance(email_config.get("smtp_port"), int):
                    msg = "SMTP port must be an integer"
                    raise ValueError(msg)

    def process_insights(self, insights: Dict) -> None:
        """Process insights and trigger appropriate notifications."""
        alerts = insights.get("alerts", [])

        for alert in alerts:
            self._handle_alert(alert, insights)

    def _handle_alert(self, alert: Dict, insights: Dict) -> None:
        """Handle individual alert based on severity."""
        severity = alert["severity"]

        if severity == "critical":
            self._send_immediate_alert(alert, insights)
        elif severity == "high":
            self._send_daily_digest(alert, insights)
        elif severity == "medium":
            self._send_weekly_summary(alert, insights)

    def _send_immediate_alert(self, alert: Dict, insights: Dict) -> None:
        """Send immediate alert for critical issues."""
        message = self._format_alert_message(alert, insights)

        # Send to Slack
        if self.config["slack"]["enabled"]:
            self._send_slack_alert(message, alert["severity"])

        # Send email
        if self.config["email"]["enabled"]:
            self._send_email_alert(message, alert["severity"])

    def _send_daily_digest(self, alert: Dict, insights: Dict) -> None:
        """Send daily digest for high-priority issues."""
        # Queue for daily digest
        self.notification_queue.append(
            {"type": "alert", "severity": "high", "alert": alert, "insights": insights}
        )

    def _send_weekly_summary(self, alert: Dict, insights: Dict) -> None:
        """Send weekly summary for medium-priority issues."""
        # Queue for weekly summary
        self.notification_queue.append(
            {
                "type": "alert",
                "severity": "medium",
                "alert": alert,
                "insights": insights,
            }
        )

    def send_weekly_report(self, insights: Dict) -> None:
        """Send comprehensive weekly report."""
        report = self._format_weekly_report(insights)

        # Send to all stakeholders
        recipients = (
            self.config["recipients"]["product_managers"]
            + self.config["recipients"]["engineering_leads"]
            + self.config["recipients"]["executives"]
        )

        if self.config["email"]["enabled"]:
            self._send_email_report(
                report, recipients, "Weekly Product Development Report"
            )

        if self.config["slack"]["enabled"]:
            self._send_slack_report(report)

    def _format_alert_message(self, alert: Dict, insights: Dict) -> str:
        """Format alert message for notifications."""
        return f"""
🚨 **Product Development Alert**

**Severity:** {alert["severity"].upper()}
**Message:** {alert["message"]}
**Action Required:** {alert["action"]}

**Current Metrics:**
{json.dumps(insights["metrics"], indent=2)}

**Timestamp:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}
"""

    def _format_weekly_report(self, insights: Dict) -> str:
        """Format comprehensive weekly report."""
        return f"""
📊 **Weekly Product Development Report**
Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}

**Key Metrics:**
{json.dumps(insights["metrics"], indent=2)}

**Recommendations:**
{chr(10).join(f"• {rec}" for rec in insights["recommendations"])}

**Alerts:**
{chr(10).join(f"• [{a['severity']}] {a['message']}" for a in insights["alerts"])}

**Next Actions:**
Review the attached insights and schedule follow-up discussions as needed.
"""

    def _send_slack_alert(self, message: str, severity: str) -> None:
        """Send alert to Slack."""
        webhook_url = self.config["slack"]["webhook_url"]
        channel = self.config["slack"]["channel"]

        payload = {
            "text": message,
            "channel": channel,
            "username": "Product Insights Bot",
            "icon_emoji": (
                ":warning:" if severity == "critical" else ":information_source:"
            ),
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=30, verify=True)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")

    def _send_email_alert(self, message: str, severity: str) -> None:
        """Send alert via email."""
        recipients = (
            self.config["recipients"]["product_managers"]
            + self.config["recipients"]["engineering_leads"]
        )

        subject = f"Product Development Alert - {severity.upper()}"
        self._send_email(recipients, subject, message)

    def _send_email_report(
        self, report: str, recipients: List[str], subject: str
    ) -> None:
        """Send email report."""
        self._send_email(recipients, subject, report)

    def _send_email(self, recipients: List[str], subject: str, body: str) -> None:
        """Send email using SMTP."""
        if not self.config["email"]["enabled"]:
            return

        try:
            # Validate recipients
            if not recipients or not all(
                isinstance(r, str) and "@" in r for r in recipients
            ):
                msg = "Invalid email recipients"
                raise ValueError(msg)

            msg = MIMEMultipart()
            msg["From"] = self.config["email"]["username"]
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(
                self.config["email"]["smtp_server"],
                self.config["email"]["smtp_port"],
                timeout=30,  # Add timeout to prevent hanging
            )
            server.starttls()
            server.login(
                self.config["email"]["username"], self.config["email"]["password"]
            )

            server.send_message(msg)
            server.quit()

        except Exception as e:
            print(f"Failed to send email: {e}")

    def create_notification_config(self) -> None:
        """Create sample notification configuration."""
        config = {
            "slack": {
                "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                "channel": "#product-alerts",
                "enabled": False,
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password",
                "enabled": False,
            },
            "recipients": {
                "product_managers": ["pm@company.com"],
                "engineering_leads": ["lead@company.com"],
                "executives": ["exec@company.com"],
            },
            "thresholds": {
                "feature_velocity": {"warning": 2, "critical": 1},
                "technical_debt_ratio": {"warning": 30, "critical": 40},
                "customer_driven_index": {"warning": 40, "critical": 30},
            },
        }

        config_path = Path("config/notifications.json")
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"Created notification config at {config_path}")
        print("Please update the configuration with your actual settings.")


class ActionTrigger:
    """Triggers actions based on analytics thresholds."""

    def __init__(self, config: Dict):
        self.config = config

    def check_triggers(self, insights: Dict) -> List[Dict]:
        """Check if any action triggers should be activated."""
        triggers = []

        # Parse metrics
        metrics = insights.get("metrics", {})

        # Check feature velocity
        velocity = float(metrics.get("feature_velocity", "0").split()[0])
        if velocity < self.config["thresholds"]["feature_velocity"]["critical"]:
            triggers.append(
                {
                    "trigger": "low_velocity",
                    "action": "resource_allocation_review",
                    "priority": "high",
                    "details": f"Feature velocity at {velocity} features/week",
                }
            )

        # Check technical debt
        debt_ratio = float(metrics.get("technical_debt_ratio", "0").split("%")[0])
        if debt_ratio > self.config["thresholds"]["technical_debt_ratio"]["critical"]:
            triggers.append(
                {
                    "trigger": "high_debt",
                    "action": "refactoring_sprint",
                    "priority": "critical",
                    "details": f"Technical debt at {debt_ratio}%",
                }
            )

        # Check customer focus
        customer_index = float(metrics.get("customer_driven_index", "0").split("%")[0])
        if (
            customer_index
            < self.config["thresholds"]["customer_driven_index"]["critical"]
        ):
            triggers.append(
                {
                    "trigger": "low_customer_focus",
                    "action": "product_research_session",
                    "priority": "medium",
                    "details": f"Customer-driven index at {customer_index}%",
                }
            )

        return triggers


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Notification System")
    parser.add_argument("action", choices=["setup", "test"], help="Action to perform")

    args = parser.parse_args()

    notifier = NotificationSystem()

    if args.action == "setup":
        notifier.create_notification_config()
    elif args.action == "test":
        # Test notification system
        test_insights = {
            "metrics": {
                "feature_velocity": "1.5 features/week",
                "technical_debt_ratio": "45%",
                "customer_driven_index": "25%",
            },
            "recommendations": ["Test recommendation"],
            "alerts": [
                {
                    "type": "test",
                    "severity": "high",
                    "message": "Test alert",
                    "action": "Test action",
                }
            ],
        }

        notifier.process_insights(test_insights)
        print("Test notification sent!")
