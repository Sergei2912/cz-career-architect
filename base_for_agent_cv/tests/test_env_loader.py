import os
from pathlib import Path

from env_loader import load_env


def test_env_loader_does_not_override_existing_env(tmp_path: Path, monkeypatch):
    (tmp_path / ".env").write_text("OPENAI_MODEL=from_env_file\n")

    monkeypatch.setenv("OPENAI_MODEL", "from_real_env")
    load_env(tmp_path)

    assert os.getenv("OPENAI_MODEL") == "from_real_env"


def test_env_loader_sets_missing_env(tmp_path: Path, monkeypatch):
    (tmp_path / ".env").write_text("OPENAI_MODEL=from_env_file\n")

    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    load_env(tmp_path)

    assert os.getenv("OPENAI_MODEL") == "from_env_file"
