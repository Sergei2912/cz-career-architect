from __future__ import annotations

from pathlib import Path

from .config import EXTRACT_PROMPT_PATH, SYSTEM_PROMPT_PATH


def load_system_prompt(path: Path | None = None) -> str:
    resolved_path = path or SYSTEM_PROMPT_PATH
    return resolved_path.read_text(encoding="utf-8")


def load_extract_prompt(path: Path | None = None) -> str:
    resolved_path = path or EXTRACT_PROMPT_PATH
    return resolved_path.read_text(encoding="utf-8")
