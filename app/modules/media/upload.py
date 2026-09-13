import os
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.core.storage import ensure_upload_dir

ALLOWED = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = settings.MAX_UPLOAD_MB * 1024 * 1024


async def save_upload(file: UploadFile, request_id: int) -> str:
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    ext = ext_map.get(file.content_type, "jpg")
    filename = f"{request_id}_{uuid4().hex}.{ext}"

    upload_dir = ensure_upload_dir()
    filepath = os.path.join(str(upload_dir), filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    return f"/static/uploads/{filename}"


# file: app/modules/media/upload.py
