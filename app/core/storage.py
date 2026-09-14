"""
طبقة تجريد للتخزين.

توفر واجهة موحّدة للتعامل مع:
- Supabase Storage (الإنتاج)
- التخزين المحلي (التطوير)

الاستخدام:
    from app.core.storage import storage, generate_path

    path = generate_path("properties/123", "cover.jpg")
    url = await storage.upload(file, bucket="property-images", path=path)
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)


# ===============================================================
# Base Backend
# ===============================================================
class StorageBackend(ABC):
    """واجهة موحّدة لأي backend تخزين."""

    @abstractmethod
    async def upload(
        self,
        file: UploadFile,
        bucket: str,
        path: str,
    ) -> str:
        """يرفع ملفاً ويعيد URL العام."""
        ...

    @abstractmethod
    async def delete(self, bucket: str, path: str) -> bool:
        """يحذف ملفاً. يعيد True عند النجاح."""
        ...

    @abstractmethod
    def public_url(self, bucket: str, path: str) -> str:
        """يعيد URL العام لملف."""
        ...


# ===============================================================
# Supabase Storage
# ===============================================================
class SupabaseStorage(StorageBackend):
    """Backend يعتمد على Supabase Storage."""

    def __init__(self) -> None:
        from supabase import create_client

        self._client = create_client(
            settings.SUPABASE_URL,
            settings.supabase_secret_key_value,
        )
        logger.info("✅ Supabase Storage initialized: %s", settings.SUPABASE_URL)

    async def upload(
        self,
        file: UploadFile,
        bucket: str,
        path: str,
    ) -> str:
        content = await file.read()
        content_type = file.content_type or "application/octet-stream"

        try:
            self._client.storage.from_(bucket).upload(
                path=path,
                file=content,
                file_options={
                    "content-type": content_type,
                    "upsert": "true",
                },
            )
        except Exception as exc:
            logger.error("❌ فشل الرفع إلى Supabase (%s/%s): %s", bucket, path, exc)
            raise

        url = self.public_url(bucket, path)
        logger.info("📤 Uploaded to Supabase: %s", url)
        return url

    async def delete(self, bucket: str, path: str) -> bool:
        try:
            self._client.storage.from_(bucket).remove([path])
            logger.info("🗑️  Deleted from Supabase: %s/%s", bucket, path)
            return True
        except Exception as exc:
            logger.warning("فشل حذف %s/%s: %s", bucket, path, exc)
            return False

    def public_url(self, bucket: str, path: str) -> str:
        return (
            f"{settings.SUPABASE_URL}"
            f"/storage/v1/object/public/{bucket}/{path}"
        )


# ===============================================================
# Local Storage
# ===============================================================
class LocalStorage(StorageBackend):
    """Backend محلي للتطوير."""

    def __init__(self) -> None:
        self._root = Path(settings.UPLOAD_DIR)
        self._root.mkdir(parents=True, exist_ok=True)
        logger.info("✅ Local Storage initialized: %s", self._root)

    async def upload(
        self,
        file: UploadFile,
        bucket: str,
        path: str,
    ) -> str:
        target = self._root / bucket / path
        target.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        target.write_bytes(content)

        url = f"/static/uploads/{bucket}/{path}"
        logger.info("📤 Uploaded locally: %s", url)
        return url

    async def delete(self, bucket: str, path: str) -> bool:
        target = self._root / bucket / path
        if target.exists():
            target.unlink()
            return True
        return False

    def public_url(self, bucket: str, path: str) -> str:
        return f"/static/uploads/{bucket}/{path}"


# ===============================================================
# Factory
# ===============================================================
def _build_storage() -> StorageBackend:
    if settings.use_supabase_storage:
        try:
            return SupabaseStorage()
        except Exception as exc:
            logger.error(
                "❌ فشل تهيئة Supabase Storage: %s — العودة إلى LocalStorage",
                exc,
            )
    return LocalStorage()


# Singleton
storage: StorageBackend = _build_storage()


# ===============================================================
# Helpers
# ===============================================================
def generate_path(prefix: str, filename: str) -> str:
    """
    يولد مساراً آمناً وفريداً.
    مثال: generate_path("properties/123", "cover.jpg")
         → "properties/123/a1b2c3d4-cover.jpg"
    """
    ext = Path(filename).suffix.lower()
    unique = uuid.uuid4().hex[:8]
    stem = Path(filename).stem[:40]
    safe_stem = "".join(c for c in stem if c.isalnum() or c in "-_")
    return f"{prefix}/{unique}-{safe_stem}{ext}"


def validate_image(file: UploadFile) -> None:
    """يتحقق من أن الملف صورة صالحة."""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise ValueError(
            f"نوع الصورة غير مدعوم: {file.content_type}. "
            f"المسموح: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    ext = Path(file.filename or "").suffix.lower()
    if ext and ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"امتداد الصورة غير مدعوم: {ext}")


def validate_video(file: UploadFile) -> None:
    """يتحقق من أن الملف فيديو صالح."""
    if file.content_type not in settings.ALLOWED_VIDEO_TYPES:
        raise ValueError(
            f"نوع الفيديو غير مدعوم: {file.content_type}. "
            f"المسموح: {', '.join(settings.ALLOWED_VIDEO_TYPES)}"
        )
    ext = Path(file.filename or "").suffix.lower()
    if ext and ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError(f"امتداد الفيديو غير مدعوم: {ext}")


async def check_size(file: UploadFile, max_mb: int) -> None:
    """يتحقق من حجم الملف ويرفع استثناء إذا تجاوز الحد."""
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    await file.seek(0)

    if size_mb > max_mb:
        raise ValueError(
            f"حجم الملف كبير جداً ({size_mb:.1f}MB) — الحد الأقصى {max_mb}MB"
        )


def extract_path_from_url(url: str) -> Optional[str]:
    """
    يستخرج الـ path من URL.
    مثال:
      https://xxx.supabase.co/storage/v1/object/public/property-images/properties/1/abc.jpg
      → properties/1/abc.jpg
    """
    marker = "/object/public/"
    if marker in url:
        after = url.split(marker, 1)[1]
        if "/" in after:
            return after.split("/", 1)[1]
    if url.startswith("/static/uploads/"):
        return url.replace("/static/uploads/", "", 1)
    return None
