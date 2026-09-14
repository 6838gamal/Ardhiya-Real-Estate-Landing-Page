"""
نقطة الاستيراد الموحّدة لكل موديلات SQLAlchemy.

يجب استيراد هذا الملف مرة واحدة على الأقل عند بدء التطبيق
(في app/main.py) وفي Alembic (alembic/env.py)، حتى تُسجَّل
جميع الموديلات في الـ registry وتُحل العلاقات النصية بنجاح.

الترتيب غير مهم من ناحية العلاقات النصية، لكن نستورد كل
ملف على حدة للوضوح.
"""

from app.core.database import Base  # noqa: F401

# ---------------------------------------------------------------
# Properties
# ---------------------------------------------------------------
from app.modules.properties.models import Property  # noqa: F401

# ---------------------------------------------------------------
# Media
# ---------------------------------------------------------------
from app.modules.media.models import PropertyImage  # noqa: F401

# ---------------------------------------------------------------
# Buyer Requests
# ---------------------------------------------------------------
from app.modules.buyer_requests.models import (  # noqa: F401
    BuyerRequest,
    RequestImage,
)


__all__ = [
    "Base",
    "Property",
    "PropertyImage",
    "BuyerRequest",
    "RequestImage",
]
