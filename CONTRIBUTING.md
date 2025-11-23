# Contributing to AI Symphony

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to AI Symphony. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## 🚀 How to Contribute

### Reporting Bugs

This section guides you through submitting a bug report for AI Symphony. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

*   **Use a clear and descriptive title** for the issue to identify the problem.
*   **Describe the exact steps which reproduce the problem** in as many details as possible.
*   **Provide specific examples** to demonstrate the steps. Include copy/pasteable snippets, which you use in those examples.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for AI Symphony, including completely new features and minor improvements to existing functionality.

*   **Use a clear and descriptive title** for the issue to identify the suggestion.
*   **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
*   **Explain why this enhancement would be useful** to most AI Symphony users.

### Pull Requests

The process is described in the README, but here is a more detailed workflow:

1.  **Fork the repo** and create your branch from `main`.
2.  **Install dependencies**: `uv sync` or `pip install -r requirements.txt`.
3.  **Test your changes**: Ensure the `minimal_test.py` still passes.
4.  **Make sure your code lints**: Run `uv run ruff check src/` and `uv run ruff format src/`.
5.  **Verify CI passes**: GitHub Actions will automatically run tests, linting, and security scans on your PR.
6.  **Issue that Pull Request!**

## 💻 Development Workflow

We use `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Run linting
uv run ruff check src/

# Format code
uv run ruff format src/

# Run the main script
uv run python src/main.py "Your test idea"
```

### CI/CD Pipeline

All pull requests automatically trigger our CI/CD pipeline which includes:
- **Linting**: Code quality checks with ruff
- **Testing**: Multi-version Python testing (3.10, 3.11, 3.12)
- **Security**: Vulnerability scanning with bandit and safety
- **Build Verification**: Ensures all dependencies resolve correctly

You can view the pipeline configuration in `.github/workflows/ci.yml`.

## 🎨 Style Guide

*   Use Python type hints.
*   Follow PEP 8.
*   Write docstrings for all classes and functions.

## 📋 Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.
