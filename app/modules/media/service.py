"""
خدمة رفع الصور والفيديوهات للعقارات.
"""

import logging
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage import (
    check_size,
    extract_path_from_url,
    generate_path,
    storage,
    validate_image,
    validate_video,
)
from app.modules.media.models import PropertyImage

logger = logging.getLogger(__name__)


# ===============================================================
# رفع صورة عقار
# ===============================================================
async def upload_property_image(
    db: Session,
    property_id: int,
    file: UploadFile,
    is_cover: bool = False,
) -> PropertyImage:
    """
    يرفع صورة عقار إلى التخزين ويسجّلها في قاعدة البيانات.
    """
    # 1. تحقق
    validate_image(file)
    await check_size(file, settings.MAX_IMAGE_MB)

    # 2. ولّد مساراً فريداً
    path = generate_path(
        prefix=f"properties/{property_id}",
        filename=file.filename or "image.jpg",
    )

    # 3. ارفع
    url = await storage.upload(
        file=file,
        bucket=settings.SUPABASE_BUCKET_PROPERTIES,
        path=path,
    )

    # 4. إذا كانت cover، أزل cover من باقي الصور
    if is_cover:
        db.query(PropertyImage).filter(
            PropertyImage.property_id == property_id,
            PropertyImage.is_cover.is_(True),
        ).update({"is_cover": False})

    # 5. احفظ في قاعدة البيانات
    image = PropertyImage(
        property_id=property_id,
        storage_path=url,
        is_cover=is_cover,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    logger.info("✅ صورة مرفوعة للعقار %s: %s", property_id, url)
    return image


# ===============================================================
# حذف صورة عقار
# ===============================================================
async def delete_property_image(
    db: Session,
    image: PropertyImage,
) -> bool:
    """يحذف صورة من التخزين وقاعدة البيانات."""
    path = extract_path_from_url(image.storage_path)
    if path:
        await storage.delete(
            bucket=settings.SUPABASE_BUCKET_PROPERTIES,
            path=path,
        )

    db.delete(image)
    db.commit()
    return True


# ===============================================================
# رفع فيديو عقار
# ===============================================================
async def upload_property_video(
    db: Session,
    property_id: int,
    file: UploadFile,
) -> str:
    """
    يرفع فيديو عقار ويعيد URL.
    ملاحظة: لا يوجد جدول للفيديوهات حالياً — يعيد URL فقط.
    """
    validate_video(file)
    await check_size(file, settings.MAX_VIDEO_MB)

    path = generate_path(
        prefix=f"properties/{property_id}/videos",
        filename=file.filename or "video.mp4",
    )

    url = await storage.upload(
        file=file,
        bucket=settings.SUPABASE_BUCKET_VIDEOS,
        path=path,
    )

    logger.info("✅ فيديو مرفوع للعقار %s: %s", property_id, url)
    return url


# ===============================================================
# جلب صور عقار
# ===============================================================
def get_property_images(
    db: Session,
    property_id: int,
) -> list[PropertyImage]:
    """يعيد كل صور عقار مع ترتيب cover أولاً."""
    return (
        db.query(PropertyImage)
        .filter(PropertyImage.property_id == property_id)
        .order_by(PropertyImage.is_cover.desc(), PropertyImage.id.asc())
        .all()
    )
