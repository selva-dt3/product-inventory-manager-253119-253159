import React from "react";

// PUBLIC_INTERFACE
export default function ProductList({ items, onEdit, onDelete }) {
  /** Renders a responsive table of products with actions. */
  if (!items || items.length === 0) {
    return <p style={{ opacity: 0.8 }}>No products found.</p>;
  }

  return (
    <div className="table-wrap" role="region" aria-label="Products">
      <table className="table">
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>Name</th>
            <th>SKU</th>
            <th>Price</th>
            <th>Qty</th>
            <th>Image</th>
            <th aria-label="actions" />
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.id}>
              <td style={{ textAlign: "left" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  {p.image_url ? (
                    <img
                      src={p.image_url}
                      alt={`${p.name}`}
                      style={{ width: 36, height: 36, objectFit: "cover", borderRadius: 4, border: "1px solid var(--border-color)" }}
                    />
                  ) : (
                    <div
                      aria-hidden
                      style={{
                        width: 36,
                        height: 36,
                        display: "inline-block",
                        background: "var(--bg-secondary)",
                        border: "1px dashed var(--border-color)",
                        borderRadius: 4,
                      }}
                    />
                  )}
                  <div>
                    <div style={{ fontWeight: 600 }}>{p.name}</div>
                    <div style={{ fontSize: 12, opacity: 0.7 }}>{p.description || "-"}</div>
                  </div>
                </div>
              </td>
              <td>{p.sku}</td>
              <td>${Number(p.price).toFixed(2)}</td>
              <td>{p.quantity}</td>
              <td>{p.image_url ? "Yes" : "No"}</td>
              <td>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                  <button className="btn" onClick={() => onEdit(p)} aria-label={`Edit ${p.name}`}>
                    Edit
                  </button>
                  <button className="btn btn-danger" onClick={() => onDelete(p)} aria-label={`Delete ${p.name}`}>
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
