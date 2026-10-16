import math
import time
from typing import Any

import httpx

from app.config import BACKOFF_SECONDS, BATCH_SIZE, MAX_RETRIES, WAREHOUSE_API_KEY, WAREHOUSE_API_URL

BATCH_SIZE = BATCH_SIZE


class WarehouseApiClient:
    def __init__(
        self,
        base_url: str = WAREHOUSE_API_URL,
        api_key: str = WAREHOUSE_API_KEY,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    @staticmethod
    def _is_retryable(status_code: int) -> bool:
        return status_code in {408, 429, 500, 502, 503, 504}

    def _retry_wait_seconds(self, response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return max(float(retry_after), 1.0)
            except ValueError:
                pass
        return min(BACKOFF_SECONDS * (2**attempt), 10.0)

    def dedupe_products(self, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()

        for item in products:
            sku = str(item.get("sku", "")).strip()
            if not sku or sku in seen:
                continue
            seen.add(sku)
            unique.append(item)

        return unique

    def _send_batch(self, batch: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {"products": batch}
        headers = {"X-API-Key": self.api_key}

        for attempt in range(MAX_RETRIES + 1):
            response = httpx.post(
                f"{self.base_url}/products/batch",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if self._is_retryable(response.status_code) and attempt < MAX_RETRIES:
                time.sleep(self._retry_wait_seconds(response, attempt))
                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError(f"Failed to send batch of {len(batch)} products after {MAX_RETRIES} retries")

    def send_products(self, products: list[dict[str, Any]]) -> dict[str, Any]:
        unique_products = self.dedupe_products(products)
        accepted: list[str] = []
        rejected: list[dict[str, Any]] = []

        for start in range(0, len(unique_products), BATCH_SIZE):
            batch = unique_products[start : start + BATCH_SIZE]
            response = self._send_batch(batch)
            accepted.extend(response.get("accepted", []))
            rejected.extend(response.get("rejected", []))

        return {
            "accepted": accepted,
            "rejected": rejected,
            "batch_count": math.ceil(len(unique_products) / BATCH_SIZE) if unique_products else 0,
        }


def send_products(products):
    return WarehouseApiClient().send_products(products)
