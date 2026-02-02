"""Legacy FastAPI entrypoint.

Historically this repository shipped a monolithic server in this file.
The canonical implementation now lives in `app/main.py`.

Keeping this shim preserves backwards compatibility for:
- `python api.py`
- `uvicorn api:app`

and ensures there is only one codepath to maintain.
"""

from app.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
