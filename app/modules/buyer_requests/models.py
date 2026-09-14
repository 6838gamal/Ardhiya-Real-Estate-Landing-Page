import enum
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RequestSource(enum.Enum):
    specs = "specs"
    image = "image"


class RequestIntent(enum.Enum):
    search_for_me = "search_for_me"
    browse_myself = "browse_myself"


class BuyerRequest(Base):
    __tablename__ = "buyer_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[Optional[str]] = mapped_column(
        String(64), index=True, nullable=True
    )
    source: Mapped[RequestSource] = mapped_column(
        Enum(RequestSource), nullable=False
    )
    intent: Mapped[Optional[RequestIntent]] = mapped_column(
        Enum(RequestIntent), nullable=True
    )
    property_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    budget_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    purpose: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    features: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    images: Mapped[List["RequestImage"]] = relationship(
        "RequestImage",
        back_populates="request",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<BuyerRequest id={self.id} source={self.source}>"


class RequestImage(Base):
    __tablename__ = "request_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("buyer_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    image_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    request: Mapped["BuyerRequest"] = relationship(
        "BuyerRequest",
        back_populates="images",
    )

    def __repr__(self) -> str:
        return f"<RequestImage id={self.id} request_id={self.request_id}>"
