from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import render
from app.core.database import get_db
from app.core.i18n import SUPPORTED
from app.modules.properties.service import list_properties

router = APIRouter()


@router.get("/{lang}/api/properties")
async def api_properties(
    request: Request,
    lang: str,
    db: Session = Depends(get_db),
):
    if lang not in SUPPORTED:
        lang = "ar"
    props = list_properties(db)
    return {"properties": [p.id for p in props]}


# file: app/modules/properties/routes.py
