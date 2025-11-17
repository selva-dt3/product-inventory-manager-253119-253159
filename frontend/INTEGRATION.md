# Frontend-Backend Integration

This React app consumes the FastAPI backend using the environment variable REACT_APP_API_BASE.

- Set the API base URL in `.env` (see `.env.example`):
  REACT_APP_API_BASE=http://localhost:8000

- The app uses the following backend endpoints:
  - GET /products
  - POST /products
  - GET /products/{id}
  - PUT /products/{id}
  - DELETE /products/{id}
  - POST /products/{id}/image
  - DELETE /products/{id}/image

- Start locally:
  1) Backend: uvicorn app.main:app --reload --port 8000
  2) Frontend (this folder): npm install && npm start

Notes:
- For image upload, the form accepts PNG/JPEG up to 5MB.
- CORS must allow http://localhost:3000 (configure backend env CORS_ORIGINS).
