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
	@echo "  dev-setup - Install and configure pre-commit hooks"

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

# Configure pre-commit (unified configuration)
dev-setup:
	@echo "Installing pre-commit hooks..."
	pre-commit install --install-hooks
	@echo "\nPre-commit configured with unified checks:"
	@echo "- Black (100 chars/line)"
	@echo "- Ruff (with auto-fix)"
	@echo "- mypy (for src/ files only)"
	@echo "- Basic file checks (whitespace, YAML, file size)"

# Alias for backward compatibility
prod-setup: dev-setup
	@echo "\nNote: Using unified pre-commit configuration (dev and prod are now the same)"
