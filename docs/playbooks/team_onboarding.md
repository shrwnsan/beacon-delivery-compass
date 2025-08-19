# Team Onboarding Guide: Week 1

## Day 1: Initial Setup and First Run
1. Install Beacon Delivery Compass using the [installation guide](../installation.md)
2. Run your first weekly report:
   `beaconled --since 1w --format extended > weekly_report.txt`
3. Share the report with your team using the [share template](../weekly_playbook.md#share-template)
4. Assign owners for key findings

## Day 2-3: Data Collection and Trend Analysis
1. Run the report again to collect JSON data:
   `beaconled --since 1w --format json > weekly_report.json`
2. Store this JSON file in your team's dashboard directory
3. Keep the last 4 JSON files to track trends over time

## Day 4-5: Automation Setup
1. Set up a CI job using the [GitHub Actions recipe](../integrations.md#weekly-ci-job)
2. Create a Slack webhook for daily summaries using the [Slack integration guide](../integrations.md#slack-webhook)

## Day 6-7: Full Workflow Implementation
1. Run the Weekly Product Review following the [playbook guide](../weekly_playbook.md)
2. Discuss findings, assign action items, and plan improvements
3. Celebrate your first successful week with Beacon!
