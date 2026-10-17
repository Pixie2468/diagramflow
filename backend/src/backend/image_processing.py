"""In-memory validation and contrast preparation for whiteboard photos."""

from io import BytesIO

from fastapi import HTTPException, status
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def prepare_image(data: bytes, declared_mime_type: str | None) -> tuple[bytes, str]:
    """Validate an uploaded image and return a contrast-enhanced PNG payload."""
    if declared_mime_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Use a PNG, JPEG, or WebP image.")
    if not data:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "The uploaded image is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image exceeds the 10 MB limit.")
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            prepared = ImageOps.autocontrast(ImageOps.grayscale(image.convert("RGB")))
            output = BytesIO()
            prepared.save(output, format="PNG", optimize=True)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "The upload is not a valid image.") from exc
    return output.getvalue(), "image/png"
