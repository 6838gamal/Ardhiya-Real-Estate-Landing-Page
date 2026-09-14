"""
خدمة طلبات المشترين — إنشاء طلبات + رفع صور مرجعية.
"""

import logging

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage import (
    check_size,
    generate_path,
    storage,
    validate_image,
)
from app.modules.buyer_requests.models import (
    BuyerRequest,
    RequestImage,
    RequestSource,
)

logger = logging.getLogger(__name__)


# ===============================================================
# إنشاء طلب من صورة
# ===============================================================
def create_image_request(
    db: Session,
    session_id: str,
    phone: str,
    notes: str,
) -> BuyerRequest:
    """ينشئ طلب شراء من صورة."""
    request = BuyerRequest(
        session_id=session_id or "",
        source=RequestSource.image,
        phone=phone,
        notes=notes,
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    logger.info("✅ طلب صورة أُنشئ: id=%s", request.id)
    return request


# ===============================================================
# إنشاء طلب من مواصفات
# ===============================================================
def create_specs_request(
    db: Session,
    session_id: str,
    **kwargs,
) -> BuyerRequest:
    """ينشئ طلب شراء من مواصفات."""
    request = BuyerRequest(
        session_id=session_id or "",
        source=RequestSource.specs,
        **kwargs,
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    logger.info("✅ طلب مواصفات أُنشئ: id=%s", request.id)
    return request


# ===============================================================
# رفع صورة مرجعية لطلب
# ===============================================================
async def upload_request_image(
    db: Session,
    request_id: int,
    file: UploadFile,
    image_type: str = "reference",
) -> RequestImage:
    """يرفع صورة مرجعية لطلب مشترٍ."""
    validate_image(file)
    await check_size(file, settings.MAX_IMAGE_MB)

    path = generate_path(
        prefix=f"requests/{request_id}",
        filename=file.filename or "image.jpg",
    )

    url = await storage.upload(
        file=file,
        bucket=settings.SUPABASE_BUCKET_REQUESTS,
        path=path,
    )

    image = RequestImage(
        request_id=request_id,
        storage_path=url,
        image_type=image_type,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    logger.info("✅ صورة مرجعية مرفوعة للطلب %s: %s", request_id, url)
    return image


# ===============================================================
# جلب طلب
# ===============================================================
def get_request(db: Session, request_id: int) -> BuyerRequest | None:
    """يعيد طلباً بواسطة ID."""
    return db.query(BuyerRequest).filter(BuyerRequest.id == request_id).first()
