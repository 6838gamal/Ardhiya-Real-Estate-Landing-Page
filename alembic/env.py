"""
Alembic env.py — متوافق مع PostgreSQL (Supabase) و SQLite.

- يستخدم settings.DATABASE_URL ديناميكياً
- لا يستخدم render_as_batch (إلا لـ SQLite)
- يستورد كل الموديلات عبر app.db.base
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.database import Base

# ⭐ استيراد موحّد لكل الموديلات — يضمن تسجيلها في registry
from app.db import base  # noqa: F401


# ===============================================================
# Alembic Config
# ===============================================================
config = context.config

# logging
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception as exc:
        print(f"⚠️  fileConfig failed: {exc}")

# ضبط DATABASE_URL من الإعدادات
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# metadata
target_metadata = Base.metadata


# ===============================================================
# Helpers
# ===============================================================
def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def include_object(object, name, type_, reflected, compare_to):
    """تجاهل جداول النظام."""
    if type_ == "table" and name in {"alembic_version"}:
        return False
    return True


# ===============================================================
# Offline mode
# ===============================================================
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        render_as_batch=_is_sqlite(url),  # ⭐ فقط لـ SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


# ===============================================================
# Online mode
# ===============================================================
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # طباعة للتشخيص
        print(f"🔗 Alembic connecting to: {connection.engine.url.dialect}")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
            render_as_batch=_is_sqlite(str(connection.engine.url)),  # ⭐ فقط لـ SQLite
        )
        with context.begin_transaction():
            context.run_migrations()


# ===============================================================
# Entry point
# ===============================================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
