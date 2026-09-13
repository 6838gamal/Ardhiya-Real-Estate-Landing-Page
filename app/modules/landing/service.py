from fastapi import Request

from app.core.config import render


def render_landing(request: Request):
    return render(request, "landing/index.html")


def render_properties(request: Request):
    return render(request, "landing/index.html", {"show_soon": True})


# file: app/modules/landing/service.py
