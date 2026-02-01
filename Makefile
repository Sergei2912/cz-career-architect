# Makefile for CZ Career Architect

.PHONY: help install dev-install test lint format clean run-chat run-api docker-build docker-run

# Default target
help:
	@echo "CZ Career Architect - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install         Install production dependencies"
	@echo "  make dev-install     Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make format          Format code with Black and isort"
	@echo "  make lint            Run linting checks"
	@echo "  make test            Run all tests"
	@echo "  make test-coverage   Run tests with HTML coverage report"
	@echo "  make test-quick      Quick test run (no verbose)"
	@echo "  make test-file FILE=<name>  Run specific test file"
	@echo "  make install-test    Install test dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run-chat        Run interactive chat mode"
	@echo "  make run-api         Run API server"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    Build Docker image"
	@echo "  make docker-run      Run Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           Remove generated files"

# Installation
install:
	pip install -r requirements.txt

dev-install: install
	pip install pytest pytest-asyncio pytest-cov flake8 black isort pre-commit
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=base_for_agent_cv --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "HTML coverage report: htmlcov/index.html"

test-quick:
	pytest tests/ -q

test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify FILE=test_name"; \
		echo "Example: make test-file FILE=test_config"; \
		exit 1; \
	fi
	pytest tests/$(FILE).py -v

install-test:
	pip install pytest pytest-asyncio pytest-cov pytest-mock

# Code quality
format:
	black base_for_agent_cv/
	isort base_for_agent_cv/

lint:
	black --check base_for_agent_cv/
	isort --check-only base_for_agent_cv/
	flake8 base_for_agent_cv/

# Running
run-chat:
	cd base_for_agent_cv && python src/main.py --mode chat

run-api:
	cd base_for_agent_cv && python api.py

run-validate:
	cd base_for_agent_cv && python src/main.py --mode check --text "$(TEXT)"

# Docker
docker-build:
	docker build -t cz-career-architect:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env cz-career-architect:latest

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache htmlcov .coverage coverage.xml
	rm -rf build dist *.egg-info
	@echo "Cleanup complete"

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Check everything before commit
check-all: format lint test
	@echo "All checks passed! Ready to commit."
