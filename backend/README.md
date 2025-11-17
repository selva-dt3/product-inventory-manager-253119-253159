# Product Inventory Manager - FastAPI Backend

FastAPI backend that exposes REST endpoints for managing products and uploading/deleting images using Supabase (Postgres + Storage).

## Features

- Products CRUD (create, read, update, delete)
- Upload/Delete product images to/from Supabase Storage
- Image validation (PNG/JPEG, max 5 MB)
- CORS configurable via env
- OpenAPI docs at `/docs` and `/openapi.json`
- Unit tests with FastAPI TestClient and mock Supabase calls

## Structure

```
backend/
  app/
    api/
      routes.py
    __init__.py (implicit)
    config.py
    db.py
    errors.py
    main.py
    models.py
    storage.py
  requirements.txt
  README.md
  tests/
    test_products.py
```

## Environment variables

These are read from the environment (configure via project `.env`):

- SUPABASE_URL (required)
- SUPABASE_SERVICE_ROLE_KEY (required)
- SUPABASE_ANON_KEY (optional)
- SUPABASE_PRODUCTS_BUCKET (required; e.g., `products`)
- CORS_ORIGINS (comma-separated list or `*` for development)
- BACKEND_PORT (default `8000`)
- LOG_LEVEL (default `INFO`)
- URL_SIGN_EXPIRY_SECONDS (default `3600`)

## Running locally

1. Create and populate `.env` at repository root with the required variables.

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Start the server:

```
uvicorn app.main:app --reload --port ${BACKEND_PORT:-8000}
```

4. Open:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## API Endpoints

- GET `/health`
- GET `/products`
- GET `/products/{id}`
- POST `/products`
- PUT `/products/{id}`
- DELETE `/products/{id}`
- POST `/products/{id}/image`
- DELETE `/products/{id}/image`

## Notes

- If the bucket is public, image URLs are returned as public URLs.
- If the bucket is private, a signed URL is generated using `URL_SIGN_EXPIRY_SECONDS`.
- The Supabase schema and storage setup are provided under `docs/supabase/` in the repository root.

## Testing

```
pytest
```
