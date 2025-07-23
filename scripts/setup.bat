@echo off

REM Create virtual environment
python -m venv .venv

REM Activate virtual environment
call .venv\Scripts\activate

REM Install in development mode with dev dependencies
pip install -e ".[dev]"

REM Verify installation
beaconled --version