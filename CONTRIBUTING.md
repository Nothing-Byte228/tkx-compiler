# Contributing to tkx-compiler

Thank you for your interest in contributing to tkx-compiler! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/tkx-compiler.git
   cd tkx-compiler
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings to all classes and functions
- Maximum line length: 100 characters
- Use descriptive variable names

### Code Formatting
- Format code with Black:
  ```bash
  black .
  ```

### Type Checking
- Run type checker:
  ```bash
  mypy core/
  ```

### Linting
- Run linter:
  ```bash
  flake8 core/
  ```

## Testing

### Running Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=core --cov-report=html
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for code style changes (formatting, etc.)
- `refactor:` for code refactoring
- `test:` for adding or updating tests
- `chore:` for maintenance tasks

Example:
```
feat: add support for grid geometry manager
```

## Pull Request Process

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request on GitHub

### PR Requirements
- Include tests for new features
- Update documentation if needed
- Ensure all tests pass
- Follow coding standards
- Add description of changes

## Project Structure

```
tkx-compiler/
├── core/              # Core functionality
├── cli/               # CLI interface
├── tests/             # Test files
├── examples/          # Example projects
└── docs/              # Documentation
```

## Issue Reporting

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (if any)

## Feature Requests

For feature requests:
- Describe the use case
- Explain why it would be useful
- Provide examples if possible
- Consider implementation complexity

## Questions

For questions:
- Check existing documentation
- Search existing issues
- Use appropriate channels (GitHub Issues, Discord, etc.)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
