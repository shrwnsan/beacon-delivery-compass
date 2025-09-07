# Frequently Asked Questions (FAQ)

## General Questions

### What is the enhanced extended format?
The enhanced extended format is an advanced output format for BeaconLED that provides comprehensive analytics and insights about your repositorys development patterns, team collaboration, and code quality trends.

### How does it differ from the basic extended format?
The enhanced format builds upon the basic extended format by adding:
- Time-based analytics (velocity trends, activity heatmaps)
- Team collaboration analysis (co-authorship patterns, knowledge distribution)
- Code quality insights (churn metrics, complexity trends)
- Risk assessment (risk indicators, hotspot detection)
- Improved visual formatting with better use of Unicode characters

### Is it backward compatible?
Yes, completely. All existing `--format extended` commands work exactly as before. The enhanced format is additive, not replacement.

## Installation and Setup

### How do I get the enhanced extended format?
The enhanced extended format is included in BeaconLED version 1.0.0 and later. Update your installation:

```bash
pip install --upgrade beaconled
```

### Do I need to install additional dependencies?
No, all required dependencies are included with the main BeaconLED package.

### Can I use it with my existing BeaconLED installation?
If you have version 1.0.0 or later, yes. If you have an older version, youll need to update.

## Usage Questions

### How do I use the enhanced extended format?
Simply change your format parameter:

```bash
# Instead of:
beaconled --format extended --since 1m

# Use:
beaconled --format enhanced-extended --since 1m
```

### What date formats are supported?
Relative formats:
- `1d` (1 day ago)
- `2w` (2 weeks ago)
- `3m` (3 months ago)
- `1y` (1 year ago)

Absolute formats:
- `YYYY-MM-DD` (date only)
- `YYYY-MM-DD HH:MM` (date and time)
- `YYYY-MM-DDTHH:MM:SS` (ISO 8601)
- `YYYY-MM-DDTHH:MM:SS+00:00` (with timezone)

### Can I analyze specific date ranges?
Yes:

```bash
beaconled --format enhanced-extended --since 2025-01-01 --until 2025-02-01
```

### How do I disable emojis in the output?
Use the `--no-emoji` flag:

```bash
beaconled --format enhanced-extended --since 1w --no-emoji
```

## Analytics Questions

### What is the bus factor analysis?
The bus factor measures how concentrated knowledge is in your team. It answers the question: "How many people would need to be hit by a bus before the project is in serious trouble?"

### How are risk factors calculated?
Risk factors consider multiple metrics:
- Code churn (frequently modified files)
- Knowledge concentration (files known by few people)
- Recent large changes (big commits in recent history)
- Complexity trends (increasingly complex code)

### What is a knowledge silo?
A knowledge silo is an area of the codebase where knowledge is concentrated among only one or a few team members, creating a risk if those members are unavailable.

### How is collaboration measured?
Collaboration is measured through:
- Co-authorship patterns (how often team members work together)
- Review participation (who reviews whose code)
- Knowledge distribution (how expertise is spread across the team)

## Performance Questions

### Why is the first run slower?
The first run builds caches for subsequent analyses. Subsequent runs with the same or similar parameters will be faster due to caching.

### How much memory does it use?
Memory usage depends on repository size:
- Small repositories (< 1,000 commits): < 50MB
- Medium repositories (< 10,000 commits): < 200MB
- Large repositories: < 500MB

### Can I disable caching?
Yes, set the `BEACON_DISABLE_CACHE=1` environment variable.

### How can I optimize performance for large repositories?
1. Use smaller date ranges
2. Run during off-peak hours
3. Ensure sufficient system resources
4. Consider disabling caching if memory is limited

## Troubleshooting Questions

### The output looks the same as before
Make sure you are using `--format enhanced-extended` (not just `--format extended`) and scroll down to see all sections.

### Unicode characters are displaying incorrectly
This is usually a terminal encoding issue. Try:

```bash
export PYTHONIOENCODING=utf-8
```

Or disable emojis:

```bash
beaconled --format enhanced-extended --since 1w --no-emoji
```

### I am getting date parsing errors
Ensure all dates are in UTC and use supported formats. All times must be in UTC.

### I am getting permission errors
Ensure you have read permissions on the repository. Test with a simple repository first.

## Integration Questions

### Can I parse the output programmatically?
Yes, though the enhanced format has more sections than the basic format. The basic structure remains the same.

### How do I integrate this with my CI/CD pipeline?
You can run it as part of your pipeline and save the output:

```bash
beaconled --format enhanced-extended --since 1w > analysis.txt
```

### Can I use it with monitoring tools?
Yes, you can schedule regular analyses and process the output with your monitoring tools.

## Best Practices

### What time range should I analyze?
- For regular monitoring: 1-4 weeks
- For retrospective analysis: 3-6 months
- For onboarding new team members: 6-12 months

### How often should I run analyses?
- Weekly for active projects
- Monthly for less active projects
- Before major releases

### How should I use the insights?
1. **Team Retrospectives**: Discuss collaboration patterns and knowledge distribution
2. **Risk Management**: Address identified risk factors proactively
3. **Process Improvement**: Use insights to improve development practices
4. **Onboarding**: Help new team members understand the codebase

### What should I watch for?
- Decreasing bus factor (knowledge becoming more concentrated)
- Increasing code churn in specific areas
- Declining collaboration scores
- Emerging knowledge silos

## Technical Questions

### What programming languages are supported?
BeaconLED works with any Git repository, regardless of programming language.

### Does it work with Git hosting services?
Yes, it works with repositories hosted on GitHub, GitLab, Bitbucket, or any other Git hosting service.

### Can I analyze subdirectories?
Yes, use the `--repo` parameter to specify the path to any Git repository or subdirectory.

### How does it handle merge commits?
Merge commits are processed as part of the overall commit history, contributing to analytics like velocity trends and collaboration patterns.

## Contributing and Support

### How can I contribute?
Check the CONTRIBUTING.md file in the repository for guidelines on contributing.

### Where can I report issues?
Create an issue on the GitHub repository.

### Is there a community forum?
Check the projects GitHub Discussions page for community support.

### How can I stay updated?
Watch the GitHub repository for releases and updates.
