"""Legacy routes compatibility layer.

This router provides the old (monolithic api.py) endpoint paths so existing
clients and older docs keep working, while the canonical implementation lives
in app/routers.

All routes are excluded from OpenAPI schema to keep /docs clean.
"""

from fastapi import APIRouter, File, Form, Header, UploadFile

from ..models.schemas import ChatRequest
from . import chat as chat_router, files as files_router

router = APIRouter(include_in_schema=False)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
):
    # Old path: POST /upload
    return await files_router.upload_file(file, session_id=session_id, x_session_id=x_session_id)


@router.get("/files")
async def list_files(
    session_id: str | None = None,
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
):
    # Old path: GET /files
    return await files_router.list_files(session_id=session_id, x_session_id=x_session_id)


@router.post("/chat")
async def chat(request: ChatRequest):
    # Old path: POST /chat
    return await chat_router.chat(request)


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    # Old path: GET /session/{id}
    return await chat_router.get_session(session_id)


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    # Old path: DELETE /session/{id}
    return await chat_router.clear_session(session_id)


# Optional: accept non-trailing-slash variants to avoid 307 redirects.
@router.get("/files/")
async def list_files_slash(
    session_id: str | None = None,
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
):
    return await files_router.list_files(session_id=session_id, x_session_id=x_session_id)


@router.post("/chat/")
async def chat_slash(request: ChatRequest):
    return await chat_router.chat(request)
