#!/bin/bash

# Pre-commit hook to check for machine-specific paths in committed files
# This helps prevent committing sensitive information like local file paths

# Check if any staged files contain machine-specific paths
# We use a pattern that matches /Users/ followed by alphanumeric characters and underscores
machine_path_pattern="/Users/[a-zA-Z0-9_]+"
staged_files=$(git diff --cached --name-only --diff-filter=ACMR)

if [ -n "$staged_files" ]; then
    echo "Checking for machine-specific paths in staged files..."
    found=0

    for file in $staged_files; do
        # Skip binary files and files that don't exist
        if [ -f "$file" ] && file "$file" | grep -q "text"; then
            # Skip our own script to avoid false positives
            if [[ "$file" == "scripts/check_machine_paths.sh" ]]; then
                continue
            fi

            # Check for machine-specific paths
            if grep -E "$machine_path_pattern" "$file" > /dev/null 2>&1; then
                echo "ERROR: Found potential machine-specific path in $file"
                grep -E -n "$machine_path_pattern" "$file"
                found=1
            fi
        fi
    done

    if [ $found -eq 1 ]; then
        echo ""
        echo "Machine-specific paths detected in staged files!"
        echo "Please remove or replace paths like '/Users/username' with '~' or relative paths."
        echo "To bypass this check, use: git commit --no-verify"
        exit 1
    fi
fi

echo "No machine-specific paths found."
exit 0
