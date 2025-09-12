#!/bin/bash

# Test runner script for Beacon Delivery Compass
# Ensures the correct Python environment is activated and PYTHONPATH is set

# Activate the virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Warning: No virtual environment found. Running with system Python."
fi

# Set Python path to include the src directory
export PYTHONPATH="./src:$PYTHONPATH"

# Run pytest with coverage and pass through any additional arguments
python -m pytest \
    -v \
    --strict-markers \
    --strict-config \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    "$@"

# Exit with pytest's exit code
exit $?
