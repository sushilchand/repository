import time
from typing import Any

import httpx

from app.config import BACKOFF_SECONDS, MAX_RETRIES, PAGE_SIZE, PRODUCT_API_KEY, PRODUCT_API_URL

PAGE_SIZE = PAGE_SIZE


class ProductApiClient:
    def __init__(
        self,
        base_url: str = PRODUCT_API_URL,
        api_key: str = PRODUCT_API_KEY,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _retry_wait_seconds(self, response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return max(float(retry_after), 1.0)
            except ValueError:
                pass
        return min(BACKOFF_SECONDS * (2**attempt), 10.0)

    @staticmethod
    def _is_retryable(status_code: int) -> bool:
        return status_code in {408, 429, 500, 502, 503, 504}

    def fetch_page(self, page: int, page_size: int = PAGE_SIZE) -> dict[str, Any]:
        if page < 1:
            raise ValueError("page must be at least 1")

        params = {"page": page, "page_size": page_size}
        headers = {"X-API-Key": self.api_key}

        for attempt in range(MAX_RETRIES + 1):
            response = httpx.get(
                f"{self.base_url}/products",
                params=params,
                headers=headers,
                timeout=self.timeout,
            )

            if self._is_retryable(response.status_code) and attempt < MAX_RETRIES:
                time.sleep(self._retry_wait_seconds(response, attempt))
                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError(f"Failed to fetch page {page} after {MAX_RETRIES} retries")

    def fetch_all_products(self, page_size: int = PAGE_SIZE) -> list[dict[str, Any]]:
        products: list[dict[str, Any]] = []
        page = 1

        while True:
            payload = self.fetch_page(page, page_size)
            page_products = payload.get("products", [])
            products.extend(page_products)

            if not payload.get("has_next"):
                return products

            page = int(payload.get("next_page") or page + 1)


def fetch_all_products() -> list[dict[str, Any]]:
    return ProductApiClient().fetch_all_products()
