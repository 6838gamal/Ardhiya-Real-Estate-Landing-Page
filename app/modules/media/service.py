from sqlalchemy.orm import Session

from app.modules.buyer_requests.models import RequestImage


def create_request_image(
    db: Session,
    request_id: int,
    storage_path: str,
    image_type: str | None = None,
) -> RequestImage:
    image = RequestImage(
        request_id=request_id,
        storage_path=storage_path,
        image_type=image_type,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


# file: app/modules/media/service.py
