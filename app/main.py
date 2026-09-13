from datetime import timedelta

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.i18n import DEFAULT, SUPPORTED, detect_lang, dir_for, make_translator
from app.modules.buyer_requests.routes import router as buyer_router
from app.modules.landing.routes import router as landing_router
from app.modules.properties.routes import router as properties_router

app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


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


@app.get("/")
async def root(request: Request):
    lang = getattr(request.state, "lang", DEFAULT)
    if lang not in SUPPORTED:
        lang = DEFAULT
    return RedirectResponse(url=f"/{lang}", status_code=302)


app.include_router(landing_router)
app.include_router(buyer_router)
app.include_router(properties_router)

# file: app/main.py
