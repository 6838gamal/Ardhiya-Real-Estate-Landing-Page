from pathlib import Path
from typing import Any

from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Ardhiya"
    DATABASE_URL: str = "sqlite:///./ardhiya.db"
    UPLOAD_DIR: str = "app/static/uploads"
    MAX_UPLOAD_MB: int = 5
    DEFAULT_LANG: str = "ar"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def render(request: Any, template_name: str, context: dict[str, Any] | None = None) -> Any:
    ctx = context or {}
    ctx.setdefault("request", request)
    ctx.setdefault("t", getattr(request.state, "t", lambda k: k))
    ctx.setdefault("lang", getattr(request.state, "lang", settings.DEFAULT_LANG))
    ctx.setdefault("dir", getattr(request.state, "dir", "rtl"))
    return templates.TemplateResponse(request, template_name, ctx)


# file: app/core/config.py
