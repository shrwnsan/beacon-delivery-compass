# Beacon Delivery Compass - Agent Guidelines

This document outlines the development guidelines for agents operating within the Beacon Delivery Compass repository.

## 1. Development Commands

*   **Run tests interactively:** `python run_tests.py`
*   **Run all tests directly:** `pytest`
*   **Run a specific test file:** `pytest tests/unit/test_analyzer.py`
*   **Run a specific test case:** `pytest tests/unit/test_analyzer.py::TestGitAnalyzer::test_get_commit_stats_success`
*   **Run tests with coverage:** `pytest --cov=. --cov-report=term-missing`
*   **Linting:** `flake8`
*   **Formatting:** `black .`
*   **Import Sorting:** `isort .`
*   **Type Checking:** `mypy .`

## 2. Code Style Guidelines

### General
*   **Imports:**
    - Group imports in this order: standard library, third-party, local
    - Use `isort` to maintain order
*   **Formatting:**
    - Follow PEP 8 standards
    - Use `black` for automatic formatting
*   **Naming Conventions:**
    - Variables and functions: `snake_case`
    - Classes: `CamelCase`
    - Constants: `UPPER_SNAKE_CASE`

### Code Structure
*   **Function Design:**
    - Keep functionality in a single function unless reusable or composable
    - Avoid unnecessary destructuring of variables
*   **Control Flow:**
    - Prefer early returns over nested conditionals
    - Avoid `else` statements unless absolutely necessary
*   **Variable Declarations:**
    - Prefer `const` over `let`
    - Use single word variable names where clear and unambiguous

### Type Safety
*   Use Python type hints for all functions, methods, and variables
*   Avoid using `any` type
*   Be explicit with type definitions

### Error Handling
*   Implement robust error handling
*   Only catch exceptions you can meaningfully handle
*   Raise specific exceptions where appropriate
*   Avoid `try/catch` blocks where possible

### Documentation
*   **Docstrings:** Use Google-style docstrings for all public modules, classes, and functions
*   **Commits:** Follow Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`)

## 3. Cursor/Copilot Rules

*   No specific Cursor or Copilot rules were found in the repository's configuration files (`.cursor/rules/`, `.github/copilot-instructions.md`).
