from pathlib import Path

from app.core.config import settings


def ensure_upload_dir() -> Path:
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


# file: app/core/storage.py
