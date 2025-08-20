#!/bin/bash
set -e

# Function to print test header with command
print_test_header() {
    echo -e "\n=== $1 ==="
}

# Test 1: Basic beaconled command
print_test_header "Test 1: Basic beaconled command"
echo "Command: beaconled"
beaconled

# Test 2: JSON output format
print_test_header "Test 2: JSON output format"
echo "Command: beaconled --format json | jq ."
beaconled --format json | jq .

# Test 3: Extended format
print_test_header "Test 3: Extended format"
echo "Command: beaconled --format extended"
beaconled --format extended

# Test 4: Date range (last 7 days)
print_test_header "Test 4: Date range (last 7 days)"
echo "Command: beaconled --since \"7d\""
beaconled --since "7d"

# Test 5: Analyze specific commit (using the latest commit)
LATEST_COMMIT=$(git rev-parse --short HEAD)
print_test_header "Test 5: Analyze specific commit (${LATEST_COMMIT})"
echo "Command: beaconled \"${LATEST_COMMIT}\""
beaconled "${LATEST_COMMIT}"

print_test_header "All basic usage tests completed successfully"
