import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, AnyHttpUrl, Field, validator


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Required env vars:
    - SUPABASE_URL
    - SUPABASE_SERVICE_ROLE_KEY
    - SUPABASE_PRODUCTS_BUCKET

    Optional:
    - SUPABASE_ANON_KEY
    - BACKEND_PORT (default 8000)
    - LOG_LEVEL (default "INFO")
    - CORS_ORIGINS (comma separated)
    - URL_SIGN_EXPIRY_SECONDS (default 3600)
    """

    SUPABASE_URL: AnyHttpUrl = Field(..., description="Supabase project URL")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase service role key (server-only)")
    SUPABASE_ANON_KEY: Optional[str] = Field(None, description="Supabase anon key (optional)")

    SUPABASE_PRODUCTS_BUCKET: str = Field(..., description="Supabase Storage bucket id/name for products")

    BACKEND_PORT: int = Field(8000, description="Port on which the FastAPI app runs")
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    URL_SIGN_EXPIRY_SECONDS: int = Field(
        3600, description="Expiry time in seconds for generated signed URLs when bucket is private"
    )
    CORS_ORIGINS: str = Field(
        "*",
        description="Comma-separated list of allowed CORS origins. Use '*' to allow all (dev only).",
    )

    @property
    def cors_origin_list(self) -> List[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        # split and strip
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance loaded from environment variables."""
    return Settings()
