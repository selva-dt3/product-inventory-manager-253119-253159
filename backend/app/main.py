import logging
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api.routes import router as api_router
from .errors import AppError

settings = get_settings()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("product-inventory-backend")

openapi_tags = [
    {"name": "Products", "description": "Product CRUD operations and image management"},
]

app = FastAPI(
    title="Product Inventory Manager - Backend",
    description="FastAPI backend exposing product CRUD and image upload/delete integrated with Supabase.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)


# CORS configuration
origins: List[str] = settings.cors_origin_list
allow_all = origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Handle known AppError types and return structured error responses."""
    return exc.to_response()


# Mount API routes
app.include_router(api_router)


# PUBLIC_INTERFACE
@app.get(
    "/",
    summary="API root",
    description="Shows basic info and health status for the service.",
)
def root():
    """
    Root endpoint providing basic service info for easy discovery.
    """
    return {
        "service": "Product Inventory Manager - Backend",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }
