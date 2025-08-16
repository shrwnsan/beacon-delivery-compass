# Contributing to Beacon

Thank you for your interest in contributing to Beacon - your delivery compass for empowered product builders!

## Development Environment Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Docker (optional, for containerized development)
- VS Code (recommended) with Remote - Containers extension

### Development Setup Options

#### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/shrwnsan/beacon-delivery-compass.git
   cd beacon-delivery-compass
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e .[dev]
   pre-commit install
   ```

#### Option 2: Containerized Development (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/shrwnsan/beacon-delivery-compass.git
   cd beacon-delivery-compass
   ```

2. **Open in VS Code with Dev Containers**
   - Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
   - Open the command palette (Ctrl+Shift+P / Cmd+Shift+P)
   - Select "Remote-Containers: Reopen in Container"
   - Wait for the container to build and start

## Development Workflow

### Using Makefile Commands

We provide a `Makefile` with common development tasks:

```bash
# Set up development environment
make setup

# Run tests with coverage
make test

# Run linters
make lint

# Run type checking
make typecheck

# Format code
make format

# Check for outdated dependencies
make check-deps

# Clean up temporary files
make clean
```

### Code Quality Standards

We maintain high code quality standards using these tools:

- **Code Formatting**: Black (line length: 88)
- **Linting**: Ruff (with Flake8 and isort plugins)
- **Type Checking**: mypy with strict mode
- **Testing**: pytest with coverage reporting
- **Security**: Bandit and Safety checks

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Branching Strategy

We follow a structured branching model to maintain a clean and organized repository:

1. **Main Branches**
   - `main`: Primary development branch (always stable)
   - `stable`: Production-ready releases (kept stable at all times)

2. **Supporting Branches**
   - `feature/*`: New features being developed
     - Naming: `feature/descriptive-name` (e.g., `feature/user-authentication`)
     - Should be created from `main`
     - Should be deleted after merging

   - `release/*`: Preparation for production releases
     - Naming: `release/x.y.z` (following semantic versioning)
     - Should be created from `main`
     - Used for final testing and version bumps

   - `hotfix/*`: Critical production bug fixes
     - Naming: `hotfix/description`
     - Should be created from `stable`
     - Merged back to both `stable` and `main`

3. **Branch Management**
   - Keep feature branches focused and small
   - Delete branches after they're merged
   - Regularly sync with `main` to avoid large merge conflicts
   - Use pull requests for all changes (except hotfixes in emergencies)

4. **Commit Messages**
   - Use present tense ("Add feature" not "Added feature")
   - Keep the first line under 50 characters
   - Include a blank line between the subject and body
   - Reference issues/tickets when applicable

2. **Make your changes**
   - Follow existing code patterns and conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Run pre-commit hooks**
   We use different pre-commit configurations for development and production environments:

   - **Development** (default):
     ```bash
     # Installs the development hooks (faster, less strict)
     pre-commit install

     # Run all hooks on all files
     pre-commit run --all-files
     ```
     The development configuration is more lenient to avoid slowing down development. It includes:
     - Black with 100-character line length
     - Basic Ruff linting and formatting
     - Basic MyPy type checking
     - Faster execution by excluding some checks

   - **Production/CI**:
     ```bash
     # Run production hooks (stricter, includes all checks)
     pre-commit run --config .pre-commit-prod.yaml --all-files
     ```
     The production configuration enforces additional quality checks:
     - Stricter MyPy with `--strict` flag
     - Additional validations (TOML, JSON, merge conflicts)
     - More comprehensive code quality checks
     - Used in CI/CD pipelines

   > **Note**: The production configuration runs automatically in CI. For local development, the development hooks are installed by default.

4. **Test your changes**
   ```bash
   # Run all tests
   make test

   # Run specific test file
   pytest tests/unit/test_your_feature.py -v
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

6. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python Code
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use Black for code formatting
- Include type hints for all functions and methods
- Write Google-style docstrings for public functions
- Keep functions small and focused (preferably < 20 lines)

### Commit Messages
We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat(analyzer): add support for custom date ranges

Add the ability to analyze commits within a specific date range using the
--since and --until flags in the CLI.

Closes #123
```

## Testing Guidelines

- Write unit tests for all new functionality
- Use descriptive test names that explain what's being tested
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test data
- Mark performance tests with `@pytest.mark.performance`
- Keep tests fast and isolated

## Pull Request Process

1. Ensure all tests pass and code coverage remains high (≥90%)
2. Update documentation as needed
3. Ensure your branch is up to date with the main branch
4. Create a draft PR early for feedback
5. Request review from at least one maintainer
6. Address all review comments
7. Once approved, squash and merge your PR

### Testing
- Write unit tests for new functionality
- Maintain or improve test coverage
- Test edge cases and error conditions
- Use descriptive test names

## Project Structure

```
src/beacon/                 # Main package
├── cli.py                  # Command-line interface
├── core/                   # Core business logic
│   ├── analyzer.py         # Git analysis engine
│   └── models.py           # Data models
└── formatters/             # Output formatters
    ├── standard.py         # Standard text output
    ├── extended.py         # Extended output
    └── json_format.py      # JSON output
```

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any error messages or logs

## Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Describe the use case clearly
- Explain how it fits with Beacon's mission
- Consider implementation complexity

## Questions?

Feel free to open an issue for questions about:
- Development setup
- Code architecture
- Feature implementation
- Best practices

## License

By contributing to Beacon, you agree that your contributions will be licensed under the MIT License.
