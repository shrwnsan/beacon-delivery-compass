# Git Worktree Setup for Issue #10 Development

## Overview

This guide explains how to set up and use git worktrees for parallel development of the Issue #10 enhancement tasks. Using worktrees allows multiple developers to work on different features simultaneously without conflicts.

## Prerequisites

- Git version 2.5 or higher
- Understanding of git branches and basic git operations
- Access to the beacon-delivery-compass repository

## Initial Setup

### 1. Create Feature Branch Structure

First, create the main feature branch and task branches from the main repository:

```bash
# Navigate to main repository
cd /path/to/beacon-delivery-compass

# Create main feature branch
git checkout -b issue-10/enhanced-extended-format

# Create task-specific branches (don't switch to them yet)
git branch issue-10/task-01-time-analytics
git branch issue-10/task-02-team-metrics
git branch issue-10/task-03-code-quality
git branch issue-10/task-04-risk-indicators
git branch issue-10/task-05-ascii-charts
git branch issue-10/task-06-heatmap-viz
git branch issue-10/task-07-trend-charts
git branch issue-10/task-08-rich-formatter
git branch issue-10/task-09-section-renderers
git branch issue-10/task-10-emoji-enhancement
git branch issue-10/task-11-integration
git branch issue-10/task-12-documentation

# Push all branches to remote
git push -u origin issue-10/enhanced-extended-format
git push -u origin issue-10/task-01-time-analytics
git push -u origin issue-10/task-02-team-metrics
# ... (repeat for all task branches)
```

### 2. Create Worktree Directories

Create separate worktree directories for each task:

```bash
# Create worktrees for each task (run from main repo directory)
git worktree add ../beacon-task-01-time-analytics issue-10/task-01-time-analytics
git worktree add ../beacon-task-02-team-metrics issue-10/task-02-team-metrics
git worktree add ../beacon-task-03-code-quality issue-10/task-03-code-quality
git worktree add ../beacon-task-04-risk-indicators issue-10/task-04-risk-indicators
git worktree add ../beacon-task-05-ascii-charts issue-10/task-05-ascii-charts
git worktree add ../beacon-task-06-heatmap-viz issue-10/task-06-heatmap-viz
git worktree add ../beacon-task-07-trend-charts issue-10/task-07-trend-charts
git worktree add ../beacon-task-08-rich-formatter issue-10/task-08-rich-formatter
git worktree add ../beacon-task-09-section-renderers issue-10/task-09-section-renderers
git worktree add ../beacon-task-10-emoji-enhancement issue-10/task-10-emoji-enhancement
git worktree add ../beacon-task-11-integration issue-10/task-11-integration
git worktree add ../beacon-task-12-documentation issue-10/task-12-documentation
```

## Directory Structure After Setup

```
/path/to/
├── beacon-delivery-compass/           # Main repository
├── beacon-task-01-time-analytics/     # Task 1 worktree
├── beacon-task-02-team-metrics/       # Task 2 worktree
├── beacon-task-03-code-quality/       # Task 3 worktree
└── ...                                # Other task worktrees
```

## Working with Worktrees

### Starting Work on a Task

```bash
# Navigate to the specific task worktree
cd ../beacon-task-01-time-analytics

# Verify you're on the correct branch
git branch
# Should show: * issue-10/task-01-time-analytics

# Create your virtual environment (if needed)
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Start development
```

### Development Workflow

```bash
# Make your changes
# Edit files, add new modules, etc.

# Regular git workflow
git add .
git commit -m "feat: implement time-based analytics core functionality"

# Push to your task branch
git push origin issue-10/task-01-time-analytics
```

### Syncing with Main Branch

Regularly sync your task branch with the main branch:

```bash
# In your task worktree
cd ../beacon-task-01-time-analytics

# Fetch latest changes
git fetch origin

# Merge main branch changes
git merge origin/main

# Or rebase (if preferred)
git rebase origin/main

# Push updated branch
git push origin issue-10/task-01-time-analytics
```

### Inter-task Dependencies

Some tasks may depend on others. Handle dependencies using this approach:

```bash
# If Task 5 depends on Task 1, merge Task 1's changes
cd ../beacon-task-05-ascii-charts

# Fetch all branches
git fetch origin

# Merge the dependency
git merge origin/issue-10/task-01-time-analytics

# Continue development
```

## Task Assignment Process

### 1. Claim a Task

```bash
# Create an issue comment or team communication
# Example: "I'm taking Task 01: Time-Based Analytics"

# Navigate to the task worktree
cd ../beacon-task-01-time-analytics

# Create a progress marker
echo "Developer: John Doe" > .task-assignment
echo "Started: $(date)" >> .task-assignment
git add .task-assignment
git commit -m "docs: claim task 01 - time analytics"
git push origin issue-10/task-01-time-analytics
```

### 2. Track Progress

Use conventional commits to track progress:

```bash
# Work in progress
git commit -m "wip: initial time analyzer structure"

# Feature complete
git commit -m "feat: complete time analytics implementation"

# Tests added
git commit -m "test: add comprehensive time analytics tests"

# Ready for review
git commit -m "ready: task 01 complete and tested"
```

## Integration Process

### 1. Prepare for Integration

```bash
# In your task worktree
cd ../beacon-task-01-time-analytics

# Ensure all tests pass
python -m pytest tests/

# Run linting
ruff check src/ tests/
black src/ tests/

# Update documentation
# Update relevant docs

# Final commit
git add .
git commit -m "ready: task 01 final integration prep"
git push origin issue-10/task-01-time-analytics
```

### 2. Create Pull Request

```bash
# Use GitHub CLI or web interface
gh pr create --title "feat: implement time-based analytics (Task 01)" \
             --body "Implements Task 01 from Issue #10 enhancement plan" \
             --base issue-10/enhanced-extended-format \
             --head issue-10/task-01-time-analytics
```

### 3. Integration into Main Feature Branch

After code review and approval:

```bash
# Switch to main feature branch (in main repo)
cd /path/to/beacon-delivery-compass
git checkout issue-10/enhanced-extended-format

# Merge the task branch
git merge origin/issue-10/task-01-time-analytics

# Run integration tests
python -m pytest tests/integration/

# Push integrated changes
git push origin issue-10/enhanced-extended-format
```

## Cleanup

### Removing Completed Worktrees

```bash
# After task is integrated and branch is merged
cd /path/to/beacon-delivery-compass

# Remove the worktree
git worktree remove ../beacon-task-01-time-analytics

# Delete the remote branch (after integration)
git push origin --delete issue-10/task-01-time-analytics

# Delete local branch
git branch -d issue-10/task-01-time-analytics
```

## Best Practices

### 1. Environment Management

Each worktree should have its own virtual environment:

```bash
cd ../beacon-task-01-time-analytics
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Testing Isolation

Run tests in each worktree independently:

```bash
# Test only your changes
python -m pytest tests/unit/analytics/test_time_analyzer.py

# Test broader integration
python -m pytest tests/
```

### 3. Communication

- Update task status regularly in team communication
- Use descriptive commit messages
- Document any inter-task dependencies
- Create draft PRs early for visibility

### 4. Conflict Resolution

If conflicts arise during integration:

```bash
# Fetch latest changes
git fetch origin

# Attempt automatic merge
git merge origin/issue-10/enhanced-extended-format

# If conflicts, resolve manually
# Edit conflicted files
git add .
git commit -m "resolve: merge conflicts with main feature branch"
```

## Troubleshooting

### Common Issues

**Worktree won't create:**
```bash
# Clean up any stale worktrees
git worktree prune
```

**Branch doesn't exist:**
```bash
# Create the branch first
git branch issue-10/task-01-time-analytics
```

**Permission issues:**
```bash
# Ensure proper permissions
chmod +x scripts/setup-worktree.sh
```

### Getting Help

- Review git worktree documentation: `git help worktree`
- Check team communication channels
- Consult the main project maintainer

---

This workflow enables efficient parallel development while maintaining code quality and integration safety.
