# Repository Guidelines

## Table of Contents
- [Project Structure](#project-structure)
- [Build, Test, and Development Commands](#build-test-and-development-commands)
- [Testing Guidelines](#testing-guidelines)
- [CI/CD Pipeline](#cicd-pipeline)
- [Coding Style & Naming Conventions](#coding-style--naming-conventions)
- [Commit & Pull Request Guidelines](#commit--pull-request-guidelines)
- [Security & Configuration](#security--configuration)

---

## Project Structure

### Module Organization

The project follows a modular structure for improved maintainability:

```
cz-career-architect/
├── src/                      # Main source code
│   ├── main.py              # Entry point for CLI
│   ├── chat.py              # Interactive chat mode
│   ├── pipeline/            # Document processing pipeline
│   │   ├── validator.py     # GDPR and ČSN validation
│   │   └── generator.py     # Document generation logic
│   └── sdk/                 # Core SDK modules
│       ├── model.py         # GPT model interactions
│       └── utils.py         # Utility functions
├── tests/                   # Test suite (pytest)
├── packages/                # Domain-specific packages
│   ├── validators/          # Validation logic
│   ├── prompts/             # System prompts
│   └── types/               # Type definitions
├── Schemas/                 # JSON schemas and validation rules
├── Examples/                # Reference documents and samples
├── out/                     # Generated outputs
├── .github/workflows/       # CI/CD configuration
├── requirements.txt         # Python dependencies
└── .env.example            # Environment template
```

### Entry Points

- **CLI**: `python src/main.py` - Command-line interface
- **Chat**: `python src/main.py --mode chat` - Interactive mode
- **API**: `python api.py` - FastAPI server
- **Validation**: `python src/main.py --mode check` - Batch validation

---

## Build, Test, and Development Commands

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Running the Application

```bash
# Interactive chat
python src/main.py --mode chat

# Generate full package with validation
python src/main.py --validate

# Validate text
python src/main.py --mode check --text "Datum narození: 15.1.1985"

# Rewrite with ČSN formatting
python src/main.py --mode rewrite --text "2015-2023"

# Start API server
python api.py
# Or: uvicorn api:app --reload --port 8000
```

### Development Tools

```bash
# Format code with Black
black base_for_agent_cv/

# Sort imports with isort
isort base_for_agent_cv/

# Lint with flake8
flake8 base_for_agent_cv/

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## Testing Guidelines

### Test Structure

Tests are organized in the `tests/` directory:

- `test_validator.py` - GDPR and ČSN validation tests
- `test_api.py` - API endpoint tests
- `test_analysis.py` - Document analysis tests
- `conftest.py` - Shared fixtures

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validator.py -v

# Run with coverage
pytest tests/ --cov=base_for_agent_cv --cov-report=html

# Run tests in parallel
pytest tests/ -n auto

# Run only failed tests from last run
pytest tests/ --lf
```

### Writing Tests

#### Test Naming Convention

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test methods: `test_<behavior>`

#### Example Test Structure

```python
import pytest
from src.pipeline.validator import validate_text

class TestGdprValidation:
    def test_detects_birth_date(self):
        """Verify GDPR validator catches birth date."""
        text = "Datum narození: 15. 1. 1985"
        findings, _ = validate_text(text)
        assert any(f.code == "GDPR_BIRTH_DATE" for f in findings)
```

### Test Coverage

- **Target**: Minimum 80% code coverage
- **Focus**: Critical validation logic, API endpoints, document generation
- **Generate report**: `pytest --cov-report=html` creates `htmlcov/index.html`

---

## CI/CD Pipeline

### GitHub Actions Workflows

The project uses GitHub Actions for automated testing and linting.

#### Workflow: `ci.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

1. **Lint Job**
   - Runs Black, isort, flake8
   - Python 3.11 on Ubuntu
   - Fails if code style violations exist

2. **Test Job**
   - Runs pytest on Python 3.9, 3.10, 3.11
   - Matrix build for multi-version testing
   - Uploads coverage to Codecov

### Local CI Simulation

Before pushing, simulate CI locally:

```bash
# Run linting (simulates lint job)
black --check base_for_agent_cv/
isort --check-only base_for_agent_cv/
flake8 base_for_agent_cv/

# Run tests (simulates test job)
pytest tests/ -v --cov=base_for_agent_cv
```

### CI/CD Best Practices

1. **Always run tests before pushing**
   ```bash
   pytest tests/ && git push
   ```

2. **Fix linting issues immediately**
   ```bash
   black base_for_agent_cv/
   isort base_for_agent_cv/
   ```

3. **Check CI status before merging PRs**
   - All checks must pass
   - Review coverage reports

---

## Coding Style & Naming Conventions

### Python Version

- **Supported**: Python 3.9, 3.10, 3.11
- **Recommended**: Python 3.11

### Code Formatting

- **Line length**: 100 characters
- **Formatter**: Black (enforced by pre-commit hooks)
- **Import sorting**: isort with Black profile

### Naming Conventions

- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: Prefix with `_`

---

## Commit & Pull Request Guidelines

### Commit Messages

Use clear, imperative commit messages:

**Format:**
```
<type>: <subject>

<optional body>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add GDPR validation for rodné číslo
fix: Correct CSN date spacing regex
docs: Update README with API examples
refactor: Extract validation logic to pipeline module
test: Add tests for ČSN typography validation
```

### Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/add-gdpr-check
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: Add GDPR validation for nationality"
   ```

3. **Run tests locally**
   ```bash
   pytest tests/ -v
   pre-commit run --all-files
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/add-gdpr-check
   ```

---

## Security & Configuration

### Environment Variables

**Never commit:**
- API keys
- Secrets
- Personal data
- Database credentials

**Use `.env` file:**
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
OPENAI_VECTOR_STORE_ID=vs_...
```

**Provide `.env.example`:**
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_VECTOR_STORE_ID=vs_your-vector-store-id-here
```

### Security Best Practices

1. **Load environment variables safely**
   ```python
   from src.sdk.utils import load_env_file
   load_env_file()
   ```

2. **Validate user input**
   - Sanitize file uploads
   - Limit file sizes
   - Check file extensions

3. **GDPR Compliance**
   - Never log sensitive data
   - Validate all outputs
   - Provide data removal mechanisms

---

**Last Updated:** 2026-01-31
