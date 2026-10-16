import csv
from datetime import datetime, timezone
from pathlib import Path

from app.clients.product_api import ProductApiClient
from app.config import EXPORT_DIR
from app.storage.s3 import S3Store


def export_catalogue(run_id: str | None = None, export_dir: str | Path | None = None, client: ProductApiClient | None = None) -> str:
    client = client or ProductApiClient()
    export_root = Path(export_dir) if export_dir is not None else EXPORT_DIR
    export_root.mkdir(parents=True, exist_ok=True)

    run_identifier = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    export_path = export_root / f"{run_identifier}.csv"
    products = client.fetch_all_products()

    with export_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "name", "category", "price", "currency", "updated_at"])
        writer.writeheader()
        writer.writerows(products)

    store = S3Store(root=export_root.parent / "s3")
    store.put_file(export_path, f"catalogue-exports/{export_path.name}")
    return str(export_path)
