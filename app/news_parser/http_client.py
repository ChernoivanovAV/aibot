"""Shared HTTP client wrapper for parsers."""

import requests
from typing import Optional

def get(
    url: str,
    *,  # передавать параметры только по имени
    headers: Optional[dict] = None,
    timeout: int = 10,
) -> requests.Response:
    """Return a simple GET response using `requests`."""
    return requests.get(
        url=url,
        headers=headers,
        timeout=timeout,
    )
