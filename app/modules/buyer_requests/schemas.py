from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BuyerRequestCreate(BaseModel):
    session_id: Optional[str] = None
    property_type: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    area: Optional[int] = None
    purpose: Optional[str] = None
    features: Optional[str] = None
    notes: Optional[str] = None
    phone: Optional[str] = None


class BuyerRequestImageCreate(BaseModel):
    session_id: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class IntentUpdate(BaseModel):
    intent: str


class BuyerRequestOut(BaseModel):
    id: int
    session_id: Optional[str] = None
    source: str
    intent: Optional[str] = None
    property_type: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    area: Optional[int] = None
    purpose: Optional[str] = None
    features: Optional[str] = None
    notes: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# file: app/modules/buyer_requests/schemas.py
