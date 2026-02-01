import sys
from pathlib import Path
import os

# Add base_for_agent_cv to path
base_path = Path(__file__).parent.parent / "base_for_agent_cv"
sys.path.insert(0, str(base_path))

import pytest
from fastapi.testclient import TestClient

# Clean environment before each test
@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables between tests to avoid pollution."""
    # Store original env
    original_env = dict(os.environ)
    yield
    # Restore original env after test
    os.environ.clear()
    os.environ.update(original_env)

# Try to import the v2.0.0 API (api.py, not legacy app/main.py)
try:
    from api import app
except ImportError:
    # Create a dummy app for tests that don't need the full API
    from fastapi import FastAPI
    app = FastAPI()

@pytest.fixture
def client():
    return TestClient(app)
