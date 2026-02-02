#!/bin/bash
# CZ Career Architect - Start API Server

cd "$(dirname "$0")"

echo "========================================"
echo "  CZ Career Architect API"
echo "========================================"
echo ""

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements_api.txt
fi

echo "Starting server on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
