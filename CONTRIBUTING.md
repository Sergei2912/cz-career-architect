# Contributing to CZ Career Architect

Thank you for your interest in contributing to CZ Career Architect! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

---

## Getting Started

### Prerequisites

- Python 3.9, 3.10, or 3.11
- Git
- OpenAI API key (for testing with actual models)

### Initial Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/cz-career-architect.git
cd cz-career-architect

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# Or: git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clear, focused code
- Follow coding standards
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Check code style
black base_for_agent_cv/
isort base_for_agent_cv/
flake8 base_for_agent_cv/

# Run pre-commit hooks
pre-commit run --all-files
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "feat: Add new validation rule for medical licenses"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

---

## Coding Standards

### Python Style

- **PEP 8** compliant (enforced by flake8)
- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **Type hints** encouraged for new code

### Naming Conventions

```python
# Variables and functions: snake_case
def validate_document(input_text):
    error_count = 0

# Classes: PascalCase
class DocumentValidator:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024
SUPPORTED_FORMATS = ['.pdf', '.docx']

# Private members: leading underscore
def _internal_helper():
    pass
```

### Documentation

```python
def validate_text(text, enable_nbsp=False):
    """
    Validate text for GDPR and ČSN compliance.
    
    Args:
        text (str): Text to validate
        enable_nbsp (bool): Whether to check non-breaking spaces
        
    Returns:
        tuple: (findings, summary_line)
        
    Raises:
        ValueError: If text is empty
        
    Example:
        >>> findings, summary = validate_text("Test text")
        >>> print(summary)
        '✅ No issues'
    """
```

---

## Testing Guidelines

### Writing Tests

```python
# tests/test_new_feature.py
import pytest
from src.pipeline.validator import validate_text

class TestNewFeature:
    def test_descriptive_name(self):
        """Test should have clear docstring."""
        # Arrange
        input_text = "Test input"
        
        # Act
        result = validate_text(input_text)
        
        # Assert
        assert result is not None
```

### Test Coverage

- Aim for 80%+ coverage
- Test edge cases and error conditions
- Include both positive and negative tests
- Mock external dependencies (API calls, file I/O)

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_validator.py -v

# With coverage
pytest tests/ --cov=base_for_agent_cv --cov-report=html

# Failed tests only
pytest tests/ --lf
```

---

## Pull Request Process

### Before Creating PR

1. ✅ Tests pass locally
2. ✅ Code follows style guide
3. ✅ Documentation updated
4. ✅ No merge conflicts
5. ✅ Commits are clean and descriptive

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Added X functionality
- Fixed Y issue
- Updated Z documentation

## Testing
- All existing tests pass
- Added N new tests
- Manual testing performed: [describe]

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Related Issues
Closes #123

## Checklist
- [ ] Code follows style guide
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No sensitive data committed
- [ ] Breaking changes documented
```

### Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least one approval required
3. **Testing**: Verify changes work as expected
4. **Documentation**: Ensure docs are updated
5. **Merge**: Squash and merge to main

---

## Reporting Issues

### Bug Reports

Include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, etc.
6. **Logs**: Relevant error messages

Example:

```markdown
## Bug: GDPR validator misses nationality field

**Description**: The GDPR validator doesn't catch "citizenship" field

**Steps to Reproduce**:
1. Run: `python src/main.py --mode check --text "citizenship: Czech"`
2. Observe result

**Expected**: Should detect GDPR violation
**Actual**: No issues reported

**Environment**: Python 3.11, Ubuntu 22.04

**Logs**:
```
✅ No issues
```
```

### Feature Requests

Include:

1. **Use Case**: Why is this needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other options considered
4. **Additional Context**: Any other relevant info

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Examples

```bash
# Good
feat(validator): Add nationality GDPR check
fix(api): Handle empty file upload gracefully
docs(readme): Add Docker installation instructions

# Bad
updated stuff
fix bug
WIP
```

---

## Additional Resources

- [Developer Guide](base_for_agent_cv/AGENTS.md)
- [User Documentation](base_for_agent_cv/README.md)
- [GitHub Issues](https://github.com/Sergei2912/cz-career-architect/issues)

---

## Questions?

If you have questions:

1. Check existing documentation
2. Search GitHub issues
3. Open a new issue with the "question" label

---

Thank you for contributing to CZ Career Architect! 🎉
