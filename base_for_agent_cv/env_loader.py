"""Environment (.env) loader.

Safe-by-default precedence: real environment variables win over .env.
This is important for production deployments (containers, K8s, secrets managers).

Supports only simple KEY=VALUE lines (same as previous implementation).
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env(root_dir: Path, filename: str = ".env") -> None:
    env_path = root_dir / filename
    if not env_path.exists():
        return

    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        # Do not override already-set env vars.
        os.environ.setdefault(key, val)
