# CZ Career Architect

AI-powered assistant for creating HR documents for Czech healthcare professionals.

**Version:** 2.0.0 | **Model:** gpt-5.2 | **Updated:** 2026-01-27

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [GDPR Compliance](#gdpr-compliance)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)

---

## Features

- **CV Generation**: ATS-safe, ČSN 01 6910 compliant CVs
- **Cover Letters**: Tailored motivational letters for Czech healthcare positions
- **GDPR Validation**: Automatic checking for GDPR compliance
- **ATS Validation**: Ensures documents are ATS-compatible
- **Interactive Chat**: Natural language interface for document generation
- **File Upload**: Support for PDF, DOCX, TXT formats
- **RAG-enabled**: Vector store integration for knowledge-based responses

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Sergei2912/cz-career-architect.git
cd cz-career-architect

# 2. Set up virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your OpenAI API key

# 5. Run the application
cd base_for_agent_cv
python src/main.py --mode chat
```

---

## Environment Setup

### Prerequisites

- **Python**: 3.9, 3.10, or 3.11
- **OpenAI API Key**: Required for GPT model access
- **pip**: Python package manager

### Docker Setup (Optional)

```bash
# Build Docker image
docker build -t cz-career-architect .

# Run container
docker run -p 8000:8000 --env-file .env cz-career-architect
```

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-5.2
OPENAI_VECTOR_STORE_ID=vs_your-vector-store-id-here
```

See `.env.example` for a complete template.

---

## Running the Application

### Interactive Chat Mode

Start an interactive chat session for guided document creation:

```bash
cd base_for_agent_cv
python src/main.py --mode chat
```

**Example interaction:**
```
You: /intake
Agent: [Shows 12-field intake template]
You: Create a CV for a dentist position at FN Motol...
```

### Full Package Generation

Generate a complete HR document package:

```bash
cd base_for_agent_cv
python src/main.py --mode full_package --validate
```

Output: `out/full_package.md` containing:
- Profile Analysis (Russian)
- CV (Czech)
- Cover Letter (Czech)

### Batch Validation

Validate text for GDPR and ČSN compliance:

```bash
cd base_for_agent_cv
python src/main.py --mode check --text "Datum narození: 15. 1. 1985"
```

### Text Rewriting

Rewrite text with ČSN typography:

```bash
cd base_for_agent_cv
python src/main.py --mode rewrite --text "Praxe 2015-2023"
```

### API Server

Run the FastAPI server for web-based access:

```bash
cd base_for_agent_cv
python api.py
# Or: uvicorn api:app --reload
```

Access the web interface at: `http://localhost:8000`

---

## API Documentation

### Endpoints

#### `GET /`
Returns the web chat interface.

**Response:** HTML page

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "2.0.0",
  "model": "gpt-5.2"
}
```

#### `POST /chat`
Send a message to the chat assistant.

**Request:**
```json
{
  "message": "Create a CV for dentist position",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "I'll help you create a CV...",
  "session_id": "session-123"
}
```

#### `POST /upload`
Upload a file for processing.

**Request:** multipart/form-data with file

**Response:**
```json
{
  "file_id": "file_abc123",
  "filename": "cv_draft.pdf",
  "size": 102400,
  "status": "processed"
}
```

#### `GET /files`
List uploaded files.

**Response:**
```json
{
  "files": [
    {
      "file_id": "file_abc123",
      "filename": "cv_draft.pdf",
      "uploaded_at": "2026-01-27T10:30:00Z"
    }
  ]
}
```

---

## GDPR Compliance

### Prohibited Information

The following data must **NOT** appear in generated documents:

- **Art. 5(1)(c)**: birth_date, age, marital_status, children, photo, nationality, full_address
- **Art. 9**: ethnicity, religion, health_status, union_member
- **Art. 87**: rodné číslo (Czech national ID)

### Allowed Information

- Name
- City and country
- Email and phone
- Professional experience
- Education and qualifications
- Medical credentials (nostrifikace, approbation status)

### Consent Clause

- **Specific job application**: NOT required (Art. 6(1)(b) or 6(1)(f))
- **Talent pool submission**: Required with withdrawal option

---

## Development

### Project Structure

```
cz-career-architect/
├── src/
│   ├── main.py           # Main entry point
│   ├── chat.py           # Interactive chat logic
│   ├── pipeline/
│   │   ├── validator.py  # Validation logic
│   │   └── generator.py  # Document generation
│   └── sdk/
│       ├── model.py      # GPT model interactions
│       └── utils.py      # Helper functions
├── tests/                # Test suite
├── packages/             # Validators and utilities
├── Schemas/              # JSON schemas
├── Examples/             # Reference documents
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .flake8               # Flake8 configuration
├── pyproject.toml        # Project configuration
└── .pre-commit-config.yaml  # Pre-commit hooks
```

### Code Quality

#### Install pre-commit hooks

```bash
pip install pre-commit
pre-commit install
```

#### Run linters manually

```bash
# Format code with Black
black base_for_agent_cv/

# Sort imports
isort base_for_agent_cv/

# Check with Flake8
flake8 base_for_agent_cv/
```

---

## Testing

### Run all tests

```bash
cd base_for_agent_cv
pytest tests/ -v
```

### Run with coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test file

```bash
pytest tests/test_validator.py -v
```

### Test Categories

- `test_validator.py`: GDPR and ČSN validation tests
- `test_api.py`: API endpoint tests
- `test_analysis.py`: Document analysis tests

---

## Contributing

### Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and commit: `git commit -m "Add new feature"`
4. Run tests: `pytest tests/`
5. Run linters: `pre-commit run --all-files`
6. Push to your fork: `git push origin feature/my-feature`
7. Create a Pull Request

### Coding Standards

- **Python version**: 3.9+
- **Code style**: Black (line length: 100)
- **Import sorting**: isort
- **Linting**: flake8
- **Type hints**: Encouraged for new code

### Commit Messages

Use clear, imperative commit messages:
- ✅ "Add GDPR validation for birth dates"
- ✅ "Fix CSN typography spacing"
- ❌ "fixed stuff"
- ❌ "WIP"

---

## CI/CD

GitHub Actions workflows run automatically on:
- Push to `main` or `develop` branches
- Pull requests

### Workflows

- **Linting**: Black, isort, flake8
- **Testing**: pytest on Python 3.9, 3.10, 3.11
- **Coverage**: Uploaded to Codecov

---

## License

[Add your license information here]

---

## Support

For questions or issues:
- Open an issue on GitHub
- Contact: [Add contact information]

---

**CZ Career Architect v2.0.0** | Powered by GPT-5.2
