"""
نقطة دخول التطبيق — Ardhiya Real Estate.

- i18n middleware
- تسجيل الـ routers
- تطبيق migrations تلقائياً عند بدء التطبيق (lifespan)
"""

import logging
from contextlib import asynccontextmanager
from datetime import timedelta

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# ⭐ 1. استيراد موحّد لكل الموديلات — قبل أي router
from app.db import base  # noqa: F401

# 2. الإعدادات والأدوات
from app.core.config import settings
from app.core.i18n import (
    DEFAULT,
    SUPPORTED,
    detect_lang,
    dir_for,
    make_translator,
)

# 3. الـ Routers
from app.modules.buyer_requests.routes import router as buyer_router
from app.modules.landing.routes import router as landing_router
from app.modules.properties.routes import router as properties_router


logger = logging.getLogger(__name__)


# ===============================================================
# تطبيق migrations عند بدء التطبيق
# ===============================================================
def run_migrations() -> None:
    """
    يطبّق migrations Alembic (upgrade head).
    آمن للاستخدام مع WEB_CONCURRENCY=1 (Render الافتراضي).
    """
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Alembic migrations applied successfully")
    except Exception as exc:
        logger.error("❌ Failed to apply migrations: %s", exc, exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """يُشغّل migrations عند بدء التطبيق."""
    logger.info("🚀 Starting application...")
    run_migrations()
    logger.info("✅ Application startup complete")
    yield
    logger.info("👋 Application shutdown")


# ===============================================================
# إنشاء التطبيق
# ===============================================================
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


# ===============================================================
# Middleware — i18n
# ===============================================================
@app.middleware("http")
async def i18n_middleware(request: Request, call_next):
    lang = detect_lang(request)
    request.state.lang = lang
    request.state.dir = dir_for(lang)
    request.state.t = make_translator(lang)

    response = await call_next(request)

    if "lang" not in request.cookies or request.cookies.get("lang") != lang:
        response.set_cookie(
            key="lang",
            value=lang,
            max_age=int(timedelta(days=365).total_seconds()),
            samesite="lax",
            httponly=True,
        )

    return response


# ===============================================================
# Root — إعادة توجيه إلى اللغة الافتراضية
# ===============================================================
@app.get("/")
async def root(request: Request):
    lang = getattr(request.state, "lang", DEFAULT)
    if lang not in SUPPORTED:
        lang = DEFAULT
    return RedirectResponse(url=f"/{lang}", status_code=302)


# ===============================================================
# تسجيل الـ Routers
# ===============================================================
app.include_router(landing_router)
app.include_router(buyer_router)
app.include_router(properties_router)
