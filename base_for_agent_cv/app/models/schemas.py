from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    file_ids: Optional[List[str]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    suggestions: Optional[List[str]] = None


class FileInfo(BaseModel):
    id: str
    name: str
    size: int
    type: str
    uploaded_at: str
    preview: Optional[str] = None
    issues: Optional[List[str]] = None
