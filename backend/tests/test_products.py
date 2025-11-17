from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@patch("app.api.routes.db.products_list")
def test_list_products(mock_list):
    mock_list.return_value = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Test",
            "sku": "SKU-1",
            "description": "Desc",
            "price": "9.99",
            "quantity": 5,
            "image_url": None,
            "image_path": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    ]
    resp = client.get("/products")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) and len(data) == 1
    assert data[0]["sku"] == "SKU-1"


@patch("app.api.routes.db.products_get")
@patch("app.api.routes.db.products_create")
def test_create_and_get_product(mock_create, mock_get):
    product = {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "New Product",
        "sku": "NEW-1",
        "description": None,
        "price": "19.99",
        "quantity": 3,
        "image_url": None,
        "image_path": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    mock_create.return_value = product
    resp = client.post(
        "/products",
        json={"name": "New Product", "sku": "NEW-1", "description": None, "price": 19.99, "quantity": 3},
    )
    assert resp.status_code == 201
    assert resp.json()["sku"] == "NEW-1"

    mock_get.return_value = product
    resp = client.get("/products/22222222-2222-2222-2222-222222222222")
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Product"


@patch("app.api.routes.db.products_get")
@patch("app.api.routes.db.products_update")
def test_update_product(mock_update, mock_get):
    existing = {
        "id": "33333333-3333-3333-3333-333333333333",
        "name": "Existing",
        "sku": "EX-1",
        "description": None,
        "price": "10.00",
        "quantity": 1,
        "image_url": None,
        "image_path": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    updated = {**existing, "name": "Updated"}
    mock_get.return_value = existing
    mock_update.return_value = updated

    resp = client.put("/products/33333333-3333-3333-3333-333333333333", json={"name": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


@patch("app.api.routes.db.products_get")
@patch("app.api.routes.db.products_delete")
def test_delete_product(mock_delete, mock_get):
    mock_get.return_value = {
        "id": "44444444-4444-4444-4444-444444444444",
        "name": "ToDelete",
        "sku": "DEL-1",
        "description": None,
        "price": "10.00",
        "quantity": 1,
        "image_url": None,
        "image_path": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    mock_delete.return_value = True

    resp = client.delete("/products/44444444-4444-4444-4444-444444444444")
    # 204 has no body; TestClient converts to 200 sometimes if body present
    assert resp.status_code in (200, 204)


@patch("app.api.routes.db.products_get")
@patch("app.api.routes.delete_product_image")
@patch("app.api.routes.upload_product_image")
@patch("app.api.routes.db.products_update")
def test_upload_image(mock_update, mock_upload, mock_delete_img, mock_get):
    product = {
        "id": "55555555-5555-5555-5555-555555555555",
        "name": "HasImage",
        "sku": "IMG-1",
        "description": None,
        "price": "10.00",
        "quantity": 1,
        "image_url": None,
        "image_path": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    mock_get.return_value = product
    mock_upload.return_value = ("https://example.com/img.png", "products/abc.png")
    mock_update.return_value = {**product, "image_url": "https://example.com/img.png", "image_path": "products/abc.png"}

    files = {"file": ("test.png", b"\x89PNG\r\n\x1a\n" + b"0" * 100, "image/png")}
    resp = client.post("/products/55555555-5555-5555-5555-555555555555/image", files=files)
    assert resp.status_code == 200
    assert resp.json()["image_url"] == "https://example.com/img.png"


@patch("app.api.routes.db.products_get")
@patch("app.api.routes.delete_product_image")
@patch("app.api.routes.db.products_update")
def test_delete_image(mock_update, mock_delete_img, mock_get):
    product = {
        "id": "66666666-6666-6666-6666-666666666666",
        "name": "HasImage",
        "sku": "IMG-2",
        "description": None,
        "price": "10.00",
        "quantity": 1,
        "image_url": "https://example.com/img.png",
        "image_path": "products/abc.png",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    mock_get.return_value = product
    mock_update.return_value = {**product, "image_url": None, "image_path": None}

    resp = client.delete("/products/66666666-6666-6666-6666-666666666666/image")
    assert resp.status_code == 200
    assert resp.json()["image_url"] is None
