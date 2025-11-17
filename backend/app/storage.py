import imghdr
import mimetypes
import uuid
from typing import Optional, Tuple

from supabase import Client
from fastapi import UploadFile, HTTPException, status

from .config import get_settings
from .db import get_supabase_client

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # ~5MB


def _validate_image(file: UploadFile, content: bytes) -> str:
    """
    Validate uploaded image content and return canonical mime type.
    """
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds 5MB limit",
        )

    # First trust declared content-type when reasonable
    declared = (file.content_type or "").lower()

    # Determine magic type using imghdr
    detected = imghdr.what(None, h=content)
    detected_mime = {
        "jpeg": "image/jpeg",
        "png": "image/png",
    }.get(detected or "", "")

    mime = detected_mime or declared
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG/PNG images are supported",
        )
    return mime


def _object_path(filename_ext: str) -> str:
    """
    Build storage object path under 'products/' prefix.
    """
    return f"products/{uuid.uuid4().hex}{filename_ext}"


def _ext_for_mime(mime: str) -> str:
    if mime == "image/png":
        return ".png"
    return ".jpg"


def upload_product_image(
    file: UploadFile, sb: Optional[Client] = None
) -> Tuple[str, str]:
    """
    Upload an image to Supabase Storage products bucket.

    Returns:
        (public_or_signed_url, object_path)
    """
    settings = get_settings()
    client = sb or get_supabase_client()
    content = file.file.read()
    mime = _validate_image(file, content)
    ext = _ext_for_mime(mime)
    object_path = _object_path(ext)

    # Upload to Storage
    bucket = client.storage.from_(settings.SUPABASE_PRODUCTS_BUCKET)
    # If object exists by chance, use upsert True
    bucket.upload(path=object_path, file=content, file_options={"content-type": mime, "upsert": True})

    # Try to get public URL; if bucket is private, generate signed URL
    public_info = bucket.get_public_url(object_path)
    public_url = None
    if isinstance(public_info, dict) and "publicURL" in public_info:
        public_url = public_info["publicURL"]
    elif hasattr(public_info, "get") and public_info.get("publicURL"):
        public_url = public_info.get("publicURL")

    if public_url:
        return public_url, object_path

    # Private bucket, sign URL
    signed = bucket.create_signed_url(object_path, expires_in=get_settings().URL_SIGN_EXPIRY_SECONDS)
    if isinstance(signed, dict) and "signedURL" in signed:
        return signed["signedURL"], object_path
    if hasattr(signed, "get") and signed.get("signedURL"):
        return signed.get("signedURL"), object_path

    # Fallback to path (unlikely)
    return object_path, object_path


def delete_product_image(object_path: str, sb: Optional[Client] = None) -> None:
    """
    Delete an object from products bucket. Ignores if not found.
    """
    settings = get_settings()
    client = sb or get_supabase_client()
    bucket = client.storage.from_(settings.SUPABASE_PRODUCTS_BUCKET)
    bucket.remove([object_path])
