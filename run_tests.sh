#!/bin/bash

# Test runner script that ensures local worktree modules are loaded
# This fixes issues where the main repository has different versions

source ../beacon-delivery-compass/.venv/bin/activate
PYTHONPATH="./src:$PYTHONPATH" python -m pytest "$@"
# Test runner script usage:
# ./run_tests.sh tests/unit/test_extended_formatter_emoji.py -v
