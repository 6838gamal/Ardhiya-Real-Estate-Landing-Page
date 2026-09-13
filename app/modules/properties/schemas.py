from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PropertyOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    property_type: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    price: Optional[int] = None
    area: Optional[int] = None
    purpose: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# file: app/modules/properties/schemas.py
