import React, { useEffect, useMemo, useState } from 'react';
import './App.css';
import { useProducts, useProductActions } from './hooks/useProducts';
import ProductList from './components/ProductList';
import ProductForm from './components/ProductForm';

// PUBLIC_INTERFACE
function App() {
  /** Root UI for Product Inventory Manager */
  const [theme, setTheme] = useState('light');
  const { items, q, setQ, loading, error, refresh } = useProducts();
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const actions = useProductActions({
    onUpdated: () => {
      refresh();
    }
  });

  // PUBLIC_INTERFACE
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const startCreate = () => {
    setEditing(null);
    setShowForm(true);
  };

  const startEdit = (p) => {
    setEditing(p);
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
  };

  const handleSave = async (payload) => {
    if (editing && editing.id) {
      await actions.update(editing.id, payload);
    } else {
      await actions.create(payload);
    }
    setShowForm(false);
  };

  const handleDelete = async (p) => {
    if (!window.confirm(`Delete "${p.name}"?`)) return;
    await actions.remove(p.id);
  };

  const uploadImage = editing?.id
    ? async (file) => actions.uploadImage(editing.id, file)
    : null;

  const deleteImage = editing?.id
    ? async () => actions.deleteImage(editing.id)
    : null;

  return (
    <div className="App">
      <header className="App-header" style={{ padding: 16, minHeight: 'auto', alignItems: 'stretch' }}>
        <div className="navbar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span role="img" aria-label="box">📦</span>
            <h1 className="title" style={{ margin: 0 }}>Product Inventory Manager</h1>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <button 
              className="theme-toggle" 
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
            </button>
          </div>
        </div>
      </header>

      <main className="container" style={{ maxWidth: 1100, margin: '16px auto', padding: '0 16px' }}>
        <section className="actions" style={{ display: 'flex', gap: 12, alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input
              aria-label="Search products"
              placeholder="Search by name..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              style={{
                padding: '10px 12px',
                borderRadius: 8,
                border: '1px solid var(--border-color)',
                background: 'var(--bg-secondary)',
                color: 'var(--text-primary)',
              }}
            />
            <button className="btn btn-secondary" onClick={refresh} disabled={loading}>
              Refresh
            </button>
          </div>
          <button className="btn" onClick={startCreate}>+ Add Product</button>
        </section>

        {error && (
          <div role="alert" className="card" style={{ borderColor: '#dc3545', marginBottom: 16 }}>
            <div className="card-body" style={{ color: '#dc3545' }}>
              Error: {error.message || 'Request failed'}
            </div>
          </div>
        )}

        {showForm && (
          <section style={{ marginBottom: 24 }}>
            <ProductForm
              initial={editing}
              onCancel={cancelForm}
              onSave={handleSave}
              onUploadImage={uploadImage}
              onDeleteImage={deleteImage}
              busy={actions.busy}
            />
          </section>
        )}

        <section>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <ProductList items={items} onEdit={startEdit} onDelete={handleDelete} />
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
