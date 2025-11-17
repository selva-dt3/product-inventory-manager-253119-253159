# End-to-End Setup and Integration Guide

## Overview

This guide walks you through setting up Supabase (database and storage), configuring backend and frontend environment variables, running the backend (FastAPI) and frontend (React) locally, and verifying CRUD operations and image uploads. It also documents storage bucket privacy options and how image URLs are returned to the client.

This document references and complements:
- docs/supabase/schema.sql
- docs/supabase/storage_setup.md
- backend/README.md
- FastAPIBackend/INTEGRATION.md

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A Supabase project (URL and keys from the Supabase Dashboard)
- Git and terminal access

## 1) Supabase Setup

### 1.1 Create database schema

Use the SQL editor in your Supabase project to run the schema file:

- File: docs/supabase/schema.sql
- This creates the products table, indexes, and a trigger to auto-update updated_at on updates.

Steps:
1. Open Supabase Dashboard → SQL Editor
2. Copy-paste the contents of docs/supabase/schema.sql
3. Run the query

Expected outcome:
- A table public.products with fields: id, name, sku, description, price, quantity, image_url, image_path, created_at, updated_at
- Indexes for lower(name) and unique SKU
- Trigger to maintain updated_at

### 1.2 Create Storage bucket and policies

A storage bucket is used for product images.

Option A: Public bucket (simple development setup)
- Follow docs/supabase/storage_setup.md, Section “Create the 'products' bucket”
- Name: products
- Public: enabled (checked)
- Add policies for anon select (read) and service role full access as described

Option B: Private bucket (recommended for production)
- Follow docs/supabase/storage_setup.md, Section “Switching to a Private Bucket”
- Make the bucket private
- Keep service role access for writes via backend
- The backend will return signed URLs to the frontend using URL_SIGN_EXPIRY_SECONDS

Note on object path convention:
- Images are stored under the products/ prefix, for example products/<uuid>.png
- The backend persists storage object path to image_path and the fetchable URL (publicURL or signedURL) to image_url

## 2) Environment Variables

The application is split into:
- Backend at product-inventory-manager-253119-253159/backend (FastAPI)
- Frontend at product-inventory-manager-253119-253159/FastAPIBackend (React)

Create a .env file at the project repository root and ensure these variables are available to the backend process. For the frontend, create a .env in the FastAPIBackend folder. Keep secrets out of source control.

### 2.1 Backend .env (project root)

These are loaded by backend/app/config.py.

Required:
- SUPABASE_URL=https://<your-project-ref>.supabase.co
- SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>  # server-only
- SUPABASE_PRODUCTS_BUCKET=products                  # or your chosen bucket name

Optional:
- SUPABASE_ANON_KEY=<your-anon-key>                  # not used by server calls, but allowed
- BACKEND_PORT=8000
- LOG_LEVEL=INFO
- CORS_ORIGINS=http://localhost:3000                 # comma separated, or * for development
- URL_SIGN_EXPIRY_SECONDS=3600                       # used when bucket is private

Example .env (backend):

```
SUPABASE_URL=https://xyzcompanyproject.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_PRODUCTS_BUCKET=products

BACKEND_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
URL_SIGN_EXPIRY_SECONDS=3600
```

Important:
- Never expose SUPABASE_SERVICE_ROLE_KEY in the frontend or in logs. This key must remain server-side only.

### 2.2 Frontend .env (FastAPIBackend/.env)

The frontend uses REACT_APP_API_BASE to determine the base URL for API calls (see FastAPIBackend/src/api/client.js and FastAPIBackend/INTEGRATION.md).

Required:
- REACT_APP_API_BASE=http://localhost:8000

You may choose to configure any additional REACT_APP_* variables, but only REACT_APP_API_BASE is read by this app’s code. Any other variables listed in deployment environments (e.g., REACT_APP_BACKEND_URL, REACT_APP_FRONTEND_URL, etc.) are not consumed by the provided code.

Example .env (frontend):

```
REACT_APP_API_BASE=http://localhost:8000
```

## 3) Running Locally

### 3.1 Backend

From product-inventory-manager-253119-253159/backend:

1) Install dependencies:
```
pip install -r requirements.txt
```

2) Start FastAPI (uvicorn):
```
uvicorn app.main:app --reload --port ${BACKEND_PORT:-8000}
```

3) Verify it’s running:
- Open Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health should return {"status":"ok"}

CORS:
- Ensure CORS_ORIGINS includes http://localhost:3000 for the React app.

### 3.2 Frontend

From product-inventory-manager-253119-253159/FastAPIBackend:

1) Create FastAPIBackend/.env with:
```
REACT_APP_API_BASE=http://localhost:8000
```

2) Install and start:
```
npm install
npm start
```

3) Open the app:
- http://localhost:3000

## 4) Verifying CRUD and Image Uploads

Follow these steps in the React UI:

1) Load product list
- The home page loads products via GET /products.
- If the list is empty, you should see “No products found.”

2) Create a product
- Click “+ Add Product”
- Fill out Name, SKU, Price, Quantity (Description optional)
- Click “Create Product”
- The item should appear in the list (POST /products).

3) Update a product
- Click “Edit” on a product
- Change a field and click “Save Changes”
- The list should refresh showing updates (PUT /products/{id}).

4) Delete a product
- Click “Delete” and confirm
- The item should be removed from the list (DELETE /products/{id}).

5) Upload a product image
- Click “Edit” on a product
- In the form’s “Product Image” section, choose a PNG or JPEG (<= 5MB)
- The preview should show the uploaded image (POST /products/{id}/image)
- The backend validates type and size and uploads to Supabase Storage

6) Remove a product image
- From the same form, click “Remove Image”
- The preview placeholder should show again (DELETE /products/{id}/image)

Notes:
- The frontend fetches image_url directly for previews. If you use a private bucket, the backend returns a signed URL with an expiry time.
- The backend persists both image_url (public/signed URL) and image_path (storage object path).

## 5) Bucket Privacy Options and URL Behavior

Public bucket:
- The backend attempts to resolve a publicURL for the uploaded object.
- image_url is set to that public URL.
- The frontend can directly display the image without additional auth.

Private bucket:
- publicURL will not be available.
- The backend generates a signed URL via create_signed_url(expires_in=URL_SIGN_EXPIRY_SECONDS).
- image_url is set to the signed URL; the frontend displays that URL for the lifetime of the signature.
- Consider cache/refresh strategies if you plan to rotate or short expiry times.

Security considerations:
- The backend always uses SUPABASE_SERVICE_ROLE_KEY when performing storage and database writes.
- Do not embed service role keys in the frontend.
- For production, prefer private buckets with signed URLs and strictly define storage policies.

## 6) Troubleshooting

- CORS errors: Ensure backend CORS_ORIGINS includes http://localhost:3000 (or * for development).
- 401/403 from Supabase operations: Double-check SUPABASE_SERVICE_ROLE_KEY and bucket policies.
- Image upload fails:
  - Ensure file type is PNG or JPEG and size <= 5MB.
  - Verify SUPABASE_PRODUCTS_BUCKET is correct and exists.
- Frontend cannot reach API:
  - Confirm REACT_APP_API_BASE is set and correct. The code trims trailing slashes.
  - Verify backend is reachable at http://localhost:8000 and /health returns ok.

## 7) Reference: Files and Sources

- Database schema: docs/supabase/schema.sql
- Storage setup: docs/supabase/storage_setup.md
- Backend configuration and env variables: backend/app/config.py, backend/README.md
- Frontend API configuration: FastAPIBackend/src/api/client.js
- Integration overview: FastAPIBackend/INTEGRATION.md

## 8) Appendix: .env Examples

Backend (.env at repository root):
```
SUPABASE_URL=https://xyzcompanyproject.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_PRODUCTS_BUCKET=products

BACKEND_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
URL_SIGN_EXPIRY_SECONDS=3600
```

Frontend (FastAPIBackend/.env):
```
REACT_APP_API_BASE=http://localhost:8000
```

These examples reflect actual variables used by the codebase:
- Backend reads all SUPABASE_* variables, CORS_ORIGINS, LOG_LEVEL, BACKEND_PORT, URL_SIGN_EXPIRY_SECONDS (see backend/app/config.py)
- Frontend reads REACT_APP_API_BASE (see FastAPIBackend/src/api/client.js)
