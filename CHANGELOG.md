# Changelog

All notable changes to CZ Career Architect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-31

### Added

#### Project Structure
- Modular `src/` directory structure with `pipeline/` and `sdk/` submodules
- Separated validation logic into `src/pipeline/validator.py`
- Separated generation logic into `src/pipeline/generator.py`
- Created SDK modules for model interactions (`src/sdk/model.py`) and utilities (`src/sdk/utils.py`)

#### Documentation
- Comprehensive root `README.md` with quick start, features, and API documentation
- Enhanced `base_for_agent_cv/README.md` with detailed usage examples
- Expanded `AGENTS.md` with testing guidelines and CI/CD instructions
- Added `CONTRIBUTING.md` with contribution guidelines
- Created `CHANGELOG.md` for version tracking

#### CI/CD
- GitHub Actions workflow for automated testing (`.github/workflows/ci.yml`)
- Linting checks with Black, isort, and flake8
- Multi-version testing (Python 3.9, 3.10, 3.11)
- Codecov integration for coverage reporting

#### Development Tools
- Pre-commit hooks configuration (`.pre-commit-config.yaml`)
- Black code formatter configuration
- isort import sorter configuration
- flake8 linting configuration
- pytest configuration in `pyproject.toml`

#### Security
- `.env.example` template for environment variables
- Enhanced `.gitignore` for security and cleanup
- Environment variable validation in utilities

#### Containerization
- `Dockerfile` for containerized deployment
- `.dockerignore` for optimized image builds
- Docker setup documentation

#### Testing
- Moved tests to root `tests/` directory
- Added pytest configuration
- Test coverage reporting setup

#### Package Management
- Enhanced `pyproject.toml` with package metadata
- Consolidated `requirements.txt` with all dependencies
- Separated development dependencies

### Changed
- Updated entry points to use new modular structure
- Refactored imports to use `src.` prefix
- Improved code organization for better maintainability
- Enhanced error handling and validation

### Deprecated
- Old flat file structure (files remain for backward compatibility)

### Fixed
- Import path issues in modular structure
- Environment variable loading consistency

### Security
- Removed hardcoded environment variable loading
- Added `.env.example` for safe credential sharing
- Enhanced `.gitignore` to prevent credential leaks

---

## [1.2.3] - 2026-01-27

### Added
- Chat-first interaction mode
- RAG-mandatory knowledge base usage
- GPT-5.2 model support
- Simplified system prompts

### Changed
- Updated to version 1.2.3
- Improved natural language dialog

---

## [1.2.2] - 2026-01-20

### Added
- Interactive chat mode
- Validation mode for text checking
- Rewrite mode for ČSN typography

### Changed
- Enhanced GDPR validation rules
- Improved ČSN typography checks

---

## [1.0.0] - 2025-12-01

### Added
- Initial release
- CV generation with GDPR compliance
- Cover letter generation
- ATS-safe document formatting
- ČSN 01 6910 typography support
- FastAPI web interface
- File upload support (PDF, DOCX, TXT)

---

[2.0.0]: https://github.com/Sergei2912/cz-career-architect/compare/v1.2.3...v2.0.0
[1.2.3]: https://github.com/Sergei2912/cz-career-architect/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/Sergei2912/cz-career-architect/compare/v1.0.0...v1.2.2
[1.0.0]: https://github.com/Sergei2912/cz-career-architect/releases/tag/v1.0.0
