import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import chat, files

# Load environment
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            os.environ[key] = val

VERSION = "1.2.3"

app = FastAPI(
    title="CZ Career Architect API",
    version=VERSION,
    description="Conversational AI for Czech healthcare HR documents",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(files.router)
app.include_router(chat.router)

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
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
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
