from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile, status
from pydantic import BaseModel, Field

from .. import db
from ..models import Product, ProductCreate, ProductUpdate
from ..storage import upload_product_image, delete_product_image

router = APIRouter(tags=["Products"], prefix="")


# PUBLIC_INTERFACE
@router.get("/health", summary="Health check", description="Simple health endpoint to verify the API is running.")
def health() -> Dict[str, str]:
    """Return API health status."""
    return {"status": "ok"}


# PUBLIC_INTERFACE
@router.get(
    "/products",
    summary="List products",
    description="List products with optional search and pagination.",
    response_model=List[Product],
)
def list_products(
    q: Optional[str] = Query(None, description="Optional search string to match product names (case-insensitive)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> List[Product]:
    """List products."""
    items = db.products_list(search=q, limit=limit, offset=offset)
    return [Product(**it) for it in items]


# PUBLIC_INTERFACE
@router.get(
    "/products/{product_id}",
    summary="Get product",
    description="Retrieve a product by its ID.",
    response_model=Product,
    responses={404: {"description": "Product not found"}},
)
def get_product(
    product_id: str = Path(..., description="UUID of the product"),
) -> Product:
    """Get single product by id."""
    item = db.products_get(product_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return Product(**item)


# PUBLIC_INTERFACE
@router.post(
    "/products",
    summary="Create product",
    description="Create a new product.",
    status_code=status.HTTP_201_CREATED,
    response_model=Product,
)
def create_product(payload: ProductCreate) -> Product:
    """Create product."""
    created = db.products_create(payload.dict())
    return Product(**created)


# PUBLIC_INTERFACE
@router.put(
    "/products/{product_id}",
    summary="Update product",
    description="Update an existing product by its ID.",
    response_model=Product,
    responses={404: {"description": "Product not found"}},
)
def update_product(
    product_id: str = Path(..., description="UUID of the product"),
    payload: ProductUpdate = None,
) -> Product:
    """Update product."""
    # Ensure exists
    existing = db.products_get(product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    updated = db.products_update(product_id, update_data)
    return Product(**updated)


# PUBLIC_INTERFACE
@router.delete(
    "/products/{product_id}",
    summary="Delete product",
    description="Delete a product by its ID. Also deletes associated image if present.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Product not found"}},
)
def delete_product(
    product_id: str = Path(..., description="UUID of the product"),
):
    """Delete product and associated image if any."""
    existing = db.products_get(product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Best-effort delete image if exists
    image_path = existing.get("image_path")
    if image_path:
        try:
            delete_product_image(image_path)
        except Exception:
            # ignore failures
            pass

    ok = db.products_delete(product_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"status": "deleted"}


# PUBLIC_INTERFACE
@router.post(
    "/products/{product_id}/image",
    summary="Upload product image",
    description="Upload an image for the specified product. JPEG and PNG up to 5MB are allowed.",
    response_model=Product,
    responses={
        404: {"description": "Product not found"},
        413: {"description": "Image too large"},
        415: {"description": "Unsupported media type"},
    },
)
def upload_image(
    product_id: str = Path(..., description="UUID of the product"),
    file: UploadFile = File(..., description="Image file (jpeg/png, max 5MB)"),
) -> Product:
    """Upload or replace a product image and update image_url and image_path."""
    existing = db.products_get(product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Upload to storage
    url, object_path = upload_product_image(file)

    # If there was a previous image, best-effort delete it
    old_path = existing.get("image_path")
    if old_path and old_path != object_path:
        try:
            delete_product_image(old_path)
        except Exception:
            pass

    updated = db.products_update(product_id, {"image_url": url, "image_path": object_path})
    return Product(**updated)


# PUBLIC_INTERFACE
@router.delete(
    "/products/{product_id}/image",
    summary="Delete product image",
    description="Delete the image associated with the specified product.",
    response_model=Product,
    responses={404: {"description": "Product not found"}},
)
def delete_image(
    product_id: str = Path(..., description="UUID of the product"),
) -> Product:
    """Delete product image and clear image_url/image_path."""
    existing = db.products_get(product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    image_path = existing.get("image_path")
    if image_path:
        try:
            delete_product_image(image_path)
        except Exception:
            pass

    updated = db.products_update(product_id, {"image_url": None, "image_path": None})
    return Product(**updated)
