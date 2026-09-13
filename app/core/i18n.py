import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import Request

SUPPORTED = ("ar", "en")
DEFAULT = "ar"
RTL_LANGS = {"ar"}

_cache: dict[str, dict[str, str]] = {}

_LOCALES_DIR = Path(__file__).resolve().parent / "locales"


def _load(lang: str) -> dict[str, str]:
    if lang not in SUPPORTED:
        lang = DEFAULT
    if lang in _cache:
        return _cache[lang]
    path = _LOCALES_DIR / f"{lang}.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    _cache[lang] = data
    return _cache[lang]


def detect_lang(request: Request) -> str:
    path_parts = request.url.path.strip("/").split("/", 1)
    if path_parts and path_parts[0] in SUPPORTED:
        return path_parts[0]
    cookie_lang = request.cookies.get("lang")
    if cookie_lang in SUPPORTED:
        return cookie_lang
    accept = request.headers.get("accept-language", "")
    for part in accept.split(","):
        code = part.strip().split("-")[0].lower()
        if code in SUPPORTED:
            return code
    return DEFAULT


def make_translator(lang: str) -> Callable[..., str]:
    data = _load(lang)

    def t(key: str, **kwargs: Any) -> str:
        val = data.get(key, key)
        if kwargs:
            try:
                val = val.format(**kwargs)
            except (KeyError, IndexError):
                pass
        return val

    return t


def dir_for(lang: str) -> str:
    return "rtl" if lang in RTL_LANGS else "ltr"


# file: app/core/i18n.py
