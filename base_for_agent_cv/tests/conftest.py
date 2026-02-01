import pytest
from fastapi.testclient import TestClient

# Import the v2.0.0 API (api.py, not legacy app/main.py)
try:
    from api import app
except ImportError:
    # Create a dummy app for tests that don't need the full API
    from fastapi import FastAPI
    app = FastAPI()

@pytest.fixture
def client():
    return TestClient(app)
