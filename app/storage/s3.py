import json
import shutil
import time
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from app.config import RUNTIME_DIR, S3_RETENTION_DAYS


class S3Store:
    """Local stand-in for the S3 boundary used by the current implementation."""

    def __init__(self, root: Optional[str] = None):
        self.root = Path(root) if root is not None else RUNTIME_DIR / "s3"
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        return self.root / key

    def put_file(self, source: str | Path, key: str) -> str:
        source_path = Path(source)
        destination = self._resolve(key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        return str(destination)

    def get_file(self, key: str) -> Path:
        return self._resolve(key)

    def write_json(self, key: str, payload: Any) -> str:
        destination = self._resolve(key)
        destination.parent.mkdir(parents=True, exist_ok=True)

        def json_default(value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            return str(value)

        destination.write_text(json.dumps(payload, indent=2, default=json_default), encoding="utf-8")
        return str(destination)

    def read_json(self, key: str) -> Any:
        return json.loads(self._resolve(key).read_text(encoding="utf-8"))

    def list_keys(self, prefix: str = "") -> list[str]:
        base = self.root / prefix if prefix else self.root
        if not base.exists():
            return []
        return [str(path.relative_to(self.root)).replace("\\", "/") for path in sorted(base.rglob("*")) if path.is_file()]

    def prune_expired(self, days: int = S3_RETENTION_DAYS) -> list[str]:
        cutoff = time.time() - (days * 86400)
        deleted: list[str] = []

        for path in self.root.rglob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                deleted.append(str(path.relative_to(self.root)).replace("\\", "/"))
                path.unlink()

        return deleted
