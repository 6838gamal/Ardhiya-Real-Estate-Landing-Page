from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings, render
from app.core.database import get_db
from app.core.i18n import SUPPORTED
from app.modules.buyer_requests.schemas import BuyerRequestCreate
from app.modules.buyer_requests.service import (
    create_image_request,
    create_specs_request,
    get_request,
    update_intent,
)
from app.modules.media.service import create_request_image
from app.modules.media.upload import save_upload

router = APIRouter()


@router.post("/{lang}/requests/specs")
async def submit_specs(
    request: Request,
    lang: str,
    db: Session = Depends(get_db),
    session_id: str | None = Form(None),
    property_type: str | None = Form(None),
    city: str | None = Form(None),
    district: str | None = Form(None),
    budget_min: int | None = Form(None),
    budget_max: int | None = Form(None),
    area: int | None = Form(None),
    purpose: str | None = Form(None),
    features: str | None = Form(None),
    notes: str | None = Form(None),
    phone: str | None = Form(None),
):
    if lang not in SUPPORTED:
        lang = "ar"
    data = BuyerRequestCreate(
        session_id=session_id,
        property_type=property_type,
        city=city,
        district=district,
        budget_min=budget_min,
        budget_max=budget_max,
        area=area,
        purpose=purpose,
        features=features,
        notes=notes,
        phone=phone,
    )
    new_request = create_specs_request(db, data)
    return render(
        request,
        "buyer_requests/next.html",
        {"req": new_request},
    )


@router.post("/{lang}/requests/image")
async def submit_image(
    request: Request,
    lang: str,
    db: Session = Depends(get_db),
    session_id: str | None = Form(None),
    phone: str | None = Form(None),
    notes: str | None = Form(None),
    file: UploadFile = File(...),
):
    if lang not in SUPPORTED:
        lang = "ar"
    new_request = create_image_request(db, session_id, phone, notes)
    storage_path = await save_upload(file, new_request.id)
    create_request_image(db, new_request.id, storage_path, file.content_type)
    return render(
        request,
        "buyer_requests/next.html",
        {"req": new_request},
    )


@router.get("/{lang}/requests/{request_id}/next")
async def next_page(
    request: Request,
    lang: str,
    request_id: int,
    db: Session = Depends(get_db),
):
    if lang not in SUPPORTED:
        lang = "ar"
    req = get_request(db, request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return render(request, "buyer_requests/next.html", {"req": req})


@router.post("/{lang}/requests/{request_id}/intent")
async def set_intent(
    request: Request,
    lang: str,
    request_id: int,
    intent: str = Form(...),
    db: Session = Depends(get_db),
):
    if lang not in SUPPORTED:
        lang = "ar"
    valid_intents = {"search_for_me", "browse_myself"}
    if intent not in valid_intents:
        raise HTTPException(status_code=400, detail="Invalid intent")
    req = update_intent(db, request_id, intent)
    if req is None:
        raise HTTPException(status_code=404, detail="Request not found")
    if intent == "browse_myself":
        return render(request, "landing/index.html", {"show_soon": True})
    return render(request, "buyer_requests/next.html", {"req": req, "done": True})


# file: app/modules/buyer_requests/routes.py
