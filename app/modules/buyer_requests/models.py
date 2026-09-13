import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RequestSource(enum.Enum):
    specs = "specs"
    image = "image"


class RequestIntent(enum.Enum):
    search_for_me = "search_for_me"
    browse_myself = "browse_myself"


class BuyerRequest(Base):
    __tablename__ = "buyer_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    source: Mapped[RequestSource] = mapped_column(Enum(RequestSource), nullable=False)
    intent: Mapped[RequestIntent | None] = mapped_column(Enum(RequestIntent), nullable=True)
    property_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area: Mapped[int | None] = mapped_column(Integer, nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(50), nullable=True)
    features: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    images: Mapped[list["RequestImage"]] = relationship(
        "RequestImage", back_populates="request", cascade="all, delete-orphan"
    )


class RequestImage(Base):
    __tablename__ = "request_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("buyer_requests.id", ondelete="CASCADE"), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    image_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    request: Mapped["BuyerRequest"] = relationship("BuyerRequest", back_populates="images")


# file: app/modules/buyer_requests/models.py
