# CZ Career Architect - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY base_for_agent_cv/ ./base_for_agent_cv/
COPY .env.example ./.env.example

# Create output directory
RUN mkdir -p base_for_agent_cv/out base_for_agent_cv/uploads

# Set Python path
ENV PYTHONPATH=/app/base_for_agent_cv

# Expose API port
EXPOSE 8000

# Default command: run API server
CMD ["python", "base_for_agent_cv/api.py"]
