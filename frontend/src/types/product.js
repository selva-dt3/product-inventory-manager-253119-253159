/**
 * Product type helpers and validation
 */

export const emptyProduct = () => ({
  name: "",
  sku: "",
  description: "",
  price: "",
  quantity: "",
});

/**
 * Validate a product payload for create/update.
 * Returns an object { field: 'error message' } for invalid fields.
 */
// PUBLIC_INTERFACE
export function validateProduct(input, { allowPartial = false } = {}) {
  /** Validate fields according to backend constraints. */
  const errors = {};

  const hasValue = (v) => v !== undefined && v !== null && String(v).trim() !== "";

  const fields = ["name", "sku", "price", "quantity"];
  for (const f of fields) {
    if (!allowPartial || hasValue(input[f])) {
      if (!hasValue(input[f])) {
        errors[f] = "Required";
      }
    }
  }

  if (hasValue(input.name) && String(input.name).length > 255) {
    errors.name = "Name must be <= 255 characters";
  }

  if (hasValue(input.sku) && String(input.sku).length > 255) {
    errors.sku = "SKU must be <= 255 characters";
  }

  if (hasValue(input.price)) {
    const price = Number(input.price);
    if (Number.isNaN(price) || price < 0) {
      errors.price = "Price must be a non-negative number";
    } else {
      // up to 2 decimals
      const str = String(input.price);
      const parts = str.split(".");
      if (parts[1] && parts[1].length > 2) {
        errors.price = "Price can have up to 2 decimal places";
      }
    }
  }

  if (hasValue(input.quantity)) {
    const qty = Number(input.quantity);
    if (!Number.isInteger(qty) || qty < 0) {
      errors.quantity = "Quantity must be an integer >= 0";
    }
  }

  return errors;
}
