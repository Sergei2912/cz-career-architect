"""Profile loader (v0)

Goal: move profile logic out of hard-coded prompts.
This is additive and does not break current runtime.

A profile is a YAML file in base_for_agent_cv/profiles/.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent
PROFILES_DIR = ROOT_DIR / "profiles"


@dataclass(frozen=True)
class Profile:
    profile_id: str
    raw: dict[str, Any]


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "PyYAML is required to load profiles. Install pyyaml."
        ) from e

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid profile YAML (expected mapping): {path}")
    return data


def load_profile(profile_id: str) -> Profile:
    path = PROFILES_DIR / f"{profile_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_id} ({path})")
    raw = _load_yaml(path)
    pid = raw.get("profile_id") or profile_id
    return Profile(profile_id=str(pid), raw=raw)


def list_profiles() -> list[str]:
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in PROFILES_DIR.glob("*.yaml"))
