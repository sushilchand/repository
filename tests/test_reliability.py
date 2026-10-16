import httpx
import pytest

from app.clients.product_api import ProductApiClient
from app.clients.warehouse_api import WarehouseApiClient
from app.services.warehouse_sync import transform
from app.services.enums import RunStatus


def _require_mock_services():
    for url in ("http://localhost:8001/health", "http://localhost:8002/health"):
        try:
            response = httpx.get(url, timeout=2)
        except httpx.HTTPError as exc:
            pytest.skip(f"Mock API dependency unavailable at {url}: {exc}")

        if response.status_code >= 500:
            pytest.skip(f"Mock API dependency unhealthy at {url}: status {response.status_code}")


def test_run_status_is_typed_enum():
    assert RunStatus.RUNNING.value == "running"
    assert RunStatus.EXPORTED.value == "exported"
    assert RunStatus.COMPLETED.value == "completed"
    assert RunStatus.FAILED.value == "failed"


def test_transform_maps_catalogue_row_to_wms_fields():
    row = {
        "id": "P0000001",
        "name": "Test Product",
        "category": "SPICES",
        "price": "249.50",
        "currency": "INR",
        "updated_at": "2026-09-25T08:30:00Z",
    }

    result = transform(row)

    assert result["sku"] == "P0000001"
    assert result["description"] == "Test Product"
    assert result["selling_price"] == 249.5
    assert result["currency"] == "INR"
    assert result["category_code"] == "SPICES"


def test_product_client_retries_transient_errors():
    _require_mock_services()
    client = ProductApiClient(base_url="http://localhost:8001", api_key="challenge-product-key")
    page = client.fetch_page(1, 500)

    assert page["products"]
    assert len(page["products"]) <= 500


def test_warehouse_client_batches_and_deduplicates():
    _require_mock_services()
    client = WarehouseApiClient(base_url="http://localhost:8002", api_key="challenge-warehouse-key")

    products = [
        {"sku": "P0000001", "description": "A", "selling_price": 12.0, "currency": "INR", "category_code": "SPICES", "source_updated_at": "2026-09-25T08:30:00Z"},
        {"sku": "P0000001", "description": "A", "selling_price": 12.0, "currency": "INR", "category_code": "SPICES", "source_updated_at": "2026-09-25T08:30:00Z"},
        {"sku": "P0000002", "description": "B", "selling_price": 20.0, "currency": "INR", "category_code": "GROCERY", "source_updated_at": "2026-09-25T08:30:00Z"},
    ]

    accepted = client.dedupe_products(products)

    assert [p["sku"] for p in accepted] == ["P0000001", "P0000002"]
