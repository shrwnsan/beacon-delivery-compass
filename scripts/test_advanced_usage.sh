#!/bin/bash
set -e

# Advanced Usage Test Suite for beacon-delivery-compass
#
# This script generates temporary output files (*.json, *.md, *.png) that contain
# email addresses and other sensitive data. These files are:
# - Saved to scripts/test_outputs/ directory
# - Added to .gitignore to prevent accidental commits
# - Cleaned up only when --cleanup flag is used
#
# Usage:
#   ./scripts/test_advanced_usage.sh           # Keep output files for inspection
#   ./scripts/test_advanced_usage.sh --cleanup # Remove output files after tests

# Get script directory for relative paths
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
OUTPUT_DIR="$SCRIPT_DIR/test_outputs"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Helper functions
print_test_header() {
    echo -e "\n\033[1;34m=== $1 ===\033[0m"
}

print_section_header() {
    echo -e "\n\033[1;32m\n========================================\033[0m"
    echo -e "\033[1;32m$1\033[0m"
    echo -e "\033[1;32m========================================\033[0m"
}

print_section_header "BASIC FUNCTIONALITY TESTS"

# Test 1: Single commit info (simplest test)
print_test_header "Test 1: Single commit information (latest)"
echo "Command: beaconled --format json"
beaconled --format json | jq '{
    commit: .hash[0:7],
    author: .author,
    date: .date,
    files_changed: .files_changed,
    lines_added: .lines_added,
    lines_deleted: .lines_deleted
}'

# Test 2: File details from latest commit
print_test_header "Test 2: File-level details from latest commit"
echo "Command: beaconled --format json | jq '.files'"
beaconled --format json | jq '.files[0:3] | map({
    path: .path,
    lines_added: .lines_added,
    lines_deleted: .lines_deleted
})'

print_section_header "DATE RANGE TESTS"

# Test 3: Simple relative dates
print_test_header "Test 3: Last 7 days (relative date)"
echo "Command: beaconled --since '7d' --format json"
beaconled --since '7d' --format json | jq '{
    total_commits: .total_commits,
    total_files_changed: .total_files_changed,
    period: "\(.start_date) to \(.end_date)"
}'

# Test 4: Future date (should be empty)
print_test_header "Test 4: Future date range (should be empty)"
FUTURE_DATE=$(date -v+1y -u +"%Y-%m-%d")
echo "Command: beaconled --since '$FUTURE_DATE' --format json"
beaconled --since "$FUTURE_DATE" --format json | jq '{
    total_commits: .total_commits,
    message: (if .total_commits == 0 then "Empty as expected" else "Unexpected data" end)
}'

print_section_header "ANALYSIS TESTS"

# Test 5: Author analysis
print_test_header "Test 5: Author contributions (last month)"
echo "Command: beaconled --since '1m' --format json | jq author analysis"
beaconled --since '1m' --format json | jq 'if .commits and (.commits | length) > 0 then
    (.commits | group_by(.author) | map({
        author: .[0].author,
        commits: length,
        files_changed: (map(.files_changed // 0) | add),
        lines_added: (map(.lines_added // 0) | add)
    }) | sort_by(.commits) | reverse | .[0:5])
else
    [{message: "No commits found"}]
end'

# Test 6: Basic health overview
print_test_header "Test 6: Basic Code Health Overview"
echo "Command: beaconled --since '1m' --format json | jq health metrics"
beaconled --since '1m' --format json | jq 'if .total_commits > 0 then
    {
        period: "\(.start_date) to \(.end_date)",
        total_commits: .total_commits,
        total_files_changed: .total_files_changed,
        stability_metrics: {
            avg_files_per_commit: (.total_files_changed / .total_commits | floor * 100 / 100),
            commit_frequency_per_day: (.total_commits / 30 | floor * 100 / 100)
        }
    }
else
    {message: "No commits found in the specified range"}
end'

print_section_header "CODE HEALTH EVOLUTION TESTS"

# Test 7: Technical debt assessment with scoring guidance
print_test_header "Test 7: Technical Debt Assessment"
echo "Command: beaconled --since '2w' --format json | jq technical debt analysis"
beaconled --since '2w' --format json | jq 'if .commits and (.commits | length) > 0 then
    {
        analysis_period: "\(.start_date) to \(.end_date)",
        total_commits: .total_commits,
        large_commits: [.commits[] | select(.files_changed > 10) | {
            hash: .hash[0:7],
            files_changed: .files_changed,
            message: (.message | split("\n")[0] | .[0:50])
        }],
        bug_fixes: [.commits[] | select(.message | test("fix|bug|patch"; "i")) | {
            hash: .hash[0:7],
            message: (.message | split("\n")[0] | .[0:50])
        }],
        health_score: (100 -
            (.total_files_changed / .total_commits * 5) -
            ([.commits[] | select(.files_changed > 10)] | length * 3)
        ) | floor,
        health_assessment: (
            if ((100 - (.total_files_changed / .total_commits * 5) - ([.commits[] | select(.files_changed > 10)] | length * 3)) | floor) >= 90 then "🟢 Excellent (90-100): Low technical debt"
            elif ((100 - (.total_files_changed / .total_commits * 5) - ([.commits[] | select(.files_changed > 10)] | length * 3)) | floor) >= 70 then "🟡 Good (70-89): Manageable debt levels"
            elif ((100 - (.total_files_changed / .total_commits * 5) - ([.commits[] | select(.files_changed > 10)] | length * 3)) | floor) >= 50 then "🟠 Fair (50-69): Needs attention"
            elif ((100 - (.total_files_changed / .total_commits * 5) - ([.commits[] | select(.files_changed > 10)] | length * 3)) | floor) >= 30 then "🔴 Poor (30-49): Significant debt"
            else "🚨 Critical (0-29): Urgent refactoring needed"
            end
        )
    }
else
    {message: "No commits found in the specified range"}
end'

# Test 8: Release readiness with scoring guidance
print_test_header "Test 8: Release Readiness Assessment"
echo "Command: beaconled --since '1w' --format json | jq release readiness"
beaconled --since '1w' --format json | jq 'if .commits and (.commits | length) > 0 then
    {
        release_period: "\(.start_date) to \(.end_date)",
        total_commits: .total_commits,
        risk_factors: {
            large_commits: [.commits[] | select(.files_changed > 15)] | length,
            recent_fixes: [.commits[] | select(.message | test("fix|bug"; "i"))] | length
        },
        readiness_score: (100 -
            ([.commits[] | select(.files_changed > 15)] | length * 15) -
            ([.commits[] | select(.message | test("fix|bug"; "i"))] | length * 10)
        ) | floor,
        readiness_assessment: (
            if (100 - ([.commits[] | select(.files_changed > 15)] | length * 15) - ([.commits[] | select(.message | test("fix|bug"; "i"))] | length * 10)) >= 90 then "🟢 Ready (90-100): Safe to release"
            elif (100 - ([.commits[] | select(.files_changed > 15)] | length * 15) - ([.commits[] | select(.message | test("fix|bug"; "i"))] | length * 10)) >= 70 then "🟡 Caution (70-89): Extra testing recommended"
            elif (100 - ([.commits[] | select(.files_changed > 15)] | length * 15) - ([.commits[] | select(.message | test("fix|bug"; "i"))] | length * 10)) >= 50 then "🟠 Risk (50-69): Delay recommended"
            elif (100 - ([.commits[] | select(.files_changed > 15)] | length * 15) - ([.commits[] | select(.message | test("fix|bug"; "i"))] | length * 10)) >= 30 then "🔴 High Risk (30-49): Significant issues"
            else "🚨 Critical Risk (0-29): Do not release"
            end
        )
    }
else
    {message: "No commits found in the specified range"}
end'

print_section_header "OUTPUT FILE GENERATION TESTS"

# Test 9: Executive summary report with productivity_index guidance
print_test_header "Test 9: Executive Summary Report"
echo "Command: beaconled --since '1m' --format json > executive-report"
echo "Output will be saved to: $OUTPUT_DIR/executive-report.json"
beaconled --since '1m' --format json | jq '{
    period: "\(.start_date) to \(.end_date)",
    total_commits: .total_commits,
    contributors: (.authors | length),
    productivity_index: (if .total_commits > 0 then (.total_lines_added / .total_commits | floor) else 0 end),
    productivity_assessment: (
        if ((.total_lines_added / .total_commits) | floor) >= 200 then "🚀 Very High (200+): Major feature development"
        elif ((.total_lines_added / .total_commits) | floor) >= 100 then "📈 High (100-199): Substantial development"
        elif ((.total_lines_added / .total_commits) | floor) >= 50 then "⚖️ Moderate (50-99): Balanced pace"
        elif ((.total_lines_added / .total_commits) | floor) >= 20 then "🔧 Light (20-49): Maintenance & fixes"
        else "📝 Minimal (<20): Minor updates"
        end
    )
}' > "$OUTPUT_DIR/executive-report.json"
echo "📄 Generated executive-report.json:"
cat "$OUTPUT_DIR/executive-report.json"

# Test 10: Team activity report (saved to file)
print_test_header "Test 10: Team Activity Report"
echo "Command: beaconled --since '1w' --format json > team-report"
echo "Output will be saved to: $OUTPUT_DIR/team-report.json"
beaconled --since '1w' --format json | jq '[.commits[] | {
    author: .author,
    date: .date,
    message: (.message | split("\n")[0]),
    files_changed: .files_changed
}] | .[0:10]' > "$OUTPUT_DIR/team-report.json"
echo "📄 Generated team-report.json (first 3 entries):"
head -n 15 "$OUTPUT_DIR/team-report.json"

# Test 11: Release notes generator (saved to file)
print_test_header "Test 11: Release Notes Generator"
echo "Command: beaconled --since '2w' --format json > release notes"
echo "Output will be saved to: $OUTPUT_DIR/RELEASE_NOTES.md"
beaconled --since '2w' --format json | jq -r '"# Release Notes\n",
"## New Features",
(.commits[] | select(.message | test("feat"; "i")) |
  "- \(.message | split("\n")[0]) (by \(.author))"),
"\n## Bug Fixes",
(.commits[] | select(.message | test("fix"; "i")) |
  "- \(.message | split("\n")[0]) (by \(.author))"),
"\n## Documentation",
(.commits[] | select(.message | test("docs"; "i")) |
  "- \(.message | split("\n")[0]) (by \(.author))")' > "$OUTPUT_DIR/RELEASE_NOTES.md"
echo "📄 Generated RELEASE_NOTES.md:"
head -n 20 "$OUTPUT_DIR/RELEASE_NOTES.md"

print_section_header "ERROR HANDLING TESTS"

# Test 12: Invalid date format (should error gracefully)
print_test_header "Test 12: Invalid date format handling"
echo "Command: beaconled --since 'yesterday' (should show error)"
beaconled --since "yesterday" 2>&1 | head -n 3 || echo "✓ Error handled as expected"

# Test 13: Non-existent repository (should error gracefully)
print_test_header "Test 13: Non-existent repository handling"
echo "Command: beaconled --repo '/nonexistent/path' (should show error)"
beaconled --repo "/nonexistent/path" --since "1d" 2>&1 | head -n 3 || echo "✓ Error handled as expected"

print_section_header "ADVANCED ANALYTICS TESTS"

# Test 14: File type analysis
print_test_header "Test 14: File Type Analysis"
echo "Command: beaconled --since '2w' --format json | jq file type breakdown"
beaconled --since '2w' --format json | jq 'if .commits and (.commits | length) > 0 then
    ([.commits[].files[]? | {
        path: (.path // ""),
        extension: (.path | split("/") | last | split(".") | if length > 1 then last else "no-ext" end)
    }] | group_by(.extension) | map({
        extension: .[0].extension,
        count: length
    }) | sort_by(.count) | reverse | .[0:5])
else
    [{message: "No files found"}]
end'

# Test 15: Enhanced Daily standup summary with detailed output
print_test_header "Test 15: Daily Standup Summary"
echo "Command: beaconled --since '1d' --format json | jq comprehensive daily summary"
beaconled --since '1d' --format json | jq -r '
"🚀 Daily Development Report - \(now | strftime("%Y-%m-%d"))",
"",
"📊 Activity Summary:",
"  Total commits: \(.total_commits // 0)",
"  Files changed: \(.total_files_changed // 0)",
"  Lines added: \(.total_lines_added // 0)",
"  Lines deleted: \(.total_lines_deleted // 0)",
"",
"👥 Top Contributors:",
(if .authors then (.authors | to_entries | sort_by(.value) | reverse | map("  - \(.key): \(.value) commits") | .[0:5] | .[]) else "  No contributors found" end),
"",
"🎯 Development Signals:",
(if .total_commits == 0 then "  🚫 No activity - check for blockers or holidays"
 elif .total_commits >= 10 then "  🔥 High activity - sprint in progress or deadline push"
 elif .total_commits >= 5 then "  ✅ Normal activity - steady development pace"
 else "  📋 Light activity - planning phase or code review focus"
 end),
"",
"🔍 Focus Areas:",
(if (.total_lines_deleted // 0) > (.total_lines_added // 0) then "  🧹 Code cleanup and refactoring"
 elif (.total_files_changed // 0) > (.total_commits // 0) * 5 then "  🔄 Large-scale changes or restructuring"
 else "  🚀 Feature development and additions"
 end)'

print_section_header "ENHANCED CODE HEALTH TESTS"

# Test 16: Multi-period health comparison with proper file notifications
print_test_header "Test 16: Multi-Period Health Comparison"
echo "Command: Compare health across recent months"
echo "Output files will be saved to: $OUTPUT_DIR/month1.json and $OUTPUT_DIR/month2.json"
echo "Simulating multi-period analysis:"

# Month 1 (2 months ago to 1 month ago)
beaconled --since '2m' --until '1m' --format json | jq '{
    period: "Month_1_ago",
    commits: .total_commits,
    files_changed: .total_files_changed,
    stability_score: (if .total_commits > 0 then (100 - (.total_files_changed / .total_commits * 10) | floor) else 100 end)
}' > "$OUTPUT_DIR/month1.json"

# Month 2 (1 month ago to now)
beaconled --since '1m' --format json | jq '{
    period: "Current_month",
    commits: .total_commits,
    files_changed: .total_files_changed,
    stability_score: (if .total_commits > 0 then (100 - (.total_files_changed / .total_commits * 10) | floor) else 100 end)
}' > "$OUTPUT_DIR/month2.json"

echo "📄 Generated $OUTPUT_DIR/month1.json:"
cat "$OUTPUT_DIR/month1.json"
echo "📄 Generated $OUTPUT_DIR/month2.json:"
cat "$OUTPUT_DIR/month2.json"

# Test 17: Advanced technical debt indicators
print_test_header "Test 17: Advanced Technical Debt Indicators"
echo "Command: beaconled --since '1m' --format json | jq advanced debt analysis"
echo "Output will be saved to: $OUTPUT_DIR/debt-analysis.json"
beaconled --since '1m' --format json | jq 'if .commits and (.commits | length) > 0 then
    {
        analysis_period: "\(.start_date) to \(.end_date)",
        total_commits: .total_commits,
        debt_indicators: {
            large_change_commits: [.commits[] | select(.files_changed > 8)] | length,
            potential_bug_fixes: [.commits[] | select(.message | test("fix|bug|patch"; "i"))] | length,
            avg_files_per_commit: (.total_files_changed / .total_commits | floor * 100 / 100),
            health_score: (100 - (.total_files_changed / .total_commits * 8) - ([.commits[] | select(.files_changed > 8)] | length * 3)) | floor
        }
    }
else
    {message: "No commits found for debt analysis"}
end' > "$OUTPUT_DIR/debt-analysis.json"
echo "📄 Generated debt-analysis.json:"
cat "$OUTPUT_DIR/debt-analysis.json"

# Test 18: Simulated CI Quality Gate
print_test_header "Test 18: CI Quality Gate (Simplified)"
echo "Command: Check for risky commits without test mentions"
echo "Output will be saved to: $OUTPUT_DIR/quality-gate.json"
beaconled --since '2w' --format json | jq '{
    period: "\(.start_date) to \(.end_date)",
    total_commits: (.commits | length),
    quality_check: {
        large_commits: [.commits[] | select(.files_changed > 8)] | length,
        commits_mentioning_tests: [.commits[] | select(.message | test("test|spec"; "i"))] | length,
        quality_score: (
            if ([.commits[] | select(.files_changed > 8 and (.message | test("test|spec"; "i") | not))] | length) > 0
            then "⚠️ Large commits without test mentions found"
            else "✅ Quality checks passed"
            end
        )
    }
}' > "$OUTPUT_DIR/quality-gate.json"
echo "📄 Generated quality-gate.json:"
cat "$OUTPUT_DIR/quality-gate.json"

print_section_header "TEST COMPLETION"

# Conditional cleanup based on --cleanup flag
if [[ "$1" == "--cleanup" ]]; then
    print_test_header "Cleanup: Removing temporary output files"
    echo "Removing files that contain sensitive data (emails, etc.)..."
    rm -rf "$OUTPUT_DIR"
    echo "✅ Cleanup complete - $OUTPUT_DIR directory removed"
else
    print_test_header "Test Complete - Output Files Available"
    echo "📁 Generated files are available in: $OUTPUT_DIR/"
    echo "   - executive-report.json     (Executive summary with productivity assessment)"
    echo "   - team-report.json          (Team activity report)"
    echo "   - RELEASE_NOTES.md          (Generated release notes)"
    echo "   - month1.json, month2.json  (Multi-period health comparison)"
    echo "   - debt-analysis.json        (Advanced technical debt indicators)"
    echo "   - quality-gate.json         (CI quality gate assessment)"
    echo ""
    echo "💡 These files contain sensitive data (emails) and are in .gitignore"
    echo "💡 Run with --cleanup flag to remove them: $0 --cleanup"
    echo "💡 Or clean manually: rm -rf $OUTPUT_DIR"
fi

echo ""
echo "🎉 Advanced usage tests completed successfully!"
echo "   Total tests run: 18"
echo "   Tests organized by complexity: Basic → Analysis → Advanced → Output Generation"
echo "   All outputs saved to organized directory structure"
echo "   Score interpretations provided for health_score, readiness_score, and productivity_index"
