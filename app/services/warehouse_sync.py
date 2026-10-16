import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.clients.warehouse_api import WarehouseApiClient
from app.storage.s3 import S3Store


def transform(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sku": row["id"],
        "description": row["name"],
        "selling_price": float(row["price"]),
        "currency": row["currency"],
        "category_code": row["category"],
        "source_updated_at": row["updated_at"],
    }


def sync_catalogue(export_path: str | Path, warehouse_client: WarehouseApiClient | None = None, run_id: str | None = None):
    warehouse_client = warehouse_client or WarehouseApiClient()
    source_path = Path(export_path)

    with source_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    transformed_products = [transform(row) for row in rows]
    unique_products = warehouse_client.dedupe_products(transformed_products)
    result = warehouse_client.send_products(unique_products)

    payload = {
        "run_id": run_id,
        "export_path": str(source_path),
        "row_count": len(rows),
        "unique_product_count": len(unique_products),
        "accepted_count": len(result["accepted"]),
        "rejected_count": len(result["rejected"]),
        "accepted": result["accepted"],
        "rejected": result["rejected"],
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    if run_id:
        state_store = S3Store(root=source_path.parent.parent / "s3")
        state_store.write_json(f"runs/{run_id}.json", payload)

    return payload
