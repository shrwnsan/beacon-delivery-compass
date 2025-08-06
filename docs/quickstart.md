# Quickstart — 10 Minutes to Weekly Product Signals

Audience: Product leaders and PMs who want an executive-ready delivery readout from real code changes.

Outcome after this guide:
- Weekly product review report you can run every Friday
- JSON metrics suitable for dashboards
- Clear next steps for CI automation

Prerequisites
- Python 3.8+ installed
- Git repository with history
- Terminal access

1) Install
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install beaconled
```

2) Run against your repo
From the root of the repository you want to analyze:
```bash
beaconled --format extended > weekly_report.txt
beaconled --format json > weekly_report.json
```

3) Get a weekly window
```bash
# Last 7 days
beaconled --range "1w" --format extended > weekly_report.txt
beaconled --range "1w" --format json > weekly_report.json
```

4) Read the signals (what to look for)
- Velocity: commits, files changed, lines added/removed
- Impact: high/medium/low by component/file type
- Risk movement: large diffs in core components, concentrated ownership
- Scope churn: net change vs. prior week

5) Share in your Weekly Product Review
- Paste top-level metrics and highlights
- Link to notable PRs/areas changed
- Add decisions and follow-ups

Recommended cadence
- Run extended format for the meeting: ./weekly_report.txt
- Store json for dashboards: ./weekly_report.json
- Compare week-over-week: keep last 4 json files for trend lines

Next steps
- Playbook: ./playbooks/weekly-product-review.md
- Full usage: ./usage.md
- Installation details: ./installation.md