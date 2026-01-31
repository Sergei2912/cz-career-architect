# CZ Career Architect - Quick Reference

## Installation

```bash
# Quick setup
./setup.sh

# Manual setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your API key
```

## Running the Application

```bash
# Interactive Chat
cd base_for_agent_cv
python src/main.py --mode chat

# Generate Full Package
python src/main.py --mode full_package --validate

# Validate Text
python src/main.py --mode check --text "Your text here"

# Rewrite with ČSN Typography
python src/main.py --mode rewrite --text "2015-2023"

# API Server
python api.py
```

## Development Commands

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Run all checks
make check-all

# Clean generated files
make clean
```

## Docker

```bash
# Build image
make docker-build

# Run container
make docker-run

# Or manually
docker build -t cz-career-architect .
docker run -p 8000:8000 --env-file .env cz-career-architect
```

## Testing

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_validator.py -v

# With coverage report
pytest tests/ --cov=base_for_agent_cv --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Code Quality

```bash
# Format with Black
black base_for_agent_cv/

# Sort imports
isort base_for_agent_cv/

# Lint with flake8
flake8 base_for_agent_cv/

# Run pre-commit hooks
pre-commit run --all-files
```

## Project Structure

```
cz-career-architect/
├── base_for_agent_cv/      # Main application
│   ├── src/                # Refactored source code
│   │   ├── main.py        # CLI entry point
│   │   ├── chat.py        # Interactive chat
│   │   ├── pipeline/      # Document processing
│   │   └── sdk/           # Core SDK
│   ├── packages/          # Validators and utilities
│   ├── Schemas/           # JSON schemas
│   └── api.py             # FastAPI server
├── tests/                 # Test suite
├── .github/workflows/     # CI/CD
└── requirements.txt       # Dependencies
```

## Environment Variables

Required in `.env`:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
OPENAI_VECTOR_STORE_ID=vs_...
```

## Common Issues

### Import Errors
```bash
# Ensure you're in the right directory
cd base_for_agent_cv
python src/main.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### OpenAI API Errors
- Check `.env` file has correct API key
- Verify model name is correct
- Check vector store ID

## API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `POST /chat` - Chat message
- `POST /upload` - File upload
- `GET /files` - List files

## GDPR Prohibited Fields

❌ Birth date / Age  
❌ Marital status / Children  
❌ Photo / Nationality  
❌ Rodné číslo  
❌ Full address  
❌ Religion / Ethnicity  

## Useful Commands

```bash
# Check Python version
python --version

# Check if OpenAI key is set
echo $OPENAI_API_KEY

# View logs
tail -f base_for_agent_cv/app.log

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## Documentation

- **User Guide**: `base_for_agent_cv/README.md`
- **Developer Guide**: `base_for_agent_cv/AGENTS.md`
- **Contributing**: `CONTRIBUTING.md`
- **Changelog**: `CHANGELOG.md`

## Support

- GitHub Issues: https://github.com/Sergei2912/cz-career-architect/issues
- Documentation: See README files

---

**Version**: 2.0.0 | **Model**: GPT-5.2
