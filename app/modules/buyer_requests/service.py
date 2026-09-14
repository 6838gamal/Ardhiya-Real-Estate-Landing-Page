"""
خدمة طلبات المشترين — متوافقة مع routes.py.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.buyer_requests.models import (
    BuyerRequest,
    RequestIntent,
    RequestSource,
)
from app.modules.buyer_requests.schemas import BuyerRequestCreate

logger = logging.getLogger(__name__)


# ===============================================================
# إنشاء طلب من مواصفات (يستقبل BuyerRequestCreate)
# ===============================================================
def create_specs_request(
    db: Session,
    data: BuyerRequestCreate,
) -> BuyerRequest:
    """
    ينشئ طلب شراء من مواصفات.
    يستقبل كائن Pydantic BuyerRequestCreate.
    """
    payload = data.model_dump(exclude_none=True)

    # إزالة session_id لأننا نمرره صراحة
    session_id = payload.pop("session_id", None) or ""

    request = BuyerRequest(
        session_id=session_id,
        source=RequestSource.specs,
        **payload,
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    logger.info("✅ طلب مواصفات أُنشئ: id=%s", request.id)
    return request


# ===============================================================
# إنشاء طلب من صورة
# ===============================================================
def create_image_request(
    db: Session,
    session_id: Optional[str],
    phone: Optional[str],
    notes: Optional[str],
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
# ⭐ تحديث النية — الدالة المفقودة
# ===============================================================
def update_intent(
    db: Session,
    request_id: int,
    intent: str | RequestIntent,
) -> Optional[BuyerRequest]:
    """
    يحدّث نية الطلب.
    يعيد None إذا لم يكن الطلب موجوداً (routes.py يعتمد على ذلك).
    """
    request = db.query(BuyerRequest).filter(BuyerRequest.id == request_id).first()
    if request is None:
        return None

    if isinstance(intent, str):
        try:
            intent = RequestIntent(intent)
        except ValueError:
            logger.warning("قيمة نية غير صالحة: %s", intent)
            return None

    request.intent = intent
    db.commit()
    db.refresh(request)

    logger.info("✅ تم تحديث نية الطلب %s إلى %s", request_id, intent.value)
    return request


# ===============================================================
# جلب طلب
# ===============================================================
def get_request(db: Session, request_id: int) -> Optional[BuyerRequest]:
    """يعيد طلباً بواسطة ID."""
    return db.query(BuyerRequest).filter(BuyerRequest.id == request_id).first()
