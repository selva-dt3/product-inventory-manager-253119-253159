import React, { useEffect, useMemo, useRef, useState } from "react";
import { emptyProduct, validateProduct } from "../types/product";

// PUBLIC_INTERFACE
export default function ProductForm({
  initial,
  onCancel,
  onSave,
  onUploadImage,
  onDeleteImage,
  busy = false,
}) {
  /**
   * Form for creating or editing a product.
   * - onSave(payload) should return a promise
   * - onUploadImage(file) optional; returns updated product
   * - onDeleteImage() optional; returns updated product
   */
  const isEdit = Boolean(initial && initial.id);
  const [values, setValues] = useState(() =>
    isEdit
      ? {
          name: initial.name || "",
          sku: initial.sku || "",
          description: initial.description || "",
          price: String(initial.price ?? ""),
          quantity: String(initial.quantity ?? ""),
        }
      : emptyProduct()
  );
  const [errors, setErrors] = useState({});
  const [imgBusy, setImgBusy] = useState(false);
  const fileRef = useRef(null);

  useEffect(() => {
    if (isEdit) {
      setValues({
        name: initial.name || "",
        sku: initial.sku || "",
        description: initial.description || "",
        price: String(initial.price ?? ""),
        quantity: String(initial.quantity ?? ""),
      });
    } else {
      setValues(emptyProduct());
    }
  }, [isEdit, initial]);

  const title = isEdit ? "Edit Product" : "Add Product";

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues((v) => ({ ...v, [name]: value }));
  };

  const submit = async (e) => {
    e.preventDefault();
    const errs = validateProduct(values, { allowPartial: false });
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    const payload = {
      name: values.name.trim(),
      sku: values.sku.trim(),
      description: values.description || null,
      price: Number(values.price),
      quantity: Number(values.quantity),
    };

    await onSave(payload);
  };

  const uploadImage = async (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file || !onUploadImage) return;
    setImgBusy(true);
    try {
      await onUploadImage(file);
      if (fileRef.current) fileRef.current.value = "";
    } finally {
      setImgBusy(false);
    }
  };

  const removeImage = async () => {
    if (!onDeleteImage) return;
    setImgBusy(true);
    try {
      await onDeleteImage();
    } finally {
      setImgBusy(false);
    }
  };

  const hasImage = Boolean(initial && initial.image_url);

  return (
    <form className="card" onSubmit={submit} aria-label={title}>
      <div className="card-header">
        <h3 className="title" style={{ margin: 0 }}>{title}</h3>
      </div>

      <div className="card-body">
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="name">Name</label>
            <input id="name" name="name" value={values.name} onChange={handleChange} placeholder="Product name" />
            {errors.name && <div className="error">{errors.name}</div>}
          </div>

          <div className="form-field">
            <label htmlFor="sku">SKU</label>
            <input id="sku" name="sku" value={values.sku} onChange={handleChange} placeholder="Unique SKU" />
            {errors.sku && <div className="error">{errors.sku}</div>}
          </div>

          <div className="form-field">
            <label htmlFor="price">Price</label>
            <input id="price" name="price" type="number" step="0.01" value={values.price} onChange={handleChange} placeholder="0.00" />
            {errors.price && <div className="error">{errors.price}</div>}
          </div>

          <div className="form-field">
            <label htmlFor="quantity">Quantity</label>
            <input id="quantity" name="quantity" type="number" step="1" value={values.quantity} onChange={handleChange} placeholder="0" />
            {errors.quantity && <div className="error">{errors.quantity}</div>}
          </div>

          <div className="form-field form-col-span">
            <label htmlFor="description">Description</label>
            <textarea id="description" name="description" rows={3} value={values.description} onChange={handleChange} placeholder="Optional description" />
          </div>
        </div>

        {isEdit && (
          <div className="image-row">
            <div>
              <div className="label">Product Image</div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                {hasImage ? (
                  <img
                    src={initial.image_url}
                    alt={`${initial.name}`}
                    style={{ width: 96, height: 96, objectFit: "cover", borderRadius: 6, border: "1px solid var(--border-color)" }}
                  />
                ) : (
                  <div
                    aria-hidden
                    style={{
                      width: 96,
                      height: 96,
                      background: "var(--bg-secondary)",
                      border: "1px dashed var(--border-color)",
                      borderRadius: 6,
                    }}
                  />
                )}

                <input
                  ref={fileRef}
                  type="file"
                  accept="image/png,image/jpeg"
                  onChange={uploadImage}
                  disabled={imgBusy || busy}
                  aria-label="Upload product image"
                />
                {hasImage && (
                  <button
                    type="button"
                    className="btn btn-danger"
                    onClick={removeImage}
                    disabled={imgBusy || busy}
                    aria-label="Remove product image"
                  >
                    Remove Image
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card-footer" style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={busy}>
          Cancel
        </button>
        <button type="submit" className="btn" disabled={busy}>
          {isEdit ? "Save Changes" : "Create Product"}
        </button>
      </div>
    </form>
  );
}
