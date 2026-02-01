import sys
from pathlib import Path

# Add base_for_agent_cv to path
base_path = Path(__file__).parent.parent / "base_for_agent_cv"
sys.path.insert(0, str(base_path))

import pytest
from fastapi.testclient import TestClient

# Try to import the app
try:
    from app.main import app
except ImportError:
    # Create a dummy app for tests that don't need the full API
    from fastapi import FastAPI
    app = FastAPI()

@pytest.fixture
def client():
    return TestClient(app)
