import os

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


ALLOWED_PHOTO_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}

ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def validate_photo_upload(uploaded_file):
    """Allow only common raster photo uploads that Pillow can read."""
    if not uploaded_file:
        return

    content_type = getattr(uploaded_file, "content_type", "")
    if content_type not in ALLOWED_PHOTO_CONTENT_TYPES:
        raise ValidationError("Upload a JPEG, PNG, GIF, or WebP photo.")

    extension = os.path.splitext(uploaded_file.name or "")[1].lower()
    if extension not in ALLOWED_PHOTO_EXTENSIONS:
        raise ValidationError("Upload a JPEG, PNG, GIF, or WebP photo.")

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError("The uploaded file is not a valid photo.")
    finally:
        uploaded_file.seek(0)
