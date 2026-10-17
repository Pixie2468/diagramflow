"""In-memory validation and contrast preparation for whiteboard photos."""

from io import BytesIO

from fastapi import HTTPException, status
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


def prepare_image(data: bytes, _declared_mime_type: str | None) -> tuple[bytes, str]:
    """Validate an uploaded image and return a contrast-enhanced PNG payload.

    The decoded format is authoritative: multipart clients do not always have a
    complete MIME database and can label a valid WebP as application/octet-stream.
    """
    if not data:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "The uploaded image is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image exceeds the 10 MB limit.")
    try:
        with Image.open(BytesIO(data)) as image:
            image_format = image.format
            image.verify()
        with Image.open(BytesIO(data)) as image:
            if image_format not in ALLOWED_IMAGE_FORMATS:
                raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Use a PNG, JPEG, or WebP image.")
            prepared = ImageOps.autocontrast(ImageOps.grayscale(image.convert("RGB")))
            output = BytesIO()
            prepared.save(output, format="PNG", optimize=True)
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "The upload is not a valid image.") from exc
    return output.getvalue(), "image/png"
