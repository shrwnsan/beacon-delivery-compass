#!/bin/bash

# Commit Analytics Script
# Generates detailed statistics for git commits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
COMMIT_HASH=""
BRANCH=""
AUTHOR=""
SHOW_DETAILED=false
OUTPUT_FORMAT="standard"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [COMMIT_HASH]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -d, --detailed      Show detailed breakdown"
    echo "  -f, --format FORMAT Output format (standard|extended|json)"
    echo "  -b, --branch BRANCH Analyze specific branch"
    echo "  -a, --author AUTHOR Filter by author"
    echo ""
    echo "Examples:"
    echo "  $0                  # Analyze latest commit"
    echo "  $0 abc123           # Analyze specific commit"
    echo "  $0 -d -f extended   # Detailed analysis with extended format"
    echo "  $0 -b main          # Analyze latest commit on main branch"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--detailed)
            SHOW_DETAILED=true
            shift
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -a|--author)
            AUTHOR="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            COMMIT_HASH="$1"
            shift
            ;;
    esac
done

# Get commit hash if not provided
if [ -z "$COMMIT_HASH" ]; then
    if [ -n "$BRANCH" ]; then
        COMMIT_HASH=$(git --no-pager rev-parse "$BRANCH")
    else
        COMMIT_HASH=$(git --no-pager rev-parse HEAD)
    fi
fi

# Verify commit exists
if ! git --no-pager cat-file -e "$COMMIT_HASH" 2>/dev/null; then
    echo -e "${RED}Error: Commit $COMMIT_HASH does not exist${NC}"
    exit 1
fi

# Get commit information
COMMIT_SHORT=$(git --no-pager rev-parse --short "$COMMIT_HASH")
COMMIT_AUTHOR=$(git --no-pager show -s --format='%an' "$COMMIT_HASH")
COMMIT_DATE=$(git --no-pager show -s --format='%ci' "$COMMIT_HASH")
COMMIT_MESSAGE=$(git --no-pager show -s --format='%s' "$COMMIT_HASH")
CURRENT_BRANCH=$(git --no-pager branch --contains "$COMMIT_HASH" | grep -v "detached" | head -1 | sed 's/^[* ] //')

# Get file statistics
STATS=$(git --no-pager show --stat "$COMMIT_HASH" | tail -1)
FILES_CHANGED=$(echo "$STATS" | grep -o '[0-9]\+ files\? changed' | grep -o '[0-9]\+')
INSERTIONS=$(echo "$STATS" | grep -o '[0-9]\+ insertions\?' | grep -o '[0-9]\+' || echo "0")
DELETIONS=$(echo "$STATS" | grep -o '[0-9]\+ deletions\?' | grep -o '[0-9]\+' || echo "0")

# Get detailed file information
FILES_INFO=$(git --no-pager show --name-status "$COMMIT_HASH" | grep -E '^[AMD]' || true)
NEW_FILES=$(echo "$FILES_INFO" | grep -c '^A' || echo "0")
MODIFIED_FILES=$(echo "$FILES_INFO" | grep -c '^M' || echo "0")
DELETED_FILES=$(echo "$FILES_INFO" | grep -c '^D' || echo "0")

# Function to get file type breakdown
get_file_type_breakdown() {
    local temp_file=$(mktemp)
    git --no-pager show --name-only "$COMMIT_HASH" | grep -v '^$' > "$temp_file"
    
    # Use a simpler approach for file type counting
    local extensions=""
    while IFS= read -r file; do
        if [[ "$file" =~ \. ]]; then
            ext=".${file##*.}"
        else
            ext="no-ext"
        fi
        extensions="$extensions$ext "
    done < "$temp_file"
    
    rm "$temp_file"
    
    # Count and display unique extensions
    echo "$extensions" | tr ' ' '\n' | sort | uniq -c | while read count ext; do
        if [ -n "$ext" ]; then
            echo "$ext: $count files"
        fi
    done
}

# Function to get component breakdown
get_component_breakdown() {
    local backend_files=$(git --no-pager show --name-only "$COMMIT_HASH" | grep -c '^backend/' || echo "0")
    local frontend_files=$(git --no-pager show --name-only "$COMMIT_HASH" | grep -c '^frontend/' || echo "0")
    local docs_files=$(git --no-pager show --name-only "$COMMIT_HASH" | grep -c '^docs/' || echo "0")
    local config_files=$(git --no-pager show --name-only "$COMMIT_HASH" | grep -cE '\.(json|yaml|yml|toml|ini|env)$' || echo "0")
    local test_files=$(git --no-pager show --name-only "$COMMIT_HASH" | grep -cE 'test_|\.test\.|\.spec\.' || echo "0")
    
    echo "Backend: $backend_files files"
    echo "Frontend: $frontend_files files"
    echo "Documentation: $docs_files files"
    echo "Configuration: $config_files files"
    echo "Tests: $test_files files"
}

# Output functions
output_standard() {
    echo -e "${BLUE}📊 Commit Stats:${NC}"
    echo -e "${GREEN}$FILES_CHANGED files changed${NC}"
    echo -e "${GREEN}$INSERTIONS insertions, $DELETIONS deletions${NC}"
    echo -e "${YELLOW}Commit Hash: $COMMIT_SHORT${NC}"
    echo -e "${YELLOW}Branch: ${CURRENT_BRANCH:-unknown}${NC}"
    echo -e "${CYAN}Author: $COMMIT_AUTHOR${NC}"
    echo -e "${CYAN}Date: $COMMIT_DATE${NC}"
    
    if [ "$SHOW_DETAILED" = true ]; then
        echo ""
        echo -e "${PURPLE}File Types:${NC}"
        get_file_type_breakdown | sed 's/^/  - /'
        
        echo ""
        echo -e "${PURPLE}Components:${NC}"
        get_component_breakdown | sed 's/^/  - /'
    fi
}

output_extended() {
    echo -e "${BLUE}--Files Added/Modified:${NC}"
    echo -e "${GREEN}$FILES_CHANGED files changed in total${NC}"
    echo -e "${GREEN}$INSERTIONS insertions, $DELETIONS deletions${NC}"
    echo -e "${GREEN}$NEW_FILES new files created${NC}"
    echo -e "${GREEN}$MODIFIED_FILES existing files improved${NC}"
    if [ "$DELETED_FILES" -gt 0 ]; then
        echo -e "${RED}$DELETED_FILES files deleted${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}--Commit Details:${NC}"
    echo -e "${YELLOW}Hash: $COMMIT_SHORT${NC}"
    echo -e "${YELLOW}Branch: ${CURRENT_BRANCH:-unknown}${NC}"
    echo -e "${CYAN}Author: $COMMIT_AUTHOR${NC}"
    echo -e "${CYAN}Date: $COMMIT_DATE${NC}"
    echo -e "${CYAN}Message: $COMMIT_MESSAGE${NC}"
    
    if [ "$SHOW_DETAILED" = true ]; then
        echo ""
        echo -e "${BLUE}--Breakdown by Component:${NC}"
        get_component_breakdown
        
        echo ""
        echo -e "${BLUE}--File Types:${NC}"
        get_file_type_breakdown
    fi
}

output_json() {
    cat << EOF
{
  "commit": {
    "hash": "$COMMIT_HASH",
    "short_hash": "$COMMIT_SHORT",
    "author": "$COMMIT_AUTHOR",
    "date": "$COMMIT_DATE",
    "message": "$COMMIT_MESSAGE",
    "branch": "${CURRENT_BRANCH:-unknown}"
  },
  "statistics": {
    "files_changed": $FILES_CHANGED,
    "insertions": $INSERTIONS,
    "deletions": $DELETIONS,
    "new_files": $NEW_FILES,
    "modified_files": $MODIFIED_FILES,
    "deleted_files": $DELETED_FILES
  }
}
EOF
}

# Main output logic
case "$OUTPUT_FORMAT" in
    "standard")
        output_standard
        ;;
    "extended")
        output_extended
        ;;
    "json")
        output_json
        ;;
    *)
        echo -e "${RED}Error: Unknown format '$OUTPUT_FORMAT'${NC}"
        echo "Available formats: standard, extended, json"
        exit 1
        ;;
esac