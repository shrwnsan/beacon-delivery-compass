#!/bin/bash

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
beaconled --version
