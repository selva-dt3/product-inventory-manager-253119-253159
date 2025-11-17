from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from supabase import Client, create_client
from .config import get_settings


def get_supabase_client() -> Client:
    """
    Create a Supabase client using service role key for server-side operations.
    Cached per-process by supabase library's internal pooling.

    Note: Do not expose SERVICE_ROLE_KEY to clients.
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


# Database access helpers for products


def products_list(
    sb: Optional[Client] = None,
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List products with optional case-insensitive name search and pagination.
    """
    client = sb or get_supabase_client()
    query = client.table("products").select("*").order("created_at", desc=True)
    if search:
        # Use ilike for case-insensitive partial match on name
        query = query.ilike("name", f"%{search}%")
    if offset:
        query = query.range(offset, offset + limit - 1)
    else:
        query = query.limit(limit)
    res = query.execute()
    return res.data or []


def products_get(product_id: str, sb: Optional[Client] = None) -> Optional[Dict[str, Any]]:
    """
    Get a product by id.
    """
    client = sb or get_supabase_client()
    res = client.table("products").select("*").eq("id", product_id).single().execute()
    return res.data if res.data else None


def products_create(
    payload: Dict[str, Any], sb: Optional[Client] = None
) -> Dict[str, Any]:
    """
    Create a product. Expects validated payload keys compatible with DB schema.
    """
    client = sb or get_supabase_client()
    res = client.table("products").insert(payload).select("*").single().execute()
    return res.data


def products_update(
    product_id: str, payload: Dict[str, Any], sb: Optional[Client] = None
) -> Optional[Dict[str, Any]]:
    """
    Update an existing product by id, returning the updated record.
    """
    client = sb or get_supabase_client()
    res = (
        client.table("products")
        .update(payload)
        .eq("id", product_id)
        .select("*")
        .single()
        .execute()
    )
    return res.data if res.data else None


def products_delete(product_id: str, sb: Optional[Client] = None) -> bool:
    """
    Delete a product by id. Returns True if a row was deleted.
    """
    client = sb or get_supabase_client()
    res = client.table("products").delete().eq("id", product_id).execute()
    # supabase returns list of deleted rows in data for delete (may be empty on no-op)
    return bool(res.data)
