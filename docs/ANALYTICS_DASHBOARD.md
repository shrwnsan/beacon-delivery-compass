# Analytics Dashboard

A short interpretation guide for Product/PM stakeholders. Use this to read weekly reports quickly.

## The 4 signals to read first
- Velocity: commits, files, lines added/removed. Expect consistency week to week. Big swings = context change or risk.
- Impact: which components changed (core logic, tests, docs, config). Healthy mixes include tests with core changes.
- Risk movement: large diffs in core or concentrated ownership indicate higher risk; call out in review.
- Scope churn: net change vs previous period; negative can be cleanup, positive may be new feature work.

## What “good” looks like
- Balanced additions/deletions across components
- Tests present for high-impact core changes
- No single contributor dominates core areas
- Week-over-week velocity within expected band

## Example interpretation
- High additions with few deletions: new feature work; confirm test coverage and downstream impacts.
- Many config changes: investigate release/deployment changes or environment stability.
- Spike in core logic without tests: flag for verification and follow-up.

## Where the numbers come from
Generated from git history using Beacon’s CLI. For details on producing reports, see Engineer Quickstart: delivery/quickstart.md.

---

Developer details, dashboards, and integrations are below (optional).

## Detailed metrics and examples
- Commit Frequency, Files Changed, Lines Added/Deleted, Net Change, Component Impact
- Health indicators: balanced vs warning vs critical
- Sample visualizations and scripts for analytics

[Developer reference sections preserved below]