.PHONY: help setup test lint typecheck format check-deps clean dev-setup prod-setup

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
	@echo "  dev-setup - Configure pre-commit for development"
	@echo "  prod-setup - Configure pre-commit for production"

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

# Run static type checking
typecheck:
	mypy beaconled

# Format code
format:
	black .

# Check for outdated dependencies
check-deps:
	pip list --outdated --format=columns

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .coverage coverage.xml htmlcov/ .ruff_cache/ .hypothesis/

# Configure pre-commit for development
dev-setup:
	@echo "Configuring pre-commit for development..."
	cp .pre-commit-dev.yaml .pre-commit-config.yaml
	pre-commit install --install-hooks
	@echo "\nDevelopment pre-commit configured. The following checks are enabled:"
	@echo "- Black (lenient: 100 chars/line)"
	@echo "- Ruff (ignoring E501,F401)"
	@echo "- mypy (non-strict)"
	@echo "\nUse 'make prod-setup' to switch to production checks before committing."

# Configure pre-commit for production
prod-setup:
	@echo "Configuring pre-commit for production..."
	cp .pre-commit-prod.yaml .pre-commit-config.yaml
	pre-commit install --install-hooks
	@echo "\nProduction pre-commit configured with strict checks."
	@echo "All hooks including isort, black, ruff, and mypy will run."
