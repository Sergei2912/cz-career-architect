#!/bin/bash
# CZ Career Architect - Start API Server

cd "$(dirname "$0")"

echo "========================================"
echo "  CZ Career Architect API v1.2.3"
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

uvicorn api:app --reload --host 0.0.0.0 --port 8000
