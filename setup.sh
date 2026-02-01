#!/bin/bash
# Quick Start Script for CZ Career Architect

set -e

echo "================================================"
echo "  CZ Career Architect - Quick Start Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo "✓ Dependencies installed"

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Setting up environment file..."
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your OpenAI API key"
    echo "   OpenAI API Key is required to run the application"
else
    echo "✓ .env file already exists"
fi

# Install pre-commit hooks (optional)
echo ""
read -p "Install pre-commit hooks? (recommended for development) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install pre-commit > /dev/null
    pre-commit install
    echo "✓ Pre-commit hooks installed"
fi

# Success message
echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your OpenAI API key:"
echo "   nano .env"
echo ""
echo "2. Run interactive chat:"
echo "   cd base_for_agent_cv"
echo "   python src/main.py --mode chat"
echo ""
echo "3. Or start API server:"
echo "   cd base_for_agent_cv"
echo "   python api.py"
echo ""
echo "For more information, see README.md"
echo ""
