import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..models.schemas import FileInfo
from ..services.text_analysis import analyze_text, extract_text

router = APIRouter(prefix="/files", tags=["files"])

# Configuration
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".rtf"}

# In-memory storage (migrated from api.py)
# Note: In a real app this should be a database or shared service
uploaded_files: dict[str, dict] = {}


def get_uploaded_files_store():
    return uploaded_files


@router.post("/upload", response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Формат не поддерживается. Разрешены: PDF, DOCX, TXT")

    # Stream upload to disk to avoid holding the whole file in memory.
    file_path_tmp = UPLOAD_DIR / f"tmp_{uuid.uuid4().hex}{suffix}"
    hasher = hashlib.md5()
    size = 0

    try:
        with file_path_tmp.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(400, "Файл слишком большой. Максимум 10 МБ")
                hasher.update(chunk)
                out.write(chunk)

        file_id = hasher.hexdigest()[:8] + "_" + str(uuid.uuid4())[:4]
        file_path = UPLOAD_DIR / f"{file_id}{suffix}"
        file_path_tmp.replace(file_path)
    finally:
        # Best-effort cleanup if anything fails before rename.
        file_path_tmp.unlink(missing_ok=True)

    text = extract_text(file_path)
    issues = analyze_text(text)
    preview = text[:300] + "..." if len(text) > 300 else text

    file_info = {
        "id": file_id,
        "name": file.filename,
        "size": size,
        "type": suffix[1:],
        "path": str(file_path),
        "text": text,
        "uploaded_at": datetime.now().isoformat(),
        "preview": preview,
        "issues": issues,
    }
    uploaded_files[file_id] = file_info

    return FileInfo(**{k: v for k, v in file_info.items() if k != "path" and k != "text"})


@router.get("/", response_model=List[FileInfo])
async def list_files():
    return [
        FileInfo(
            id=f["id"],
            name=f["name"],
            size=f["size"],
            type=f["type"],
            uploaded_at=f["uploaded_at"],
            preview=f.get("preview"),
            issues=f.get("issues"),
        )
        for f in uploaded_files.values()
    ]


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    if file_id not in uploaded_files:
        raise HTTPException(404, "Файл не найден")

    file_info = uploaded_files[file_id]
    Path(file_info["path"]).unlink(missing_ok=True)
    del uploaded_files[file_id]

    return {"status": "deleted"}
