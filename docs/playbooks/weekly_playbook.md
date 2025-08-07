# Playbook — Weekly Product Review

Audience: Product leadership (PMs, Heads of Eng). Goal: consistent, outcome-driven review grounded in code reality.

Purpose
- Make product decisions with engineering truth
- Highlight progress, risk, and scope movement
- Align roadmap and commitments with actual changes

Inputs (prepare before the meeting)
- Extended report (human-readable): ../weekly_report.txt
- JSON metrics (for trends/dashboards): ../weekly_report.json
- Notable PRs/changes list (optional)

Agenda (30 minutes)
1) Outcomes recap (5m)
   - What shipped, what moved the needle, what slipped
2) Delivery signals (10m) — from Beacon
   - Velocity: commits, files changed, lines added/removed
   - Impact: high/medium/low areas; core components touched
   - Risk movement: large diffs, concentrated ownership, hot spots
   - Scope churn: net change vs previous week
3) Decisions (10m)
   - Reconfirm priorities, unblock owners, adjust scope
4) Actions & owners (5m)
   - Assign follow-ups, set due dates

How to produce the signals
```bash
# From repo root with venv active
beaconled --range --since "1 week ago" --format extended > weekly_report.txt
beaconled --range --since "1 week ago" --format json > weekly_report.json
```

What “good” looks like
- Clear linkage from changes to product outcomes
- Risk acknowledged with owners and dates
- Minimal status theater; facts over narratives
- Trend lines visible over 4–8 weeks

Red flags to watch
- Large diffs in core components without tests
- High activity with low user impact
- Ownership bottlenecks (one person dominates)
- Persistent scope churn without decisions

Share-out template
- Summary: 2–3 bullets on outcomes
- Highlights: Top 3 meaningful changes (links/areas)
- Risks: Top 3 with owner + mitigation date
- Next week: 2–3 commitments

Links
- Quickstart: ../quickstart.md
- Usage Guide: ../usage.md
- Installation: ../installation.md
- Docs Home: ../README.md