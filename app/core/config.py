"""
إعدادات التطبيق — Ardhiya Real Estate.

يدعم:
- PostgreSQL (Supabase) للإنتاج
- SQLite للتطوير المحلي
- Supabase Storage للصور والفيديوهات
- تخزين محلي كبديل
- i18n (عربي/إنجليزي)

⚠️ جميع القيم الحساسة تُقرأ من متغيرات البيئة:
- DATABASE_URL
- SUPABASE_URL
- SUPABASE_SECRET_KEY
- SUPABASE_PUBLIC_KEY
- SECRET_KEY
"""

from pathlib import Path
from typing import Any, Optional

from fastapi.templating import Jinja2Templates
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ===============================================================
# Settings
# ===============================================================
class Settings(BaseSettings):
    # -----------------------------------------------------------
    # التطبيق
    # -----------------------------------------------------------
    APP_NAME: str = "Ardhiya"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = False

    # -----------------------------------------------------------
    # قاعدة البيانات
    # -----------------------------------------------------------
    DATABASE_URL: str = "postgresql+psycopg://localhost:5432/ardhiya"

    DATABASE_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # -----------------------------------------------------------
    # Supabase — Storage (للصور والفيديوهات)
    # -----------------------------------------------------------
    # ⚠️ لا تضع قيمة صلبة هنا — يُقرأ من متغير البيئة SUPABASE_URL
    # في التطوير: اتركه فارغاً → local storage
    # في الإنتاج: اضبطه عبر Environment Variable
    # مثال: https://xxxx.supabase.co
    SUPABASE_URL: str = ""

    SUPABASE_PUBLIC_KEY: Optional[SecretStr] = None
    SUPABASE_SECRET_KEY: Optional[SecretStr] = None

    # نوع التخزين: supabase | local
    STORAGE_TYPE: str = "local"

    # Buckets
    SUPABASE_BUCKET_PROPERTIES: str = "property-images"
    SUPABASE_BUCKET_REQUESTS: str = "request-images"
    SUPABASE_BUCKET_VIDEOS: str = "property-videos"
    SUPABASE_BUCKET_THUMBNAILS: str = "thumbnails"
    SUPABASE_BUCKET_TEMP: str = "temp"

    # -----------------------------------------------------------
    # التخزين المحلي (للتطوير)
    # -----------------------------------------------------------
    UPLOAD_DIR: str = "app/static/uploads"

    # -----------------------------------------------------------
    # حدود الرفع
    # -----------------------------------------------------------
    MAX_IMAGE_MB: int = 10
    MAX_VIDEO_MB: int = 100
    MAX_UPLOAD_MB: int = 10  # للتوافق مع الكود القديم

    ALLOWED_IMAGE_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/bmp",
    ]

    ALLOWED_VIDEO_TYPES: list[str] = [
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/webm",
        "video/x-matroska",
    ]

    ALLOWED_IMAGE_EXTENSIONS: list[str] = [
        ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp",
    ]

    ALLOWED_VIDEO_EXTENSIONS: list[str] = [
        ".mp4", ".mov", ".avi", ".webm", ".mkv",
    ]

    # -----------------------------------------------------------
    # i18n
    # -----------------------------------------------------------
    DEFAULT_LANG: str = "ar"
    SUPPORTED_LANGS: list[str] = ["ar", "en"]

    # -----------------------------------------------------------
    # الأمان
    # -----------------------------------------------------------
    SECRET_KEY: SecretStr = SecretStr("change-me-in-production")
    ALLOWED_ORIGINS: list[str] = ["*"]

    # -----------------------------------------------------------
    # Pydantic Settings Config
    # -----------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===========================================================
    # Validators
    # ===========================================================
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_db_url(cls, v: Any) -> Any:
        """
        تطبيع DATABASE_URL:
        - postgres://        → postgresql+psycopg://
        - postgresql://      → postgresql+psycopg://
        - sqlite:///...      → يبقى كما هو
        """
        if not isinstance(v, str):
            return v
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    # ⭐ SUPABASE_URL — من متغير البيئة فقط
    @field_validator("SUPABASE_URL", mode="before")
    @classmethod
    def _normalize_supabase_url(cls, v: Any) -> str:
        """
        تطبيع SUPABASE_URL:
        - إزالة المسافات
        - إزالة الشرطة المائلة في النهاية
        - إرجاع "" إذا كان فارغاً
        """
        if v is None:
            return ""
        if not isinstance(v, str):
            return ""
        return v.strip().rstrip("/")

    @field_validator("SUPABASE_URL")
    @classmethod
    def _validate_supabase_url(cls, v: str) -> str:
        """التحقق من صيغة SUPABASE_URL."""
        if v == "":
            # فارغ مقبول في التطوير — سيُرفض في الإنتاج عبر _validate_on_startup
            return ""
        if not v.startswith("https://"):
            raise ValueError(
                f"SUPABASE_URL يجب أن يبدأ بـ https:// — وصل: {v}"
            )
        return v

    @field_validator("STORAGE_TYPE")
    @classmethod
    def _validate_storage_type(cls, v: str) -> str:
        allowed = {"supabase", "local"}
        v_lower = v.lower().strip()
        if v_lower not in allowed:
            raise ValueError(
                f"STORAGE_TYPE يجب أن يكون واحداً من: {allowed} — وصل: {v}"
            )
        return v_lower

    @field_validator("ENVIRONMENT")
    @classmethod
    def _validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        v_lower = v.lower().strip()
        if v_lower not in allowed:
            raise ValueError(f"ENVIRONMENT يجب أن يكون واحداً من: {allowed}")
        return v_lower

    # ===========================================================
    # Properties
    # ===========================================================
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def supabase_configured(self) -> bool:
        """هل Supabase Storage مضبوط بالكامل؟"""
        if not self.SUPABASE_URL or not self.SUPABASE_SECRET_KEY:
            return False

        url_ok = (
            self.SUPABASE_URL.startswith("https://")
            and "supabase.co" in self.SUPABASE_URL
        )

        key = self.SUPABASE_SECRET_KEY.get_secret_value()
        key_ok = bool(key and len(key) > 20)

        return url_ok and key_ok

    @property
    def use_supabase_storage(self) -> bool:
        """هل نستخدم Supabase Storage فعلاً؟"""
        return self.STORAGE_TYPE == "supabase" and self.supabase_configured

    @property
    def supabase_secret_key_value(self) -> Optional[str]:
        if self.SUPABASE_SECRET_KEY:
            return self.SUPABASE_SECRET_KEY.get_secret_value()
        return None

    @property
    def supabase_public_key_value(self) -> Optional[str]:
        if self.SUPABASE_PUBLIC_KEY:
            return self.SUPABASE_PUBLIC_KEY.get_secret_value()
        return None

    @property
    def max_image_bytes(self) -> int:
        return self.MAX_IMAGE_MB * 1024 * 1024

    @property
    def max_video_bytes(self) -> int:
        return self.MAX_VIDEO_MB * 1024 * 1024


# ===============================================================
# Singleton
# ===============================================================
settings = Settings()


# ===============================================================
# Templates
# ===============================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def render(
    request: Any,
    template_name: str,
    context: dict[str, Any] | None = None,
) -> Any:
    """Render a Jinja2 template with i18n context."""
    ctx = context or {}
    ctx.setdefault("request", request)
    ctx.setdefault("t", getattr(request.state, "t", lambda k: k))
    ctx.setdefault("lang", getattr(request.state, "lang", settings.DEFAULT_LANG))
    ctx.setdefault("dir", getattr(request.state, "dir", "rtl"))
    return templates.TemplateResponse(request, template_name, ctx)


# ===============================================================
# Validation on import
# ===============================================================
def _validate_on_startup() -> None:
    """تحقق من الإعدادات الحرجة عند بدء التطبيق."""
    import warnings as _w

    warnings_list: list[str] = []
    errors: list[str] = []

    # SECRET_KEY
    if settings.is_production:
        if settings.SECRET_KEY.get_secret_value() == "change-me-in-production":
            errors.append(
                "SECRET_KEY يجب تغييره في الإنتاج! "
                "اضبط متغير البيئة SECRET_KEY بقيمة عشوائية آمنة."
            )

    # DATABASE_URL
    if settings.is_production and "sqlite" in settings.DATABASE_URL:
        warnings_list.append(
            "⚠️  DATABASE_URL يستخدم SQLite في الإنتاج — "
            "هذا غير مستدام على Render. استخدم PostgreSQL (Supabase)."
        )

    # STORAGE_TYPE=supabase — تحقق مفصّل
    if settings.STORAGE_TYPE == "supabase":
        if not settings.SUPABASE_URL:
            errors.append(
                "STORAGE_TYPE=supabase لكن SUPABASE_URL غير مضبوط! "
                "اضبط متغير البيئة SUPABASE_URL=https://xxx.supabase.co"
            )
        if not settings.SUPABASE_SECRET_KEY:
            errors.append(
                "STORAGE_TYPE=supabase لكن SUPABASE_SECRET_KEY غير مضبوط! "
                "اضبط متغير البيئة SUPABASE_SECRET_KEY."
            )
        if settings.SUPABASE_URL and not settings.supabase_configured:
            errors.append(
                "STORAGE_TYPE=supabase لكن SUPABASE_URL أو SUPABASE_SECRET_KEY "
                "غير صالحين (تحقق من الصيغة)."
            )

    # STORAGE_TYPE=local في الإنتاج
    if settings.is_production and settings.STORAGE_TYPE == "local":
        warnings_list.append(
            "⚠️  STORAGE_TYPE=local في الإنتاج — "
            "الملفات ستُفقد عند إعادة النشر على Render. "
            "استخدم STORAGE_TYPE=supabase."
        )

    # اطبع التحذيرات
    for w in warnings_list:
        _w.warn(w, UserWarning)

    # ارفع الأخطاء في الإنتاج
    if errors:
        if settings.is_production:
            raise ValueError(" | ".join(errors))
        else:
            for e in errors:
                _w.warn(f"[DEV] {e}", UserWarning)


_validate_on_startup()
