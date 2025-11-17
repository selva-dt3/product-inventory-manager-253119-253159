//
// Simple API client for Product Inventory Manager
//
// PUBLIC_INTERFACE
export class ApiError extends Error {
  /** Represents an HTTP/API error with status and optional response body. */
  constructor(message, status, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

/**
 * Get API base URL from environment.
 * Uses REACT_APP_API_BASE; defaults to same-origin if not set.
 */
export function getApiBase() {
  const base = process.env.REACT_APP_API_BASE || "";
  // Remove trailing slash for consistency
  return base.endsWith("/") ? base.slice(0, -1) : base;
}

// PUBLIC_INTERFACE
export async function apiFetch(path, options = {}) {
  /** Wrapper around fetch with JSON handling and error normalization. */
  const url = `${getApiBase()}${path}`;
  const headers = Object.assign(
    { Accept: "application/json" },
    options.headers || {}
  );

  const opts = { ...options, headers };
  const res = await fetch(url, opts);

  const contentType = res.headers.get("content-type") || "";
  let body = null;
  if (contentType.includes("application/json")) {
    try {
      body = await res.json();
    } catch {
      body = null;
    }
  } else {
    // attempt to read text for debugging
    try {
      body = await res.text();
    } catch {
      body = null;
    }
  }

  if (!res.ok) {
    const msg =
      (body && body.error && body.error.message) ||
      (typeof body === "string" ? body : "Request failed");
    throw new ApiError(msg, res.status, body);
  }

  return body;
}

// PUBLIC_INTERFACE
export const ProductsAPI = {
  /** List products with optional search, pagination */
  async list({ q, limit = 100, offset = 0 } = {}) {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (limit != null) params.set("limit", String(limit));
    if (offset != null) params.set("offset", String(offset));
    const qs = params.toString();
    return apiFetch(`/products${qs ? `?${qs}` : ""}`, { method: "GET" });
  },

  /** Get a single product by id */
  async get(id) {
    return apiFetch(`/products/${encodeURIComponent(id)}`, { method: "GET" });
  },

  /** Create a product */
  async create(payload) {
    return apiFetch(`/products`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  /** Update a product */
  async update(id, payload) {
    return apiFetch(`/products/${encodeURIComponent(id)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  /** Delete a product */
  async remove(id) {
    return apiFetch(`/products/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
  },

  /** Upload or replace an image for a product */
  async uploadImage(id, file) {
    const form = new FormData();
    form.append("file", file);
    return apiFetch(`/products/${encodeURIComponent(id)}/image`, {
      method: "POST",
      body: form,
    });
  },

  /** Delete product image */
  async deleteImage(id) {
    return apiFetch(`/products/${encodeURIComponent(id)}/image`, {
      method: "DELETE",
    });
  },
};
