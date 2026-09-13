from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.properties.models import Property


def list_properties(db: Session, limit: int = 20) -> list[Property]:
    stmt = select(Property).order_by(Property.created_at.desc()).limit(limit)
    return list(db.execute(stmt).scalars().all())


# file: app/modules/properties/service.py
