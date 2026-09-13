from fastapi import APIRouter, Request

from app.core.config import render
from app.core.i18n import SUPPORTED

router = APIRouter()


@router.get("/{lang}")
async def landing_page(request: Request, lang: str):
    if lang not in SUPPORTED:
        lang = "ar"
    return render(request, "landing/index.html")


@router.get("/{lang}/properties")
async def properties_page(request: Request, lang: str):
    if lang not in SUPPORTED:
        lang = "ar"
    return render(request, "landing/index.html", {"show_soon": True})


# file: app/modules/landing/routes.py
