from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, constr, condecimal, validator


class ProductBase(BaseModel):
    """Common attributes for Product create/update"""

    name: constr(strip_whitespace=True, min_length=1, max_length=255) = Field(..., description="Name of the product")
    sku: constr(strip_whitespace=True, min_length=1, max_length=255) = Field(..., description="Unique SKU")
    description: Optional[str] = Field(None, description="Optional product description")
    price: condecimal(max_digits=10, decimal_places=2) = Field(..., description="Product price")
    quantity: int = Field(..., ge=0, description="Quantity in stock (>= 0)")

    @validator("sku")
    def normalize_sku(cls, v: str) -> str:
        # Enforce simple normalization: trim; could extend to uppercase etc.
        return v.strip()


class ProductCreate(ProductBase):
    """Payload for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Payload for updating an existing product."""
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    sku: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    description: Optional[str] = None
    price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    quantity: Optional[int] = Field(None, ge=0)

    @validator("sku")
    def normalize_sku(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v is not None else v


class Product(ProductBase):
    """Product model returned by API."""
    id: str = Field(..., description="UUID of the product")
    image_url: Optional[str] = Field(None, description="Public or signed URL of the product image")
    image_path: Optional[str] = Field(None, description="Storage object path for server-side operations")
    created_at: datetime
    updated_at: datetime


class ProductList(BaseModel):
    """Paginated list of products."""
    items: List[Product]
    total: int
