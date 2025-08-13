.PHONY: help setup test lint typecheck format check-deps clean

# Default target
help:
	@echo "Available targets:"
	@echo "  setup     - Set up development environment"
	@echo "  test      - Run tests with coverage"
	@echo "  lint      - Run linters (ruff, black, isort)"
	@echo "  typecheck - Run static type checking (mypy)"
	@echo "  format    - Format code (black, isort)"
	@echo "  check-deps - Check for outdated dependencies"
	@echo "  clean     - Clean up temporary files"

# Set up development environment
setup:
	python -m pip install --upgrade pip
	pip install -e .[dev]
	pre-commit install

# Run tests with coverage
test:
	pytest tests/ -v --cov=beaconled --cov-report=term-missing --cov-report=xml

# Run linters
lint:
	ruff check .
	black --check .
	isort --check-only .

# Run static type checking
typecheck:
	mypy beaconled

# Format code
format:
	black .
	isort .

# Check for outdated dependencies
check-deps:
	pip list --outdated --format=columns

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .coverage coverage.xml htmlcov/ .ruff_cache/ .hypothesis/
