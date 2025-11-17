import { useCallback, useEffect, useMemo, useState } from "react";
import { ProductsAPI } from "../api/client";

/**
 * Hook for managing products list with loading/error/search.
 */
// PUBLIC_INTERFACE
export function useProducts() {
  /** Provides list, loading, error, search, and refresh helpers. */
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchList = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ProductsAPI.list({ q });
      setItems(data || []);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [q]);

  useEffect(() => {
    fetchList();
  }, [fetchList]);

  const refresh = useCallback(() => {
    fetchList();
  }, [fetchList]);

  return { items, q, setQ, loading, error, refresh };
}

/**
 * Hook to create/update/delete product and refresh the list on success.
 */
// PUBLIC_INTERFACE
export function useProductActions({ onUpdated } = {}) {
  /** Provides create, update, remove, uploadImage, deleteImage with loading/error states. */
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const wrap = useCallback(
    (fn) => async (...args) => {
      setBusy(true);
      setError(null);
      try {
        const res = await fn(...args);
        if (onUpdated) onUpdated(res);
        return res;
      } catch (e) {
        setError(e);
        throw e;
      } finally {
        setBusy(false);
      }
    },
    [onUpdated]
  );

  return {
    busy,
    error,
    create: wrap(ProductsAPI.create),
    update: wrap(ProductsAPI.update),
    remove: wrap(ProductsAPI.remove),
    uploadImage: wrap(ProductsAPI.uploadImage),
    deleteImage: wrap(ProductsAPI.deleteImage),
  };
}
