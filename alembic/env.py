"""
Alembic env.py — متوافق مع PostgreSQL (Supabase) و SQLite.

- يستخدم settings.DATABASE_URL ديناميكياً
- render_as_batch فقط لـ SQLite
- يستورد كل الموديلات عبر app.db.base
- طباعة تشخيصية كاملة لسجل Render
"""

import sys
import traceback
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.database import Base

# ⭐ استيراد موحّد لكل الموديلات — يضمن تسجيلها في registry
from app.db import base  # noqa: F401


# ===============================================================
# مساعد للطباعة الفورية في سجل Render
# ===============================================================
def log(msg: str) -> None:
    """طباعة فورية إلى stderr — تظهر دائماً في سجل Render."""
    print(f"🔧 [ALEMBIC] {msg}", file=sys.stderr, flush=True)


# ===============================================================
# Alembic Config
# ===============================================================
log("=" * 60)
log("START env.py")
log("=" * 60)

config = context.config

log(f"config_file_name = {config.config_file_name}")

# logging من alembic.ini
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
        log("✅ fileConfig loaded successfully")
    except Exception as exc:
        log(f"⚠️  fileConfig failed: {exc}")
        traceback.print_exc(file=sys.stderr)

# ⭐ ضبط DATABASE_URL من الإعدادات
try:
    db_url = settings.DATABASE_URL
    log(f"📌 DATABASE_URL = {db_url[:70]}...")
    log(f"📌 Dialect = {db_url.split('://')[0]}")
    config.set_main_option("sqlalchemy.url", db_url)
    log("✅ set_main_option('sqlalchemy.url') OK")
except Exception as exc:
    log(f"❌ Failed to read DATABASE_URL: {exc}")
    traceback.print_exc(file=sys.stderr)
    raise

# metadata
target_metadata = Base.metadata
log(f"📌 Tables in metadata: {list(target_metadata.tables.keys())}")


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
    log("MODE: offline")
    url = config.get_main_option("sqlalchemy.url")
    log(f"📌 Using URL: {url[:70]}...")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        render_as_batch=_is_sqlite(url),
    )

    log("✅ Context configured (offline)")

    with context.begin_transaction():
        log("✅ Transaction begun (offline)")
        context.run_migrations()
        log("✅ Migrations completed (offline)")


# ===============================================================
# Online mode
# ===============================================================
def run_migrations_online() -> None:
    log("MODE: online")

    # -----------------------------------------------------------
    # 1. بناء الـ engine
    # -----------------------------------------------------------
    try:
        section = config.get_section(config.config_ini_section, {})
        log(f"📌 Config section keys: {list(section.keys())}")

        connectable = engine_from_config(
            section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        log("✅ Engine created")
    except Exception as exc:
        log(f"❌ Failed to create engine: {exc}")
        traceback.print_exc(file=sys.stderr)
        raise

    # -----------------------------------------------------------
    # 2. الاتصال
    # -----------------------------------------------------------
    try:
        with connectable.connect() as connection:
            dialect = connection.engine.url.dialect
            log(f"✅ Connected to database (dialect={dialect})")

            # ---------------------------------------------------
            # 3. تكوين الـ context
            # ---------------------------------------------------
            try:
                context.configure(
                    connection=connection,
                    target_metadata=target_metadata,
                    compare_type=True,
                    compare_server_default=True,
                    include_object=include_object,
                    render_as_batch=_is_sqlite(str(connection.engine.url)),
                )
                log("✅ Context configured")
            except Exception as exc:
                log(f"❌ Failed to configure context: {exc}")
                traceback.print_exc(file=sys.stderr)
                raise

            # ---------------------------------------------------
            # 4. تشغيل migrations
            # ---------------------------------------------------
            try:
                with context.begin_transaction():
                    log("✅ Transaction begun")
                    log("🔄 Running migrations...")
                    context.run_migrations()
                    log("✅ Migrations completed successfully")
            except Exception as exc:
                log(f"❌ Migration failed: {exc}")
                traceback.print_exc(file=sys.stderr)
                raise

    except Exception as exc:
        log(f"❌ Connection or migration error: {exc}")
        traceback.print_exc(file=sys.stderr)
        raise


# ===============================================================
# Entry point
# ===============================================================
try:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
    log("=" * 60)
    log("END env.py — SUCCESS")
    log("=" * 60)
except Exception as exc:
    log("=" * 60)
    log(f"END env.py — FAILED: {exc}")
    log("=" * 60)
    raise
