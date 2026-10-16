import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", str(BASE_DIR / "runtime")))
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", str(RUNTIME_DIR / "exports")))
RUN_DIR = Path(os.getenv("RUN_DIR", str(RUNTIME_DIR / "runs")))
STATE_DIR = Path(os.getenv("STATE_DIR", str(RUNTIME_DIR / "state")))

PRODUCT_API_URL = os.getenv("PRODUCT_API_URL", "http://localhost:8001")
WAREHOUSE_API_URL = os.getenv("WAREHOUSE_API_URL", "http://localhost:8002")
PRODUCT_API_KEY = os.getenv("PRODUCT_API_KEY", "challenge-product-key")
WAREHOUSE_API_KEY = os.getenv("WAREHOUSE_API_KEY", "challenge-warehouse-key")

PAGE_SIZE = int(os.getenv("PAGE_SIZE", "500"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
BACKOFF_SECONDS = float(os.getenv("BACKOFF_SECONDS", "1.0"))
S3_RETENTION_DAYS = int(os.getenv("S3_RETENTION_DAYS", "90"))

for directory in (RUNTIME_DIR, EXPORT_DIR, RUN_DIR, STATE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
