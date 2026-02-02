import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import chat, files, legacy
from .security import require_api_key

# Load environment
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            os.environ[key] = val

VERSION = os.getenv("APP_VERSION", "2.0.0")

app = FastAPI(
    title="CZ Career Architect API",
    version=VERSION,
    description="Conversational AI for Czech healthcare HR documents",
)


def _parse_csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    return [part.strip() for part in raw.split(",") if part.strip()]


cors_allow_origins = _parse_csv_env(
    "CORS_ALLOW_ORIGINS",
    ["http://localhost:8000", "http://127.0.0.1:8000"],
)

# Safe-by-default: do not allow cookies/credentials unless explicitly enabled.
# Note: allow_credentials=True with allow_origins=["*"] is unsafe/invalid in browsers.
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() in {
    "1",
    "true",
    "yes",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
_auth_dependency = [Depends(require_api_key)]

app.include_router(files.router, dependencies=_auth_dependency)
app.include_router(chat.router, dependencies=_auth_dependency)
# Legacy aliases (old api.py routes)
app.include_router(legacy.router, dependencies=_auth_dependency)

# Serve frontend
FRONTEND_DIR = ROOT_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    if (FRONTEND_DIR / "index.html").exists():
        return FileResponse(FRONTEND_DIR / "index.html")
    return {"message": f"CZ Career Architect API v{VERSION}", "docs": "/docs"}


@app.get("/health")
async def health():
    return {
        "status": "online",
        "version": VERSION,
        "model": os.getenv("OPENAI_MODEL", "gpt-5.2"),
    }


if __name__ == "__main__":
    import uvicorn

    print(f"""
╔══════════════════════════════════════════════════════╗
║       CZ Career Architect API v{VERSION}               ║
╠══════════════════════════════════════════════════════╣
║  🌐 Server:  http://localhost:8000                   ║
║  📚 Docs:    http://localhost:8000/docs              ║
║  💬 Chat:    http://localhost:8000                   ║
╚══════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
