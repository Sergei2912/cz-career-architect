import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def _reset_global_stores(monkeypatch, tmp_path):
    """Prevent cross-test coupling by resetting in-memory stores and upload dir."""

    # Ensure auth does not block tests unless explicitly tested.
    monkeypatch.delenv("API_KEY", raising=False)

    from app.routers import chat as chat_router, files as files_router

    # Reset in-memory stores
    chat_router.chat_sessions.clear()
    files_router.uploaded_files.clear()

    # Redirect uploads to a temp directory
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    files_router.UPLOAD_DIR = upload_dir


@pytest.fixture
def client():
    return TestClient(app)
