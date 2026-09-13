from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.buyer_requests.models import BuyerRequest, RequestIntent, RequestSource
from app.modules.buyer_requests.schemas import BuyerRequestCreate


def create_specs_request(db: Session, data: BuyerRequestCreate) -> BuyerRequest:
    request = BuyerRequest(
        session_id=data.session_id,
        source=RequestSource.specs,
        property_type=data.property_type,
        city=data.city,
        district=data.district,
        budget_min=data.budget_min,
        budget_max=data.budget_max,
        area=data.area,
        purpose=data.purpose,
        features=data.features,
        notes=data.notes,
        phone=data.phone,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def create_image_request(
    db: Session,
    session_id: str | None,
    phone: str | None,
    notes: str | None,
) -> BuyerRequest:
    request = BuyerRequest(
        session_id=session_id,
        source=RequestSource.image,
        phone=phone,
        notes=notes,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get_request(db: Session, request_id: int) -> BuyerRequest | None:
    return db.get(BuyerRequest, request_id)


def update_intent(db: Session, request_id: int, intent: str) -> BuyerRequest | None:
    request = db.get(BuyerRequest, request_id)
    if request is None:
        return None
    request.intent = RequestIntent(intent)
    db.commit()
    db.refresh(request)
    return request


# file: app/modules/buyer_requests/service.py
