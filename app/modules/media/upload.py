"""
رفع الملفات — Supabase Storage أو Local.
متوافق مع routes.py الذي يستدعي: save_upload(file, request_id)
"""

import logging

from fastapi import UploadFile

from app.core.config import settings
from app.core.storage import (
    check_size,
    generate_path,
    storage,
    validate_image,
)

logger = logging.getLogger(__name__)


async def save_upload(
    file: UploadFile,
    request_id: int,
) -> str:
    """
    يرفع ملف صورة مرجعية ويعيد URL/المسار المخزّن.
    """
    # 1. تحقق
    validate_image(file)
    await check_size(file, settings.MAX_IMAGE_MB)

    # 2. ولّد مساراً
    path = generate_path(
        prefix=f"requests/{request_id}",
        filename=file.filename or "image.jpg",
    )

    # 3. ارفع
    url = await storage.upload(
        file=file,
        bucket=settings.SUPABASE_BUCKET_REQUESTS,
        path=path,
    )

    logger.info("✅ save_upload: request=%s → %s", request_id, url)
    return url
