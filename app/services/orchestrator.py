from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.config import RUN_DIR
from app.services.catalogue_export import export_catalogue
from app.services.enums import RunStatus
from app.services.warehouse_sync import sync_catalogue
from app.storage.s3 import S3Store


def run_catalogue_sync() -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = Path(RUN_DIR) / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    state_store = S3Store(root=run_root)

    manifest = {
        "run_id": run_id,
        "status": RunStatus.RUNNING,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "export_path": None,
    }
    state_store.write_json("manifest.json", manifest)

    try:
        export_path = export_catalogue(run_id=run_id, export_dir=run_root.parent.parent / "exports")
        manifest["status"] = RunStatus.EXPORTED
        manifest["export_path"] = export_path
        state_store.write_json("manifest.json", manifest)

        result = sync_catalogue(export_path, run_id=run_id)
        manifest["status"] = RunStatus.COMPLETED
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        manifest["summary"] = {
            "row_count": result["row_count"],
            "unique_product_count": result["unique_product_count"],
            "accepted_count": result["accepted_count"],
            "rejected_count": result["rejected_count"],
        }
        state_store.write_json("manifest.json", manifest)

        return {
            "run_id": run_id,
            "status": RunStatus.COMPLETED.value,
            "export_path": export_path,
            "summary": manifest["summary"],
        }
    except Exception as exc:  # pragma: no cover - runtime recovery path
        manifest["status"] = RunStatus.FAILED
        manifest["failed_at"] = datetime.now(timezone.utc).isoformat()
        manifest["error"] = str(exc)
        state_store.write_json("manifest.json", manifest)
        raise RuntimeError(f"Catalogue sync run {run_id} failed: {exc}") from exc
