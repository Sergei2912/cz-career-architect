# CZ Career Architect

[![CI](https://github.com/Sergei2912/cz-career-architect/workflows/CI/badge.svg)](https://github.com/Sergei2912/cz-career-architect/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**English** | **[Русский](README_RU.md)**

AI-powered assistant for creating GDPR-compliant HR documents for Czech healthcare professionals.

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/Sergei2912/cz-career-architect.git
cd cz-career-architect
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your OpenAI API key

# Run interactive chat
cd base_for_agent_cv
python src/main.py --mode chat
```

---

## 📋 Features

- ✅ **GDPR-Compliant CV Generation** - Automatic validation and compliance checking
- ✅ **ČSN 01 6910 Typography** - Correct Czech typography standards
- ✅ **ATS-Safe Documents** - Optimized for Applicant Tracking Systems
- ✅ **Cover Letter Generation** - Tailored motivational letters
- ✅ **Interactive Chat Interface** - Natural language document creation
- ✅ **Batch Validation** - Validate existing documents
- ✅ **API Server** - RESTful API with web interface
- ✅ **File Upload Support** - PDF, DOCX, TXT processing

---

## 📖 Documentation

- **[User Guide](base_for_agent_cv/README.md)** - Detailed usage instructions and API documentation
- **[Developer Guide](base_for_agent_cv/AGENTS.md)** - Contributing, testing, and CI/CD guidelines
- **[API Reference](#api-endpoints)** - REST API documentation

---

## 🛠️ Installation

### Prerequisites

- Python 3.9, 3.10, or 3.11
- OpenAI API key
- pip package manager

### Standard Installation

```bash
# Clone repository
git clone https://github.com/Sergei2912/cz-career-architect.git
cd cz-career-architect

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements.txt[dev]
```

### Docker Installation

```bash
# Build image
docker build -t cz-career-architect .

# Run container
docker run -p 8000:8000 --env-file .env cz-career-architect
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-5.2
OPENAI_VECTOR_STORE_ID=vs_your-vector-store-id-here
```

See [`.env.example`](.env.example) for complete template.

---

## 🎯 Usage

### Command Line Interface

```bash
cd base_for_agent_cv

# Interactive chat mode
python src/main.py --mode chat

# Generate full package with validation
python src/main.py --mode full_package --validate

# Validate text for GDPR compliance
python src/main.py --mode check --text "Datum narození: 15.1.1985"

# Rewrite with correct ČSN typography
python src/main.py --mode rewrite --text "Praxe 2015-2023"
```

### API Server

```bash
cd base_for_agent_cv

# Start server
python api.py

# Access web interface
open http://localhost:8000
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Chat
```bash
POST /chat
Content-Type: application/json

{
  "message": "Create a CV for dentist position at FN Motol",
  "session_id": "optional-session-id"
}
```

#### File Upload
```bash
POST /upload
Content-Type: multipart/form-data

file: [binary file data]
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=base_for_agent_cv --cov-report=html

# Specific test file
pytest tests/test_validator.py -v
```

### Code Quality

```bash
# Format code
black base_for_agent_cv/

# Sort imports
isort base_for_agent_cv/

# Lint
flake8 base_for_agent_cv/

# Run pre-commit hooks
pre-commit run --all-files
```

---

## 🔒 GDPR Compliance

### Prohibited Data

Documents **MUST NOT** contain:

- ❌ Birth date / Age
- ❌ Marital status / Children
- ❌ Photo / Nationality
- ❌ Rodné číslo (Czech national ID)
- ❌ Full address
- ❌ Religion / Ethnicity
- ❌ Health status

### Allowed Data

Documents **CAN** contain:

- ✅ Name
- ✅ City and country
- ✅ Email and phone
- ✅ Professional experience
- ✅ Education
- ✅ Medical credentials (nostrifikace, approbation)

---

## 📁 Project Structure

```
cz-career-architect/
├── base_for_agent_cv/           # Main application directory
│   ├── src/                     # Source code
│   │   ├── main.py             # CLI entry point
│   │   ├── chat.py             # Interactive chat
│   │   ├── pipeline/           # Document processing
│   │   │   ├── validator.py   # GDPR/ČSN validation
│   │   │   └── generator.py   # Document generation
│   │   └── sdk/                # Core SDK
│   │       ├── model.py        # GPT model interactions
│   │       └── utils.py        # Utilities
│   ├── packages/               # Domain packages
│   ├── Schemas/                # JSON schemas
│   ├── Examples/               # Reference documents
│   └── tests/                  # Legacy tests (moved to root)
├── tests/                       # Test suite
├── .github/workflows/           # CI/CD configuration
├── requirements.txt             # Dependencies
├── .env.example                # Environment template
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Developer Guide](base_for_agent_cv/AGENTS.md) for:

- Coding standards
- Testing guidelines
- CI/CD workflow
- Pull request process

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run tests: `pytest tests/ -v`
5. Run linters: `pre-commit run --all-files`
6. Commit: `git commit -m "feat: Add my feature"`
7. Push: `git push origin feature/my-feature`
8. Create Pull Request

---

## 🔄 CI/CD

GitHub Actions automatically runs:

- ✅ **Linting** - Black, isort, flake8
- ✅ **Testing** - pytest on Python 3.9, 3.10, 3.11
- ✅ **Coverage** - Codecov integration

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for details.

---

## 📊 Project Status

- **Version**: 2.0.0
- **Model**: GPT-5.2
- **Status**: Beta
- **Python**: 3.9, 3.10, 3.11

---

## 📄 License

[Add your license here]

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/Sergei2912/cz-career-architect/issues)
- **Documentation**: [User Guide](base_for_agent_cv/README.md)
- **Developer Guide**: [AGENTS.md](base_for_agent_cv/AGENTS.md)

---

## 🙏 Acknowledgments

- OpenAI for GPT models
- Czech healthcare community
- All contributors

---

**CZ Career Architect v2.0.0** | Powered by GPT-5.2
